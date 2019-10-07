
class InputUserSkewQuadrupole(object):

    # geometrical constraints of given magnet
    strand_diameter = 0.7       # [mm]
    winding_side = 0.941        # [mm]
    coil_long_side = 413.21     # [mm]
    coil_short_side = 126.81    # [mm]
    coil_initial_radius = 9.15  # [mm]
    number_turns_in_layer = 29  # [-]
    number_layers = 26          # [-]

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



