
from source.pre_processor.pre_processor import PreProcessor
from source.common_functions.interpolation_functions import InterpolationFunctions
from source.common_functions.general_functions import GeneralFunctions

class PreProcessorQuenchVelocity(PreProcessor):

    def __init__(self, mat_props, ansys_commands, factory):
        PreProcessor.__init__(self, mat_props, ansys_commands, factory)

    def define_material_properties(self, magnetic_map):
        self.ansys_commands.input_winding_non_quenched_material_properties(
            magnetic_map, class_mat=self.mat_props, element_name="link68")
        if self.input_data.geometry_settings.type_input.type_insulation_settings.insulation_analysis:
            self.ansys_commands.create_insulation_material_properties(class_mat=self.mat_props)
            self.ansys_commands.create_point_mass_material_properties(class_mat=self.mat_props)

    def adjust_material_properties_with_current_discharge(self, class_postprocessor, class_solver, class_circuit):
        if class_circuit.estimate_current_drop() is True and class_solver.end_of_analysis is False:

            # material assignment in a quenched zone
            for winding in class_postprocessor.quenched_windings_list:
                self.ansys_commands.input_winding_quench_material_properties(
                    magnetic_field_map=class_postprocessor.magnetic_map.im_short_mag_dict,
                    class_mat=self.mat_props,
                    winding_number=GeneralFunctions.extract_number_from_string(winding))
            self.set_new_material_properties_repository(class_postprocessor.quench_fronts)

            # material assignment in a non-quenched zone
            if class_circuit.qds_detection is True and class_postprocessor.is_all_coil_quenched is False:
                self.ansys_commands.input_winding_non_quenched_material_properties(
                    magnetic_field_map=class_postprocessor.magnetic_map.im_short_mag_dict,
                    class_mat=self.mat_props,
                    element_name="link68")

    def adjust_material_properties_in_quenched_zone(self, class_postprocessor, class_solver):
        if class_solver.end_of_analysis is False:
            if class_postprocessor.is_all_coil_quenched is False:
                if class_solver.iteration[0] == 0:
                    windings_set = class_postprocessor.quenched_windings_list
                elif class_postprocessor.new_winding_quenched is False:
                    windings_set = []
                elif class_postprocessor.new_winding_quenched is True:
                    windings_set = class_postprocessor.quenched_windings_list_new
                else:
                    raise ValueError("Class postprocessor needs to be redefined")

                for winding in windings_set:
                    self.ansys_commands.input_winding_quench_material_properties(
                        magnetic_field_map=class_postprocessor.magnetic_map.im_short_mag_dict,
                        class_mat=self.mat_props,
                        winding_number=GeneralFunctions.extract_number_from_string(winding))
            if class_postprocessor.is_all_coil_quenched is False :
                self.set_new_material_properties_repository(class_postprocessor.quench_fronts)

    def set_new_material_properties_repository(self, quench_fronts):
        for qf in quench_fronts:
            quench_dict = self.geometry.retrieve_winding_numbers_and_quenched_nodes(
                x_down_node=qf.x_down_node, x_up_node=qf.x_up_node)

            for key in quench_dict:
                winding_number = int(float(key[7:]))
                self.ansys_commands.select_nodes_in_analysis_mag(
                    winding_number=key, x_down_node=qf.x_down_node,
                    x_up_node=qf.x_up_node, class_geometry=self.geometry)
                self.ansys_commands.select_elem_from_nodes()

                # ADDED TO TAKE INTO ACCOUNT MASS ELEMENTS !!!
                if self.input_data.geometry_settings.type_input.u_ins < 1.0 or \
                        self.input_data.geometry_settings.type_input.u_resin > 0.0:
                    self.ansys_commands.unselect_element_type_from_set_of_elements(
                        element_number_to_unselect=2*self.input_data.
                            geometry_settings.type_input.n_windings + 3)

                self.ansys_commands.modify_material_type(
                    element_number=winding_number + self.input_data.geometry_settings.type_input.n_windings)
                self.ansys_commands.modify_material_constant(
                    constant_number=winding_number + self.input_data.geometry_settings.type_input.n_windings)
                self.ansys_commands.modify_material_number(
                    material_number=winding_number + self.input_data.geometry_settings.type_input.n_windings)

    def start_discharge_after_qds_switch(self, class_circuit, class_postprocessor):
        if class_circuit.check_quench_with_qds(class_postprocessor):
            self.ansys_commands.enter_preprocessor()
            self.ansys_commands.allsel()
            self.ansys_commands.mapdl.executeCommand("rmodif,{},1,{}".format("et_switch_resistor", "1e-12"))
            self.ansys_commands.mapdl.executeCommand("rmodif,{},1,{},{},{},{}".format("et_curr_source", 0, 0, 1e12, 0))

    @staticmethod
    def inductance_to_string(inductance):
        return "-------------\nINDUCTANCE AT CURRENT TIME STEP EQUALS: {} H\n-------------".format(inductance)

    def adjust_nonlinear_inductance(self, class_circuit):
        inductance = InterpolationFunctions.get_value_from_linear_1d_interpolation(
            f_interpolation=class_circuit.diff_inductance_interpolation, x=class_circuit.current)[0]
        self.ansys_commands.enter_preprocessor()
        self.ansys_commands.allsel()
        self.ansys_commands.mapdl.executeCommand("rmodif,{},1,{}".format("et_inductor", inductance))
        print(self.inductance_to_string(inductance))
