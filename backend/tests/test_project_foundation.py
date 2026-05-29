import sys


def test_python_version():
    assert sys.version_info >= (3, 12), "Python 3.12+ is required"


def test_backend_app_is_importable():
    import backend.app

    assert hasattr(backend.app, "__version__")
    assert backend.app.__version__ is not None
