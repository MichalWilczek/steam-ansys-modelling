
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
ans.input_material_properties()
ans.input_geometry()

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
quench_fronts.append(QuenchFront(x_down=CaseFactory.get_quench_init_x_down(), x_up=CaseFactory.get_quench_init_x_up(), label=quench_label))
quench_label += 1
quench_state_plot = Plots.plot_and_save_quench(coil_geometry, quench_fronts, iteration=i, time_step=t)
quench_state_plots.append(quench_state_plot)

# position transformation into nodes
quench_fronts[0].convert_quench_front_to_nodes(coil_length=coil_geometry)

# initial analysis definition
ans.select_nodes_in_analysis(x_down_node=quench_fronts[0].x_down_node, x_up_node=quench_fronts[0].x_up_node, class_geometry=coil_geo)
ans.select_elem_from_nodes()
ans.modify_material_type(element_number=1)
ans.modify_material_constant(constant_number=1)
ans.modify_material_number(material_number=1)

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
# set initial quench temperature
ans.select_nodes_in_analysis(x_down_node=quench_fronts[0].x_down_node, x_up_node=quench_fronts[0].x_up_node, class_geometry=coil_geo)
ans.set_quench_temperature(q_temperature=20.0)

# set constant inflow current
ans.select_nodes_for_current(class_geometry=coil_geo)
ans.set_current(node_number="all", value=AnalysisBuilder().get_current())

# set ground
ans.set_ground_in_analysis(class_geometry=coil_geo)

# ans.save_analysis()
# ans.terminate_analysis()

# input solver ANSYS APDL file
ans.input_solver()

# get temperature profile
temperature_profile = ans.get_temperature_profile(npoints=npoints, class_geometry=coil_geo)

# calculate quench propagation
for qf in quench_fronts:
    qf.calculate_quench_front_position(t_step=t, min_length=min_coil_length, max_length=max_coil_length)

# detect new quench position
quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile)
for qf in quench_front_new:
    quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label))
    quench_label += 1

# plot temperature and quench
temperature_plot = Plots.plot_and_save_temperature(coil_geometry, temperature_profile, iteration=i, time_step=t)
quench_temperature_plots.append(temperature_plot)

# start calculation after initial time step
for i in range(1, len(time)):
    ans.save_analysis()
    t = time[i]

    print("iteration number: {} \n time step: {} \n ______________".format(i, t))
    # what if quench fronts meet
    quench_fronts = QuenchMerge.quench_merge(quench_fronts)
    quench_state_plot = Plots.plot_and_save_quench(coil_geometry, quench_fronts, iteration=i, time_step=t)
    quench_state_plots.append(quench_state_plot)

    for qf in quench_fronts:
        # position transformation into nodes
        qf.convert_quench_front_to_nodes(coil_geometry)

        # initial analysis definition
        ans.enter_preprocessor()
        ans.select_nodes_in_analysis(x_down_node=qf.x_down_node, x_up_node=qf.x_up_node, class_geometry=coil_geo)
        ans.select_elem_from_nodes()
        ans.modify_material_type(element_number=1)
        ans.modify_material_constant(constant_number=1)
        ans.modify_material_number(material_number=1)

    ans.enter_solver()
    ans.restart_analysis()
    ans.set_time_step(time_step=t, iteration=i)

    # input solver ANSYS APDL file
    ans.input_solver()

    # get temperature profile
    temperature_profile = ans.get_temperature_profile(npoints=npoints, class_geometry=coil_geo)

    # detect new quench position
    quench_front_new = q_det.detect_quench(quench_fronts, temperature_profile)
    for qf in quench_front_new:
        quench_fronts.append(QuenchFront(x_down=qf[0], x_up=qf[1], label=quench_label))
        quench_label += 1

    # calculate quench propagation
    for qf in quench_fronts:
        qf.calculate_quench_front_position(t_step=time[i]-time[i-1], min_length=min_coil_length, max_length=max_coil_length)

    # plot temperature and quench
    temperature_plot = Plots.plot_and_save_temperature(coil_geometry, temperature_profile, iteration=i, time_step=t)
    quench_temperature_plots.append(temperature_plot)

Plots.create_video(plot_array=quench_state_plots, filename='video_quench_state.gif')
Plots.create_video(plot_array=quench_temperature_plots, filename='video_temperature_distribution.gif')
ans.save_analysis()
ans.terminate_analysis()
