
class InputUser(object):

    # directory for initial material properties
    material_properties_directory = "C:\\gitlab\\steam-ansys-modelling\\material_properties"

    # specify the co-simulation criteria
    build_electric_circuit = False
    transient_electric_analysis = False

    # specify whether thermal quench propagation analysis in ANSYS
    # should be calculated by means of electro-thermal elements or thermal-elements
    electric_ansys_elements = False

    # specify magnetic map model
    # ("1D_constant", "2D_constant", "2D_static", "2D_transient")
    # if magnetic field is constant, specify its value, otherwise, assign None
    # if magnetic field is a 2D map, specify whether plotting the graphs should happen in the analysis (True or False)
    # in case of 1D, leave None value
    magnetic_map_model = "2D_constant"
    constant_magnetic_field_value = 2.0     # [T]
    magnetic_field_map_plot = False

    # specify which type of analysis should be conducted for thermal quench propagation ("1D", "multiple_1D", "2D")
    dimensionality = "multiple_1D"

    # specify what type of analysis should be conducted ("heat_balance", "quench_velocity")
	# if "heat_balance" is chosen, leave v_quench_model = None
	# otherwise, choose between "constant" and "numerical"
    analysis_type = "heat_balance"
    v_quench_model = None

    # specify initial conditions for quench position
    quench_init_position = 0.5      # [m]
    quench_init_length = 0.1        # [m]

    # specify final length of the simulation
    time_total_simulation = 0.04    # [s]
    time_step_cosimulation = 0.01   # [s] - coupling time between ANSYS and Python
    time_step_min_ansys = 1.0     # [ms]
    time_step_max_ansys = 10.0      # [ms]

    # specify initial conditions for the simulation
    current_init = 100.0                                # [A]
    temperature_init = 1.9                              # [K]
    temperature_max_init_quenched_zone = 10.0           # [K]
    magnetic_field_initially_quenched_winding = 2.0     # [B]

    # specify initial temperature distribution in quenched zone ("uniform", "gaussian_distribution")
    temperature_init_distr = "uniform"

    # specify material properties repository ("linear", "nonlinear")
    material_properties_type = "nonlinear"

    # specify geometry type to analyse ("slab", "skew_quadrupole", next ones to be added in the future...)
    geometry_type = "slab"

    # specify whether insulation should be analysed
    insulation_analysis = True