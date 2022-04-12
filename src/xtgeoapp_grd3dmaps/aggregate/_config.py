"""
Configuration for the `aggregate` module. Starting from `RootConfig`, it is possible to
deduce mandatory and optional parameters, as well as default values for whatever is not
explicitly provided.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple, Dict


class AggregationMethod(Enum):
    MAX = "max"
    MIN = "min"
    MEAN = "mean"
    SUM = "sum"


@dataclass
class Property:
    source: str
    name: Optional[str] = None
    lower_threshold: Optional[float] = None

    def __post_init__(self):
        if isinstance(self.lower_threshold, str):
            self.lower_threshold = float(self.lower_threshold)


@dataclass
class Input:
    grid: str
    properties: List[Property]

    def __post_init__(self):
        if (
            len(self.properties) > 0
            and isinstance(self.properties[0], dict)
        ):
            self.properties = [Property(**p) for p in self.properties]


@dataclass
class ZProperty:
    source: str
    name: Optional[str] = None


@dataclass
class Zonation:
    zproperty: Optional[ZProperty] = None
    zranges: List[Dict[str, Tuple[int, int]]] = field(default_factory=list)

    def __post_init__(self):
        if self.zproperty is None or isinstance(self.zproperty, ZProperty):
            return
        self.zproperty = ZProperty(**self.zproperty)


@dataclass
class ComputeSettings:
    aggregation: AggregationMethod = AggregationMethod.MAX
    weight_by_dz: bool = False
    all: bool = True
    zone: bool = True

    def __post_init__(self):
        if isinstance(self.aggregation, str):
            self.aggregation = AggregationMethod(self.aggregation.lower())
        if self.all is False and self.zone is False:
            raise ValueError(
                "Both 'all' and 'zone' is turned off, meaning no maps will be computed"
            )


@dataclass
class MapSettings:
    xori: Optional[float] = None
    xinc: Optional[float] = None
    yori: Optional[float] = None
    yinc: Optional[float] = None
    ncol: Optional[int] = None
    nrow: Optional[int] = None
    templatefile: Optional[str] = None
    pixel_to_cell_ratio: float = 2.0


@dataclass
class Output:
    mapfolder: str
    plotfolder: Optional[str] = None
    use_plotly: bool = False
    aggregation_tag: bool = True

    def __post_init__(self):
        if self.mapfolder == "fmu-dataio":
            raise NotImplementedError(
                "Export via fmu-dataio is not implemented for this action"
            )


@dataclass
class RootConfig:
    input: Input
    output: Output
    zonation: Zonation = Zonation()
    computesettings: ComputeSettings = ComputeSettings()
    mapsettings: MapSettings = MapSettings()
