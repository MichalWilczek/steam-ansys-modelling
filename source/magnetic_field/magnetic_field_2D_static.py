
from source.magnetic_field.magnetic_field_map import MagneticFieldMap
from source.magnetic_field.winding_remap import WindingRemap

class MagneticField2DStatic(MagneticFieldMap, WindingRemap):

    def __init__(self, factory):
        MagneticFieldMap.__init__(self, factory)
        WindingRemap.__init__(self, factory)
        self.magnetic_field_map_filename = self.input_data.magnetic_field_settings.input.magnetic_field_map_filename
        self.winding_side = self.input_data.geometry_settings.type_input.winding_side
        self.number_turns_in_layer = self.input_data.geometry_settings.type_input.number_turns_in_layer
        self.number_layers = self.input_data.geometry_settings.type_input.number_layers

        self.mag_map = self.load_magnetic_field_map(directory=self.input_directory,
                                                    filename=self.magnetic_field_map_filename)
        self.pos_x_winding = self.make_winding_pos_x(winding_side=self.winding_side,
                                                     number_turns_in_layer=self.number_turns_in_layer,
                                                     number_layers=self.number_layers)
        self.pos_y_winding = self.make_winding_pos_y(winding_side=self.winding_side,
                                                     number_turns_in_layer=self.number_turns_in_layer,
                                                     number_layers=self.number_layers)
        self.interpolation_f = self.create_interpolation_f_magnetic_field(self.mag_map)

        self.mag_dict = self.assign_magnetic_field_to_windings()
        self.plot_magnetic_map_figures()
        self.im_short_mag_dict = self.assign_magnetic_field_to_geometry()

    def assign_magnetic_field_to_geometry(self):
        real_wind_numbers = self.create_wind_real_number_list(winding_list=self.map_winding_list())
        short_mag_dict = self.shorten_mag_map_dict(self.mag_dict, real_wind_numbers)
        im_short_mag_dict = self.change_winding_number_to_fit_geometry(real_wind_numbers, short_mag_dict)
        print(self.magnetic_field_to_string(im_short_mag_dict))
        return im_short_mag_dict

    def plot_magnetic_map_figures(self):
        if self.input_data.magnetic_field_settings.input.magnetic_field_map_plot_output:
            self.make_magnetic_contour_plot(self.mag_map, directory=self.output_directory_magnetic_field)
            self.make_magnetic_colour_plot(self.mag_map, directory=self.output_directory_magnetic_field)
            self.plot_winding_vector_arrangement(x_pos_windings=self.winding_x_pos_list(
                self.winding_side, self.number_layers), y_pos_windings=
                self.winding_y_pos_list(self.winding_side, self.number_turns_in_layer),
                directory=self.output_directory_magnetic_field)

            self.make_winding_pos_map(pos_x_winding=self.pos_x_winding,
                                      pos_y_winding=self.pos_y_winding, directory=self.output_directory_magnetic_field)
            self.plot_interpolated_function(mag_map=self.mag_map, winding_side=self.winding_side,
                                            number_layers=self.number_layers,
                                            number_turns_in_layer=self.number_turns_in_layer,
                                            directory=self.output_directory_magnetic_field)

    def assign_magnetic_field_to_windings(self):
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

