
class InputSlab(object):

    # geometrical constraints of given geometry
    STRAND_DIAMETER = 0.7       # [mm]
    WINDING_SIDE = 0.941        # [mm]
    NUMBER_TURNS_IN_LAYER = 2  # [-]
    NUMBER_LAYERS = 2          # [-]
    length_per_winding = 1.0  # [m]

    # mesh specification
    # mesh of the winding
    division_per_winding = 1000  # [-]

    # material properties specification
    rrr = 193.0                 # [-]
