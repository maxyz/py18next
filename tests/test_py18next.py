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
