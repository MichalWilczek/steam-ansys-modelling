
class InitialTemperature(object):

    def __init__(self, ansys_commands, class_geometry, input_data, mat_props):
        self.ansys_commands = ansys_commands
        self.geometry = class_geometry
        self.material_properties = mat_props
        self.factory = input_data

    def set_initial_temperature(self):
        self.ansys_commands.set_initial_temperature(temperature=self.factory.temperature_init)

    def set_temperature_in_time_step(self, **kwargs):
        pass

    @staticmethod
    def initial_energy_deposition_to_string(energy_deposition):
        return "----------------------------------------------------------------------\
               \n \n The initially stored energy inside the coil equals: {} [J] \n \n \
                ----------------------------------------------------------------------".format(energy_deposition)

    def calculate_energy_initially_deposited_inside_the_coil(self, node_down, node_up, temperature_init_distr,
                                                             magnetic_field_value):
        energy_deposition = self.material_properties.calculate_energy(
            n_down=node_down, n_up=node_up, im_temp_profile=temperature_init_distr,
            im_coil_geom=self.geometry.coil_geometry, mag_field=magnetic_field_value,
            wire_diameter=self.factory.STRAND_DIAMETER, ref_temperature=self.factory.temperature_init)
        print(self.initial_energy_deposition_to_string(energy_deposition))
        return energy_deposition
