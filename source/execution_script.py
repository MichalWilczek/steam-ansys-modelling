import time
from time_stepping import Time
from ansys import Commands
from plots import Plots
from geometry import Geometry
from quench_velocity import QuenchFront
from quench_merge import QuenchMerge
from quench_detection import QuenchDetect

analysis_directory = "C:\\gitlab\\steam-ansys-modelling\\source\\APDL"
ans = Commands(directory=analysis_directory)

division = 1000
npoints = division+1           # number of nodes
coil_length = 10                # [m]
quench_init_pos = 0.5          # [m]
quench_init_length = 0.01      # [m]
total_time = 1.0               # [s]
time_division = 100.0          # number of time steps
time_step = total_time / time_division
init_x_up = quench_init_pos + quench_init_length
init_x_down = quench_init_pos - quench_init_length
# variables for ansys boundary/initial conditions
current = 100  # [A]
initial_temperature = 1.9  # [K]

# analysis initialization
ans.delete_file(filename='Variable_Input.inp')
ans.delete_file(filename='File_Position.txt')
ans.delete_file(filename='Process_Finished.txt')

ans.create_variable_file(npoints=npoints, division=division, coil_length=coil_length)
time.sleep(1)
ans.input_file(filename='Variable_Input', extension='inp')
ans.input_file(filename='Material_Properties_Superconducting', extension='inp', add_directory='Quench_Detection_Input_Files')
ans.input_file(filename='Geometry', extension='inp', add_directory='Quench_Detection_Input_Files')

coil_geometry = Geometry().length_coil(directory=analysis_directory, filename="File_Position.txt", division=division)
q_det = QuenchDetect(coil_length=coil_geometry, directory=analysis_directory, npoints=npoints)
min_coil_length = coil_geometry[0, 1]
max_coil_length = coil_geometry[len(coil_geometry)-1, 1]
time = Time.linear_time_stepping(time_step=time_step, total_time=total_time)     # user's time stepping vector

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
quench_fronts[0].front_down_to_node(coil_length=coil_geometry)
quench_fronts[0].front_up_to_node(coil_length=coil_geometry)
print(quench_fronts[0].to_string_node())

# initial analysis definition
ans.enter_preprocessor()
ans.select_nodes(node_down=quench_fronts[0].x_down_node, node_up=quench_fronts[0].x_up_node)
ans.select_elem_from_nodes()
ans.modify_material_type(element_number=1)
ans.modify_material_constant(constant_number=1)
ans.modify_material_number(material_number=1)

# temporary material properties to imitate turn-2-turn propagation
ans.select_nodes(node_down=495, node_up=505)
ans.select_elem_from_nodes()
ans.modify_material_number(material_number=6)
ans.select_nodes(node_down=895, node_up=905)
ans.select_elem_from_nodes()
ans.modify_material_number(material_number=7)
ans.enter_solver()
ans.set_analysis_setting()
ans.set_initial_temperature(temperature=initial_temperature)
ans.select_nodes(node_down=quench_fronts[0].x_down_node, node_up=quench_fronts[0].x_up_node)
ans.set_quench_temperature(q_temperature=q_det.calculate_critical_temperature())
ans.set_current(node_number=1, value=current)
ans.set_ground(node_number=npoints, value=0)
ans.set_time_step(time_step=t)
ans.input_file(filename='Solve_Get_Temp', extension='inp', add_directory='Quench_Detection_Input_Files')

# calculate new quench velocity
quench_fronts[0].calculate_q_front_pos_down(t_step=t, min_length=min_coil_length)
quench_fronts[0].calculate_q_front_pos_up(t_step=t, max_length=max_coil_length)
quench_fronts[0].front_down_to_node(coil_length=coil_geometry)
quench_fronts[0].front_up_to_node(coil_length=coil_geometry)
print(quench_fronts[0].to_string_node())

# detect new quench position
quench_front_new = q_det.detect_quench(input_quench_front_vector=quench_fronts, temperature_profile_file="Temperature_Data.txt")
for qf in quench_front_new:
    quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label))
    quench_label += 1

# plot temperature and quench
temporary_temperature_plot = Plots().plot_and_save_temperature(coil_length=coil_geometry, directory=analysis_directory, filename="Temperature_Data.txt", iteration=i, time_step=t)
quench_temperature_plots.append(temporary_temperature_plot)

# start calculation after initial time step
for i in range(1, len(time)):
    t = time[i]
    print("iteration number: {} \n time step: {} \n ______________".format(i, t))
    # what if quench fronts meet
    quench_fronts = QuenchMerge.quench_merge(quench_fronts=quench_fronts)
    temporary_quench_state_plot = Plots().plot_and_save_quench(coil_length=coil_geometry, quench_fronts=quench_fronts, iteration=i, time_step=t)
    quench_state_plots.append(temporary_quench_state_plot)

    for qf in quench_fronts:
        # position transformation into nodes
        qf.front_down_to_node(coil_length=coil_geometry)
        qf.front_up_to_node(coil_length=coil_geometry)
        print(qf.to_string_node())
        # apdl commands for material reassignment
        ans.select_nodes(node_down=qf.x_down_node, node_up=qf.x_up_node)
        ans.select_elem_from_nodes()
        ans.enter_preprocessor()
        ans.modify_material_type(element_number=1)
        ans.modify_material_constant(constant_number=1)
        ans.modify_material_number(material_number=1)
    ans.enter_solver()
    ans.restart_analysis()
    ans.set_time_step(time_step=t)
    ans.input_file(filename='Solve_Get_Temp', extension='inp', add_directory='Quench_Detection_Input_Files')

    # detect new quench position
    quench_front_new = q_det.detect_quench(input_quench_front_vector=quench_fronts, temperature_profile_file="Temperature_Data.txt")
    for qf in quench_front_new:
        print(qf[0])
        print(qf[1])
        quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label))
        quench_label += 1

    # calculate quench propagation
    for qf in quench_fronts:
        qf.calculate_q_front_pos_down(time_step, min_coil_length)
        qf.calculate_q_front_pos_up(time_step, max_coil_length)
    # plot temperature and quench
    temporary_temperature_plot = Plots().plot_and_save_temperature(coil_length=coil_geometry, directory=analysis_directory, filename="Temperature_Data.txt", iteration=i, time_step=t)
    quench_temperature_plots.append(temporary_temperature_plot)

Plots().create_video(plot_array=quench_state_plots, filename='video_quench_state.gif')
Plots().create_video(plot_array=quench_temperature_plots, filename='video_temperature_distribution.gif')
ans.save_analysis()
ans.terminate_analysis()
























#