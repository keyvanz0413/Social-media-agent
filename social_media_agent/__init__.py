"""Compatibility package loader for src layout."""
from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_src_pkg = _pkg_root.parent / "src" / "social_media_agent"
if _src_pkg.exists():
    __path__.append(str(_src_pkg))
