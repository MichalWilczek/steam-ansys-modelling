
from source.plots import Plots
from source.quench_merge import QuenchMerge
from source.quench_detection import QuenchDetect
from source.factory import AnalysisBuilder
from source.model_input import ModelInput
from source.case_factory import CaseFactory
import numpy as np

# input Class instances
case = CaseFactory()
plots = Plots()
ans = case.get_ansys_class()
mag = case.get_magnetic_map_class(winding_start=1, winding_end=3, number_of_reels=2)
mat = case.get_material_properties_class()
QuenchFront = case.get_quench_velocity_class()

ans.delete_old_files()
ans.create_variable_file()
ans.input_file(filename='Variable_Input', extension='inp')

# input magnetic map, assign magnetic field strength if 2D map is not used
magnetic_map = mag.im_short_mag_dict
ans.input_winding_non_quenched_material_properties(magnetic_map, class_mat=mat, element_name="fluid116")
ans.input_insulation_material_properties(class_mat=mat)

# input geometry
ans.input_geometry(filename='1D_1D_1D_Geometry_slab')
coil_geo = case.get_geometry_class()
npoints = coil_geo.load_parameter(filename="Nnode.txt")
coil_geometry = coil_geo.coil_geometry
min_coil_length = coil_geometry[0, 1]
max_coil_length = coil_geometry[len(coil_geometry)-1, 1]

# input class for quench detect
q_det = QuenchDetect(npoints, class_geometry=coil_geo)

# ans.input_initial_power_curve
ans.input_heat_flow_table()

# input user's time stepping vector
time = ModelInput.power_input_time_stepping()

quench_fronts = []
quench_state_plots = []
quench_temperature_plots = []

#####################
# INITIAL TIME STEP #
#####################

quench_label = 1
i = 0
t = time[i]
print("iteration number: {} \n time step: {} \n ______________".format(i, t))

nodes_to_couple_windings_list = coil_geo.create_node_list_to_couple_windings()
for nodes_list in nodes_to_couple_windings_list:
    nodes_to_select_ansys = coil_geo.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_list)
    ans.select_nodes_list(nodes_list=nodes_to_select_ansys)
    ans.couple_nodes(dof="temp")

ans.enter_solver()
ans.set_analysis_setting()
ans.set_time_step(time_step=t, iteration=0)
ans.set_initial_temperature(temperature=AnalysisBuilder().get_initial_temperature())

# to be defined for power input
ans.select_nodes_in_analysis(coil_geo, x_down_node=751, x_up_node=751)
ans.set_heat_flow_into_nodes(value="%heat_flow%")  # power applied to one node/element

# input solver ANSYS APDL file
ans.input_solver()

# get temperature profile
temperature_profile = ans.get_temperature_profile(npoints=npoints, class_geometry=coil_geo)

# detect new quench position
# create new heat_gen curves for quenched windings !!!
quenched_winding_list = []
quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile, magnetic_field_map=magnetic_map)
for qf in quench_front_new:
    quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label))
    quench_label += 1
    quench_fronts[len(quench_fronts) - 1].convert_quench_front_to_nodes(coil_geometry)
    quench_fronts[len(quench_fronts) - 1].find_front_winding_numbers(coil_geo.coil_data)
    quenched_winding_list.append(coil_geo.retrieve_quenched_winding_numbers_from_quench_fronts(
        coil_data=coil_geo.coil_data, x_down_node=quench_fronts[len(quench_fronts) - 1].x_down_node,
        x_up_node=quench_fronts[len(quench_fronts) - 1].x_up_node))
quenched_winding_list = coil_geo.remove_repetitive_values_from_list(coil_geo.make_one_list_from_list_of_lists(quenched_winding_list))
for winding in quenched_winding_list:
    ans.input_heat_generation_table_winding(class_mat=mat, magnetic_field=magnetic_map["winding"+str(winding)], winding_number=str(winding))

# calculate resistance in python as R = f(T, B)
coil_resistance = 0.0
for qf in quench_fronts:
    qf_resistance = 0.0
    quench_dict = coil_geo.retrieve_winding_numbers_and_quenched_nodes(x_down_node=qf.x_down_node,
                                                                       x_up_node=qf.x_up_node)
    for key in quench_dict:
        winding_number = int(float(key[7:]))
        mag_field = magnetic_map["winding"+str(winding_number)]
        n_down = quench_dict["winding"+str(winding_number)][0]
        n_up = quench_dict["winding" + str(winding_number)][1]
        qf_resistance = mat.calculate_qf_resistance(qf_down=n_down, qf_up=n_up, im_temp_profile=temperature_profile,
                                                    im_coil_geom=coil_geometry, mag_field=mag_field,
                                                    wire_diameter=ans.STRAND_DIAMETER)
    coil_resistance += qf_resistance

# plot python resistive voltage
res_voltage = case.get_current()*coil_resistance
plots.plot_resistive_voltage(res_voltage, time_step=t, iteration=i, additional_descr="python")
res_voltage_array = np.zeros((1, 2))
res_voltage_array[0, 0] = t
res_voltage_array[0, 1] = res_voltage
plots.write_line_in_file("Res_Voltage.txt", res_voltage_array)

# plot temperature and quench
temperature_plot = plots.plot_and_save_temperature(coil_geometry, temperature_profile, iteration=i, time_step=t)
plots.save_array("Temperature_Profile_"+str(i)+".txt", temperature_profile)
quench_temperature_plots.append(temperature_plot)
quench_state_plot = plots.plot_and_save_quench(coil_geometry, quench_fronts, iteration=i, time_step=t)
quench_state_plots.append(quench_state_plot)

###################
# NEXT TIME STEPS #
###################

for i in range(1, len(time)):
    ans.save_analysis()
    t = time[i]
    print("iteration number: {} \n time step: {} \n ______________".format(i, t))

    # what if quench fronts meet
    quench_fronts = QuenchMerge.quench_merge(quench_fronts)

    # calculate quench propagation
    for qf in quench_fronts:
        qf.return_quench_front_position(initial_time=time[i - 1], final_time=time[i], min_length=min_coil_length,
                                        max_length=max_coil_length, mag_field_map=magnetic_map)
        qf.convert_quench_front_to_nodes(coil_geometry)
        qf.find_front_winding_numbers(coil_geo.coil_data)

    # update new magnetic field map
    # magnetic_map = ans.create_artificial_magnetic_field_map(case.get_number_of_windings())
    # create new non-resistive materials for coil dependent on magnetic field strength
    # ans.input_winding_non_quenched_material_properties(magnetic_map, class_mat=mat)

    # set new heat_gen curves on quenched nodes
    for qf in quench_fronts:
        quench_dict = coil_geo.retrieve_winding_numbers_and_quenched_nodes(x_down_node=qf.x_down_node, x_up_node=qf.x_up_node)
        for key in quench_dict:
            ans.enter_solver()
            winding_number = int(float(key[7:]))
            ans.select_nodes_in_analysis_mag(winding_number=key, x_down_node=qf.x_down_node, x_up_node=qf.x_up_node, class_geometry=coil_geo)
            ans.input_heat_generation_on_windings(winding_number=key)

    ans.enter_solver()
    ans.restart_analysis()
    ans.set_time_step(time_step=t, iteration=i)

    # input solver ANSYS APDL file
    ans.input_solver()

    # get temperature profile
    temperature_profile = ans.get_temperature_profile(npoints=npoints, class_geometry=coil_geo)

    # detect new quench position
    quenched_winding_list_new = []
    quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile, magnetic_field_map=magnetic_map)
    for qf in quench_front_new:
        quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label))
        quench_label += 1
        quench_fronts[len(quench_fronts)-1].convert_quench_front_to_nodes(coil_geometry)
        quench_fronts[len(quench_fronts)-1].find_front_winding_numbers(coil_geo.coil_data)
        quenched_winding_list_new.append(coil_geo.retrieve_quenched_winding_numbers_from_quench_fronts(
            coil_data=coil_geo.coil_data, x_down_node=quench_fronts[len(quench_fronts) - 1].x_down_node,
            x_up_node=quench_fronts[len(quench_fronts) - 1].x_up_node))
    quenched_winding_list_new = coil_geo.remove_repetitive_values_from_list(coil_geo.make_one_list_from_list_of_lists(quenched_winding_list_new))

    quenched_winding_list_2 = []
    quenched_winding_list_2.append(quenched_winding_list)
    quenched_winding_list_2.append(quenched_winding_list_new)
    quenched_winding_list = coil_geo.remove_repetitive_values_from_list(coil_geo.make_one_list_from_list_of_lists(quenched_winding_list_2))

    for winding in quenched_winding_list_new :
        ans.input_heat_generation_table_winding(class_mat=mat, magnetic_field=magnetic_map[winding],
                                                winding_number=winding)

    # calculate resistance in python as R = f(T, B)
    coil_resistance = 0.0
    for qf in quench_fronts:
        qf_resistance = 0.0
        quench_dict = coil_geo.retrieve_winding_numbers_and_quenched_nodes(x_down_node=qf.x_down_node,
                                                                           x_up_node=qf.x_up_node)
        for key in quench_dict:
            winding_number = int(float(key[7:]))
            mag_field = magnetic_map["winding" + str(winding_number)]
            n_down = quench_dict["winding" + str(winding_number)][0]
            n_up = quench_dict["winding" + str(winding_number)][1]
            qf_resistance = mat.calculate_qf_resistance(qf_down=n_down, qf_up=n_up, im_temp_profile=temperature_profile,
                                                        im_coil_geom=coil_geometry, mag_field=mag_field,
                                                        wire_diameter=ans.STRAND_DIAMETER)
        coil_resistance += qf_resistance

    # plot python resistive voltage
    res_voltage = case.get_current() * coil_resistance
    plots.plot_resistive_voltage(res_voltage, time_step=t, iteration=i, additional_descr="python")
    res_voltage_array = np.zeros((1, 2))
    res_voltage_array[0, 0] = t
    res_voltage_array[0, 1] = res_voltage
    plots.write_line_in_file("Res_Voltage.txt", res_voltage_array)

    # plot temperature and quench
    temperature_plot = plots.plot_and_save_temperature(coil_geometry, temperature_profile, iteration=i, time_step=t)
    plots.save_array("Temperature_Profile_" + str(i) + ".txt", temperature_profile)
    quench_temperature_plots.append(temperature_plot)
    quench_state_plot = plots.plot_and_save_quench(coil_geometry, quench_fronts, iteration=i, time_step=t)
    quench_state_plots.append(quench_state_plot)

plots.create_video(plot_array=quench_state_plots, filename='video_quench_state.gif')
plots.create_video(plot_array=quench_temperature_plots, filename='video_temperature_distribution.gif')
ans.save_analysis()
ans.terminate_analysis()
