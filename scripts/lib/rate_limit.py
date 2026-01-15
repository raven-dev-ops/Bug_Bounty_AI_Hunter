import threading
import time


class RateLimiter:
    def __init__(self, min_delay_seconds):
        self.min_delay_seconds = max(0.0, float(min_delay_seconds or 0))
        self._lock = threading.Lock()
        self._last = 0.0

    def wait(self):
        if self.min_delay_seconds <= 0:
            return
        with self._lock:
            now = time.time()
            delay = self.min_delay_seconds - (now - self._last)
            if delay > 0:
                time.sleep(delay)
            self._last = time.time()
