from __future__ import annotations

import os
from pathlib import Path

CLASS_MANAGER_ROOT = Path(__file__).parent.parent.resolve()


def detect_root(start: Path | None = None) -> Path:
    """确定项目根目录"""
    env = os.getenv("CLASS_MANAGER_ROOT")
    if env:
        try:
            return Path(env).expanduser().resolve()
        except Exception:
            pass
    cur = Path(start or CLASS_MANAGER_ROOT)
    return cur.resolve()


def env_path(name: str, default: Path) -> Path:
    """环境变量优先"""
    val = os.getenv(name)
    try:
        return Path(val).expanduser().resolve() if val else default
    except Exception:
        return default


ROOT = detect_root()
DATA = env_path("CLASS_DATA_DIR", ROOT / "data")
CONFIG = env_path("CLASS_CONFIG_DIR", ROOT / "config")
LOGS = env_path("CLASS_LOGS_DIR", ROOT / "logs")
CACHE = env_path("CLASS_CACHE_DIR", ROOT / "cache")
TMP = env_path("CLASS_TMP_DIR", ROOT / "tmp")
UI = env_path("CLASS_UI_DIR", ROOT / "ui")
QML = env_path("CLASS_QML_DIR", UI / "qml")
RES = env_path("CLASS_RES_DIR", UI / "resources")
TESTS = env_path("CLASS_TESTS_DIR", ROOT / "tests")
SCRIPTS = env_path("CLASS_SCRIPTS_DIR", ROOT / "scripts")
_BASES = (DATA, CONFIG, LOGS, CACHE, TMP, UI, QML, RES, TESTS, SCRIPTS)


def ensure_dirs():
    for d in _BASES:
        d.mkdir(parents=True, exist_ok=True)


def touch_in(base: Path, *parts: str) -> Path:
    p = base.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)
    return p
