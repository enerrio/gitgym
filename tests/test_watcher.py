"""Tests for the polling-based watcher module."""

import threading
from pathlib import Path
from unittest import mock

from click.testing import CliRunner

import gitgym.watcher as watcher_module
from gitgym.exercise import Exercise
from gitgym.watcher import (
    POLL_INTERVAL,
    _HAS_WATCHDOG,
    _collect_mtimes,
    _has_changed,
    _watch_with_polling,
    _watch_with_watchdog,
    watch,
    watch_and_verify,
)


def _make_exercise(exercise_dir: Path, name: str = "test_exercise") -> Exercise:
    """Create an Exercise instance pointing at exercise_dir."""
    return Exercise(
        name=name,
        topic="Test",
        title="Test Exercise",
        description="A test exercise.",
        goal_summary="A test goal.",
        hints=[],
        path=exercise_dir,
    )


# --- _collect_mtimes tests ---


def test_collect_mtimes_empty_for_missing_directory(tmp_path):
    missing = tmp_path / "nonexistent"
    assert _collect_mtimes(missing) == {}


def test_collect_mtimes_empty_for_empty_directory(tmp_path):
    assert _collect_mtimes(tmp_path) == {}


def test_collect_mtimes_returns_entry_for_file(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("hi")
    mtimes = _collect_mtimes(tmp_path)
    assert f in mtimes
    assert isinstance(mtimes[f], float)


def test_collect_mtimes_returns_entries_for_multiple_files(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    mtimes = _collect_mtimes(tmp_path)
    assert len(mtimes) == 2


def test_collect_mtimes_recurses_into_subdirectories(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    f = sub / "nested.txt"
    f.write_text("nested")
    mtimes = _collect_mtimes(tmp_path)
    assert f in mtimes


def test_collect_mtimes_does_not_include_directories(tmp_path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    mtimes = _collect_mtimes(tmp_path)
    assert sub not in mtimes


# --- _has_changed tests ---


def test_has_changed_returns_false_for_identical_dicts(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("content")
    mtime = f.stat().st_mtime
    prev = {f: mtime}
    curr = {f: mtime}
    assert _has_changed(prev, curr) is False


def test_has_changed_returns_true_when_mtime_differs(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("content")
    prev = {f: 1000.0}
    curr = {f: 2000.0}
    assert _has_changed(prev, curr) is True


def test_has_changed_returns_true_when_file_added(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    prev = {f1: 1000.0}
    curr = {f1: 1000.0, f2: 2000.0}
    assert _has_changed(prev, curr) is True


def test_has_changed_returns_true_when_file_removed(tmp_path):
    f1 = tmp_path / "a.txt"
    prev = {f1: 1000.0}
    curr = {}
    assert _has_changed(prev, curr) is True


def test_has_changed_returns_false_for_empty_dicts():
    assert _has_changed({}, {}) is False


# --- watch generator tests ---


def test_poll_interval_default_is_one_second():
    assert POLL_INTERVAL == 1


def _make_watch_gen(tmp_path, mtime_sequence):
    """Helper: build a watch() generator whose _collect_mtimes returns values
    from *mtime_sequence* in order (last value repeated once exhausted)."""
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace" / "01_basics" / "01_init"
    workspace_dir.mkdir(parents=True)

    exercise = _make_exercise(exercises_dir)

    idx = 0

    def fake_collect(_directory):
        nonlocal idx
        val = mtime_sequence[min(idx, len(mtime_sequence) - 1)]
        idx += 1
        return val

    patches = [
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch("gitgym.watcher.time.sleep"),
        mock.patch("gitgym.watcher._collect_mtimes", side_effect=fake_collect),
    ]

    return exercise, patches


def test_watch_yields_on_file_change(tmp_path):
    """Generator yields when mtime dict changes between polls."""
    f = tmp_path / "workspace" / "01_basics" / "01_init" / "file.txt"
    # Sequence: initial collection (empty) → first poll (file appears)
    state_before = {}
    state_after = {f: 1.0}

    exercise, patches = _make_watch_gen(tmp_path, [state_before, state_after])

    with patches[0], patches[1], patches[2], patches[3]:
        gen = watch(exercise, poll_interval=0)
        # First next() should yield because state changed
        next(gen)  # raises StopIteration only if generator is exhausted


def test_watch_does_not_yield_when_no_change(tmp_path):
    """Generator does not yield when mtime dict is stable."""
    f = tmp_path / "workspace" / "01_basics" / "01_init" / "file.txt"
    state = {f: 1.0}

    # All polls return the same state → no change → generator never yields
    # We use a finite sequence to avoid an infinite loop: simulate two identical
    # consecutive polls then raise StopIteration from our side.

    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace" / "01_basics" / "01_init"
    workspace_dir.mkdir(parents=True)

    exercise = _make_exercise(exercises_dir)

    call_count = 0

    def fake_collect(_directory):
        nonlocal call_count
        call_count += 1
        return dict(state)  # same every time

    yielded = []

    with (
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch("gitgym.watcher.time.sleep"),
        mock.patch("gitgym.watcher._collect_mtimes", side_effect=fake_collect),
    ):
        gen = watch(exercise, poll_interval=0)

        import threading

        def _drive():
            try:
                # This will block forever (or until interrupted) because no
                # change is ever detected.
                next(gen)
                yielded.append(True)
            except StopIteration:
                yielded.append(False)

        t = threading.Thread(target=_drive, daemon=True)
        t.start()
        # Give the thread a little time to run through several iterations
        t.join(timeout=0.3)

        # Thread should still be running (blocked), meaning no yield happened
        assert t.is_alive(), "watcher yielded unexpectedly when no change occurred"
        assert yielded == []


def test_watch_yields_again_after_second_change(tmp_path):
    """Generator yields each time a new change is detected."""
    f = tmp_path / "workspace" / "01_basics" / "01_init" / "file.txt"
    state_a = {f: 1.0}
    state_b = {f: 2.0}
    state_c = {f: 3.0}

    exercise, patches = _make_watch_gen(tmp_path, [state_a, state_b, state_c])

    with patches[0], patches[1], patches[2], patches[3]:
        gen = watch(exercise, poll_interval=0)
        # First yield: state_a (initial) → state_b
        next(gen)
        # Second yield: state_b → state_c
        next(gen)  # should not raise StopIteration


def test_watch_workspace_path_is_derived_from_exercise(tmp_path):
    """watch() watches the correct workspace subdirectory for the exercise."""
    exercises_dir = tmp_path / "exercises" / "02_committing" / "01_amend"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace" / "02_committing" / "01_amend"
    workspace_dir.mkdir(parents=True)

    exercise = _make_exercise(exercises_dir)

    collected_dirs = []

    def fake_collect(directory):
        collected_dirs.append(directory)
        # Change on second call so the generator yields and we can stop
        if len(collected_dirs) == 1:
            return {}
        return {directory / "x": 1.0}

    with (
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch("gitgym.watcher.time.sleep"),
        mock.patch("gitgym.watcher._collect_mtimes", side_effect=fake_collect),
    ):
        gen = watch(exercise, poll_interval=0)
        next(gen)

    expected = tmp_path / "workspace" / "02_committing" / "01_amend"
    assert all(d == expected for d in collected_dirs)


# --- watch_and_verify tests ---


def _setup_watch_and_verify(tmp_path):
    """Set up directories and return an exercise for watch_and_verify tests."""
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace" / "01_basics" / "01_init"
    workspace_dir.mkdir(parents=True)
    exercise = _make_exercise(exercises_dir)
    return exercise


def test_watch_and_verify_stops_on_success(tmp_path):
    """watch_and_verify returns after verify.sh succeeds."""
    exercise = _setup_watch_and_verify(tmp_path)
    f = tmp_path / "workspace" / "01_basics" / "01_init" / "file.txt"

    change_sequence = [{}, {f: 1.0}]
    idx = 0

    def fake_collect(_directory):
        nonlocal idx
        val = change_sequence[min(idx, len(change_sequence) - 1)]
        idx += 1
        return val

    with (
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch("gitgym.watcher.time.sleep"),
        mock.patch("gitgym.watcher._collect_mtimes", side_effect=fake_collect),
        mock.patch("gitgym.watcher.run_verify", return_value=(True, "Great job!")),
    ):
        # Should return without raising
        watch_and_verify(exercise, poll_interval=0)


def test_watch_and_verify_calls_on_completed_callback(tmp_path):
    """watch_and_verify invokes on_completed when verify succeeds."""
    exercise = _setup_watch_and_verify(tmp_path)
    f = tmp_path / "workspace" / "01_basics" / "01_init" / "file.txt"

    change_sequence = [{}, {f: 1.0}]
    idx = 0

    def fake_collect(_directory):
        nonlocal idx
        val = change_sequence[min(idx, len(change_sequence) - 1)]
        idx += 1
        return val

    completed = []

    with (
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch("gitgym.watcher.time.sleep"),
        mock.patch("gitgym.watcher._collect_mtimes", side_effect=fake_collect),
        mock.patch("gitgym.watcher.run_verify", return_value=(True, "Done!")),
    ):
        watch_and_verify(
            exercise, poll_interval=0, on_completed=lambda: completed.append(True)
        )

    assert completed == [True]


def test_watch_and_verify_does_not_call_on_completed_on_failure(tmp_path):
    """watch_and_verify does not invoke on_completed when verify fails."""
    exercise = _setup_watch_and_verify(tmp_path)
    f = tmp_path / "workspace" / "01_basics" / "01_init" / "file.txt"

    # Two changes: both fail; we stop after two by raising KeyboardInterrupt
    call_count = 0

    def fake_collect(_directory):
        nonlocal call_count
        call_count += 1
        # Alternate between two states to produce two changes
        return {f: float(call_count)}

    completed = []

    def fake_verify(_exercise):
        return (False, "Not done yet.")

    # We stop after the second failure via KeyboardInterrupt from our side
    verify_calls = []

    def counting_verify(_exercise):
        verify_calls.append(1)
        if len(verify_calls) >= 2:
            raise KeyboardInterrupt
        return (False, "Not done yet.")

    with (
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch("gitgym.watcher.time.sleep"),
        mock.patch("gitgym.watcher._collect_mtimes", side_effect=fake_collect),
        mock.patch("gitgym.watcher.run_verify", side_effect=counting_verify),
    ):
        watch_and_verify(
            exercise, poll_interval=0, on_completed=lambda: completed.append(True)
        )

    assert completed == []


def test_watch_and_verify_continues_after_failed_verify(tmp_path):
    """watch_and_verify keeps watching after a failed verify and stops on success."""
    exercise = _setup_watch_and_verify(tmp_path)
    f = tmp_path / "workspace" / "01_basics" / "01_init" / "file.txt"

    call_count = 0

    def fake_collect(_directory):
        nonlocal call_count
        call_count += 1
        return {f: float(call_count)}

    verify_calls = []

    def fake_verify(_exercise):
        verify_calls.append(1)
        # Fail first, succeed second
        if len(verify_calls) == 1:
            return (False, "Not yet.")
        return (True, "Done!")

    completed = []

    with (
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch("gitgym.watcher.time.sleep"),
        mock.patch("gitgym.watcher._collect_mtimes", side_effect=fake_collect),
        mock.patch("gitgym.watcher.run_verify", side_effect=fake_verify),
    ):
        watch_and_verify(
            exercise, poll_interval=0, on_completed=lambda: completed.append(True)
        )

    assert len(verify_calls) == 2
    assert completed == [True]


def test_watch_and_verify_stops_on_keyboard_interrupt(tmp_path):
    """watch_and_verify returns gracefully when interrupted by Ctrl-C."""
    exercise = _setup_watch_and_verify(tmp_path)

    def fake_collect(_directory):
        # Never change → generator never yields; KeyboardInterrupt fires from sleep
        return {}

    sleep_calls = []

    def fake_sleep(_t):
        sleep_calls.append(1)
        if len(sleep_calls) >= 2:
            raise KeyboardInterrupt

    with (
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch("gitgym.watcher.time.sleep", side_effect=fake_sleep),
        mock.patch("gitgym.watcher._collect_mtimes", side_effect=fake_collect),
    ):
        # Should not raise
        watch_and_verify(exercise, poll_interval=0)


# --- watchdog dispatch tests ---


def test_has_watchdog_flag_is_bool():
    """_HAS_WATCHDOG must be a plain bool (True when watchdog installed, else False)."""
    assert isinstance(_HAS_WATCHDOG, bool)


def test_watch_dispatches_to_polling_when_flag_false(tmp_path):
    """watch() delegates to _watch_with_polling when _HAS_WATCHDOG is False."""
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    exercise = _make_exercise(exercises_dir)

    polling_calls = []

    def fake_polling(ex, poll_interval=POLL_INTERVAL):
        polling_calls.append(ex)
        return
        yield  # make it a generator

    with (
        mock.patch("gitgym.watcher._HAS_WATCHDOG", False),
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch("gitgym.watcher._watch_with_polling", side_effect=fake_polling),
    ):
        gen = watch(exercise, poll_interval=0)
        try:
            next(gen)
        except StopIteration:
            pass

    assert polling_calls == [exercise]


def test_watch_dispatches_to_watchdog_when_flag_true(tmp_path):
    """watch() delegates to _watch_with_watchdog when _HAS_WATCHDOG is True."""
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    exercise = _make_exercise(exercises_dir)

    watchdog_calls = []

    def fake_watchdog(ex):
        watchdog_calls.append(ex)
        return
        yield  # make it a generator

    with (
        mock.patch("gitgym.watcher._HAS_WATCHDOG", True),
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch("gitgym.watcher._watch_with_watchdog", side_effect=fake_watchdog),
    ):
        gen = watch(exercise, poll_interval=0)
        try:
            next(gen)
        except StopIteration:
            pass

    assert watchdog_calls == [exercise]


def test_watch_with_watchdog_yields_on_event(tmp_path):
    """_watch_with_watchdog yields each time the Observer fires an event."""
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace" / "01_basics" / "01_init"
    workspace_dir.mkdir(parents=True)

    exercise = _make_exercise(exercises_dir)

    # A minimal mock Observer that fires one event by setting the Event
    # immediately when start() is called.
    class _InstantObserver:
        def __init__(self):
            self._handler = None

        def schedule(self, handler, path, recursive=False):
            self._handler = handler

        def start(self):
            # Simulate an immediate filesystem event
            self._handler._change_event.set()

        def stop(self):
            pass

        def join(self):
            pass

    # A minimal mock handler class that accepts change_event in its constructor
    class _MockHandler:
        def __init__(self, change_event):
            self._change_event = change_event

    with (
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch.object(watcher_module, "_Observer", _InstantObserver, create=True),
        mock.patch.object(watcher_module, "_ChangeHandler", _MockHandler, create=True),
    ):
        gen = _watch_with_watchdog(exercise)
        # Should yield immediately because the mock observer fires an event on start()
        next(gen)


def test_watch_with_watchdog_observer_stopped_on_generator_close(tmp_path):
    """Observer.stop() and join() are called when the watchdog generator is closed."""
    exercises_dir = tmp_path / "exercises" / "01_basics" / "01_init"
    exercises_dir.mkdir(parents=True)
    workspace_dir = tmp_path / "workspace" / "01_basics" / "01_init"
    workspace_dir.mkdir(parents=True)

    exercise = _make_exercise(exercises_dir)

    stopped = []
    joined = []

    class _MockObserver:
        def __init__(self):
            self._handler = None

        def schedule(self, handler, path, recursive=False):
            self._handler = handler

        def start(self):
            self._handler._change_event.set()

        def stop(self):
            stopped.append(True)

        def join(self):
            joined.append(True)

    class _MockHandler:
        def __init__(self, change_event):
            self._change_event = change_event

    with (
        mock.patch("gitgym.watcher.EXERCISES_DIR", tmp_path / "exercises"),
        mock.patch("gitgym.watcher.WORKSPACE_DIR", tmp_path / "workspace"),
        mock.patch.object(watcher_module, "_Observer", _MockObserver, create=True),
        mock.patch.object(watcher_module, "_ChangeHandler", _MockHandler, create=True),
    ):
        gen = _watch_with_watchdog(exercise)
        next(gen)  # consume first yield
        gen.close()  # trigger finally block

    assert stopped == [True]
    assert joined == [True]
