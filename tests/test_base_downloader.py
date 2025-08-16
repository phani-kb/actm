from actm.downloaders.base_downloader import _save_to_file
from actm.common.enums import DataSaveFormat


def test_save_to_file_csv(tmp_path):
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    file_path = tmp_path / "test.csv"
    _save_to_file(data, str(file_path), DataSaveFormat.CSV)
    content = file_path.read_text()
    assert "a" in content and "b" in content
    assert "1" in content and "4" in content


def test_save_to_file_csv_empty(tmp_path):
    data = []
    file_path = tmp_path / "empty.csv"
    _save_to_file(data, str(file_path), DataSaveFormat.CSV)
    content = file_path.read_text()
    assert content == ""


def test_save_to_file_json(tmp_path):
    data = [{"x": 10}]
    file_path = tmp_path / "test.json"
    _save_to_file(data, str(file_path), DataSaveFormat.JSON)
    content = file_path.read_text()
    assert "x" in content and "10" in content
