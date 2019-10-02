
class PreProcessor(object):

    def __init__(self, mat_props, ansys_commands, input_data):
        self.mat_props = mat_props
        self.ansys_commands = ansys_commands
        self.factory = input_data

    def create_ansys_input_variable_file(self):
        self.ansys_commands.delete_old_files()
        self.ansys_commands.create_variable_file()
        self.ansys_commands.input_file(filename='Variable_Input', extension='inp')

    # @staticmethod
    # def define_magnetic_map(mag_map):
    #     magnetic_map = mag_map.im_short_mag_dict
    #     print(magnetic_map)
    #     return magnetic_map

    def define_material_properties(self, magnetic_map):
        self.ansys_commands.input_winding_non_quenched_material_properties(magnetic_map, class_mat=self.mat_props)
        if self.factory.insulation_analysis:
            self.ansys_commands.input_insulation_material_properties(class_mat=self.mat_props)

    def define_geometry(self):
        self.ansys_commands.input_geometry()







