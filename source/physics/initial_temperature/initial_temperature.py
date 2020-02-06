
from source.post_processor.plots import Plots
from source.common_functions.general_functions import GeneralFunctions

class InitialTemperature(object):

    def __init__(self, ansys_commands, class_geometry, mat_props, factory):
        self.plots = Plots(factory)
        self.ansys_commands = ansys_commands
        self.geometry = class_geometry
        self.material_properties = mat_props
        self.input_data = factory.input_data
        self.output_directory = factory.output_directory

    def set_initial_temperature(self):
        self.ansys_commands.set_initial_temperature(
            temperature=self.input_data.temperature_settings.input.temperature_init)

    def set_temperature_in_time_step(self, **kwargs):
        pass

    @staticmethod
    def initial_energy_deposition_to_string(energy_deposition):
        return "----------------------------------------------------------------------\
                \n The initially stored energy inside the coil equals: {} [J] \n" \
               "----------------------------------------------------------------------".format(energy_deposition)

    def calculate_energy_initially_deposited_inside_the_coil(self, temperature_init_distr,
                                                             magnetic_field_value):
        energy_deposition = self.material_properties.calculate_energy(
            im_temp_profile=temperature_init_distr,
            im_coil_geom=self.geometry.coil_geometry, mag_field=magnetic_field_value,
            wire_diameter=self.input_data.geometry_settings.type_input.strand_diameter,
            ref_temperature=self.input_data.temperature_settings.input.temperature_init)
        GeneralFunctions.write_line_to_file(self.plots.output_directory_temperature, "initial_energy_deposition_in_strand.txt",
                                            "Initial deposited energy equals: {} [J]".format(energy_deposition))
        print(self.initial_energy_deposition_to_string(energy_deposition))
        return energy_deposition
