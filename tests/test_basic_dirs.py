import importlib
from pathlib import Path


def _reload_basic_dirs():
    """Reload utils.basic_dirs to re-evaluate env overrides in each test."""
    import utils.basic_dirs as bd
    importlib.reload(bd)
    return bd


def test_constants_and_functions_types():
    import utils.basic_dirs as bd
    # 常量类型
    assert isinstance(bd.ROOT_DIR, Path)
    assert isinstance(bd.DATA_DIR, Path)
    assert isinstance(bd.CONFIG_DIR, Path)
    # 语法糖函数返回 Path
    p = bd.DATA("x", "y")
    assert isinstance(p, Path)
    assert p.as_posix().endswith("x/y")


def test_env_override_for_data(tmp_path, monkeypatch):
    monkeypatch.setenv("CLASS_DATA_DIR", str(tmp_path / "data_override"))
    bd = _reload_basic_dirs()
    assert bd.DATA_DIR == tmp_path / "data_override"
    assert bd.DATA("a", "b.txt") == tmp_path / "data_override" / "a" / "b.txt"


def test_env_override_root_then_ensure(tmp_path, monkeypatch):
    # 覆盖项目根后，ensure_all_base_dirs 能够创建所有基础目录
    monkeypatch.setenv("CLASS_MANAGER_ROOT", str(tmp_path))
    bd = _reload_basic_dirs()
    bd.ensure_all_base_dirs()
    for d in [
        bd.DATA_DIR,
        bd.CONFIG_DIR,
        bd.LOGS_DIR,
        bd.CACHE_DIR,
        bd.TMP_DIR,
        bd.UI_DIR,
        bd.QML_DIR,
        bd.RES_DIR,
        bd.TESTS_DIR,
        bd.SCRIPTS_DIR,
    ]:
        assert d.exists(), f"{d} should exist after ensure_all_base_dirs()"


def test_touch_in_creates_file(tmp_path, monkeypatch):
    monkeypatch.setenv("CLASS_TMP_DIR", str(tmp_path / "tmp"))
    bd = _reload_basic_dirs()
    file_path = bd.touch_in(bd.TMP_DIR, "nested", "file.txt")
    assert file_path.is_file()
    assert file_path.parent.exists()