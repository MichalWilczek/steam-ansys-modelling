
from source.plots import Plots
from source.quench_merge import QuenchMerge
from source.quench_detection import QuenchDetect
from source.winding_remap import WindingRemap
from source.factory import AnalysisBuilder
from source.model_input import ModelInput
from source.case_factory import CaseFactory
from source.polynomial_fit import Polynomials
import numpy as np

# input Class instances
case = CaseFactory()
plots = Plots()
ans = case.get_ansys_class()
remap = WindingRemap(start_winding=233, end_winding=237, layers=9)
mag = case.get_magnetic_map_class(winding_list=remap.map_winding_list())
mat = case.get_material_properties_class()
QuenchFront = case.get_quench_velocity_class()

ans.delete_old_files()
ans.create_variable_file()
ans.input_file(filename='Variable_Input', extension='inp')

# input magnetic map, assign magnetic field strength if 2D map is not used
magnetic_map = mag.im_short_mag_dict
print(magnetic_map)
ans.input_winding_non_quenched_material_properties(magnetic_map, class_mat=mat)
ans.input_insulation_material_properties(class_mat=mat)

# input geometry
ans.input_geometry()        # magnet geometry, not a 3D slab
coil_geo = case.get_geometry_class()
npoints = coil_geo.load_parameter(filename="Nnode.txt")
coil_geometry = coil_geo.coil_geometry
min_coil_length = coil_geometry[0, 1]
max_coil_length = coil_geometry[len(coil_geometry)-1, 1]

# input class for quench detect
q_det = QuenchDetect(npoints, class_geometry=coil_geo)

# input user's time stepping vector
time = ModelInput.power_input_time_stepping()
temperature_bc_list = Polynomials.create_linear_interpolation_for_temp_vector(time)

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
    ans.couple_nodes(dof="volt")
    ans.couple_nodes(dof="temp")

ans.enter_solver()
ans.set_analysis_setting()
ans.set_time_step(time_step=t, iteration=0)
ans.set_initial_temperature(temperature=AnalysisBuilder().get_initial_temperature())

# to be defined for temperature at quenched node
ans.select_nodes_in_analysis(coil_geo, x_down_node=5809, x_up_node=5809)
ans.set_quench_temperature(q_temperature=temperature_bc_list[i])

# set constant inflow current
ans.select_nodes_for_current(class_geometry=coil_geo)
ans.set_current(node_number="all", value=AnalysisBuilder().get_current())

# set ground
ans.set_ground_in_analysis(class_geometry=coil_geo)

# input solver ANSYS APDL file
ans.input_solver()

# get temperature profile
temperature_profile = ans.get_temperature_profile(npoints=npoints, class_geometry=coil_geo)

# detect new quench position
quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile, magnetic_field_map=magnetic_map)
for qf in quench_front_new:
    quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label,
                                     coil_geometry=coil_geometry, coil_data=coil_geo.coil_data))
    quench_label += 1

# get ansys voltage
resistive_voltage = coil_geo.load_parameter(filename="Resistive_Voltage.txt")
plots.plot_resistive_voltage_ansys(voltage=resistive_voltage, time_step=t, iteration=i)

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
plots.plot_resistive_voltage_python(res_voltage, time_step=t, iteration=i)
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

    # update new magnetic field map
    # magnetic_map = ans.create_artificial_magnetic_field_map(case.get_number_of_windings())
    # create new non-resistive materials for coil dependent on magnetic field strength
    # ans.input_winding_non_quenched_material_properties(magnetic_map, class_mat=mat)

    # create new resistive materials for coil dependent on magnetic field strength
    quenched_winding_list = []
    for qf in quench_fronts:
        quenched_winding_list.append(coil_geo.retrieve_quenched_winding_numbers_from_quench_fronts(coil_data=coil_geo.coil_data, x_down_node=qf.x_down_node, x_up_node=qf.x_up_node))
    quenched_winding_list = coil_geo.remove_repetitive_values_from_list(coil_geo.make_one_list_from_list_of_lists(quenched_winding_list))
    for winding in quenched_winding_list:
        ans.input_winding_quench_material_properties(magnetic_map, class_mat=mat, winding_number=winding)

    # set new material properties repository
    for qf in quench_fronts:
        quench_dict = coil_geo.retrieve_winding_numbers_and_quenched_nodes(x_down_node=qf.x_down_node, x_up_node=qf.x_up_node)
        for key in quench_dict:
            winding_number = int(float(key[7:]))
            ans.select_nodes_in_analysis_mag(winding_number=key, x_down_node=qf.x_down_node, x_up_node=qf.x_up_node, class_geometry=coil_geo)
            ans.select_elem_from_nodes()
            ans.modify_material_type(element_number=winding_number + case.get_number_of_windings())
            ans.modify_material_constant(constant_number=winding_number + case.get_number_of_windings())
            ans.modify_material_number(material_number=winding_number + case.get_number_of_windings())

    ans.enter_solver()
    ans.restart_analysis()
    ans.set_time_step(time_step=t, iteration=i)

    # to be defined for temperature at quenched node
    ans.select_nodes_in_analysis(coil_geo, x_down_node=5809, x_up_node=5809)
    ans.set_quench_temperature(q_temperature=temperature_bc_list[i])

    # input solver ANSYS APDL file
    ans.input_solver()

    # get temperature profile
    temperature_profile = ans.get_temperature_profile(npoints=npoints, class_geometry=coil_geo)

    # detect new quench position
    quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile, magnetic_field_map=magnetic_map)
    for qf in quench_front_new:
        quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label,
                                         coil_geometry=coil_geometry, coil_data=coil_geo.coil_data))
        quench_label += 1

    # get ansys voltage
    resistive_voltage = coil_geo.load_parameter(filename="Resistive_Voltage.txt")
    plots.plot_resistive_voltage_ansys(voltage=resistive_voltage, time_step=t, iteration=i)

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
    plots.plot_resistive_voltage_python(res_voltage, time_step=t, iteration=i)
    res_voltage_array = np.zeros((1, 2))
    res_voltage_array[0, 0] = t
    res_voltage_array[0, 1] = res_voltage
    plots.write_line_in_file("Res_Voltage.txt", res_voltage_array, newfile=False)

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
