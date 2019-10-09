
from source.magnetic_field.magnetic_field_map import MagneticFieldMap

class MagneticFieldConstant(MagneticFieldMap):

    def __init__(self, factory):
        MagneticFieldMap.__init__(self, factory)
        self.im_short_mag_dict = self.assign_magnetic_field_to_geometry()

    def assign_magnetic_field_to_geometry(self):
        mag_field_dict = {}
        for i in range(self.input_data.geometry_settings.number_of_windings):
            key_name = "winding" + str(i+1)
            mag_field_dict[key_name] = self.input_data.magnetic_field_settings.constant_magnetic_field_value
        print(self.magnetic_field_to_string(mag_field_dict))
        return mag_field_dict
