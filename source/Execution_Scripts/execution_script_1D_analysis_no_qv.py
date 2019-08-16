
from source.plots import Plots
from source.quench_velocity import QuenchFront
from source.quench_merge import QuenchMerge
from source.quench_detection import QuenchDetect
from source.factory import AnalysisBuilder
from source.model_input import ModelInput
from source.case_factory import CaseFactory

CaseFactory = CaseFactory()
Plots = Plots()
ans = CaseFactory.get_ansys_class()
ans.delete_old_files()
ans.create_variable_file()
ans.input_file(filename='Variable_Input', extension='inp')

# input of magnetic map onto material properties
magnetic_map = ans.create_artificial_magnetic_field_map(CaseFactory.get_number_of_windings(), magnetic_field=3.0)
ans.input_winding_non_quenched_material_properties(magnetic_map, element_name="fluid116")
# ans.input_insulation_material_properties()
ans.input_heat_generation_curve(magnetic_field=magnetic_map["winding1"])

# input geometry
ans.input_geometry(filename='1D_1D_1D_Geometry_slab')

coil_geo = CaseFactory.get_geometry_class()
npoints = coil_geo.load_parameter(filename="Nnode.txt")
coil_geometry = coil_geo.coil_geometry
min_coil_length = coil_geometry[0, 1]
max_coil_length = coil_geometry[len(coil_geometry)-1, 1]

# user's time stepping vector
time = ModelInput.linear_time_stepping()

q_det = QuenchDetect(coil_geometry, npoints)
quench_fronts = []
quench_state_plots = []
quench_temperature_plots = []

# initial iteration
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

gaussian_initial_temperature = coil_geo.define_gaussian_temperature_distribution_array(coil_geometry, magnetic_field=magnetic_map["winding1"])
ans.set_gaussian_initial_temperature_distribution(gaussian_initial_temperature)

ans.allsel()
ans.set_heat_generation_in_nodes(node_number="all", value="%hgen_table%")

# input solver ANSYS APDL file
ans.input_solver()

# get temperature profile
temperature_profile = ans.get_temperature_profile(npoints=npoints, class_geometry=coil_geo)

# detect new quench position
quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile, magnetic_field=magnetic_map["winding1"])

# plot temperature and quench
temperature_plot = Plots.plot_and_save_temperature(coil_geometry, temperature_profile, iteration=i, time_step=t)
quench_temperature_plots.append(temperature_plot)


# ans.save_analysis()
# ans.terminate_analysis()


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

    # plot temperature and quench
    temperature_plot = Plots.plot_and_save_temperature(coil_geometry, temperature_profile, iteration=i, time_step=t)
    quench_temperature_plots.append(temperature_plot)

Plots.create_video(plot_array=quench_temperature_plots, filename='video_temperature_distribution.gif')
ans.save_analysis()
ans.terminate_analysis()
