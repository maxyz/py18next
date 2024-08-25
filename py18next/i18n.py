import json
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Literal, Self

import yaml
from babel.dates import format_datetime

SUPPORTED_FORMAT = ["json", "yaml"]
DEFAULT_FORMAT = "json"
DEFAULT_LOCALE = "en"

type FileFormat = Literal["json", "yaml"]

type _TData = dict[str, _TValue]
type _TValue = str | _TData


class Translator:
    data: _TData
    locale: str

    def __init__(
        self,
        translations_folder: Path | str,
        file_format: FileFormat = DEFAULT_FORMAT,
        default_locale=DEFAULT_LOCALE,
    ):
        self.data = {}
        self.locale = default_locale

        # check if format is supported
        if file_format not in SUPPORTED_FORMAT:
            return

        # get list of files with specific extensions
        filepaths = Path(translations_folder).glob(f"*.{file_format}")
        for filepath in filepaths:
            # get the name of the file without extension, will be used as locale name
            locale = filepath.stem
            with filepath.open(encoding="utf8") as f:
                self.data[locale] = _process_file(f, file_format)

    def set_locale(self, locale: str) -> Self:
        if locale not in self.data:
            msg = "Invalid locale"
            raise ValueError(msg)
        self.locale = locale
        return self

    def get_locale(self) -> str:
        return self.locale

    def translate(
        self, key: str | Sequence[str], default: str | None = None
    ) -> str | None:
        path = _get_translation_path(key)

        def _default():
            return ".".join(path) if default is None else default

        # return the key instead of translation text if locale is not supported
        if self.locale not in self.data:
            return _default()

        return _deep_get(self.data[self.locale], path, default=_default)


def str_to_datetime(dt_str: str, format="%Y-%m-%d") -> datetime:
    return datetime.strptime(dt_str, format).replace(tzinfo=UTC)


def datetime_to_str(dt: datetime, format="MMMM dd, yyyy", locale="en") -> str:
    return format_datetime(dt, format=format, locale=locale)


def _process_file(f: IO[str], format: FileFormat):
    match format:
        case "json":
            return json.load(f)
        case "yaml":
            return yaml.safe_load(f)


def _get_translation_path(key: str | Sequence[str]) -> tuple[str, ...]:
    match key:
        case str():
            return tuple(key.split("."))
        case Sequence():
            return tuple(key)


def _deep_get(
    data: _TValue,
    keys: Iterable[str],
    default: str | Callable[[], str | None] | None = None,
):
    def _default():
        match default:
            case Callable():
                return default()
            case _:
                return default

    def _resolve(value: _TValue):
        match value:
            case str(s):
                return s
            case _:
                return _default()

    value: _TValue = data
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return _default()
        value = value[key]
    return _resolve(value)
