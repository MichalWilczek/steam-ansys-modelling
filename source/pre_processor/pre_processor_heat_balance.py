
from source.pre_processor.pre_processor import PreProcessor

class PreProcessorHeatBalance(PreProcessor):

    def __init__(self, mat_props, ansys_commands, factory):
        PreProcessor.__init__(self, mat_props, ansys_commands, factory)

    def define_material_properties(self, magnetic_map):
        self.ansys_commands.input_winding_non_quenched_material_properties(
            magnetic_map, class_mat=self.mat_props, element_name="link33")
        if self.input_data.insulation_analysis:
            self.ansys_commands.input_insulation_material_properties(class_mat=self.mat_props)

