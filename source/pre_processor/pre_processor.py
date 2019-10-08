
class PreProcessor(object):

    def __init__(self, mat_props, ansys_commands, input_data):
        self.mat_props = mat_props
        self.ansys_commands = ansys_commands
        self.factory = input_data
        self.geometry = None

    def create_ansys_input_variable_file(self):
        self.ansys_commands.delete_old_files()
        self.ansys_commands.create_variable_file()
        self.ansys_commands.input_file(filename='Variable_Input', extension='inp')

    def define_material_properties(self, magnetic_map):
        pass

    def define_geometry(self):
        self.ansys_commands.input_geometry()

    def include_class_geometry_in_class_instance(self, class_geometry):
        self.geometry = class_geometry

    def adjust_material_properties_in_analysis(self, class_postprocessor):
        pass

    def update_magnetic_field_map(self, class_postprocessor):
        pass
