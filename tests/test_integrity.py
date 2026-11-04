from fsociety.modules.integrity import check_integrity, create_baseline


def test_baseline_detects_change_new_and_deleted(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "keep.txt").write_text("one", encoding="utf-8")
    (root / "delete.txt").write_text("old", encoding="utf-8")
    baseline_path = tmp_path / "baseline.json"
    baseline = create_baseline(root, baseline_path)
    assert "keep.txt" in baseline["files"]
    (root / "keep.txt").write_text("two", encoding="utf-8")
    (root / "delete.txt").unlink()
    (root / "new.txt").write_text("new", encoding="utf-8")
    result = check_integrity(root, baseline_path)
    assert result["modified"] == ["keep.txt"]
    assert result["deleted"] == ["delete.txt"]
    assert result["new"] == ["new.txt"]
    assert result["ok"] is False


def test_unchanged_baseline(tmp_path):
    (tmp_path / "a").write_text("a", encoding="utf-8")
    baseline = create_baseline(tmp_path)
    assert check_integrity(tmp_path, baseline)["ok"] is True
