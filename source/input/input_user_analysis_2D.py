
class InputUserAnalysis2D(object):

    # total number of windings to be analysed
    number_of_windings = 1

    # geometric constraints
    length_per_winding = 1.0                 # [m]
    # transverse size of 2D elements for windings and insulation
    transverse_dimension_winding = 0.000941  # [m]
    transverse_dimension_insulation = 0.0    # [m]

    # mesh size
    division_per_winding = 1000              # [-]
    # max number of elements across the winding domain in transverse direction
    # one needs to specify what maximum number of nodes is created across the given number of elements
    transverse_division_winding = 3
    winding_plane_max_number_nodes = 5       # [-]
