
from source.magnetic_field.magnetic_field import MagneticField
from source.factory.general_functions import GeneralFunctions
from source.factory.interpolation_functions import InterpolationFunctions
from source.factory.unit_conversion import UnitConversion
import os
import numpy as np

class MagneticFieldMap(MagneticField, InterpolationFunctions, UnitConversion):

    def __init__(self, factory):
        MagneticField.__init__(self, factory)
        self.layers = self.input_data.geometry_settings.type_input.number_layers
        self.magnetic_field_map_directory = factory.input_data.magnetic_field_settings.\
            input.magnetic_field_map_repository
        self.mag_map_interpolation = self.get_magnetic_interpolation_function()

        self.winding_side = self.input_data.geometry_settings.type_input.winding_side * UnitConversion.milimeters_to_meters
        self.number_turns_in_layer = self.input_data.geometry_settings.type_input.number_turns_in_layer

        self.pos_x_winding = self.make_winding_pos_x(winding_side=self.winding_side,
                                                     number_turns_in_layer=self.number_turns_in_layer,
                                                     number_layers=self.layers)
        self.pos_y_winding = self.make_winding_pos_y(winding_side=self.winding_side,
                                                     number_turns_in_layer=self.number_turns_in_layer,
                                                     number_layers=self.layers)

    def calculate_interpolated_magnetic_field(self, x_pos, y_pos, current):
        return InterpolationFunctions.get_value_from_linear_3d_interpolation(f_interpolation=self.mag_map_interpolation,
                                                                             x=x_pos, y=y_pos, z=current)

    def get_magnetic_interpolation_function(self):
        mag_map = self.load_magnetic_maps_dependent_on_current()
        return InterpolationFunctions.interpolate_linear_3d_function(
            x=mag_map[0], y=mag_map[1], z=mag_map[2], data=mag_map[3])

    def load_x_y_nodal_magnet_position(self, decimal_tolerance=10):
        filename = "magnetic_field_current_1.txt"
        path = os.path.join(self.magnetic_field_map_directory, filename)
        array = np.loadtxt(path, skiprows=9).round(decimal_tolerance)
        array.sort(axis=0)
        x_pos = np.unique(array[:, 0])
        y_pos = np.unique(array[:, 1])
        return x_pos, y_pos

    def load_magnetic_maps_dependent_on_current(self, decimal_tolerance=10):
        filename_list = GeneralFunctions.make_list_of_filenames_in_directory(self.magnetic_field_map_directory)
        current_axis_number = GeneralFunctions.count_number_of_occurencies_of_substring_in_list(
            list_of_strings=filename_list, substring="magnetic_field_current_")
        magnet_nodal_pos = self.load_x_y_nodal_magnet_position()
        x_pos = magnet_nodal_pos[0]
        y_pos = magnet_nodal_pos[1]

        b_field_array = np.zeros((len(x_pos), len(y_pos), current_axis_number))
        current_list = []
        for filename in filename_list:
            if "magnetic_field_current_" in filename:
                path = os.path.join(self.magnetic_field_map_directory, filename)
                array = np.loadtxt(path, skiprows=9).round(decimal_tolerance)
                array_sorted = array[np.lexsort((array[:, 1], array[:, 0]))]
                b_field = array_sorted[:, 5]
                b_field_reshaped = b_field.reshape(len(x_pos), len(y_pos))
                current_value = float(filename.replace("magnetic_field_current_", " ").replace(".txt", " "))
                current_list.append(current_value)
                b_field_array[:, :, int(current_value)-1] = b_field_reshaped
        current_list.sort()
        current_array = np.asarray(current_list)
        return x_pos, y_pos, current_array, b_field_array

    @staticmethod
    def winding_y_pos_list(winding_side, number_turns_in_layer):
        """
        Creates a horizontal array with y-position of a consecutive magnet layer
        :return: numpy array with one row
        """
        init_pos_x = winding_side / 2.0
        array = np.arange(init_pos_x, winding_side*number_turns_in_layer+init_pos_x, winding_side)
        return array

    @staticmethod
    def winding_x_pos_list(winding_side, number_layers):
        """
        Creates a horizontal array with x-position of a consecutive magnet layer
        :return: numpy array with one row
        """
        init_pos_x = winding_side / 2.0
        array = np.arange(init_pos_x, winding_side*number_layers+init_pos_x, winding_side)
        return array

    def make_winding_pos_x(self, winding_side, number_turns_in_layer, number_layers):
        """
        Creates vertical array where each row represents x_position of a winding in numerical order
        :return: numpy array, 1st column x_pos of winding as float
        """
        init_pos_x = float(self.input_data.geometry_settings.type_input.which_layer_first_in_analysis - 1)* winding_side + winding_side / 2.0
        pos_x = np.zeros((number_turns_in_layer * number_layers, 1))
        wind_counter_x = 1
        for i in range(number_layers):
            for j in range(number_turns_in_layer):
                pos_x[wind_counter_x - 1] = init_pos_x
                wind_counter_x += 1
            init_pos_x += winding_side
        return pos_x

    def make_winding_pos_y(self, winding_side, number_turns_in_layer, number_layers):
        """
        Creates vertical array where each row represents y_position of a winding in numerical order
        :return: numpy array, 1st column y_pos of winding as float
        """
        pos_y = np.zeros((number_turns_in_layer * number_layers, 1))
        wind_counter_y = 1
        for i in range(0, number_layers, 2):
            init_pos_y1 = float(self.input_data.geometry_settings.type_input.which_turn_first_in_analysis - 1) * \
                          winding_side + winding_side / 2.0
            for j in range(number_turns_in_layer):
                pos_y[wind_counter_y - 1] = init_pos_y1
                init_pos_y1 += winding_side
                wind_counter_y += 1
            wind_counter_y += number_turns_in_layer
        wind_counter_y = number_turns_in_layer
        for i in range(0, number_layers-1, 2):
            init_pos_y2 = winding_side / 2.0 + (float(number_turns_in_layer) - 1) * winding_side + \
                          float(self.input_data.geometry_settings.type_input.which_turn_first_in_analysis - 1)* \
                          winding_side
            for j in range(number_turns_in_layer):
                pos_y[wind_counter_y] = init_pos_y2
                if j != number_turns_in_layer - 1:
                    init_pos_y2 -= winding_side
                wind_counter_y += 1
            wind_counter_y += number_turns_in_layer
        return pos_y

