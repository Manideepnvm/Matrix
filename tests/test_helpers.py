
import os
import tempfile
from utils import helpers


def test_clean_query():
    assert helpers.clean_query("  Hello WORLD  ") == "hello world"
    assert helpers.clean_query(None) is None


def test_check_file_and_folder_exists():
    # Create a temporary file and folder
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = os.path.join(tmpdir, "sample.txt")
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write("hello")

        assert helpers.check_file_exists(tmp_file) is True
        assert helpers.check_folder_exists(tmpdir) is True

        # Non-existent
        assert helpers.check_file_exists(os.path.join(tmpdir, "nope.txt")) is False


def test_get_file_and_folder_size():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = os.path.join(tmpdir, "sample.txt")
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write("a" * 1024 * 10)  # ~10 KB

        size = helpers.get_file_size(tmp_file)
        assert size is not None and size > 0

        folder_size = helpers.get_folder_size(tmpdir)
        assert folder_size is not None and folder_size > 0


def test_current_time_and_date():
    t = helpers.get_current_time()
    d = helpers.get_current_date()
    assert isinstance(t, str) and len(t) > 0
    assert isinstance(d, str) and len(d) > 0


def test_contains_keyword():
    assert helpers.contains_keyword("Open Chrome and search", "chrome") is True
    assert helpers.contains_keyword("Open Chrome and search", ["firefox", "chrome"]) is True
    assert helpers.contains_keyword(12345, "test") is False
