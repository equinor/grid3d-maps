# pylint: disable=missing-class-docstring
"""
Configuration for the `aggregate` module. Starting from `RootConfig`, it is possible to
deduce mandatory and optional parameters, as well as default values for whatever is not
explicitly provided.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class AggregationMethod(Enum):
    """
    Enum representing the available aggregation methods for `grid3d_aggregate_map`
    """

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
    properties: Optional[List[Property]] = None
    dates: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.dates = [str(d).replace("-", "") for d in self.dates]
        if (
            self.properties is not None
            and len(self.properties) > 0
            and isinstance(self.properties[0], dict)
        ):
            self.properties = [Property(**p) for p in self.properties]


@dataclass
class ZProperty:
    source: str
    name: Optional[str] = None
    zones: List[Dict[str, List[int]]] = field(default_factory=list)


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
            # pylint: disable=no-member
            self.aggregation = AggregationMethod(self.aggregation.lower())
        if self.all is False and self.zone is False:
            raise ValueError(
                "Both 'all' and 'zone' is turned off, meaning no maps will be computed"
            )


@dataclass
class CO2MassSettings:
    unrst_source: str
    init_source: str
    maps: Optional[List[str]] = None
    zones: Optional[List[str]] = None

    def __post_init__(self):
        pass


@dataclass
class MapSettings:
    # pylint: disable=too-many-instance-attributes
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
    lowercase: bool = True
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
    zonation: Zonation = field(default_factory=Zonation)
    computesettings: ComputeSettings = field(default_factory=ComputeSettings)
    mapsettings: MapSettings = field(default_factory=MapSettings)
    co2_mass_settings: Optional[CO2MassSettings] = None
