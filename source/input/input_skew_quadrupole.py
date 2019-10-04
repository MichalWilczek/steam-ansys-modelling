
class InputSkewQuadrupole(object):

    # geometrical constraints of given magnet
    STRAND_DIAMETER = 0.7       # [mm]
    WINDING_SIDE = 0.941        # [mm]
    COIL_LONG_SIDE = 413.21     # [mm]
    COIL_SHORT_SIDE = 126.81    # [mm]
    COIL_INITIAL_RADIUS = 9.15  # [mm]
    NUMBER_TURNS_IN_LAYER = 29  # [-]
    NUMBER_LAYERS = 26          # [-]

    # mesh specification
    # mesh of the winding
    division_long_side = 100
    division_short_side = 30
    division_radius = 5

    # material properties specification
    rrr = 193.0                 # [-]

    # analysis constraints
    # specify how many windings should be analysed and which number should be counted as first in Python geometry
    winding_number_first_in_analysis = 233
    winding_number_last_in_first_layer = 234
    number_of_layers_in_analysis = 2



