import numpy as np
from matplotlib import path


def points_in_polygon(polygon, pts):
    """Get boolean mask of points in a polygon reusing matplotlib implementation.

    The fallback code is based from StackOverflow answer by ``Ta946`` in this question:
    https://stackoverflow.com/questions/36399381/whats-the-fastest-way-of-checking-if-a-point-is-inside-a-polygon-in-python

    This is a proof of concept and depending on your use case, willingness
    to add other dependencies, and your performance needs one of the other answers
    on the above question would serve you better (ex. shapely, etc).
    """
    # Filter vertices out of the polygon's bounding box, this serve as an early optimization whenever number of vertices
    # to filter out is huge.
    x1, x2, y1, y2 = min(polygon[:, 0]), max(polygon[:, 0]), min(polygon[:, 1]), max(polygon[:, 1])
    selection_mask = (x1 < pts[:, 0]) & (pts[:, 0] < x2) & (y1 < pts[:, 1]) & (pts[:, 1] < y2)
    pts_in_bbox = pts[selection_mask]

    # Select vertices inside the polygon.
    if path is not None:
        polygon = path.Path(polygon[:, :2], closed=True)
        polygon_mask = polygon.contains_points(pts_in_bbox[:, :2])
    else:
        contour2 = np.vstack((polygon[1:], polygon[:1]))
        test_diff = contour2 - polygon
        m1 = (polygon[:, 1] > pts_in_bbox[:, None, 1]) != (contour2[:, 1] > pts_in_bbox[:, None, 1])
        slope = ((pts_in_bbox[:, None, 0] - polygon[:, 0]) * test_diff[:, 1]) - (
                test_diff[:, 0] * (pts_in_bbox[:, None, 1] - polygon[:, 1]))
        m2 = slope == 0
        mask2 = (m1 & m2).any(-1)
        m3 = (slope < 0) != (contour2[:, 1] < polygon[:, 1])
        m4 = m1 & m3
        count = np.count_nonzero(m4, axis=-1)
        mask3 = ~(count % 2 == 0)
        polygon_mask = mask2 | mask3

    # Return the full selection mask based on bounding box & polygon selection.
    selection_mask[np.where(selection_mask == True)] &= polygon_mask

    return selection_mask


def select(polygon_vertices, points, scatter):
    # Set default mask to filter everything since user selection
    # is not yet calculated.
    selected_mask = np.full((len(points), 4), (1, 1, 0, 1))

    if polygon_vertices is not None:
        # Optimization: It's faster to convert lasso selection straight to visual coordinates since there's generally less vertices
        # this would speed up the processing depending on the scene.
        polygon_vertices = scatter.get_transform('canvas', 'visual').map(polygon_vertices)
        selected_mask = points_in_polygon(polygon_vertices, points)

    return selected_mask
