
from source.factory.factory import Factory

# creation of analysis directories
json_file_directory = "C:\\1D_COMSOL_ANSYS_Benchmarking\\no_insulation"
json_filename = "input.json"
factory = Factory(json_file_directory, json_filename)

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
preprocessor = factory.get_preprocessor_class(mat_props=mat, ansys_commands=ans, factory=factory)
preprocessor.create_ansys_input_variable_file()
preprocessor.define_material_properties(magnetic_map=mag.im_short_mag_dict)
preprocessor.define_geometry()
# since geometry is created, Python starts mapping procedure
coil_geo = factory.get_geometry_class(factory)
preprocessor.include_class_geometry_in_class_instance(class_geometry=coil_geo)
# input circuit creator
circuit = factory.get_circuit_class(ansys_commands=ans, class_geometry=coil_geo, factory=factory)

############################
# INITIAL TIME STEP SOLVER #
############################

# creation of instances necessary to run the solver
ic_temperature = factory.get_initial_temperature_class(ansys_commands=ans, factory=factory,
                                                       class_geometry=coil_geo, mat_props=mat)
solver = factory.get_solver_type(mat_props=mat, mag_map=mag, ansys_commands=ans, class_geometry=coil_geo,
                                 circuit=circuit, ic_temperature_class=ic_temperature, factory=factory)
# adjustment of resistive material properties in initially quenched zone
solver.create_ic_temperature_profile()
postprocessor = factory.get_postprocessor_class(class_geometry=coil_geo, ansys_commands=ans,
                                                v_quench=v_quench, solver=solver, factory=factory)
postprocessor.check_quench_state()
postprocessor.plot_quench_state_in_analysis()
preprocessor.adjust_material_properties_in_analysis(postprocessor)
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
postprocessor.get_temperature_profile()      # write down temperature profile, plot temperature
postprocessor.estimate_coil_resistance()     # estimate resistance in ansys and python, plot resistance
postprocessor.estimate_quench_velocity()
postprocessor.check_quench_state()           # estimate_quench_velocity, write_down_quench_velocity, plot_quench_state
postprocessor.plot_quench_state_in_analysis()
ans.finish()

ans.enter_preprocessor()
preprocessor.update_magnetic_field_map(postprocessor)
preprocessor.adjust_material_properties_in_analysis(postprocessor)
solver.end_of_time_step()
ans.finish()

############################
# FURTHER TIME STEP SOLVER #
############################
for i in range(2, len(solver.time_step_vector)):
    ans.enter_solver()
    solver.restart_analysis()
    solver.set_time_step()
    solver.set_time_step_temperature()
    solver.solve()

####################################
# FURTHER TIME STEP POST-PROCESSOR #
####################################
    ans.enter_postprocessor()
    postprocessor.get_temperature_profile()    # write down temperature profile
    postprocessor.estimate_coil_resistance()   # estimate resistance in ansys and python, plot resistance
    postprocessor.estimate_quench_velocity()
    postprocessor.check_quench_state()         # estimate_quench_velocity, write_down_quench_velocity, plot_quench_state
    postprocessor.plot_quench_state_in_analysis()
    ans.finish()

    ans.enter_preprocessor()
    preprocessor.update_magnetic_field_map(postprocessor)
    preprocessor.adjust_material_properties_in_analysis(postprocessor)
    ans.finish()
    solver.end_of_time_step()

postprocessor.make_gif()
ans.save_analysis()
ans.terminate_analysis()
factory.copy_ansys_analysis_files_to_output_results_directory()
