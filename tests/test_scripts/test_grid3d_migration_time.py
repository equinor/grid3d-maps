import pytest
import xtgeo

from xtgeoapp_grd3dmaps.aggregate import grid3d_migration_time


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
    swat = xtgeo.surface_from_file(result / "all--MigrationTime.gri")
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
    assert (result / "lower_zone--MigrationTime.gri").is_file()
    assert not (result / "all--MigrationTime.gri").is_file()
