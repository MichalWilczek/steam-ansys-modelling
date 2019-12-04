
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
        self.im_short_mag_dict = self.assign_magnetic_field_to_geometry()
        MagneticFieldPlotting.plot_mag_field_in_windings(x_vector=self.mag_map_array[:, 0],
                                                         y_vector=self.mag_map_array[:, 1],
                                                         b_field_vector=self.mag_map_array[:, 2])

    def update_magnetic_field_during_analysis(self, current):
        winding_data = self.assign_magnetic_field_to_windings(current=current)
        self.mag_dict = winding_data[0]
        self.mag_map_array = winding_data[1]
        self.im_short_mag_dict = self.assign_magnetic_field_to_geometry()

    def assign_magnetic_field_to_geometry(self):
        real_wind_numbers = self.create_wind_real_number_list(winding_list=self.map_winding_list())
        short_mag_dict = self.shorten_mag_map_dict(self.mag_dict, real_wind_numbers)
        im_short_mag_dict = self.change_winding_number_to_fit_geometry(real_wind_numbers, short_mag_dict)
        print(self.magnetic_field_to_string(im_short_mag_dict))
        return im_short_mag_dict

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
    def change_winding_number_to_fit_geometry(real_wind_numbers, short_mag_dict):
        """
        Assigns real winding number to imaginary winding numbers taken into consideration in Python
        :return: magnetic field map dictionary with changed keys
        """
        new_mag_dict = {}
        for i in range(len(real_wind_numbers)):
            new_mag_dict["winding"+str(i+1)] = short_mag_dict[real_wind_numbers[i]]
        return new_mag_dict

