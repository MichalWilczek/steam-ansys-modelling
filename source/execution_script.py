
from source.factory import Factory
from source.quench_detection import QuenchDetect
from source.pre_processor import PreProcessor

######################################################
# DEFINITION OF INITIAL INSTANCES TO RUN THE PROGRAMME
######################################################

inp_data = Factory.get_input_data_class()
ans = Factory.get_ansys_class()
mat = Factory.get_material_properties_class()
mag = Factory.get_magnetic_map_class()

#########################
# GENERAL PRE-PROCESSOR #
#########################

# definition of initial magnetic field, initial material properties and coil geometry
preproc_store = {}
preprocessor = PreProcessor(mat_props=mat, ansys_commands=ans, input_data=inp_data)
preprocessor.create_ansys_input_variable_file()
preprocessor.define_material_properties(magnetic_map=mag.im_short_mag_dict)
preprocessor.define_geometry()

# since geometry is created, Python starts mapping procedure
coil_geo = Factory.get_geometry_class()
preproc_store["npoints"] = coil_geo.load_parameter(filename="Nnode.txt")
preproc_store["coil_geometry"] = coil_geo.coil_geometry
preproc_store["min_coil_length"] = preproc_store["coil_geometry"][0, 1]
preproc_store["max_coil_length"] = preproc_store["coil_geometry"][len(preproc_store["coil_geometry"])-1, 1]

# input instance which will detect quench front from mapped Python geometry
q_det = QuenchDetect(preproc_store["npoints"], class_geometry=coil_geo)
# input circuit instance
circuit = Factory.get_circuit_class(ansys_commands=ans, class_geometry=coil_geo)
# save before entering the solver
ans.save_analysis()

############################
# INITIAL TIME STEP SOLVER #
############################

solver = Factory.get_solver_type(ansys_commands=ans, class_geometry=coil_geo, circuit=circuit)
solver.couple_nodes_in_analysis()
solver.enter_solver_settings()
solver.set_time_step()
solver.set_initial_temperature()
solver.set_time_step_temperature()
solver.set_bcs()
solver.solve()

####################################
# INITIAL TIME STEP POST-PROCESSOR #
####################################




############################
# FURTHER TIME STEP SOLVER #
############################





####################################
# FURTHER TIME STEP POST-PROCESSOR #
####################################



