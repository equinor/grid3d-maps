import numpy as np
import numpy.testing as npt
import pytest
import xtgeo

from grid3d_maps.aggregate import AggregationMethod, aggregate_maps


@pytest.fixture(name="example_grid")
def fixture_example_grid():
    grid_x, grid_y = np.meshgrid(
        np.linspace(-100, 100, 21),
        np.linspace(-60, 60, 13),
        indexing="ij",
    )
    depths = np.array([100, 107, 114, 128])
    coordsv = np.dstack(
        [
            grid_x,
            grid_y,
            np.ones_like(grid_x) * depths[0],
            grid_x,
            grid_y,
            np.ones_like(grid_x) * depths[-1],
        ]
    )
    zcornsv = np.ones_like(grid_x)[:, :, np.newaxis] * depths
    zcornsv = zcornsv[:, :, :, np.newaxis] * np.ones(4)
    zcornsv = zcornsv.astype(np.float32)
    actnum = np.ones(np.array(zcornsv.shape[:-1]) - 1, dtype=np.int32)
    grid = xtgeo.Grid(coordsv, zcornsv, actnum)
    grid.gridprops.append_props([generate_example_property(grid)])
    return grid


@pytest.fixture(name="example_property")
def fixture_example_property(example_grid):
    return example_grid.props[0]


@pytest.fixture(name="default_args")
def fixture_default_args(example_grid, example_property):
    return dict(
        map_template=1.0,
        grid=example_grid,
        grid_props=[example_property],
        inclusion_filters=[None],
        method=AggregationMethod.MAX,
        weight_by_dz=False,
    )


def generate_example_property(grid):
    values = np.full(grid.dimensions, fill_value=np.nan)
    xyz = grid.get_xyz()
    d_xy = np.sqrt(xyz[0].values ** 2 + xyz[1].values ** 2)[:, :, 0]
    values[:, :, 1] = np.exp(-((d_xy / 100) ** 2))
    values[:, :, 0] = np.exp(-((d_xy / 33) ** 2))
    return xtgeo.GridProperty(grid, values=np.ma.masked_where(np.isnan(values), values))


def test_default_testing_args(default_args, example_property):
    xn, yn, maps = aggregate_maps(**default_args)
    map_ = maps[0][0]
    assert xn.size == 20
    assert yn.size == 12
    assert map_.shape == (20, 12)
    npt.assert_allclose(map_, example_property.values[:, :, 1], atol=1e-12, rtol=0)


def test_surface_template(default_args, example_property):
    surf = xtgeo.RegularSurface(
        ncol=20,
        nrow=12,
        xinc=10,
        yinc=10,
        xori=-95,
        yori=-55,
    )
    kwargs = {**default_args, "map_template": surf}
    xn, yn, maps = aggregate_maps(**kwargs)
    map_ = maps[0][0]
    assert xn.size == surf.ncol
    assert yn.size == surf.nrow
    npt.assert_allclose(map_, example_property.values[:, :, 1], atol=1e-12, rtol=0)


def test_with_exclusions(default_args, example_grid, example_property):
    excludes = [np.ones(example_grid.dimensions, dtype=bool) for _ in range(5)]
    excludes[0][:, :, 0] = 0
    excludes[1][:, :, 1] = 0
    excludes[2][:, :, 2] = 0
    excludes[3][:, :6, :] = 0
    excludes[4][:10, :6, :] = 0
    excludes[4] = ~excludes[4]
    includes = [~ex.flatten() for ex in excludes]
    kwargs = {**default_args, "inclusion_filters": includes}
    _, _, maps = aggregate_maps(**kwargs)
    tols = dict(atol=1e-12, rtol=0)
    npt.assert_allclose(maps[0][0], example_property.values[:, :, 0], **tols)
    npt.assert_allclose(maps[1][0], example_property.values[:, :, 1], **tols)
    assert np.all(np.isnan(maps[2][0]))
    npt.assert_allclose(maps[3][0][:, :6], example_property.values[:, :6, 1], **tols)
    assert np.all(np.isnan(maps[3][0][excludes[3][:, :, 0]]))
    npt.assert_allclose(
        maps[4][0][~excludes[4][:, :, 0]],
        example_property.values[:, :, 1][~excludes[4][:, :, 0]],
        **tols,
    )
    assert np.all(np.isnan(maps[4][0][excludes[4][:, :, 0]]))


def test_mean_method(default_args, example_property):
    kwargs = {**default_args, "method": AggregationMethod.MEAN}
    _, _, maps = aggregate_maps(**kwargs)
    map_ = maps[0][0]
    assert np.all(map_ <= example_property.values[:, :, 1])
    assert np.all(map_ >= example_property.values[:, :, 0])


def test_min_method(default_args, example_property):
    kwargs = {**default_args, "method": AggregationMethod.MIN}
    _, _, maps = aggregate_maps(**kwargs)
    npt.assert_allclose(
        maps[0][0], example_property.values[:, :, 0], atol=1e-12, rtol=0
    )


def test_weight_by_dz(default_args, example_property):
    kwargs1 = {**default_args, "method": AggregationMethod.MEAN, "weight_by_dz": True}
    _, _, maps1 = aggregate_maps(**kwargs1)
    map_1 = maps1[0][0]
    kwargs2 = {**default_args, "method": AggregationMethod.SUM, "weight_by_dz": True}
    _, _, maps2 = aggregate_maps(**kwargs2)
    map_2 = maps2[0][0]
    npt.assert_array_less(map_1, map_2 + 1e-12)
