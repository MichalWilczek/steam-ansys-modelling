
class InputSlab(object):

    # geometrical constraints of given geometry
    strand_diameter = 0.7       # [mm]
    winding_side = 0.941        # [mm]
    number_turns_in_layer = 1  # [-]
    number_layers = 1          # [-]
    length_per_winding = 1.0  # [m]

    # mesh specification
    # mesh of the winding
    division_per_winding = 100  # [-]

    # material properties specification
    rrr = 193.0                 # [-]
