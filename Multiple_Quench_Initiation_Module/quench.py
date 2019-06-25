from plots import Plots
from variables import Variables
from geometry import Geometry
from quench_velocity import QuenchFront
from ansys import Commands
import time

 # analysis initialization
Commands().delete_file(filename='Variable_Input', extension='inp')
Commands().delete_file(filename='File_Position', extension='inp')
Commands().delete_file(filename='Process_Finished', extension='txt')

Commands().create_variable_file()
time.sleep(1)
Commands().input_file(filename='Variable_Input', extension='inp')
# Commands().input_file(filename='Material_Properties_NonSuperconducting', extension='inp', file_directory='input_files')
Commands().input_file(filename='Material_Properties_Superconducting', extension='inp', file_directory='input_files')
Commands().input_file(filename='Geometry', extension='inp', file_directory='input_files')

coil_length = Geometry().length_coil()
min_coil_length = coil_length[0, 1]
max_coil_length = coil_length[len(coil_length)-1, 1]

time = Variables().time_vector()                    # user's time stepping vector
q_pos_vector = Variables().quench_pos_vector()      # temporary quench position vector before T verification is created
quench_fronts = []
quench_plots = []
quench_temperature_plots = []

# initial iteration
i=0
print("iteration number: {} \n ____".format(i))
t = time[i]
quench_fronts.append(QuenchFront(x_down=q_pos_vector[i][0], x_up=q_pos_vector[i][1], label=i))
quench_fronts[0].calculate_q_front_pos_up(Variables().time_step, max_coil_length)
quench_fronts[0].calculate_q_front_pos_down(Variables().time_step, min_coil_length)
quench_plots.append(Plots().save_quench_plot(fig=Plots().plot_quench(coil_length=coil_length,
                                             quench_fronts=quench_fronts), iteration=i))
# position transformation into
quench_fronts[0].front_down_to_node()
quench_fronts[0].front_up_to_node()
# initial analysis definition
Commands().enter_preprocessor()
Commands().select_nodes(node_down=quench_fronts[0].x_down_node, node_up=quench_fronts[0].x_up_node)
Commands().select_elem_from_nodes()
Commands().modify_material_type(element_number=1)
Commands().modify_material_constant(constant_number=1)
Commands().modify_material_number(material_number=1)
Commands().enter_solver()
Commands().set_analysis_setting()
Commands().set_initial_temperature(temperature=Variables().T_initial)
Commands().set_current(node_number=1, value=Variables().current)
Commands().set_ground(node_number=Variables().npoints, value=0)
Commands().set_time_step(time_step=t)
Commands().input_file(filename='Solve_Get_Temp', extension='inp',
                      file_directory='input_files')
quench_temperature_plots.append(Plots().save_temperature_plot(
    fig=Plots().plot_temperature(coil_length=coil_length), iteration=i))
print(quench_fronts[0].to_string_node())

# start calculation after initial time step
for i in range(1, len(time)):

    print("iteration number: {} \n ____".format(i))
    t = time[i]
    # find new quench locations
    q_pos_new = q_pos_vector[i]
    if not any(quench_front.is_position_in_front(q_pos_new[0]) and quench_front.is_position_in_front(q_pos_new[1])
               for quench_front in quench_fronts):
        if q_pos_vector[i][0] != 0 and q_pos_vector[i][1] != 0:
            quench_fronts.append(QuenchFront(x_down=q_pos_vector[i][0], x_up=q_pos_vector[i][1], label=i))

    # calculate quench propagation
    for qf in quench_fronts:
        qf.calculate_q_front_pos_down(Variables().time_step, min_coil_length)
        qf.calculate_q_front_pos_up(Variables().time_step, max_coil_length)

    # what if quench fronts meet
    # list sorted with increasing x_down
    quench_fronts_sorted = sorted(quench_fronts, key=lambda QuenchFront: QuenchFront.x_down)
    for qf in quench_fronts_sorted:
        print("label: {}, x_down = {}, x_up = {}".format(qf.label, qf.x_down, qf.x_up))

    # merging procedure
    quench_fronts_merged = []
    index = 0
    while index < len(quench_fronts_sorted):
        qfOuter = quench_fronts_sorted[index]
        qf_merged = None
        for j in range(index + 1, len(quench_fronts_sorted)):
            qfInner = quench_fronts_sorted[j]
            isOverlap = qfOuter.check_overlap(qfInner)
            isSetIncluded = qfOuter.check_set_included(qfInner)
            to_be__merged = isOverlap or isSetIncluded
            print("Checking overlap of: {} and {}. The result is {}".format(qfOuter.label, qfInner.label, isOverlap))
            if to_be__merged:
                qf_merged = qfOuter.merge(qfInner)
                qfOuter = qf_merged
                index = j + 1

        if qf_merged is None:
            quench_fronts_merged.append(qfOuter)
            index = index + 1
        else:
            quench_fronts_merged.append(qf_merged)

    print("\nSituation after merging:")
    for qfm in quench_fronts_merged:
        print(qfm.to_string())
    print("______")

    # set new number of non-merged quench waves
    quench_fronts = quench_fronts_merged
    quench_plots.append(Plots().save_quench_plot(Plots().plot_quench(coil_length=coil_length,
                                                              quench_fronts=quench_fronts), iteration=i))
    Commands().enter_preprocessor()
    for qf in quench_fronts:
        # position transformation into nodes
        qf.front_down_to_node()
        qf.front_up_to_node()
        print(qf.to_string_node())
        # apdl commands for material reassignment
        Commands().select_nodes(node_down=qf.x_down_node, node_up=qf.x_up_node)
        Commands().select_elem_from_nodes()
        Commands().modify_material_type(element_number=1)
        Commands().modify_material_constant(constant_number=1)
        Commands().modify_material_number(material_number=1)

    Commands().enter_solver()
    # Commands().load_parameters()
    Commands().restart_analysis()
    Commands().set_time_step(time_step=t)
    Commands().input_file(filename='Solve_Get_Temp', extension='inp',
                          file_directory='input_files')
    # Commands().save_analysis()
    quench_temperature_plots.append(Plots().save_temperature_plot(
        fig=Plots().plot_temperature(coil_length=coil_length), iteration=i))

Plots().create_video(plot_array=quench_plots, filename='video_quench_propagation', extension='.gif')
Plots().create_video(plot_array=quench_temperature_plots, filename='video_temperature_propagation', extension='.gif')
Commands().save_analysis()
Commands().terminate_analysis()