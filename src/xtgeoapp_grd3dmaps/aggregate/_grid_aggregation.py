from typing import List, Optional, Tuple, Union
import numpy as np
import xtgeo
import scipy.interpolate
import scipy.spatial
import scipy.sparse

from xtgeoapp_grd3dmaps.aggregate._config import AggregationMethod


def aggregate_maps(
    map_template: Union[xtgeo.RegularSurface, float],
    grid: xtgeo.Grid,
    grid_props: List[xtgeo.GridProperty],
    inclusion_filters: List[Optional[np.ndarray]],
    method: AggregationMethod,
    weight_by_dz: bool,
) -> Tuple[np.ndarray, np.ndarray, List[List[np.ndarray]]]:
    """
    Aggregate multiple grid properties, using multiple grid cell filters, to 2D maps.

    Args:
        map_template: Template to use for the generated maps. If a float is provided, it
            will be used as an approximate pixel-to-cell-size ratio to automatically set
            map bounds and resolution from the grid.
        grid: The 3D grid
        grid_props: List of the grid properties to be aggregated
        inclusion_filters: List containing the grid cell filters. A filter is defined by
            either a numpy array or `None`. If a numpy array is used, it must be a
            boolean 1D array representing which cells (among the active cells) that are
            to be included. A `1` indicates inclusion. If `None` is provided, all of the
            grid cells are included.
        method: The aggregation method to apply for pixels that overlap more than one
            grid cell in the xy-plane
        weight_by_dz: Weights cells by thickness (dz) when aggregating. Not relevant if
            method is MIN or MAX

    Returns:
        Doubly nested list of maps. The first index corresponds to `ìnclusion_filters`,
        and the second index to `grid_props`.
    """
    # Determine cells where properties are always masked
    active = grid.actnum_array.flatten().astype(bool)
    props = [p.values1d[active] for p in grid_props]
    if weight_by_dz:
        weights = grid.get_dz().values1d[active]
    else:
        weights = None
    props, active, inclusion_filters, weights = _remove_where_all_props_are_masked(
        props, active, inclusion_filters, weights
    )
    # Map nodes (pixel locations) and connections
    x_nodes, y_nodes, connections = _find_nodes_and_connections(
        grid,
        active,
        map_template
    )
    # Iterate filters
    results = []
    for incl in inclusion_filters:
        rows0, cols0 = connections
        if incl is not None:
            to_remove = ~np.isin(connections[1], np.argwhere(incl).flatten())
            rows0 = rows0[~to_remove]
            cols0 = cols0[~to_remove]
        results.append([])
        for prop in props:
            results[-1].append(_property_to_map(
                (rows0, cols0),
                prop,
                weights,
                x_nodes.size,
                y_nodes.size,
                method,
            ))
    return x_nodes, y_nodes, results


def _remove_where_all_props_are_masked(
    props: np.ma.MaskedArray,
    active: np.ndarray,
    inclusion_filters: List[Optional[np.ma.MaskedArray]],
    weights: np.ndarray,
):
    all_masked = np.all([p.mask for p in props], axis=0)
    if not any(i is None for i in inclusion_filters):
        all_masked |= ~np.any(inclusion_filters, axis=0)
    active[active] = ~all_masked
    props = [p[~all_masked] for p in props]
    inclusion_filters = [
        None if inc is None else inc[~all_masked]
        for inc in inclusion_filters
    ]
    if weights is not None:
        weights = weights[~all_masked]
    return props, active, inclusion_filters, weights


def _find_nodes_and_connections(
    grid: xtgeo.Grid,
    active_cells: np.ndarray,
    map_template: Union[xtgeo.RegularSurface, float],
):
    boxes, footprints = _cell_footprints(grid, active_cells)
    if isinstance(map_template, xtgeo.RegularSurface):
        x_nodes = (
            map_template.xori
            + map_template.xinc * np.arange(0, map_template.ncol, dtype=float)
        )
        y_nodes = (
            map_template.yori
            + map_template.yinc * np.arange(0, map_template.nrow, dtype=float)
        )
    else:
        x_nodes, y_nodes = _derive_map_nodes(
            boxes, pixel_to_cell_size_ratio=map_template
        )
    # Find connections
    connections = _connect_grid_and_map(
        x_nodes,
        y_nodes,
        boxes,
        footprints,
    )
    return x_nodes, y_nodes, connections


def _derive_map_nodes(boxes, pixel_to_cell_size_ratio):
    box = np.min(boxes[0]), np.min(boxes[1]), np.max(boxes[2]), np.max(boxes[3])
    res = np.mean([np.mean(boxes[2] - boxes[0]), np.mean(boxes[3] - boxes[1])])
    res /= pixel_to_cell_size_ratio
    x_nodes = np.arange(box[0] + res / 2, box[2] - res / 2 + 1e-12, res)
    y_nodes = np.arange(box[1] + res / 2, box[3] - res / 2 + 1e-12, res)
    return x_nodes, y_nodes


def _extract_all_overlaps(i0, i_range, j0, j_range):
    ij_pairs = []
    indices = []
    for ni in range(1, i_range.max() + 1):
        for nj in range(1, j_range.max() + 1):
            ix = (i_range == ni) & (j_range == nj)
            if ix.sum() == 0:
                continue
            __i0 = i0[ix]
            __j0 = j0[ix]
            for qi in range(ni):
                for qj in range(nj):
                    i = __i0 + qi
                    j = __j0 + qj
                    ij_pairs.append(np.column_stack((i, j)))
            n_tot = ni * nj
            indices.append(np.kron(
                np.ones(n_tot, dtype=int), np.argwhere(ix).flatten()
            ))
    return np.vstack(ij_pairs), np.hstack(indices)


def _connect_grid_and_map(
    x_nodes,
    y_nodes,
    boxes,
    footprints,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns a mapping between the provided grid nodes and map pixels as an np.ndarray
    pair, the first referring to pixel indices and the second to corresponding grid
    indices. A grid node may be mapped to multiple pixels, and vice verse.
    """
    i0, i_range = _find_overlapped_nodes(x_nodes, boxes[0], boxes[2])
    j0, j_range = _find_overlapped_nodes(y_nodes, boxes[1], boxes[3])
    pixels_ij, box_indices = _extract_all_overlaps(i0, i_range, j0, j_range)
    rows = np.ravel_multi_index(pixels_ij.T, (x_nodes.size, y_nodes.size))
    cols = box_indices
    x_mesh, y_mesh = np.meshgrid(x_nodes, y_nodes, indexing="ij")
    rows, cols = _filter_on_footprint(
        (rows, cols),
        footprints,
        nodes_xx=x_mesh.flatten(),
        nodes_yy=y_mesh.flatten(),
    )
    return rows, cols


def _find_overlapped_nodes(nodes, cell_lower, cell_upper):
    i0 = np.searchsorted(nodes, cell_lower)
    i1 = np.searchsorted(nodes, cell_upper)
    lengths = i1 - i0
    return i0, lengths


def _cell_footprints(grid: xtgeo.Grid, active_cells):
    corners = grid.get_xyz_corners()
    xyz = [c.values1d[active_cells] for c in corners]
    avg_xyz = [(xyz[i] + xyz[i + 12]) / 2 for i in range(12)]
    x_corners = avg_xyz[::3]
    y_corners = avg_xyz[1::3]
    # z_corners = avg_xyz[2::3]
    boxes = (
        np.minimum.reduce(x_corners),
        np.minimum.reduce(y_corners),
        np.maximum.reduce(x_corners),
        np.maximum.reduce(y_corners),
    )
    fp_x = np.array(x_corners)
    fp_y = np.array(y_corners)
    fp_x = fp_x[[0, 1, 3, 2]].T
    fp_y = fp_y[[0, 1, 3, 2]].T
    return boxes, (fp_x, fp_y)


def _filter_on_footprint(connections, footprints, nodes_xx, nodes_yy):
    """
    Filters pixel-grid cell connections based on the actual polygonal footprint of a
    grid cell, not only the bounding box around the grid cell.
    """
    # N - number of pixel-grid cell pairs
    # Extract the grid cell polygons and node locations for each pair
    grid_xs = footprints[0][connections[1]]  # N x 4
    grid_ys = footprints[1][connections[1]]  # N x 4
    node_xs = nodes_xx[connections[0]]  # N
    node_ys = nodes_yy[connections[0]]  # N

    # Wrap polygons so that first point is duplicated as the last. Transpose for easier
    # indexing.
    grid_xs = np.column_stack((grid_xs, grid_xs[:, 0])).T  # 5 x N
    grid_ys = np.column_stack((grid_ys, grid_ys[:, 0])).T  # 5 x N
    # The following checks if a given node is contained within its corresponding grid
    # cell based on the following. A line is drawn in y-direction from the pixel
    # location to negative infinity. The number of intersections between this line and
    # the lines comprising the polygon is counted. If this number is odd, the pixel is
    # within the grid cell, otherwise, it is outside.
    dx = np.diff(grid_xs, axis=0)
    too_small = np.abs(dx) < 1e-12
    dx[too_small] = np.sign(dx[too_small]) * 1e-12
    # w and interp_y is calculated everywhere, but technically only used where overlap_x
    # is True. For performance, we can calculate overlap_x first, then interp_y and w
    # only where overlap_x is True. Future work...
    w = (node_xs - grid_xs[:-1]) / dx
    interp_y = (1 - w) * grid_ys[:-1] + w * grid_ys[1:]
    overlap_x = (w <= 1.0) & (w >= 0.0)
    overlap_y = (interp_y >= node_ys)
    crosses = (overlap_x & overlap_y).astype(int).sum(axis=0)
    pt_in_cell = (crosses % 2) == 1
    return connections[0][pt_in_cell], connections[1][pt_in_cell]


def _property_to_map(
    connections: Tuple[np.ndarray, np.ndarray],
    prop: np.ndarray,
    weights: Optional[np.ndarray],
    nx: int,
    ny: int,
    method: AggregationMethod,
):
    rows, cols = connections
    assert rows.shape == cols.shape
    assert weights is None or weights.shape == prop.shape
    if weights is not None:
        assert method in [AggregationMethod.MEAN, AggregationMethod.SUM]
    data = prop[cols]
    col_weights = np.ones_like(data) if weights is None else weights[cols]
    if data.mask.any():
        invalid = data.mask
        rows = rows[~invalid]
        cols = cols[~invalid]
        data = data[~invalid]
        col_weights = col_weights[~invalid]

    if data.size == 0:
        return np.full((nx, ny), fill_value=np.nan)
    shape = (nx * ny, max(cols) + 1)
    # Calculate temporary data shift to avoid unintended deletion of data by tocsc:
    if method == AggregationMethod.MAX:
        shift = data.min() - 1
    elif method == AggregationMethod.MIN:
        shift = data.max() + 1
    elif method in (AggregationMethod.MEAN, AggregationMethod.SUM):
        shift = 0.0
    else:
        raise NotImplementedError

    p_arr = scipy.sparse.coo_matrix(
        (data - shift, (rows, cols)), shape=shape
    ).tocsc()
    w_arr = scipy.sparse.coo_matrix(
        (col_weights, (rows, cols)), shape=shape
    ).tocsc()
    total_weight = w_arr.sum(axis=1)
    # Make sure to shift data to avoid
    if method == AggregationMethod.MAX:
        res = p_arr.max(axis=1).toarray()
    elif method == AggregationMethod.MIN:
        res = p_arr.min(axis=1).toarray()
    elif method == AggregationMethod.MEAN:
        div = np.where(total_weight > 0, total_weight, 1)  # Avoid division by zero
        res = (p_arr.multiply(w_arr)).sum(axis=1) / div
        res = np.asarray(res)
    elif method == AggregationMethod.SUM:
        # res = np.asarray(sarr.sum(axis=1))
        res = np.asarray((p_arr.multiply(w_arr)).sum(axis=1))
    else:
        raise NotImplementedError
    total_weight = np.array(total_weight).flatten()
    res = res.flatten() + shift
    res[total_weight == 0] = np.nan
    res = res.reshape(nx, ny)
    return res
