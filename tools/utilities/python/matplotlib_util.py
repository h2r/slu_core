from spatial_features_cxx import math2d_dist
def size_of_axes_in_data_coordinates(axes):
    pt = axes.transAxes.transform_point((1, 1))
    max_p = axes.transData.inverted().transform_point(pt)

    pt = axes.transAxes.transform_point((0, 0))
    min_p = axes.transData.inverted().transform_point(pt)
    
    return math2d_dist(min_p, max_p)
