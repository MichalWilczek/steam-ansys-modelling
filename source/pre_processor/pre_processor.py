
class PreProcessor(object):

    def __init__(self, mat_props, ansys_commands, factory):
        self.mat_props = mat_props
        self.ansys_commands = ansys_commands
        self.input_data = factory.input_data
        self.directory = factory.directory
        self.geometry = None

    def create_ansys_input_variable_file(self):
        self.ansys_commands.delete_old_ansys_analysis_files()
        self.ansys_commands.create_variable_file()
        self.ansys_commands.input_file(filename='Variable_Input', extension='inp', directory=self.directory)

    def define_material_properties(self, magnetic_map):
        pass

    def define_geometry(self):
        self.ansys_commands.input_geometry()

    def include_class_geometry_in_class_instance(self, class_geometry):
        self.geometry = class_geometry

    def adjust_material_properties_in_quenched_zone(self, class_postprocessor):
        pass

    def adjust_material_properties_in_non_quenched_zone(self, class_postprocessor):
        pass

    def start_discharge_after_qds_switch(self, class_circuit, class_postprocessor):
        pass

    def adjust_nonlinear_inductance(self, class_circuit):
        pass
