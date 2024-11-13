import os
import pathlib
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, RootModel
from ruamel.yaml import YAML


class Property(BaseModel):
    name: str
    source: Optional[str] = None
    dates: List[int] = Field(default_factory=list)
    diffdates: List[int] = Field(default_factory=list)


class Input(BaseModel):
    eclroot: str
    grid: Optional[str] = Field(default="$eclroot.EGRID")
    dates: List[int] = Field(default_factory=list)
    properties: List[Property] = Field(default_factory=list)


class Zonation(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    zones: Optional[Dict[str, List[int]]] = None
    zranges: List[Dict[str, List[int]]] = Field(default_factory=list)


class Filter(BaseModel):
    name: str
    discrete: bool
    source: str
    discrange: List[int]


class ComputeSettings(BaseModel):
    zone: bool = Field(default=False)
    all: bool = Field(default=True)
    mask_zeros: bool = Field(default=True)
    mode: Optional[str] = "oil"
    critmode: Optional[str] = None
    shc_interval: Optional[List[float]] = None
    method: Optional[str] = None


class TemplateMapSettings(BaseModel):
    template: Union[str, pathlib.Path, None] = None


class DetailedMapSettings(BaseModel):
    xori: float
    xinc: float
    yori: float
    yinc: float
    ncol: float
    nrow: float


class MapSettings(RootModel[Union[TemplateMapSettings, DetailedMapSettings]]):
    pass


class Output(BaseModel):
    tag: str = Field(default="")
    mapfolder: str = Field(default="dataio")
    plotfolder: str = Field(default="")
    prefix: str = Field(default="")


class Config(BaseModel):
    title: Optional[str] = Field(default="Name missing")
    script: Optional[str] = Literal["hcthickness", "average"]
    version: Optional[int] = Field(default=1)
    input: Input = Field(default_factory=Input)
    zonation: Optional[Zonation] = None
    computesettings: ComputeSettings = Field(default_factory=ComputeSettings)
    mapsettings: Optional[MapSettings] = None
    output: Output = Field(default_factory=Output)


class IncludeFromLoader:
    """Allow to include data from other files with: !include_from file.yaml::key"""

    def __init__(self, base_path):
        self.base_path = base_path

    def __call__(self, loader, node):
        file_path, key = loader.construct_scalar(node).split("::")
        full_path = os.path.join(self.base_path, file_path)
        with open(full_path, "r") as f:
            data = YAML().load(f)
        for part in key.split("."):
            data = data[part]
        return data


def parse_validate_config(filename: str | pathlib.Path) -> Config:
    yaml = YAML()
    yaml.Constructor.add_constructor("!include_from", IncludeFromLoader(base_path="."))
    with open(filename, "r") as stream:
        yaml_data = yaml.load(stream)
    return Config(**yaml_data)
