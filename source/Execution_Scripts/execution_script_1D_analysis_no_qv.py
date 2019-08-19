
from source.plots import Plots
from source.quench_velocity import QuenchFront
from source.quench_merge import QuenchMerge
from source.quench_detection import QuenchDetect
from source.factory import AnalysisBuilder
from source.model_input import ModelInput
from source.case_factory import CaseFactory
import numpy as np

gaussian_init_temp = False
CaseFactory = CaseFactory()
Plots = Plots()
ans = CaseFactory.get_ansys_class()
mat = CaseFactory.get_material_properties_class()
ans.delete_old_files()
ans.create_variable_file()
ans.input_file(filename='Variable_Input', extension='inp')

# input of magnetic map onto material properties
magnetic_map = ans.create_artificial_magnetic_field_map(CaseFactory.get_number_of_windings(), magnetic_field=3.0)
ans.input_winding_non_quenched_material_properties(magnetic_map, element_name="fluid116")
# ans.input_insulation_material_properties()

# ans.input_heat_generation_curve(magnetic_field=magnetic_map["winding1"])
ans.input_heat_generation_table(magnetic_field=magnetic_map["winding1"])
ans.input_heat_flow_table()

# input geometry
ans.input_geometry(filename='1D_1D_1D_Geometry_slab')

coil_geo = CaseFactory.get_geometry_class()
npoints = coil_geo.load_parameter(filename="Nnode.txt")
coil_geometry = coil_geo.coil_geometry
min_coil_length = coil_geometry[0, 1]
max_coil_length = coil_geometry[len(coil_geometry)-1, 1]

# user's time stepping vector
time = ModelInput.power_input_time_stepping()
q_v_time_array = np.zeros((len(time)-1, 2))

q_det = QuenchDetect(coil_geometry, npoints)
quench_fronts = []
quench_state_plots = []
quench_temperature_plots = []

# initial iteration
quench_label = 1
i = 0
t = time[i]
print("iteration number: {} \n time step: {} \n ______________".format(i, t))

ans.enter_solver()
ans.set_analysis_setting()
ans.set_time_step(time_step=t, iteration=0)

ans.set_initial_temperature(temperature=AnalysisBuilder().get_initial_temperature())
if gaussian_init_temp:
    gaussian_initial_temperature = coil_geo.define_gaussian_temperature_distribution_array(coil_geometry, magnetic_field=magnetic_map["winding1"])
    ans.set_gaussian_initial_temperature_distribution(gaussian_initial_temperature)
else:
    ans.select_nodes_in_analysis(coil_geo, x_down_node=501, x_up_node=501)
    ans.set_heat_flow_into_nodes(value="%heat_flow%")  # power applied to one node/element

ans.allsel()
ans.set_heat_generation_in_nodes(node_number="all", value="%heatgen%")

# input solver ANSYS APDL file
ans.input_solver()

# get temperature profile
temperature_profile = ans.get_temperature_profile(npoints=npoints, class_geometry=coil_geo)

# detect new quench position
quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile, magnetic_field=magnetic_map["winding1"])
if len(quench_front_new) > 0:
    pos_x_up = quench_front_new[0][1]
    pos_x_down = quench_front_new[0][1]

for qf in quench_front_new:
    quench_fronts = [QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label)]

# here add the function with resistivity
quenched_winding_list = []
for qf in quench_fronts:
    # position transformation into nodes
    qf.convert_quench_front_to_nodes(coil_geometry)
    quenched_winding_list.append(coil_geo.retrieve_quenched_winding_numbers_from_quench_fronts(coil_data=coil_geo.coil_data, x_down_node=qf.x_down_node, x_up_node=qf.x_up_node))

coil_resistance = 0.0
for qf in quench_fronts:
    qf_resistance = 0.0
    quench_dict = coil_geo.retrieve_winding_numbers_and_quenched_nodes(x_down_node=qf.x_down_node, x_up_node=qf.x_up_node)
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
quench_temperature_plots.append(temperature_plot)

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
    quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile, magnetic_field=magnetic_map["winding1"])
    if len(quench_front_new) > 0:
        q_length_up = abs(pos_x_up - q_v_time_array[i-1, 0])
        q_length_down = abs(pos_x_down - CaseFactory.get_quench_init_pos())
        q_vel = ((q_length_up + q_length_down) / 2.0) / t
        q_v_time_array[i-1, 0] = t
        q_v_time_array[i-1, 1] = q_vel
        pos_x_up = quench_front_new[0][1]
        pos_x_down = quench_front_new[0][1]

    # plot temperature and quench
    temperature_plot = Plots.plot_and_save_temperature(coil_geometry, temperature_profile, iteration=i, time_step=t)
    quench_temperature_plots.append(temperature_plot)

array_filename = ans.analysis_directory + "\\Q_V_array.txt"
np.savetxt(array_filename, q_v_time_array)
Plots.create_video(plot_array=quench_temperature_plots, filename='video_temperature_distribution.gif')
ans.save_analysis()
ans.terminate_analysis()
