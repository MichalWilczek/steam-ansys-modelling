
from source.pre_processor.pre_processor import PreProcessor
from source.factory.interpolation_functions import InterpolationFunctions

class PreProcessorQuenchVelocity(PreProcessor, InterpolationFunctions):

    def __init__(self, mat_props, ansys_commands, factory):
        PreProcessor.__init__(self, mat_props, ansys_commands, factory)

    def define_material_properties(self, magnetic_map):
        self.ansys_commands.input_winding_non_quenched_material_properties(
            magnetic_map, class_mat=self.mat_props, element_name="link68")
        if self.input_data.geometry_settings.type_input.type_insulation_settings.insulation_analysis:
            self.ansys_commands.input_insulation_material_properties(class_mat=self.mat_props)

    def adjust_material_properties_in_analysis(self, class_postprocessor):
        quench_fronts = class_postprocessor.quench_fronts
        im_short_mag_dict = class_postprocessor.magnetic_map.im_short_mag_dict
        self.create_new_resistive_materials_dependent_on_mag_field(quench_fronts, magnetic_map=im_short_mag_dict)
        self.set_new_material_properties_repository(quench_fronts)

    def create_new_resistive_materials_dependent_on_mag_field(self, quench_fronts, magnetic_map):
        quenched_winding_list = []
        for qf in quench_fronts:
            quenched_winding_list.append(self.geometry.retrieve_quenched_winding_numbers_from_quench_fronts(
                coil_data=self.geometry.coil_data, x_down_node=qf.x_down_node, x_up_node=qf.x_up_node))
        quenched_winding_list = self.geometry.remove_repetitive_values_from_list(self.geometry.flatten_list(quenched_winding_list))
        for winding in quenched_winding_list:

            self.ansys_commands.input_winding_quench_material_properties(magnetic_map, class_mat=self.mat_props, winding_number=winding)

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
                self.ansys_commands.modify_material_type(
                    element_number=winding_number + self.input_data.geometry_settings.type_input.number_of_windings)
                self.ansys_commands.modify_material_constant(
                    constant_number=winding_number + self.input_data.geometry_settings.type_input.number_of_windings)
                self.ansys_commands.modify_material_number(
                    material_number=winding_number + self.input_data.geometry_settings.type_input.number_of_windings)

    def start_discharge_after_qds_switch(self, class_circuit, class_postprocessor):
        if class_circuit.check_quench_with_qds(class_postprocessor):
            self.ansys_commands.enter_preprocessor()
            self.ansys_commands.allsel()
            self.ansys_commands.mapdl.executeCommand("rmodif,{},1,{}".format("et_switch_resistor", "1e-12"))
            self.ansys_commands.mapdl.executeCommand("rmodif,{},1,{},{},{},{}".format("et_curr_source", 0, 0, 1e12, 0))

    def adjust_nonlinear_inductance(self, class_circuit):
        inductance = InterpolationFunctions.get_value_from_linear_1d_interpolation(
            f_interpolation=class_circuit.diff_inductance_interpolation, x=class_circuit.current)[0]
        self.ansys_commands.enter_preprocessor()
        self.ansys_commands.allsel()
        self.ansys_commands.mapdl.executeCommand("rmodif,{},1,{}".format("et_inductor", inductance))

