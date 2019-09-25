
from source.plots import Plots
from source.class_quench_velocity.quench_velocity import QuenchFront
from source.quench_detection import QuenchDetect
from source.winding_remap import WindingRemap
from source.factory import AnalysisBuilder
from source.model_input import ModelInput
from source.factory_case import CaseFactory
import numpy as np

mag_field_const = 2.0  # T
gaussian_init_temp = True
power_input = True

CaseFactory = CaseFactory()
Plots = Plots()
ans = CaseFactory.get_ansys_class()
mat = CaseFactory.get_material_properties_class()

remap = WindingRemap(start_winding=1, end_winding=1, layers=1)
mag = CaseFactory.get_magnetic_map_class(winding_list=remap.map_winding_list(), magnetic_field=mag_field_const)

ans.delete_old_files()
ans.create_variable_file()
ans.input_file(filename='Variable_Input', extension='inp')

# input of magnetic map onto material properties
magnetic_map = mag.im_short_mag_dict
ans.input_winding_non_quenched_material_properties(magnetic_map, class_mat=mat, element_name="link33")
ans.input_insulation_material_properties(class_mat=mat)
# ans.input_heat_generation_table(class_mat=mat, magnetic_field=magnetic_map["winding1"])

# input geometry
# ans.input_geometry(filename='1D_1D_1D_Geometry_slab')
ans.input_geometry()

ans.save_analysis()
ans.terminate_analysis()

coil_geo = CaseFactory.get_geometry_class()
npoints = coil_geo.load_parameter(filename="Nnode.txt")
coil_geometry = coil_geo.coil_geometry
min_coil_length = coil_geometry[0, 1]
max_coil_length = coil_geometry[len(coil_geometry)-1, 1]

# user's time stepping vector
if power_input:
    time = ModelInput.power_input_time_stepping()
else:
    time = ModelInput.linear_time_stepping()

q_det = QuenchDetect(npoints, class_geometry=coil_geo)
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

ans.enter_solver()
ans.set_analysis_setting()
ans.set_time_step(time_step=t, iteration=0)

ans.set_initial_temperature(temperature=AnalysisBuilder().get_initial_temperature())
mag_field = magnetic_map["winding1"]
if gaussian_init_temp:
    gaussian_initial_temperature = coil_geo.define_gaussian_temperature_distribution_array(coil_geometry, magnetic_field = magnetic_map["winding1"])
    # ans.set_gaussian_initial_temperature_distribution(gaussian_initial_temperature)
    # calculate energy deposited initially inside the coil
    energy_deposition = mat.calculate_energy(n_down=coil_geometry[0, 0], n_up=coil_geometry[len(coil_geometry) - 1, 0],
                                             im_temp_profile=gaussian_initial_temperature, im_coil_geom=coil_geometry,
                                             mag_field=mag_field, wire_diameter=ans.STRAND_DIAMETER,
                                             ref_temperature=AnalysisBuilder().get_initial_temperature())
else:
    node_down = 190
    node_up = 201
    q_temperature = 20.0
    ans.select_nodes_in_analysis(coil_geo, x_down_node=node_down, x_up_node=node_up)
    # calculate energy deposited initially inside the coil
    ic_temp_array = np.zeros((len(coil_geometry[:, 0]), 2))
    ic_temp_array[:, 0] = coil_geometry[:, 0]
    ic_temp_array[:, 1] = AnalysisBuilder().get_initial_temperature()
    ic_temp_array[(node_down-1):node_up, 1] = q_temperature
    temp_critic = mat.calculate_critical_temperature(magnetic_field=mag_field_const)
    ans.set_quench_temperature(q_temperature=q_temperature)
    energy_deposition = mat.calculate_energy(n_down=node_down, n_up=node_up,
                                             im_temp_profile=ic_temp_array, im_coil_geom=coil_geometry,
                                             mag_field=mag_field, wire_diameter=ans.STRAND_DIAMETER,
                                             ref_temperature=AnalysisBuilder().get_initial_temperature())
    # ans.set_heat_flow_into_nodes(value="%heat_flow%")  # power applied to one node/element

ans.allsel()
ans.set_heat_generation_in_nodes(node_number="all", value="%heatgen%")

# input solver ANSYS APDL file
ans.input_solver()

# get temperature profile
temperature_profile = ans.get_temperature_profile(npoints=npoints, class_geometry=coil_geo)

# detect new quench position and calculate quench velocity
q_v_time_array = np.zeros((1, 3))
quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile, magnetic_field_map=magnetic_map)
if len(quench_front_new) > 0:
    pos_x_down = quench_front_new[0][0]
    pos_x_up = quench_front_new[0][1]
    q_length_up = abs(pos_x_up - CaseFactory.get_quench_init_pos())
    q_length_down = abs(pos_x_down - CaseFactory.get_quench_init_pos())
    q_vel = ((q_length_up + q_length_down) / 2.0) / t
    q_v_time_array[0, 0] = t
    q_v_time_array[0, 1] = q_length_down + q_length_up
    q_v_time_array[0, 2] = q_vel
else:
    q_v_time_array[0, 0] = t
    q_v_time_array[0, 1] = 0.0
    q_v_time_array[0, 2] = 0.0

# write down quench velocity
if i == 1:
    Plots.write_line_in_file("Q_V_array.txt", q_v_time_array)
else:
    Plots.write_line_in_file("Q_V_array.txt", q_v_time_array, newfile=False)

for qf in quench_front_new:
    quench_fronts = [QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label,
                                 coil_geometry=coil_geometry, coil_data=coil_geo.coil_data)]

# calculate coil resistance
quenched_winding_list = []
for qf in quench_fronts:
    # position transformation into nodes
    qf.convert_quench_front_to_nodes(coil_geometry)
    quenched_winding_list.append(coil_geo.retrieve_quenched_winding_numbers_from_quench_fronts(
        coil_data=coil_geo.coil_data, x_down_node=qf.x_down_node, x_up_node=qf.x_up_node))

coil_resistance = 0.0
for qf in quench_fronts:
    qf_resistance = 0.0
    quench_dict = coil_geo.retrieve_winding_numbers_and_quenched_nodes(
        x_down_node=qf.x_down_node, x_up_node=qf.x_up_node)
    for key in quench_dict:
        winding_number = int(float(key[7:]))
        mag_field = magnetic_map["winding"+str(winding_number)]
        n_down = quench_dict["winding"+str(winding_number)][0]
        n_up = quench_dict["winding" + str(winding_number)][1]
        qf_resistance = mat.calculate_qf_resistance(qf_down=n_down, qf_up=n_up, im_temp_profile=temperature_profile,
                                                    im_coil_geom=coil_geometry, mag_field=mag_field,
                                                    wire_diameter=ans.STRAND_DIAMETER)
    coil_resistance += qf_resistance

# plot temperature and quench
temperature_plot = Plots.plot_and_save_temperature(coil_geometry, temperature_profile, iteration=i, time_step=t)
Plots.save_array("Temperature_Profile_"+str(i)+".txt", temperature_profile)
quench_temperature_plots.append(temperature_plot)

# plot resistive voltage
res_voltage = CaseFactory.get_current()*coil_resistance
Plots.plot_resistive_voltage_python(res_voltage, time_step=t, iteration=i)
res_voltage_array = np.zeros((1, 2))
res_voltage_array[0, 0] = t
res_voltage_array[0, 1] = res_voltage
Plots.write_line_in_file("Res_Voltage.txt", res_voltage_array)

# start calculation after initial time step
for i in range(1, len(time)):
    ans.save_analysis()
    t = time[i]

    print("iteration number: {} \n time step: {} \n ______________".format(i, t))
    # what if quench fronts meet
    ans.enter_solver()
    ans.restart_analysis()
    ans.set_time_step(time_step=t, iteration=i)

    # input solver ANSYS APDL file
    ans.input_solver()

    # get temperature profile
    temperature_profile = ans.get_temperature_profile(npoints=npoints, class_geometry=coil_geo)

    # detect new quench position
    q_v_time_array = np.zeros((1, 3))
    quench_fronts = []
    quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile, magnetic_field_map=magnetic_map)
    if len(quench_front_new) > 0:
        pos_x_down = quench_front_new[0][0]
        pos_x_up = quench_front_new[0][1]
        q_length_up = abs(pos_x_up - CaseFactory.get_quench_init_pos())
        q_length_down = abs(pos_x_down - CaseFactory.get_quench_init_pos())
        q_vel = ((q_length_up + q_length_down) / 2.0) / t
        q_v_time_array[0, 0] = t
        q_v_time_array[0, 1] = q_length_down + q_length_up
        q_v_time_array[0, 2] = q_vel

    if i == 1:
        Plots.write_line_in_file("Q_V_array.txt", q_v_time_array)
    else:
        Plots.write_line_in_file("Q_V_array.txt", q_v_time_array, newfile=False)

    for qf in quench_front_new:
        quench_fronts = [QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label,
                                     coil_geometry=coil_geometry, coil_data=coil_geo.coil_data)]

    # here add the function with resistivity
    quenched_winding_list = []
    for qf in quench_fronts:
        # position transformation into nodes
        qf.convert_quench_front_to_nodes(coil_geometry)
        quenched_winding_list.append(
            coil_geo.retrieve_quenched_winding_numbers_from_quench_fronts(
                coil_data=coil_geo.coil_data, x_down_node=qf.x_down_node, x_up_node=qf.x_up_node))
    coil_resistance = 0.0
    for qf in quench_fronts:
        qf_resistance = 0.0
        quench_dict = coil_geo.retrieve_winding_numbers_and_quenched_nodes(x_down_node=qf.x_down_node, x_up_node=qf.x_up_node)
        for key in quench_dict:
            winding_number = int(float(key[7:]))
            mag_field = magnetic_map["winding" + str(winding_number)]
            n_down = quench_dict["winding" + str(winding_number)][0]
            n_up = quench_dict["winding" + str(winding_number)][1]
            qf_resistance = mat.calculate_qf_resistance(qf_down=n_down, qf_up=n_up, im_temp_profile=temperature_profile,
                                                        im_coil_geom=coil_geometry, mag_field=mag_field,
                                                        wire_diameter=ans.STRAND_DIAMETER)
        coil_resistance += qf_resistance

    # plot temperature and quench
    temperature_plot = Plots.plot_and_save_temperature(coil_geometry, temperature_profile, iteration=i, time_step=t)
    Plots.save_array("Temperature_Profile_" + str(i) + ".txt", temperature_profile)
    quench_temperature_plots.append(temperature_plot)

    # plot resistive voltage
    res_voltage = CaseFactory.get_current() * coil_resistance
    Plots.plot_resistive_voltage_python(res_voltage, time_step=t, iteration=i)
    res_voltage_array = np.zeros((1, 2))
    res_voltage_array[0, 0] = t
    res_voltage_array[0, 1] = res_voltage
    Plots.write_line_in_file("Res_Voltage.txt", res_voltage_array, newfile=False)

Plots.create_video(plot_array=quench_temperature_plots, filename='video_temperature_distribution.gif')
ans.save_analysis()
ans.terminate_analysis()
