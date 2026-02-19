from click.testing import CliRunner

from gitgym import __version__
from gitgym.cli import main


def test_version_exits_zero():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0


def test_version_output_contains_version_string():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert __version__ in result.output


def test_version_output_contains_program_name():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert "gitgym" in result.output
