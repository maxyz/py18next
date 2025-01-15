from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, ConfigDict, TypeAdapter

type ResourceValue = str | ResourceNamespace | None
type ResourceNamespace = dict[str, ResourceValue]
type ResourceLocale = dict[str, ResourceNamespace]
type Resources = dict[str, ResourceLocale]


class FormatType(StrEnum):
    JSON = "json"
    YAML = "yaml"


class BackendOptions(BaseModel):
    model_config = ConfigDict(frozen=True, extra="allow")

    load_path: str | None = None
    file_format: FormatType = FormatType.JSON


class Options(BaseModel):
    model_config = ConfigDict(frozen=True, extra="allow")

    debug: bool = False

    resources: dict[str, ResourceLocale] | None = None

    locale: str | None = None
    fallback_locale: str | None = None

    namespace: str = "translation"
    default_namespace: str = "translation"
    fallback_namespace: str | None = None

    backend: BackendOptions | None = None


options_ta = TypeAdapter(Options)


class PluginType(StrEnum):
    BACKEND = "backend"


class Plugin(Protocol):
    type: PluginType


class BackendPlugin(Protocol):
    type: PluginType = PluginType.BACKEND
    options: BackendOptions

    def __init__(
        self,
        /,
        options: Options | None = None,
        services: None = None,
        backend_options: BackendOptions | None = None,
    ): ...

    def read(self, language: str, namespace: str) -> ResourceNamespace: ...
