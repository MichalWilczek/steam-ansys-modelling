
from source.factory import Factory

######################################################
# DEFINITION OF INITIAL INSTANCES TO RUN THE PROGRAMME
######################################################

inp_data = Factory.get_input_data_class()
ans = Factory.get_ansys_class()
mat = Factory.get_material_properties_class()
mag = Factory.get_magnetic_map_class()
v_quench = Factory.get_quench_velocity_class()

#########################
# GENERAL PRE-PROCESSOR #
#########################

# definition of initial magnetic field, initial material properties and coil geometry
preproc_store = {}
preprocessor = Factory.get_preprocessor_class(mat_props=mat, ansys_commands=ans, input_data=inp_data)
preprocessor.create_ansys_input_variable_file()
preprocessor.define_material_properties(magnetic_map=mag.im_short_mag_dict)
preprocessor.define_geometry()
# since geometry is created, Python starts mapping procedure
coil_geo = Factory.get_geometry_class()
# input circuit creator
circuit = Factory.get_circuit_class(ansys_commands=ans, class_geometry=coil_geo)
# save before entering the solver
ans.save_analysis()
ans.finish()

############################
# INITIAL TIME STEP SOLVER #
############################
ans.enter_solver()
# creation of instances necessary to run the solver
ic_temperature = Factory.get_initial_temperature_class(ansys_commands=ans, class_geometry=coil_geo, mat_props=mat)
solver = Factory.get_solver_type(mat_props=mat, mag_map=mag, ansys_commands=ans, class_geometry=coil_geo,
                                 circuit=circuit, ic_temperature_class=ic_temperature)
solver.set_circuit_bcs()
solver.set_initial_temperature()
solver.set_time_step_temperature()
solver.set_solver_bcs()
solver.enter_solver_settings()
solver.set_time_step()
solver.solve()

####################################
# INITIAL TIME STEP POST-PROCESSOR #
####################################
ans.enter_postprocessor()
postprocessor = Factory.get_postprocessor_class(class_geometry=coil_geo, ansys_commands=ans,
                                                v_quench=v_quench, solver=solver)
postprocessor.get_temperature_profile()      # write down temperature profile, plot temperature
postprocessor.check_quench_state()           # estimate_quench_velocity, write_down_quench_velocity, plot_quench_state
postprocessor.estimate_coil_resistance()     # estimate resistance in ansys and python, plot resistance
ans.finish()

ans.enter_preprocessor()
preprocessor.adjust_material_properties_in_analysis()
preprocessor.update_magnetic_field_map()
ans.finish()

solver.end_of_time_step()

############################
# FURTHER TIME STEP SOLVER #
############################
for i in range(1, len(solver.time_step_vector)):
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
    postprocessor.check_quench_state()         # estimate_quench_velocity, write_down_quench_velocity, plot_quench_state
    postprocessor.estimate_coil_resistance()   # estimate resistance in ansys and python, plot resistance
    ans.finish()

    ans.enter_preprocessor()
    preprocessor.adjust_material_properties_in_analysis()
    preprocessor.update_magnetic_field_map()
    ans.finish()

    solver.end_of_time_step()

postprocessor.make_gif()
ans.save_analysis()
ans.terminate_analysis()