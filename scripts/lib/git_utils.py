from pathlib import Path


def get_git_commit(repo_root=None):
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[2]
    head_path = root / ".git" / "HEAD"
    if not head_path.exists():
        return None
    head = head_path.read_text(encoding="utf-8").strip()
    if head.startswith("ref:"):
        ref = head.split(" ", 1)[1].strip()
        ref_path = root / ".git" / ref
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()
        return None
    return head or None
