from collections.abc import Callable, Iterable, Sequence
from typing import Any, Self, cast

from .plugins import FSBackend as FSBackend  # noqa: PLC0414
from .types import (
    BackendPlugin,
    Options,
    Plugin,
    PluginType,
    ResourceNamespace,
    ResourceValue,
    options_ta,
)


class Py18Next:
    options: Options
    services: None = None

    def __init__(self: Self, options: Options | dict[str, Any] | None = None):
        self.options = _get_options(options)
        self._backends = []

    def init(self, options: Options | dict[str, Any]) -> Self:
        self.options = _merge_options(self.options, options)
        return self

    def use(self, plugin: type[Plugin]) -> Self:
        match plugin.type:
            case PluginType.BACKEND:
                backend_plugin = cast(type[BackendPlugin], plugin)
                plugin_instance = backend_plugin(
                    options=self.options,
                    backend_options=self.options.backend,
                    services=self.services,
                )
                self._backends.append(plugin_instance)
        return self

    def t(
        self, key: str | Sequence[str], options: Options | dict[str, Any] | None = None
    ) -> str | None:
        path = _get_translation_path(key)
        default = key

        def _default():
            return default if isinstance(default, str) else ".".join(default)

        options = _merge_options(self.options, options)
        locale = _resolve_locale(options) or ""
        namespace = _resolve_namespace(options) or ""

        translations = None
        translation = None
        for backend in self._backends:
            translations = backend.read(locale=locale, namespace=namespace)
            if translations is None:
                continue
            translation = _deep_get(translations, path, default=None)
            if translation:
                break

        if translation is not None:
            return translation

        # fallback to resources
        resources = options.resources or {}
        if ((namespaces := resources.get(locale)) is None) or (
            (translations := namespaces.get(namespace)) is None
        ):
            return _default()

        return _deep_get(translations, path, default=_default)


def create(options: Options | dict[str, Any]) -> Py18Next:
    return Py18Next(options=options)


def _get_options(options: Options | dict[str, Any] | None) -> Options:
    match options:
        case dict():
            options = options_ta.validate_python(options)
        case None:
            options = Options()
    return options


def _merge_options(
    options: Options, update: Options | dict[str, Any] | None = None
) -> Options:
    update = _dump_options(update)
    return options.model_copy(update=update)


def _dump_options(options: Options | dict[str, Any] | None) -> dict[str, Any]:
    match options:
        case Options():
            return options_ta.dump_python(options)
        case None:
            return {}
        case dict():
            return options


def _resolve_locale(options: Options) -> str | None:
    return (
        options.locale
        if options.locale is not None
        else options.fallback_locale
        if options.fallback_locale is not None
        else None
    )


def _resolve_namespace(options: Options) -> str | None:
    return (
        options.namespace
        if options.namespace is not None
        else options.fallback_namespace
        if options.fallback_namespace is not None
        else None
    )


def _get_translation_path(key: str | Sequence[str]) -> tuple[str, ...]:
    match key:
        case str():
            return tuple(key.split("."))
        case Sequence():
            return tuple(key)


def _deep_get(
    resource: ResourceNamespace,
    keys: Iterable[str],
    default: str | Callable[[], str | None] | None = None,
) -> str | None:
    def _default():
        match default:
            case Callable():
                return default()
            case _:
                return default

    def _resolve(value: ResourceValue):
        match value:
            case str(s):
                return s
            case None:
                return None
            case _:
                return _default()

    value: ResourceValue = resource
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return _default()
        value = value[key]
    return _resolve(value)
