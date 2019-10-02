
from source.magnetic_field.magnetic_field_map import MagneticFieldMap
from source.magnetic_field.magnetic_field_constant import MagneticFieldConstant


class MagneticField2D(MagneticFieldMap, MagneticFieldConstant):

    def __init__(self, input_data):
        self.factory = input_data
        self.im_short_mag_dict = self.assign_magnetic_field_to_geometry()

    def assign_magnetic_field_to_geometry(self):
        mag_field_dict = {}
        for i in range(self.factory.number_of_windings):
            key_name = "winding" + str(i)
            mag_field_dict[key_name] = self.factory.constant_magnetic_field_value
        print(self.magnetic_field_to_string(mag_field_dict))
        return mag_field_dict
