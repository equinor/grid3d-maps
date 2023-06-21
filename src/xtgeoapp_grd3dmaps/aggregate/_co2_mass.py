from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np

from ecl.eclfile import EclFile
from ecl.grid import EclGrid
import xtgeo


TRESHOLD_SGAS = 1e-16
TRESHOLD_AMFG = 1e-16
CO2_MASS_PNAME = "CO2Mass"


def generate_co2_mass_property(
    properties: List[xtgeo.GridProperty],
):
    pass


# NBNB-AS: From Subscript:

@dataclass
class SourceData:
    x: np.ndarray
    y: np.ndarray
    DATES: List[str]
    VOL: Optional[Dict[str, np.ndarray]] = None
    SWAT: Optional[Dict[str, np.ndarray]] = None
    SGAS: Optional[Dict[str, np.ndarray]] = None
    RPORV: Optional[Dict[str, np.ndarray]] = None
    PORV: Optional[Dict[str, np.ndarray]] = None
    AMFG: Optional[Dict[str, np.ndarray]] = None
    YMFG: Optional[Dict[str, np.ndarray]] = None
    XMF2: Optional[Dict[str, np.ndarray]] = None
    YMF2: Optional[Dict[str, np.ndarray]] = None
    DWAT: Optional[Dict[str, np.ndarray]] = None
    DGAS: Optional[Dict[str, np.ndarray]] = None
    BWAT: Optional[Dict[str, np.ndarray]] = None
    BGAS: Optional[Dict[str, np.ndarray]] = None
    zone: Optional[np.ndarray] = None


def _try_prop(unrst: EclFile,
              prop_name: str):
    try:
        prop = unrst[prop_name]
    except KeyError:
        prop = None
    return prop


def _read_props(
        unrst: EclFile,
        prop_names: List,
) -> dict:
    props_att = {p: _try_prop(unrst, p) for p in prop_names}
    act_prop_names = [k for k in prop_names if props_att[k] is not None]
    act_props = {k: props_att[k] for k in act_prop_names}
    return act_props


def _fetch_properties(
        unrst: EclFile,
        properties_to_extract: List
) -> Tuple[Dict[str, Dict[str, List[np.ndarray]]], List[str]]:
    dates = [d.strftime("%Y%m%d") for d in unrst.report_dates]
    properties = _read_props(unrst, properties_to_extract)
    properties = {p: {d[1]: properties[p][d[0]].numpy_copy()
                      for d in enumerate(dates)}
                  for p in properties}
    return properties, dates


def _identify_gas_less_cells(
        sgases: dict,
        amfgs: dict
) -> np.ndarray:
    gas_less = np.logical_and.reduce([np.abs(sgases[s]) < TRESHOLD_SGAS for s in sgases])
    gas_less &= np.logical_and.reduce([np.abs(amfgs[a]) < TRESHOLD_AMFG for a in amfgs])
    return gas_less


def _reduce_properties(properties: Dict[str, Dict[str, List[np.ndarray]]],
                       keep_idx: np.ndarray) -> Dict:
    return {p: {d: properties[p][d][keep_idx] for d in properties[p]} for p in properties}


def _is_subset(first: List[str], second: List[str]) -> bool:
    return all(x in second for x in first)


def _extract_source_data(
        grid_file: str,
        unrst_file: str,
        properties_to_extract: List[str],
        init_file: Optional[str] = None,
        zone_file: Optional[str] = None
) -> SourceData:
    print("Start extracting source data")
    grid = EclGrid(grid_file)
    unrst = EclFile(unrst_file)
    init = EclFile(init_file)
    properties, dates = _fetch_properties(unrst, properties_to_extract)
    print("Done fetching properties")

    active = np.where(grid.export_actnum().numpy_copy() > 0)[0]
    print("Number of active grid cells: " + str(len(active)))
    if _is_subset(["SGAS", "AMFG"], list(properties.keys())):
        gasless = _identify_gas_less_cells(properties["SGAS"], properties["AMFG"])
    elif _is_subset(["SGAS", "XMF2"], list(properties.keys())):
        gasless = _identify_gas_less_cells(properties["SGAS"], properties["XMF2"])
    else:
        error_text = "CO2 containment calculation failed. Cannot find required properties "
        error_text += "SGAS+AMFG or SGAS+XMF2."
        raise RuntimeError(error_text)
    global_active_idx = active[~gasless]
    properties = _reduce_properties(properties, ~gasless)
    xyz = [grid.get_xyz(global_index=a) for a in global_active_idx]  # Tuple with (x,y,z) for each cell
    cells_x = np.array([coord[0] for coord in xyz])
    cells_y = np.array([coord[1] for coord in xyz])
    zone = None
    if zone_file is not None:
        zone = xtgeo.gridproperty_from_file(zone_file, grid=grid)
        zone = zone.values.data[global_active_idx]
    VOL0 = [grid.cell_volume(global_index=x) for x in global_active_idx]
    properties["VOL"] = {d: VOL0 for d in dates}
    try:
        PORV = init["PORV"]
        properties["PORV"] = {d: PORV[0].numpy_copy()[global_active_idx] for d in dates}
    except KeyError:
        pass
    sd = SourceData(
        cells_x,
        cells_y,
        dates,
        **{
            p: v for p, v in properties.items()
        },
        **{"zone": zone}
    )
    return sd
