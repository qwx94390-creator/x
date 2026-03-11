from run_bot import _print_missing_dependency_help


def test_missing_dependency_help_mentions_quick_install(capsys) -> None:
    err = ModuleNotFoundError("No module named 'aiosqlite'")
    err.name = "aiosqlite"
    _print_missing_dependency_help(err)
    output = capsys.readouterr().err
    assert "aiosqlite" in output
    assert "pip install aiosqlite" in output
