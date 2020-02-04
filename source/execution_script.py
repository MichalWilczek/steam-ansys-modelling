
from source.analysis_engine.analysis_factory import AnalysisFactory

# creation of analysis directories
input_file_directory = "G:\\Workspaces\\a\\ANSYS_Modelling\\1_quench_velocity_modelling" \
                       "\\documentation\\Test Simulation Workflow\\2_analysis_v_quench_map\input"
json_filename = "input.json"
factory = AnalysisFactory(input_file_directory, json_filename)

######################################################
# DEFINITION OF INITIAL INSTANCES TO RUN THE PROGRAMME
######################################################
ans = factory.get_ansys_class(factory)
mat = factory.get_material_properties_class(factory)
mag = factory.get_magnetic_map_class(factory)
v_quench = factory.get_quench_velocity_class()

#########################
# GENERAL PRE-PROCESSOR #
#########################
# definition of initial magnetic field, initial material properties and coil geometry
preprocessor = factory.get_preprocessor_class(
    mat_props=mat, ansys_commands=ans, factory=factory)
preprocessor.create_ansys_input_variable_file()
preprocessor.define_material_properties(
    magnetic_map=mag.im_short_mag_dict)
preprocessor.define_geometry()
# since geometry is created, Python starts mapping procedure
coil_geo = factory.get_geometry_class(factory)
preprocessor.include_class_geometry_in_class_instance(
    class_geometry=coil_geo)
# input circuit creator
circuit = factory.get_circuit_class(
    ansys_commands=ans, class_geometry=coil_geo, factory=factory)

############################
# INITIAL TIME STEP SOLVER #
############################
# creation of instances necessary to run the solver
ic_temperature = factory.get_initial_temperature_class(
    ansys_commands=ans, factory=factory,
    class_geometry=coil_geo, mat_props=mat)
solver = factory.get_solver_type(
    mat_props=mat, mag_map=mag, ansys_commands=ans, class_geometry=coil_geo,
    circuit=circuit, ic_temperature_class=ic_temperature, factory=factory)
# adjustment of resistive material properties in initially quenched zone
solver.create_ic_temperature_profile()
postprocessor = factory.get_postprocessor_class(
    class_geometry=coil_geo, ansys_commands=ans,
    v_quench=v_quench, solver=solver, factory=factory)
postprocessor.check_quench_state()
postprocessor.plot_quench_state_in_analysis()
preprocessor.adjust_material_properties_in_quenched_zone(
    postprocessor, solver)
solver.end_of_time_step()
ans.enter_solver()
solver.set_circuit_bcs()
solver.set_initial_temperature()
solver.set_time_step_temperature()
solver.set_solver_boundary_conditions()
solver.enter_solver_settings()
solver.set_time_step()
solver.solve()

####################################
# INITIAL TIME STEP POST-PROCESSOR #
####################################
ans.enter_postprocessor()
postprocessor.get_temperature_profile()
postprocessor.get_current()
postprocessor.check_quench_state_heat_balance()
postprocessor.estimate_resistive_voltage()
postprocessor.estimate_quench_velocity()
postprocessor.check_quench_state_quench_velocity()
postprocessor.plot_quench_state_in_analysis()
ans.finish()

solver.check_if_analysis_is_finished()
ans.enter_preprocessor()
postprocessor.update_magnetic_field()
preprocessor.adjust_material_properties_in_quenched_zone(
    postprocessor, solver)
preprocessor.adjust_material_properties_with_current_discharge(
    postprocessor, solver, circuit)

# QDS verifying the quench state
preprocessor.start_discharge_after_qds_switch(circuit, postprocessor)
preprocessor.adjust_nonlinear_inductance(circuit)

solver.end_of_time_step()

############################
# FURTHER TIME STEP SOLVER #
############################
while solver.end_of_analysis is False:
    solver.set_next_time_step(postprocessor)
    ans.enter_solver()
    solver.restart_analysis()
    solver.set_time_step()
    solver.set_time_step_temperature()
    solver.solve()

####################################
# FURTHER TIME STEP POST-PROCESSOR #
####################################
    ans.enter_postprocessor()
    postprocessor.get_temperature_profile()
    postprocessor.get_current()
    postprocessor.check_quench_state_heat_balance()
    postprocessor.estimate_resistive_voltage()
    postprocessor.estimate_quench_velocity()
    postprocessor.check_quench_state_quench_velocity()
    postprocessor.plot_quench_state_in_analysis()

    solver.check_if_analysis_is_finished()
    ans.enter_preprocessor()
    postprocessor.update_magnetic_field()
    preprocessor.adjust_material_properties_in_quenched_zone(
        postprocessor, solver)
    preprocessor.adjust_material_properties_with_current_discharge(
        postprocessor, solver, circuit)

    # QDS verifying the quench state
    preprocessor.start_discharge_after_qds_switch(
        circuit, postprocessor)
    preprocessor.adjust_nonlinear_inductance(circuit)
    solver.end_of_time_step()

postprocessor.make_gif()
ans.save_analysis()
ans.terminate_analysis()
factory.copy_ansys_analysis_files_to_output_results_directory()
