import pytest
from pytest import CaptureFixture
from ghrm.display import display_result, display_list, display_empty

@pytest.fixture
def capture_output(capsys: CaptureFixture):
    """Fixture to capture stdout and stderr"""
    return capsys

def test_display_list_empty_items(capture_output):
    """Test display_list with empty items list"""
    display_list("Empty List", [], ["Column1", "Column2"])
    captured = capture_output.readouterr()
    assert "Empty List" in captured.out
    assert "Column1" in captured.out
    assert "Column2" in captured.out

def test_display_list_invalid_columns(capture_output):
    """Test display_list with mismatched columns"""
    items = [("item1", "desc1")]
    columns = ["Column1"]
    display_list("Invalid List", items, columns)
    captured = capture_output.readouterr()
    assert "Invalid List" in captured.out
    assert "Column1" in captured.out
    assert "item1" in captured.out
    assert "desc1" in captured.out
