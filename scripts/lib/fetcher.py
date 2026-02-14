import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser


class Fetcher:
    def __init__(
        self,
        cache_dir=None,
        user_agent="bbhai-catalog/0.1",
        timeout_seconds=15,
        max_retries=2,
        backoff_seconds=1.0,
        min_delay_seconds=0.0,
        max_requests_per_domain=10,
        max_bytes_per_domain=None,
        allow_domains=None,
        robots_mode=True,
        public_only=False,
    ):
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.min_delay_seconds = min_delay_seconds
        self.max_requests_per_domain = max_requests_per_domain
        self.max_bytes_per_domain = max_bytes_per_domain
        self.allow_domains = set(item.lower() for item in allow_domains or [])
        self.robots_mode = robots_mode
        self.public_only = public_only

        self._last_request = {}
        self._domain_requests = {}
        self._domain_bytes = {}
        self._robots = {}

        self.metrics = {
            "requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "failures": 0,
            "retries": 0,
            "throttle_sleeps": 0,
            "domains": {},
        }

    def _domain_metrics(self, domain):
        metrics = self.metrics["domains"].setdefault(
            domain,
            {
                "requests": 0,
                "cache_hits": 0,
                "failures": 0,
                "retries": 0,
                "total_time_ms": 0,
                "bytes": 0,
            },
        )
        return metrics

    def _cache_paths(self, url):
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        parsed = urlparse(url)
        host = parsed.netloc.replace(":", "_") or "unknown"
        base = Path(host) / digest
        body_path = base.with_suffix(".body")
        meta_path = base.with_suffix(".json")
        return body_path, meta_path

    def _read_cache(self, url):
        if not self.cache_dir:
            return None, None
        body_path, meta_path = self._cache_paths(url)
        body_path = self.cache_dir / body_path
        meta_path = self.cache_dir / meta_path
        if not body_path.exists() or not meta_path.exists():
            return None, None
        body = body_path.read_bytes()
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        metadata["from_cache"] = True
        return body, metadata

    def _write_cache(self, url, body, metadata):
        if not self.cache_dir:
            return
        body_path, meta_path = self._cache_paths(url)
        body_path = self.cache_dir / body_path
        meta_path = self.cache_dir / meta_path
        body_path.parent.mkdir(parents=True, exist_ok=True)
        body_path.write_bytes(body)
        meta_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    def _enforce_budget(self, domain, size_bytes):
        count = self._domain_requests.get(domain, 0) + 1
        self._domain_requests[domain] = count
        if self.max_requests_per_domain and count > self.max_requests_per_domain:
            raise SystemExit(f"Request budget exceeded for domain: {domain}")

        if self.max_bytes_per_domain is None:
            return
        total_bytes = self._domain_bytes.get(domain, 0) + size_bytes
        self._domain_bytes[domain] = total_bytes
        if total_bytes > self.max_bytes_per_domain:
            raise SystemExit(f"Byte budget exceeded for domain: {domain}")

    def _throttle(self, domain):
        if not self.min_delay_seconds:
            return
        last = self._last_request.get(domain)
        if last is None:
            return
        elapsed = time.time() - last
        remaining = self.min_delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)
            self.metrics["throttle_sleeps"] += 1

    def _check_allowlist(self, url):
        parsed = urlparse(url)
        if self.public_only and parsed.scheme not in ("http", "https"):
            raise SystemExit(f"Blocked non-public URL: {url}")
        domain = parsed.netloc.lower()
        if self.allow_domains and domain not in self.allow_domains:
            raise SystemExit(f"Domain not allowlisted: {domain}")
        return domain

    def _robots_allowed(self, domain, url):
        if not self.robots_mode:
            return True
        parser = self._robots.get(domain)
        if parser is None:
            robots_url = f"https://{domain}/robots.txt"
            parser = RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
            except Exception:
                return False
            self._robots[domain] = parser
        return parser.can_fetch(self.user_agent, url)

    def fetch_text(self, url):
        domain = self._check_allowlist(url)
        if not self._robots_allowed(domain, url):
            raise SystemExit(f"Robots policy disallows URL: {url}")

        cached_body, cached_meta = self._read_cache(url)
        if cached_body is not None:
            self.metrics["cache_hits"] += 1
            self._domain_metrics(domain)["cache_hits"] += 1
            return cached_body.decode("utf-8", errors="replace"), cached_meta

        self.metrics["cache_misses"] += 1
        self._throttle(domain)

        headers = {"User-Agent": self.user_agent}
        request = Request(url, headers=headers)
        attempt = 0
        while True:
            start = time.perf_counter()
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    body = response.read()
                    elapsed_ms = int((time.perf_counter() - start) * 1000)
                    size_bytes = len(body)
                    self._enforce_budget(domain, size_bytes)
                    metadata = {
                        "url": url,
                        "status": response.status,
                        "headers": dict(response.headers),
                        "fetched_at": time.strftime(
                            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                        ),
                        "elapsed_ms": elapsed_ms,
                        "content_length": size_bytes,
                        "from_cache": False,
                    }
                    self._write_cache(url, body, metadata)

                    self.metrics["requests"] += 1
                    domain_metrics = self._domain_metrics(domain)
                    domain_metrics["requests"] += 1
                    domain_metrics["total_time_ms"] += elapsed_ms
                    domain_metrics["bytes"] += size_bytes
                    self._last_request[domain] = time.time()

                    return body.decode("utf-8", errors="replace"), metadata
            except Exception:
                self.metrics["failures"] += 1
                domain_metrics = self._domain_metrics(domain)
                domain_metrics["failures"] += 1
                if attempt >= self.max_retries:
                    raise
                attempt += 1
                self.metrics["retries"] += 1
                domain_metrics["retries"] += 1
                time.sleep(self.backoff_seconds * (2 ** (attempt - 1)))
