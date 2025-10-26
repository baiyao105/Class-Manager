from __future__ import annotations

import os
from pathlib import Path

ROOT_HOME = Path(__file__).parent.parent.resolve()


def detect_root(start: Path | None = None) -> Path:
    """确定根目录"""
    env = os.getenv("ROOT_HOME")
    if env:
        try:
            return Path(env).expanduser().resolve()
        except Exception:
            pass
    cur = Path(start or ROOT_HOME)
    return cur.resolve()


def env_path(name: str, default: Path) -> Path:
    """环境变量优先"""
    val = os.getenv(name)
    try:
        return Path(val).expanduser().resolve() if val else default
    except Exception:
        return default


ROOT = detect_root()
DATA = env_path("DATA_DIR", ROOT / "data")
CONFIG = env_path("CONFIG_DIR", ROOT / "config")
LOGS = env_path("LOGS_DIR", ROOT / "logs")
CACHE = env_path("CACHE_DIR", ROOT / "cache")
TMP = env_path("TMP_DIR", ROOT / "tmp")
UI = env_path("UI_DIR", ROOT / "ui")
QML = env_path("QML_DIR", UI / "qml")
RES = env_path("RES_DIR", UI / "resources")
TESTS = env_path("TESTS_DIR", ROOT / "tests")
SCRIPTS = env_path("SCRIPTS_DIR", ROOT / "scripts")
_BASES = (DATA, CONFIG, LOGS, CACHE, TMP, UI, QML, RES, TESTS, SCRIPTS)


def ensure_dirs():
    for d in _BASES:
        d.mkdir(parents=True, exist_ok=True)


def touch_in(base: Path, *parts: str) -> Path:
    p = base.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)
    return p
