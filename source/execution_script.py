
from source.ansys_input import AnsysInput
from source.ansys import AnsysCommands
from source.model_input import ModelInput

from source.plots import Plots
from source.geometry import Geometry
from source.quench_velocity import QuenchFront
from source.quench_merge import QuenchMerge
from source.quench_detection import QuenchDetect
from source.factory import AnalysisDirectory
from source.factory import AnalysisBuilder


AnsysInput.delete_old_files()
AnsysInput.create_variable_file()
AnsysCommands().input_file(filename='Variable_Input', extension='inp')
AnsysInput.input_material_properties()
AnsysInput.input_geometry()

npoints = Geometry.load_parameter(filename="Nnode.txt")
coil_geometry = Geometry().create_geometry()

q_det = QuenchDetect(coil_length=coil_geometry, npoints=npoints)
min_coil_length = coil_geometry[0, 1]
max_coil_length = coil_geometry[len(coil_geometry)-1, 1]
time = ModelInput.linear_time_stepping()     # user's time stepping vector

quench_fronts = []
quench_state_plots = []
quench_temperature_plots = []

# initial iteration
quench_label = 1
i = 0
t = time[i]
print("iteration number: {} \n time step: {} \n ______________".format(i, t))
quench_fronts.append(QuenchFront(x_down=AnalysisBuilder().get_quench_init_x_down(),
                                 x_up=AnalysisBuilder().get_quench_init_x_up(), label=quench_label))
quench_label += 1
temporary_quench_state_plot = Plots().plot_and_save_quench(coil_length=coil_geometry, quench_fronts=quench_fronts,
                                                           iteration=i, time_step=t)
quench_state_plots.append(temporary_quench_state_plot)

# position transformation into nodes
quench_fronts[0].convert_quench_front_to_nodes(coil_length=coil_geometry)

# initial analysis definition
AnsysCommands().enter_preprocessor()
AnsysInput.select_nodes_for_multiple_dimensions(x_down_node=quench_fronts[0].x_down_node,
                                                x_up_node=quench_fronts[0].x_up_node)
AnsysCommands().select_elem_from_nodes()
AnsysCommands().modify_material_type(element_number=1)
AnsysCommands().modify_material_constant(constant_number=1)
AnsysCommands().modify_material_number(material_number=1)

# couple nodes, not for 1D analysis
if AnalysisBuilder().get_dimensionality() != "1D":
    nodes_to_couple_interfaces_list = Geometry.create_node_list_to_couple_interfaces()
    AnsysCommands().allsel()
    nodes_to_unselect_ansys = Geometry.prepare_ansys_nodes_selection_list(
        real_nodes_list=nodes_to_couple_interfaces_list)
    AnsysCommands().unselect_nodes_list(nodes_list=nodes_to_unselect_ansys)
    AnsysCommands().couple_interface(dof="temp")

AnsysCommands().enter_solver()
AnsysCommands().set_analysis_setting()
AnsysCommands().set_time_step(time_step=t)
AnsysCommands().set_initial_temperature(temperature=AnalysisBuilder().get_initial_temperature())

# set initial quench temperature
AnsysInput.select_nodes_for_multiple_dimensions(x_down_node=quench_fronts[0].x_down_node,
                                                x_up_node=quench_fronts[0].x_up_node)
AnsysCommands().set_quench_temperature(q_temperature=9.5)

# set constant inflow current
AnsysInput.select_nodes_for_current_for_multiple_dimensions()
AnsysCommands().set_current(node_number="all", value=AnalysisBuilder().get_current())

# set ground
AnsysInput.set_ground_for_multiple_dimensions()

# input solver ANSYS APDL file
AnsysInput.input_solver_file_for_multiple_dimensions()

# get temperature profile
temperature_profile = AnsysInput.get_temperature_profile_for_multiple_dimensions(npoints=npoints) # needs to be updated

# detect new quench position
quench_front_new = q_det.detect_quench(input_quench_front_vector=quench_fronts, temperature_profile=temperature_profile)

for qf in quench_front_new:
    quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label))
    quench_label += 1

# plot temperature and quench
temporary_temperature_plot = Plots().plot_and_save_temperature(coil_length=coil_geometry, temperature_profile_1d=temperature_profile, iteration=i, time_step=t)
quench_temperature_plots.append(temporary_temperature_plot)

# start calculation after initial time step
for i in range(1, len(time)):
    AnsysCommands().save_analysis()
    t = time[i]
    print("iteration number: {} \n time step: {} \n ______________".format(i, t))
    # what if quench fronts meet
    quench_fronts = QuenchMerge.quench_merge(quench_fronts=quench_fronts)
    temporary_quench_state_plot = Plots().plot_and_save_quench(coil_length=coil_geometry, quench_fronts=quench_fronts, iteration=i, time_step=t)
    quench_state_plots.append(temporary_quench_state_plot)

    for qf in quench_fronts:
        # position transformation into nodes
        qf.convert_quench_front_to_nodes(coil_length=coil_geometry)

        # initial analysis definition
        AnsysCommands().enter_preprocessor()
        AnsysInput.select_nodes_for_multiple_dimensions(x_down_node=quench_fronts[0].x_down_node,
                                                        x_up_node=quench_fronts[0].x_up_node)
        AnsysCommands().select_elem_from_nodes()
        AnsysCommands().enter_preprocessor()
        AnsysCommands().modify_material_type(element_number=1)
        AnsysCommands().modify_material_constant(constant_number=1)
        AnsysCommands().modify_material_number(material_number=1)

    AnsysCommands().enter_solver()
    AnsysCommands().restart_analysis()
    AnsysCommands().set_time_step(time_step=t)


























