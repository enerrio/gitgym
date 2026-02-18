from click.testing import CliRunner

from gitgym.cli import main


def test_help_exits_zero():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0


def test_help_contains_usage():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "Usage:" in result.output


def test_help_contains_description():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "gitgym" in result.output.lower()
