import functools
import json
from collections.abc import Callable
from pathlib import Path
from typing import IO

import yaml

from .types import BackendOptions, FormatType, PluginType, ResourceNamespace
from .types import Options as Py18NextOptions


class FSBackend:
    type: PluginType = PluginType.BACKEND
    options: BackendOptions

    def __init__(
        self,
        /,
        options: Py18NextOptions | None = None,
        services: None = None,
        backend_options: BackendOptions | None = None,
    ):
        _ = services
        if backend_options is None:
            backend_options = None if options is None else options.backend
        if backend_options is None:
            backend_options = BackendOptions()
        self.options = backend_options

    def read(self, locale: str, namespace: str) -> ResourceNamespace:
        format = self.options.file_format
        path_template = self.options.load_path or "{locale}/{namespace}.{format}"
        return _memo_read(
            locale=locale,
            namespace=namespace,
            format=format,
            path_template=path_template,
        )


@functools.lru_cache
def _memo_read(
    *, locale: str, namespace: str, format: FormatType, path_template: str
) -> ResourceNamespace:
    _ = locale, namespace, format
    filepath = path_template.format(**locals())
    reader = _get_reader(format)
    with Path(filepath).open() as fp:
        return reader(fp)


def _get_reader(format: FormatType) -> Callable[[IO], ResourceNamespace]:
    match format:
        case FormatType.JSON:
            return json.load
        case FormatType.YAML:
            return yaml.safe_load
