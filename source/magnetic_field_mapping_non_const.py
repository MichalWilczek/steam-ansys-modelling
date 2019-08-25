
from source.magnetic_field_mapping import MagneticMap


class MagneticMapNonConst(MagneticMap):

    def __init__(self, windings_in_geometry):
        MagneticMap.__init__(self)
        self.mag_dict = self.assign_magnetic_field_to_windings()
        self.real_wind_numbers = self.create_wind_real_number_list(winding_list=windings_in_geometry)
        self.short_mag_dict = self.shorten_mag_map_dict(self.mag_dict, self.real_wind_numbers)
        self.im_short_mag_dict = self.change_winding_number_to_fit_geometry()

    def assign_magnetic_field_to_windings(self, **kwargs):
        """
        Calculates magnetic field strength in each winding based on interpolation function
        :return: dictionary; key: winding%number%, value: magnetic field strength as float
        """
        winding_main_dict = {}
        pos_x_win = self.pos_x_winding
        pos_y_wind = self.pos_y_winding
        for i in range(len(pos_x_win)):
            wind_data = []
            wind_data.append(pos_x_win[i, :][0])
            wind_data.append(pos_y_wind[i, :][0])
            wind_data.append(self.interpolation_f.__call__(pos_y_wind[i, :][0], pos_x_win[i, :][0])[0][0])
            winding_main_dict["winding"+str(i+1)] = wind_data
        return winding_main_dict

    def change_winding_number_to_fit_geometry(self):
        new_mag_dict = {}
        for i in range(len(self.real_wind_numbers)):
            new_mag_dict["winding"+str(i+1)] = self.short_mag_dict[self.real_wind_numbers[i]]
        return new_mag_dict