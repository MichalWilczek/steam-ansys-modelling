
from source.magnetic_field.magnetic_field_constant import MagneticFieldConstant


class MagneticField1D(MagneticFieldConstant):

    def __init__(self, input_data):
        self.factory = input_data
        self.im_short_mag_dict = self.assign_magnetic_field_to_geometry()

    def assign_magnetic_field_to_geometry(self):
        mag_field_dict = {}
        mag_field_dict["winding1"] = self.factory.constant_magnetic_field_value
        print(self.magnetic_field_to_string(mag_field_dict))
        return mag_field_dict


