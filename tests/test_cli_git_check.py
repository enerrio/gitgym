"""Tests for the git-installed check in cli.py."""

import subprocess
from unittest.mock import patch

import click
from click.testing import CliRunner

from gitgym.cli import GitGymGroup, _is_git_installed, main


def test_is_git_installed_true():
    """_is_git_installed returns True when git is on PATH and exits 0."""
    assert _is_git_installed() is True


def test_is_git_installed_false_when_not_on_path():
    """_is_git_installed returns False when git is not found on PATH."""
    with patch("shutil.which", return_value=None):
        assert _is_git_installed() is False


def test_is_git_installed_false_when_subprocess_fails():
    """_is_git_installed returns False when git --version returns non-zero."""
    mock_result = subprocess.CompletedProcess(args=["git", "--version"], returncode=1)
    with patch("shutil.which", return_value="/usr/bin/git"):
        with patch("subprocess.run", return_value=mock_result):
            assert _is_git_installed() is False


def test_is_git_installed_false_on_os_error():
    """_is_git_installed returns False when subprocess.run raises OSError."""
    with patch("shutil.which", return_value="/usr/bin/git"):
        with patch("subprocess.run", side_effect=OSError("not found")):
            assert _is_git_installed() is False


def _make_test_app() -> click.BaseCommand:
    """Build a minimal app using GitGymGroup with one dummy subcommand for testing."""

    @click.group(cls=GitGymGroup)
    def app():
        """Test app."""

    @app.command()
    def dummy():
        click.echo("ok")

    return app


def test_git_check_passes_when_git_present():
    """When git is installed, subcommands run normally."""
    app = _make_test_app()
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=True):
        result = runner.invoke(app, ["dummy"])
    assert result.exit_code == 0
    assert "ok" in result.output


def test_git_check_fails_when_git_missing():
    """When git is not installed, subcommands exit 1 with an error message."""
    app = _make_test_app()
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=False):
        result = runner.invoke(app, ["dummy"])
    assert result.exit_code == 1
    assert "git is not installed" in result.output


def test_git_missing_error_includes_install_instructions():
    """Error output includes platform-specific install instructions."""
    app = _make_test_app()
    runner = CliRunner()
    with patch("gitgym.cli._is_git_installed", return_value=False):
        result = runner.invoke(app, ["dummy"])
    assert "brew install git" in result.output or "apt install git" in result.output


def test_main_uses_gitgym_group():
    """The main group uses the GitGymGroup class."""
    assert isinstance(main, GitGymGroup)
