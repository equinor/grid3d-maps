"""Testing suite avg4."""

import pytest
import xtgeo

import grid3d_maps.avghc.grid3d_average_map as grid3d_average_map

# =============================================================================
# Do tests
# =============================================================================


def test_average_map4a(datatree):
    """Test AVG with YAML config example 4a ECL w keywords with spaces; based on 2a."""
    result = datatree / "map4a_folder"
    result.mkdir(parents=True)
    dump = result / "avg4a.yml"
    grid3d_average_map.main(
        [
            "--config",
            "tests/yaml/avg4a.yml",
            "--dump",
            str(dump),
            "--mapfolder",
            str(result),
            "--plotfolder",
            str(result),
        ]
    )
    mymap1 = xtgeo.surface_from_file(
        result / "zone2+3--avg4a_average_pressure--19991201.gri"
    )
    assert mymap1.values.mean() == pytest.approx(336.5236, abs=0.01)

    mymap2 = xtgeo.surface_from_file(
        result / "zone2+3--avg4a_average_w8f--19991201.gri"
    )
    assert mymap2.values.mean() == pytest.approx(0.837027, abs=0.01)
