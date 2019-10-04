

class MagneticField(object):

    def assign_magnetic_field_to_geometry(self):
        pass

    @staticmethod
    def magnetic_field_to_string(mag_field_dict):
        return "------------------------------------------------------ \
               \n Magnetic Field map in the created windings is: \n {} \n ------------------------------------------------------".format(mag_field_dict)
