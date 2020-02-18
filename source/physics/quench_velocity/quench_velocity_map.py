
import os
import numpy as np
from source.common_functions.interpolation_functions import InterpolationFunctions
from source.common_functions.general_functions import GeneralFunctions


class QuenchVelocityMap(object):

    def __init__(self, factory):
        self.input_directory = factory.input_directory
        self.quench_velocity_map_filename = os.path.join(
            factory.input_directory, factory.input_data.analysis_type.input.v_quench_map_filename)

        current_grid = self.upload_current_grid()
        magnetic_field_grid = self.upload_magnetic_field_grid()
        quench_velocity_grid = self.upload_quench_velocity_grid(factory)
        self.quench_velocity_interpolation = InterpolationFunctions.interpolate_linear_2d_function(
            x=current_grid, y=magnetic_field_grid, z=quench_velocity_grid)

    def upload_current_grid(self):
        with open(self.quench_velocity_map_filename) as file:
            line1 = file.readline()
        headers = line1.split(sep=",")
        current_list = []
        for header in headers:
            if "current=" in header:
                current_list.append(float(header.replace("current=", " ")))
        return current_list

    def upload_magnetic_field_grid(self):
        quench_velocity_map_array = np.loadtxt(self.quench_velocity_map_filename, delimiter=",", skiprows=1)
        return quench_velocity_map_array[:, 0]

    def upload_quench_velocity_grid(self, factory):
        quench_velocity_map_array = np.loadtxt(self.quench_velocity_map_filename, delimiter=",", skiprows=1)
        GeneralFunctions.copy_file_to_directory(
            filename=factory.input_data.analysis_type.input.v_quench_map_filename,
            filename_directory=factory.input_directory,
            desired_filename_directory=factory.input_copy_directory
        )
        return quench_velocity_map_array[:, 1:]

    def get_quench_velocity(self, b_field, current):
        return InterpolationFunctions.get_value_from_linear_2d_interpolation(
            self.quench_velocity_interpolation, current, b_field)
