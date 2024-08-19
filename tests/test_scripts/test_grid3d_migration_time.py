import pytest
import xtgeo

from grid3d_maps.aggregate import grid3d_migration_time


def test_migration_time1(datatree):
    result = datatree / "migration_time1_folder"
    result.mkdir(parents=True)
    grid3d_migration_time.main(
        [
            "--config",
            "tests/yaml/migration_time1.yml",
            "--mapfolder",
            str(result),
        ]
    )
    swat = xtgeo.surface_from_file(result / "all--migrationtime.gri")
    assert swat.values.max() == pytest.approx(3.08767, abs=0.001)


def test_migration_time2(datatree):
    result = datatree / "migration_time2_folder"
    result.mkdir(parents=True)
    grid3d_migration_time.main(
        [
            "--config",
            "tests/yaml/migration_time2.yml",
            "--mapfolder",
            str(result),
        ]
    )
    assert (result / "lower_zone--migrationtime.gri").is_file()
    assert not (result / "all--migrationtime.gri").is_file()
