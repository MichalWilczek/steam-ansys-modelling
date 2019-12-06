
import numpy as np
from source.magnetic_field.magnetic_field_map import MagneticFieldMap
from source.magnetic_field.magnetic_field_plotting import MagneticFieldPlotting

class MagneticField2DStatic(MagneticFieldMap, MagneticFieldPlotting):

    def __init__(self, factory):
        MagneticFieldMap.__init__(self, factory)
        winding_data = self.assign_magnetic_field_to_windings(current=self.input_data.circuit_settings.
                                                              electric_ansys_element_input.current_init)
        self.mag_dict = winding_data[0]
        self.mag_map_array = winding_data[1]
        MagneticFieldPlotting.plot_mag_field_in_windings(x_vector=self.mag_map_array[:, 0],
                                                         y_vector=self.mag_map_array[:, 1],
                                                         b_field_vector=self.mag_map_array[:, 2])
        self.im_short_mag_dict = self.simplify_the_magnetic_field_dictionary(self.mag_dict)
        print("CURRENT MAGNETIC FIELD MAP: {}".format(self.im_short_mag_dict))

    def update_magnetic_field_during_analysis(self, current):
        winding_data = self.assign_magnetic_field_to_windings(current=current)
        self.mag_dict = winding_data[0]
        self.mag_map_array = winding_data[1]
        self.im_short_mag_dict = self.simplify_the_magnetic_field_dictionary(self.mag_dict)
        print("CURRENT MAGNETIC FIELD MAP: {}".format(self.im_short_mag_dict))

    def create_array_with_magnetic_field_in_windings(self, current):
        pos_x_wind = self.pos_x_winding
        pos_y_wind = self.pos_y_winding

        mag_map_array = np.zeros((len(pos_x_wind), 3))
        for i in range(len(pos_x_wind)):
            mag_map_array[i, 0] = pos_x_wind[i]
            mag_map_array[i, 1] = pos_y_wind[i]
            mag_map_array[i, 2] = self.calculate_interpolated_magnetic_field(pos_x_wind[i], pos_y_wind[i], current)

    def assign_magnetic_field_to_windings(self, current):
        """
        Calculates magnetic field strength in each winding based on interpolation function
        :return: dictionary; key: winding%number%, value: magnetic field strength as float
        """
        winding_main_dict = {}
        pos_x_win = self.pos_x_winding
        pos_y_win = self.pos_y_winding
        mag_map_array = np.zeros((len(pos_x_win), 3))

        for i in range(len(pos_x_win)):
            wind_data = []
            x_pos = pos_x_win[i, :][0]
            y_pos = pos_y_win[i, :][0]
            b_field_interpolated = self.calculate_interpolated_magnetic_field(x_pos, y_pos, current)
            wind_data.extend([x_pos, y_pos, b_field_interpolated])
            winding_main_dict["winding"+str(i+1)] = wind_data

            mag_map_array[i, 0] = pos_x_win[i]
            mag_map_array[i, 1] = pos_y_win[i]
            mag_map_array[i, 2] = b_field_interpolated

        return winding_main_dict, mag_map_array

    @staticmethod
    def simplify_the_magnetic_field_dictionary(dictionary):
        new_dict = {}
        for key in dictionary:
            new_dict[key] = dictionary[key][2]
        return new_dict
