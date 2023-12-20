from dataclasses import dataclass, fields
import glob
from typing import Dict, List, Literal, Optional, Tuple
import numpy as np
import os
from ecl.eclfile import EclFile
from ecl.grid import EclGrid
import xtgeo

from xtgeoapp_grd3dmaps.aggregate import (
    _config,
)

DEFAULT_CO2_MOLAR_MASS = 44.0
DEFAULT_WATER_MOLAR_MASS = 18.0
TRESHOLD_SGAS = 1e-16
TRESHOLD_AMFG = 1e-16
CO2_MASS_PNAME = "CO2Mass"

@dataclass
class SourceData:
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
    ################# HACK START #################
    if False:
        print("\nBefore:")
        for x in properties:
            print(x)
        properties["AMFG"] = []
        properties["PORV"] = []
        properties["DGAS"] = []
        properties["DWAT"] = []
        properties["YMFG"] = []
        for x in properties["SGAS"]:
            properties["AMFG"].append(x.copy())
            properties["PORV"].append(x.copy())
            properties["DGAS"].append(x.copy())
            properties["DWAT"].append(x.copy())
            properties["YMFG"].append(x.copy())
        for y in properties["AMFG"]:
            a = y.numpy_view()
            for i in range(0, len(a)):
                a[i] = a[i] * 0.02
        for y in properties["PORV"]:
            a = y.numpy_view()
            for i in range(0, len(a)):
                a[i] = 0.3
        for y in properties["DGAS"]:
            a = y.numpy_view()
            for i in range(0, len(a)):
                a[i] = 100.0
        for y in properties["DWAT"]:
            a = y.numpy_view()
            for i in range(0, len(a)):
                a[i] = 1000.0
        for y in properties["YMFG"]:
            a = y.numpy_view()
            for i in range(0, len(a)):
                a[i] = 0.99
        print("\nAfter:")
        for x in properties:
            print(x)
        print("")
    else:
        print("Skip HACK")
    ################# HACK END  ###################
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
    grid = EclGrid(grid_file)
    unrst = EclFile(unrst_file)
    init = EclFile(init_file)
    properties, dates = _fetch_properties(unrst, properties_to_extract)
    
    active = np.where(grid.export_actnum().numpy_copy() > 0)[0]
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
    water_molar_mass: float = DEFAULT_WATER_MOLAR_MASS
) -> Co2Data:
    
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
        co2_mass_cell = _pflotran_co2mass(
            source_data, co2_molar_mass, water_molar_mass
        )
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
    unrst_file: str,
    properties_to_extract: List[str],
    out_file: str,
    maps: List[str]
) -> List[List[xtgeo.GridProperty]]:

    grid = EclGrid(grid_file)
    grid_pf = xtgeo.grid_from_file(grid_file)
    unrst = EclFile(unrst_file)
    properties, dates = _fetch_properties(unrst, properties_to_extract)
    gdf = grid_pf.get_dataframe()
    gdf = (gdf.sort_values(by=['KZ','JY','IX']))

    active = np.where(grid.export_actnum().numpy_copy() > 0)[0]
    
    if _is_subset(["SGAS", "AMFG"], list(properties.keys())):
        gasless = _identify_gas_less_cells(properties["SGAS"], properties["AMFG"])
    elif _is_subset(["SGAS", "XMF2"], list(properties.keys())):
        gasless = _identify_gas_less_cells(properties["SGAS"], properties["XMF2"])
    else:
        error_text = "CO2 containment calculation failed. Cannot find required properties "
        error_text += "SGAS+AMFG or SGAS+XMF2."
        raise RuntimeError(error_text)
    
    gdf = gdf.loc[~gasless]
    
    triplets = []

    for index,row in gdf.iterrows():
        triplet = (row['IX'], row['JY'], row['KZ'])
        triplets.append(triplet)

    triplets = [(int(x-1), int(y-1), int(z-1)) for x, y, z in triplets]
    mask = np.ones((grid_pf.ncol,grid_pf.nrow,grid_pf.nlay),dtype=bool)

    for x in triplets:
        mask[x] = False

    mass_total_prop_list = []
    mass_aqu_phase_prop_list = []
    mass_gas_phase_prop_list = []
    out_list = []
    all_maps_bool = False
    for x in co2_data.data_list:
        mass_total = x.total_mass()
        mass_aqu_phase = x.aqu_phase
        mass_gas_phase = x.gas_phase

        gdf['mass_total'] = mass_total
        gdf['mass_aqu_phase'] = mass_aqu_phase
        gdf['mass_gas_phase'] = mass_gas_phase

        mass_total_array = np.zeros((grid_pf.ncol,grid_pf.nrow,grid_pf.nlay))
        mass_aqu_phase_array = np.zeros((grid_pf.ncol,grid_pf.nrow,grid_pf.nlay))
        mass_gas_phase_array = np.zeros((grid_pf.ncol,grid_pf.nrow,grid_pf.nlay))

        for i in range(len(triplets)):
            mass_total_array[triplets[i]]=mass_total[i]
            mass_aqu_phase_array[triplets[i]]=mass_aqu_phase[i]
            mass_gas_phase_array[triplets[i]]=mass_gas_phase[i]

        ## Setting up the grid folder to store the gridproperties
        grid_out_dir = out_file+"/grid"
        if not os.path.exists(grid_out_dir):
            os.makedirs(grid_out_dir)
        mass_total_name = "co2_mass_total--"+str(x.date)
        mass_total_prop = xtgeo.grid3d.GridProperty(ncol=grid_pf.ncol,nrow=grid_pf.nrow,nlay=grid_pf.nlay,values=mass_total_array,name=mass_total_name,date=str(x.date))

        mass_aqu_phase_name = "co2_mass_aqu_phase--"+str(x.date)
        mass_aqu_phase_prop = xtgeo.grid3d.GridProperty(ncol=grid_pf.ncol,nrow=grid_pf.nrow,nlay=grid_pf.nlay,values=mass_aqu_phase_array,name=mass_aqu_phase_name,date=str(x.date))

        mass_gas_phase_name = "co2_mass_gas_phase--"+str(x.date)
        mass_gas_phase_prop = xtgeo.grid3d.GridProperty(ncol=grid_pf.ncol,nrow=grid_pf.nrow,nlay=grid_pf.nlay,values=mass_gas_phase_array,name=mass_gas_phase_name,date=str(x.date))

        if maps is None:
            maps = []
        elif isinstance(maps,str):
            maps = [maps]
        maps = [map_name.lower() for map_name in maps]
        
        if "all" in maps or len(maps)==0:
            mass_total_prop.to_file(grid_out_dir + "/MASS_TOTAL_"+str(x.date)+".roff", fformat="roff")
            mass_aqu_phase_prop.to_file(grid_out_dir + "/MASS_AQU_PHASE_"+str(x.date)+".roff", fformat="roff")
            mass_gas_phase_prop.to_file(grid_out_dir + "/MASS_GAS_PHASE_"+str(x.date)+".roff", fformat="roff")
            mass_total_prop_list.append(mass_total_prop)
            mass_aqu_phase_prop_list.append(mass_aqu_phase_prop)
            mass_gas_phase_prop_list.append(mass_gas_phase_prop)
            all_maps_bool = True
        if "free_co2" in maps and all_maps_bool==False:
            mass_gas_phase_prop.to_file(grid_out_dir + "/MASS_GAS_PHASE_"+str(x.date)+".roff", fformat="roff")
            mass_gas_phase_prop_list.append(mass_gas_phase_prop)
        if "dissolved_co2" in maps and all_maps_bool==False:
            mass_aqu_phase_prop.to_file(grid_out_dir + "/MASS_AQU_PHASE_"+str(x.date)+".roff", fformat="roff")
            mass_aqu_phase_prop_list.append(mass_aqu_phase_prop)
        if "total_co2" in maps and all_maps_bool==False:
            mass_total_prop.to_file(grid_out_dir + "/MASS_TOTAL_"+str(x.date)+".roff", fformat="roff")
            mass_total_prop_list.append(mass_total_prop)

    out_list = [mass_gas_phase_prop_list,mass_aqu_phase_prop_list,mass_total_prop_list]
    return out_list

def _temp_make_property_copy(source: str, grid_file: Optional[str], dates: List[str]) -> xtgeo.GridProperty:
    try:
        grid = None if grid_file is None else xtgeo.grid_from_file(grid_file)
        props = xtgeo.gridproperties_from_file(
            source, grid=grid,
        )
        b = props.props
    except (RuntimeError, ValueError):
        print("ERROR")
        exit()
