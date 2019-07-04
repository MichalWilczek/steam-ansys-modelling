import time
from model_input import ModelInput
from ansys import Commands
from plots import Plots
from geometry import Geometry
from quench_velocity import QuenchFront
from quench_merge import QuenchMerge
from quench_detection import QuenchDetect

# 1D version needs to be updated for the current version of the program

analysis_directory = None
coil_geometry = None
dimensionality = "2D"

# parameters for 2D analysis
number_windings = 5             # number of windings analyzed
max_nodes_cross_section = 5     # maximum number of nodes that can be in the winding cross-section
winding_length = 0.5            # [m]
winding_width = 0.840*0.001     # [m]

length_division = 500          # number of element divisions along one winding
insulation_division = 3         # number of element divisions across the insulation layer
insulation_width = 0.101*0.001
winding_division = 2            # number of element divisions across the coil cross-section

quench_init_pos = 1.75          # [m]
quench_init_length = 0.01       # [m]
total_time = 0.5                # [s]
time_division = 200.0           # number of time steps
time_step = total_time / time_division
init_x_up = quench_init_pos + quench_init_length
init_x_down = quench_init_pos - quench_init_length

# variables for ansys boundary/initial conditions
current = 10000                 # [A]
initial_temperature = 1.9       # [K]

if dimensionality == "1D":
    analysis_directory = "C:\\gitlab\\steam-ansys-modelling\\source\APDL\\1D"
elif dimensionality == "2D" or dimensionality == "3D":
    analysis_directory = "C:\\gitlab\\steam-ansys-modelling\\source\\APDL\\2D"
ans = Commands(directory=analysis_directory)

# analysis initialization
ans.delete_file(filename='Variable_Input.inp')
ans.delete_file(filename='File_Position.txt')
ans.delete_file(filename='Process_Finished.txt')

if dimensionality == "1D":
    print("Update Required...")
elif dimensionality == "2D":
    ans.create_variable_file_2d(number_windings, max_nodes_cross_section, winding_length, winding_width,
                                length_division, insulation_division, insulation_width, winding_division)
time.sleep(1)
ans.input_file(filename='Variable_Input', extension='inp')
if dimensionality == "1D":
    ans.input_file(filename='1D_Material_Properties_Superconducting', extension='inp', add_directory='Input_Files')
    ans.input_file(filename='1D_Geometry', extension='inp', add_directory='1D\\Input_Files')
elif dimensionality == "2D":
    ans.input_file(filename='2D_Material_Properties_Superconducting', extension='inp', add_directory='Input_Files')
    ans.input_file(filename='2D_Geometry', extension='inp', add_directory='Input_Files')

npoints = Geometry.load_parameter(directory=analysis_directory, filename="Nnode.txt")
if dimensionality == "1D":
    geo_1d = Geometry(file_directory=analysis_directory)
    coil_geometry = geo_1d.length_coil()
elif dimensionality == "2D":
    geo_2d = Geometry(file_directory=analysis_directory)
    coil_geometry = geo_2d.coil_length_1d

q_det = QuenchDetect(coil_length=coil_geometry, directory=analysis_directory, npoints=npoints)
min_coil_length = coil_geometry[0, 1]
max_coil_length = coil_geometry[len(coil_geometry)-1, 1]
time = ModelInput.linear_time_stepping(time_step=time_step, total_time=total_time)     # user's time stepping vector

quench_fronts = []
quench_state_plots = []
quench_temperature_plots = []

# initial iteration
quench_label = 1
i = 0
t = time[i]
print("iteration number: {} \n time step: {} \n ______________".format(i, t))

quench_fronts.append(QuenchFront(x_down=init_x_down, x_up=init_x_up, label=quench_label))
quench_label += 1
temporary_quench_state_plot = Plots().plot_and_save_quench(coil_length=coil_geometry, quench_fronts=quench_fronts, iteration=i, time_step=t)
quench_state_plots.append(temporary_quench_state_plot)

# position transformation into nodes
quench_fronts[0].convert_quench_front_to_nodes(coil_length=coil_geometry)

# initial analysis definition
ans.enter_preprocessor()
if dimensionality == "1D":
    ans.select_nodes(node_down=quench_fronts[0].x_down_node, node_up=quench_fronts[0].x_up_node)
elif dimensionality == "2D":
    nodes_to_select = geo_2d.convert_imaginary_node_set_into_real_nodes(x_down_node=quench_fronts[0].x_down_node, x_up_node=quench_fronts[0].x_up_node)
    nodes_to_select_ansys = geo_2d.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_select)
    ans.select_nodes_list(nodes_list=nodes_to_select_ansys)
ans.select_elem_from_nodes()
ans.modify_material_type(element_number=1)
ans.modify_material_constant(constant_number=1)
ans.modify_material_number(material_number=1)

# couple neighbouring windings
nodes_to_couple_windings_list = geo_2d.create_node_list_to_couple_windings()
for nodes_list in nodes_to_couple_windings_list:
    nodes_to_select_ansys = geo_2d.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_list)
    ans.select_nodes_list(nodes_list=nodes_to_select_ansys)
    ans.couple_nodes(dof="volt")
    ans.couple_nodes(dof="temp")

# couple neighbouring interfaces
nodes_to_couple_interfaces_list = geo_2d.create_node_list_to_couple_interfaces()
ans.allsel()
nodes_to_unselect_ansys = geo_2d.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_couple_interfaces_list)
ans.unselect_nodes_list(nodes_list=nodes_to_unselect_ansys)
ans.couple_interface(dof="temp")

ans.enter_solver()
ans.set_analysis_setting()
ans.set_time_step(time_step=t)
ans.set_initial_temperature(temperature=initial_temperature)

# set initial quench temperature
if dimensionality == "1D":
    ans.select_nodes(node_down=quench_fronts[0].x_down_node, node_up=quench_fronts[0].x_up_node)
elif dimensionality == "2D":
    nodes_to_select = geo_2d.convert_imaginary_node_set_into_real_nodes(x_down_node=quench_fronts[0].x_down_node, x_up_node=quench_fronts[0].x_up_node)
    nodes_to_select_ansys = geo_2d.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_select)
    ans.select_nodes_list(nodes_list=nodes_to_select_ansys)
# ans.set_quench_temperature(q_temperature=q_det.calculate_critical_temperature())
ans.set_quench_temperature(q_temperature=9.5)

# set constant inflow current
if dimensionality == "1D":
    ans.set_current(node_number=1, value=current)
elif dimensionality == "2D":
    nodes_for_current = geo_2d.create_node_list_for_current()
    nodes_to_select_ansys = geo_2d.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_for_current)
    ans.select_nodes_list(nodes_list=nodes_to_select_ansys)
    ans.set_current(node_number="all", value=current)

# set ground
if dimensionality == "1D":
    ans.set_ground(node_number=npoints, value=0)
elif dimensionality == "2D":
    nodes_for_ground = geo_2d.create_node_list_for_ground()
    nodes_to_select_ansys = geo_2d.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_for_ground)
    ans.select_nodes_list(nodes_list=nodes_to_select_ansys)
    ans.set_ground(node_number="all", value=0)

if dimensionality == "1D":
    ans.input_file(filename='1D_Solve_Get_Temp', extension='inp', add_directory='input_files')
elif dimensionality == "2D":
    ans.input_file(filename='2D_Solve_Get_Temp', extension='inp', add_directory='input_files')

# calculate new quench velocity
quench_fronts[0].calculate_quench_front_position(t_step=t, min_length=min_coil_length, max_length=max_coil_length)

# detect new quench position
if dimensionality == "1D":
    quench_front_new = q_det.detect_quench_1d(input_quench_front_vector=quench_fronts, temperature_profile_file="Temperature_Data.txt")
elif dimensionality == "2D":
    temperature_profile_1d = geo_2d.create_1d_imaginary_temperature_profile(directory=analysis_directory, npoints=npoints)
    quench_front_new = q_det.detect_quench_2d_3d(input_quench_front_vector=quench_fronts, temperature_profile=temperature_profile_1d)

for qf in quench_front_new:
    quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label))
    quench_label += 1

# plot temperature and quench
if dimensionality == "1D":
    print("Update Required...")
elif dimensionality == "2D":
    temporary_temperature_plot = Plots().plot_and_save_temperature(coil_length=coil_geometry, directory=analysis_directory, temperature_profile_1d=temperature_profile_1d, iteration=i, time_step=t)
    quench_temperature_plots.append(temporary_temperature_plot)

# start calculation after initial time step
for i in range(1, len(time)):
# for i in range(1, 11):
    ans.save_analysis()
    t = time[i]
    print("iteration number: {} \n time step: {} \n ______________".format(i, t))
    # what if quench fronts meet
    quench_fronts = QuenchMerge.quench_merge(quench_fronts=quench_fronts)
    temporary_quench_state_plot = Plots().plot_and_save_quench(coil_length=coil_geometry, quench_fronts=quench_fronts, iteration=i, time_step=t)
    quench_state_plots.append(temporary_quench_state_plot)

    for qf in quench_fronts:
        # position transformation into nodes
        qf.convert_quench_front_to_nodes(coil_length=coil_geometry)

        if dimensionality == "1D":
            ans.select_nodes(node_down=qf.x_down_node, node_up=qf.x_up_node)
        elif dimensionality == "2D":
            nodes_to_select = geo_2d.convert_imaginary_node_set_into_real_nodes(x_down_node=qf.x_down_node, x_up_node=qf.x_up_node)
            nodes_to_select_ansys = geo_2d.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_to_select)
            ans.select_nodes_list(nodes_list=nodes_to_select_ansys)
        ans.select_elem_from_nodes()
        ans.enter_preprocessor()
        ans.modify_material_type(element_number=1)
        ans.modify_material_constant(constant_number=1)
        ans.modify_material_number(material_number=1)

    ans.enter_solver()
    ans.restart_analysis()
    ans.set_time_step(time_step=t)

    if dimensionality == "1D":
        ans.input_file(filename='1D_Solve_Get_Temp', extension='inp', add_directory='input_files')
    elif dimensionality == "2D":
        ans.input_file(filename='2D_Solve_Get_Temp', extension='inp', add_directory='input_files')

    # detect new quench position
    if dimensionality == "1D":
        quench_front_new = q_det.detect_quench_1d(input_quench_front_vector=quench_fronts, temperature_profile_file="Temperature_Data.txt")
    elif dimensionality == "2D":
        temperature_profile_1d = geo_2d.create_1d_imaginary_temperature_profile(directory=analysis_directory, npoints=npoints)
        quench_front_new = q_det.detect_quench_2d_3d(input_quench_front_vector=quench_fronts, temperature_profile=temperature_profile_1d)

    for qf in quench_front_new:
        quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label))
        quench_label += 1

    # calculate quench propagation
    for qf in quench_fronts:
        qf.calculate_quench_front_position(t_step=t, min_length=min_coil_length, max_length=max_coil_length)

    if dimensionality == "1D":
        print("Update Required...")
    elif dimensionality == "2D":
        temporary_temperature_plot = Plots().plot_and_save_temperature(coil_length=coil_geometry, directory=analysis_directory, temperature_profile_1d=temperature_profile_1d, iteration=i, time_step=t)
        quench_temperature_plots.append(temporary_temperature_plot)

Plots().create_video(plot_array=quench_state_plots, filename='video_quench_state.gif')
Plots().create_video(plot_array=quench_temperature_plots, filename='video_temperature_distribution.gif')
ans.save_analysis()
ans.terminate_analysis()
























#