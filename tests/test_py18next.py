import pytest

import py18next


@pytest.fixture
def instance():
    return py18next.create({"bar": "foo"})


def test_create(instance):
    assert instance.options.bar == "foo"


@pytest.fixture
def instance_with_init(instance):
    return instance.init({"foo": "bar"})


def test_init(instance_with_init):
    instance = instance_with_init
    assert instance.options.foo == "bar"
    assert instance.options.bar == "foo"


@pytest.fixture
def instance_with_defaults():
    return py18next.Py18Next(
        {
            "backend": {"load_path": "./tests/files/simple/{locale}.json"},
            "fallback_locale": "en",
            "resources": {
                "en": {
                    "translation": {
                        "key": "normal",
                        "key_null": None,
                        "key_empty": "",
                    }
                }
            },
        }
    )


def test_defaults(instance_with_defaults):
    p18 = instance_with_defaults
    assert p18.t("key") == "normal"
    assert p18.t("key_null") is None
    assert p18.t("key_empty") == ""


@pytest.fixture
def instance_with_backend(instance_with_defaults):
    return instance_with_defaults.use(py18next.FSBackend)


def test_backend(instance_with_backend):
    p18 = instance_with_backend
    assert p18.t("key") == "simple value"
    assert p18.t("key_empty") == ""
