
from source.class_magnetic_field.magnetic_field_mapping import MagneticMap


class MagneticMapConst(MagneticMap):

    def __init__(self, windings_in_geometry, **kwargs):
        MagneticMap.__init__(self)
        MagneticMap.check_if_kwarg_exists(kwargs, "magnetic_field")
        magnetic_field = kwargs["magnetic_field"]
        self.mag_dict = self.assign_magnetic_field_to_windings(magnetic_field=magnetic_field)
        self.real_wind_numbers = self.create_wind_real_number_list(winding_list=windings_in_geometry)
        self.short_mag_dict = self.shorten_mag_map_dict(self.mag_dict, self.real_wind_numbers)
        self.im_short_mag_dict = self.change_winding_number_to_fit_geometry()

    def assign_magnetic_field_to_windings(self, **kwargs):
        """
        Creates artificial magnetic field map in case when magnetic field is assumed to be constant
        :param magnetic_field: float
        :return: dictionary; key: winding%number%, value: magnetic field as float
        """
        MagneticMap.check_if_kwarg_exists(kwargs, "magnetic_field")
        magnetic_field = kwargs["magnetic_field"]
        number_of_windings = MagneticMap.NUMBER_LAYERS * MagneticMap.NUMBER_TURNS_IN_LAYER
        magnetic_field_map = {}
        pos_x_win = self.pos_x_winding
        pos_y_wind = self.pos_y_winding
        for i in range(number_of_windings):
            wind_data = []
            wind_data.append(pos_x_win[i, :][0])
            wind_data.append(pos_y_wind[i, :][0])
            wind_data.append(magnetic_field)
            magnetic_field_map["winding"+str(i+1)] = wind_data
        return magnetic_field_map

    def change_winding_number_to_fit_geometry(self):
        """
        Assigns real winding number to imaginary winding numbers taken into consideration in Python
        :return: magnetic field map dictionary with changed keys
        """
        new_mag_dict = {}
        for i in range(len(self.real_wind_numbers)):
            new_mag_dict["winding"+str(i+1)] = self.short_mag_dict[self.real_wind_numbers[i]]
        return new_mag_dict
