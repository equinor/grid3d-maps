import os
from dataclasses import dataclass, fields
from typing import Dict, List, Literal, Optional, Tuple

import numpy as np
import xtgeo
from ecl.eclfile import EclFile
from ecl.grid import EclGrid

from xtgeoapp_grd3dmaps.aggregate._config import CO2MassSettings

DEFAULT_CO2_MOLAR_MASS = 44.0
DEFAULT_WATER_MOLAR_MASS = 18.0
TRESHOLD_SGAS = 1e-16
TRESHOLD_AMFG = 1e-16
CO2_MASS_PNAME = "CO2Mass"


# pylint: disable=invalid-name,too-many-instance-attributes
@dataclass
class SourceData:
    """
    Dataclass with the information of the necessary properties
    for the calculation of CO2 mass
    """

    x_coord: np.ndarray
    y_coord: np.ndarray
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

    def get_vol(self):
        """Get VOL"""
        if self.VOL is not None:
            return self.VOL
        return {}

    def get_swat(self):
        """Get SWAT"""
        if self.SWAT is not None:
            return self.SWAT
        return {}

    def get_sgas(self):
        """Get SGAS"""
        if self.SGAS is not None:
            return self.SGAS
        return {}

    def get_rporv(self):
        """Get RPORV"""
        if self.RPORV is not None:
            return self.RPORV
        return {}

    def get_porv(self):
        """Get PORV"""
        if self.PORV is not None:
            return self.PORV
        return {}

    def get_amfg(self):
        """Get AMFG"""
        if self.AMFG is not None:
            return self.AMFG
        return {}

    def get_ymfg(self):
        """Get YMFG"""
        if self.YMFG is not None:
            return self.YMFG
        return {}

    def get_xmf2(self):
        """Get XMF2"""
        if self.XMF2 is not None:
            return self.XMF2
        return {}

    def get_ymf2(self):
        """Get YMF2"""
        if self.YMF2 is not None:
            return self.YMF2
        return {}

    def get_dwat(self):
        """Get DWAT"""
        if self.DWAT is not None:
            return self.DWAT
        return {}

    def get_dgas(self):
        """Get DGAS"""
        if self.DGAS is not None:
            return self.DGAS
        return {}

    def get_bwat(self):
        """Get BWAT"""
        if self.BWAT is not None:
            return self.BWAT
        return {}

    def get_bgas(self):
        """Get BGAS"""
        if self.BGAS is not None:
            return self.BGAS
        return {}

    def get_zone(self):
        """Get zone"""
        if self.zone is not None:
            return self.zone
        return None


@dataclass
class Co2DataAtTimeStep:
    """
    Dataclass with amount of co2 for each phase (dissolved/gas/undefined)
    at a given time step.

    Args:
      date (str): The time step
      aqu_phase (np.ndarray): The amount of CO2 in aqueous phase
      gas_phase (np.ndarray): The amount of CO2 in gaseous phase
      volume_covarage (np.ndarray): The volume of a cell (specific of
                                    calc_type_input = volume_extent)
    """

    date: str
    aqu_phase: np.ndarray
    gas_phase: np.ndarray
    volume_coverage: np.ndarray

    def total_mass(self) -> np.ndarray:
        """
        Computes total mass as the sum of gas in aqueous and gas
        phase.
        """
        return self.aqu_phase + self.gas_phase


@dataclass
class Co2Data:
    """
    Dataclass with amount of CO2 at (x,y) coordinates

    Args:
      x_coord (np.ndarray): x coordinates
      y_coord (np.ndarray): y coordinates
      data_list (List): List with CO2 amounts calculated
                        at multiple time steps
      units (Literal): Units of the calculated amount of CO2
      zone (np.ndarray):

    """

    x_coord: np.ndarray
    y_coord: np.ndarray
    data_list: List[Co2DataAtTimeStep]
    units: Literal["kg", "m3"]
    zone: Optional[np.ndarray] = None


def _try_prop(unrst: EclFile, prop_name: str):
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
    unrst: EclFile, properties_to_extract: List
) -> Tuple[Dict[str, Dict[str, List[np.ndarray]]], List[str]]:
    dates = [d.strftime("%Y%m%d") for d in unrst.report_dates]
    properties = _read_props(unrst, properties_to_extract)
    properties = {
        p: {d[1]: properties[p][d[0]].numpy_copy() for d in enumerate(dates)}
        for p in properties
    }
    return properties, dates


def _identify_gas_less_cells(
    sgases: Dict[str, List[np.ndarray]],
    amfgs: Dict[str, List[np.ndarray]],
) -> np.ndarray:
    gas_less = np.logical_and.reduce(
        [np.abs(sgases[s]) < TRESHOLD_SGAS for s in sgases]
    )
    gas_less &= np.logical_and.reduce([np.abs(amfgs[a]) < TRESHOLD_AMFG for a in amfgs])
    return gas_less


def _get_gasless(properties: Dict[str, Dict[str, List[np.ndarray]]]) -> np.ndarray:
    if _is_subset(["SGAS", "AMFG"], list(properties.keys())):
        gasless = _identify_gas_less_cells(properties["SGAS"], properties["AMFG"])
    elif _is_subset(["SGAS", "XMF2"], list(properties.keys())):
        gasless = _identify_gas_less_cells(properties["SGAS"], properties["XMF2"])
    else:
        error_text = (
            "CO2 containment calculation failed. "
            "Cannot find required properties SGAS+AMFG or SGAS+XMF2."
        )
        raise RuntimeError(error_text)
    return gasless


def _reduce_properties(
    properties: Dict[str, Dict[str, List[np.ndarray]]], keep_idx: np.ndarray
) -> Dict:
    return {
        p: {d: properties[p][d][keep_idx] for d in properties[p]} for p in properties
    }


def _is_subset(first: List[str], second: List[str]) -> bool:
    return all(x in second for x in first)


def extract_source_data(
    grid_file: str,
    unrst_file: str,
    properties_to_extract: List[str],
    init_file: Optional[str] = None,
    zone_file: Optional[str] = None,
) -> SourceData:
    """
    Extracts relevant grid properties from the source files from Eclipse/PFlotran
    """
    grid = EclGrid(grid_file)
    properties, dates = _fetch_properties(EclFile(unrst_file), properties_to_extract)

    active = np.where(grid.export_actnum().numpy_copy() > 0)[0]
    gasless = _get_gasless(properties)

    active = active[~gasless]
    properties = _reduce_properties(properties, ~gasless)
    xyz = [
        grid.get_xyz(global_index=a) for a in active
    ]  # Tuple with (x,y,z) for each cell
    zone = None
    if zone_file is not None:
        zone = xtgeo.gridproperty_from_file(zone_file, grid=grid)
        zone = zone.values.data[active]
    vol0 = [grid.cell_volume(global_index=x) for x in active]
    properties["VOL"] = {d: vol0 for d in dates}
    try:
        init = EclFile(init_file)
        porv = init["PORV"]
        properties["PORV"] = {d: porv[0].numpy_copy()[active] for d in dates}
    except KeyError:
        pass
    return SourceData(
        np.array([coord[0] for coord in xyz]),
        np.array([coord[1] for coord in xyz]),
        dates,
        **dict(properties.items()),
        **{"zone": zone},
    )


def _mole_to_mass_fraction(prop: np.ndarray, m_co2: float, m_h20: float) -> np.ndarray:
    """
    Converts from mole fraction to mass fraction

    Args:
      prop (np.ndarray): Information with mole fractions to be converted
      m_co2 (float): Molar mass of CO2
      m_h20 (float): Molar mass of H2O

    Returns:
      np.ndarray

    """
    return prop * m_co2 / (m_h20 + (m_co2 - m_h20) * prop)


def _pflotran_co2mass(
    source_data: SourceData,
    co2_molar_mass: float = DEFAULT_CO2_MOLAR_MASS,
    water_molar_mass: float = DEFAULT_WATER_MOLAR_MASS,
) -> Dict:
    """
    Calculates CO2 mass based on the existing properties in PFlotran

    Args:
      source_data (SourceData): Data with the information of the necessary properties
                                for the calculation of CO2 mass
      co2_molar_mass (float): CO2 molar mass - Default is 44 g/mol
      water_molar_mass (float): Water molar mass - Default is 18 g/mol

    Returns:
      Dict

    """
    dates = source_data.DATES
    dwat = source_data.get_dwat()
    dgas = source_data.get_dgas()
    amfg = source_data.get_amfg()
    ymfg = source_data.get_ymfg()
    sgas = source_data.get_sgas()
    eff_vols = source_data.get_porv()
    co2_mass = {}
    for date in dates:
        co2_mass[date] = [
            eff_vols[date]
            * (1 - sgas[date])
            * dwat[date]
            * _mole_to_mass_fraction(amfg[date], co2_molar_mass, water_molar_mass),
            eff_vols[date]
            * sgas[date]
            * dgas[date]
            * _mole_to_mass_fraction(ymfg[date], co2_molar_mass, water_molar_mass),
        ]
    return co2_mass


def _eclipse_co2mass(
    source_data: SourceData, co2_molar_mass: float = DEFAULT_CO2_MOLAR_MASS
) -> Dict:
    """
    Calculates CO2 mass based on the existing properties in Eclipse

    Args:
      source_data (SourceData): Data with the information of the necessary properties
                                for the calculation of CO2 mass
      co2_molar_mass (float): CO2 molar mass - Default is 44 g/mol

    Returns:
      Dict

    """
    dates = source_data.DATES
    bgas = source_data.get_bgas()
    bwat = source_data.get_bwat()
    xmf2 = source_data.get_xmf2()
    ymf2 = source_data.get_ymf2()
    sgas = source_data.get_sgas()
    eff_vols = source_data.get_rporv()
    conv_fact = co2_molar_mass
    co2_mass = {}
    for date in dates:
        co2_mass[date] = [
            conv_fact * bwat[date] * xmf2[date] * (1 - sgas[date]) * eff_vols[date],
            conv_fact * bgas[date] * ymf2[date] * sgas[date] * eff_vols[date],
        ]
    return co2_mass


def generate_co2_mass_data(
    source_data: SourceData,
    co2_molar_mass: float = DEFAULT_CO2_MOLAR_MASS,
    water_molar_mass: float = DEFAULT_WATER_MOLAR_MASS,
) -> Co2Data:
    """
    Calculate CO2 mass based on the existing properties from Eclipse/PFlotran
    """
    props_check = [
        x.name
        for x in fields(source_data)
        if x.name not in ["x_coord", "y_coord", "DATES", "zone", "VOL"]
    ]
    active_props_idx = np.where(
        [getattr(source_data, x) is not None for x in props_check]
    )[0]
    active_props = [props_check[i] for i in active_props_idx]
    if _is_subset(["SGAS"], active_props):
        if _is_subset(["PORV", "RPORV"], active_props):
            active_props.remove("PORV")
        if _is_subset(["PORV", "DGAS", "DWAT", "AMFG", "YMFG"], active_props):
            source = "PFlotran"
        elif _is_subset(["RPORV", "BGAS", "BWAT", "XMF2", "YMF2"], active_props):
            source = "Eclipse"
        else:
            error_text = "Lacking some required properties to compute CO2 mass/volume"
            raise RuntimeError(error_text)
    else:
        error_text = "Lacking some required properties to compute CO2 mass/volume"
        error_text += "\nMissing: SGAS"
        raise RuntimeError(error_text)

    if source == "PFlotran":
        co2_mass_cell = _pflotran_co2mass(source_data, co2_molar_mass, water_molar_mass)
    else:
        co2_mass_cell = _eclipse_co2mass(source_data, co2_molar_mass)
    return Co2Data(
        source_data.x_coord,
        source_data.y_coord,
        [
            Co2DataAtTimeStep(key, value[0], value[1], np.zeros_like(value[1]))
            for key, value in co2_mass_cell.items()
        ],
        "kg",
        source_data.get_zone(),
    )


def translate_co2data_to_property(
    co2_data: Co2Data,
    grid_file: str,
    co2_mass_settings: CO2MassSettings,
    properties_to_extract: List[str],
    grid_out_dir: str,
) -> List[List[xtgeo.GridProperty]]:
    """
    Convert CO2 mass arrays and save calculated CO2 mass as grid files
    """
    dimensions, triplets = _get_dimensions_and_triplets(
        grid_file, co2_mass_settings.unrst_source, properties_to_extract
    )

    # Setting up the grid folder to store the gridproperties
    if not os.path.exists(grid_out_dir):
        os.makedirs(grid_out_dir)

    maps = co2_mass_settings.maps
    if maps is None:
        maps = []
    elif isinstance(maps, str):
        maps = [maps]
    maps = [map_name.lower() for map_name in maps]

    total_mass_list = []
    dissolved_mass_list = []
    free_mass_list = []

    store_all = "all" in maps or len(maps) == 0
    for co2_at_date in co2_data.data_list:
        date = str(co2_at_date.date)
        mass_as_grids = _convert_to_grid(co2_at_date, dimensions, triplets)
        if store_all or "total_co2" in maps:
            mass_as_grids["mass-total"].to_file(
                grid_out_dir + "/MASS_TOTAL_" + date + ".roff", fformat="roff"
            )
            total_mass_list.append(mass_as_grids["mass-total"])
        if store_all or "dissolved_co2" in maps:
            mass_as_grids["mass-aqu-phase"].to_file(
                grid_out_dir + "/MASS_AQU_PHASE_" + date + ".roff",
                fformat="roff",
            )
            dissolved_mass_list.append(mass_as_grids["mass-aqu-phase"])
        if store_all or "free_co2" in maps:
            mass_as_grids["mass-gas-phase"].to_file(
                grid_out_dir + "/MASS_GAS_PHASE_" + date + ".roff",
                fformat="roff",
            )
            free_mass_list.append(mass_as_grids["mass-gas-phase"])

    return [
        free_mass_list,
        dissolved_mass_list,
        total_mass_list,
    ]


def _get_dimensions_and_triplets(
    grid_file: str,
    unrst_file: str,
    properties_to_extract: List[str],
) -> Tuple[Tuple[int, int, int], List[Tuple[int, int, int]]]:
    grid_pf = xtgeo.grid_from_file(grid_file)
    dimensions = (grid_pf.ncol, grid_pf.nrow, grid_pf.nlay)
    unrst = EclFile(unrst_file)
    properties, _ = _fetch_properties(unrst, properties_to_extract)
    gdf = grid_pf.get_dataframe()
    gdf = gdf.sort_values(by=["KZ", "JY", "IX"])

    gasless = _get_gasless(properties)
    gdf = gdf.loc[~gasless]
    triplets = [
        (int(row["IX"] - 1), int(row["JY"] - 1), int(row["KZ"] - 1))
        for _, row in gdf.iterrows()
    ]
    return dimensions, triplets


def _convert_to_grid(
    co2_at_date: Co2DataAtTimeStep,
    dimensions: Tuple[int, int, int],
    triplets: List[Tuple[int, int, int]],
) -> Dict[str, xtgeo.GridProperty]:
    """
    Store the CO2 mass arrays in grid objects
    """
    grids = {}
    date = str(co2_at_date.date)
    for mass, name in zip(
        [co2_at_date.total_mass(), co2_at_date.aqu_phase, co2_at_date.gas_phase],
        ["mass-total", "mass-aqu-phase", "mass-gas-phase"],
    ):
        mass_array = np.zeros(dimensions)
        for i, triplet in enumerate(triplets):
            mass_array[triplet] = mass[i]
        mass_name = "co2-" + name + "--" + date
        grids[name] = xtgeo.grid3d.GridProperty(
            ncol=dimensions[0],
            nrow=dimensions[1],
            nlay=dimensions[2],
            values=mass_array,
            name=mass_name,
            date=date,
        )
    return grids
