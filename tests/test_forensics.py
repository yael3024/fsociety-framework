import hashlib

from fsociety.modules.forensics import evidence_record, hash_file, inventory_files


def test_hashes_and_evidence(tmp_path):
    target = tmp_path / "evidence.bin"
    target.write_bytes(b"evidence")
    assert hash_file(target) == hashlib.sha256(b"evidence").hexdigest()
    record = evidence_record(target)
    assert record["sha512"] == hashlib.sha512(b"evidence").hexdigest()
    assert record["size"] == 8


def test_inventory_uses_relative_paths_and_hashes(tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "item.txt").write_text("hello", encoding="utf-8")
    items = inventory_files(tmp_path)
    assert items[0]["relative_path"] == "nested/item.txt"
    assert items[0]["sha256"] == hashlib.sha256(b"hello").hexdigest()
