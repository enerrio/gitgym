import json
from pathlib import Path
from unittest import mock

from gitgym.progress import load_progress, save_progress


def _patch_progress_file(tmp_path: Path):
    """Return a context manager patching PROGRESS_FILE to a temp path."""
    return mock.patch("gitgym.progress.PROGRESS_FILE", tmp_path / "progress.json")


def test_load_progress_missing_file_returns_default(tmp_path):
    with _patch_progress_file(tmp_path):
        result = load_progress()
    assert result == {"version": 1, "exercises": {}}


def test_load_progress_existing_file_returns_data(tmp_path):
    progress_file = tmp_path / "progress.json"
    data = {
        "version": 1,
        "exercises": {
            "01_basics/01_init": {
                "status": "completed",
                "completed_at": "2026-02-16T10:30:00Z",
                "hints_used": 0,
            }
        },
    }
    progress_file.write_text(json.dumps(data))

    with mock.patch("gitgym.progress.PROGRESS_FILE", progress_file):
        result = load_progress()

    assert result == data


def test_save_progress_writes_json(tmp_path):
    progress_file = tmp_path / "progress.json"
    data = {"version": 1, "exercises": {"01_basics/01_init": {"status": "in_progress"}}}

    with mock.patch("gitgym.progress.PROGRESS_FILE", progress_file):
        save_progress(data)

    assert progress_file.exists()
    with open(progress_file) as f:
        loaded = json.load(f)
    assert loaded == data


def test_save_progress_creates_parent_dirs(tmp_path):
    progress_file = tmp_path / "nested" / "dir" / "progress.json"
    data = {"version": 1, "exercises": {}}

    with mock.patch("gitgym.progress.PROGRESS_FILE", progress_file):
        save_progress(data)

    assert progress_file.exists()


def test_save_and_load_roundtrip(tmp_path):
    progress_file = tmp_path / "progress.json"
    data = {
        "version": 1,
        "exercises": {
            "01_basics/01_init": {
                "status": "completed",
                "completed_at": "2026-02-16T10:30:00Z",
                "hints_used": 2,
            },
            "01_basics/02_staging": {
                "status": "in_progress",
                "started_at": "2026-02-16T11:00:00Z",
                "hints_used": 0,
            },
        },
    }

    with mock.patch("gitgym.progress.PROGRESS_FILE", progress_file):
        save_progress(data)
        result = load_progress()

    assert result == data
