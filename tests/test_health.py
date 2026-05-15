import mockagent


def test_package_version_is_available() -> None:
    assert mockagent.__version__ == "0.1.0"
