
class InitialTemperature(object):

    def __init__(self, ansys_commands, class_geometry, input_data):
        self.ansys_commands = ansys_commands
        self.geometry = class_geometry
        self.factory = input_data

    def set_initial_temperature(self):
        self.ansys_commands.set_initial_temperature(temperature=self.factory.temperature_init)

    def set_temperature_in_time_step(self, *args):
        pass
