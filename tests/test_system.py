from fsociety.core.platform import platform_info
from fsociety.modules.system import process_inventory


def test_process_inventory_is_list():
    assert isinstance(process_inventory(), list)


def test_platform_detection_has_common_fields():
    info = platform_info()
    assert info["system"]
    assert info["family"]
