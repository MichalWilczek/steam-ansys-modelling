
from source.factory.general_functions import GeneralFunctions

class MagneticField(GeneralFunctions):

    def __init__(self, factory):
        self.input_directory = factory.input_directory
        self.input_data = factory.input_data
        self.output_directory = factory.output_directory
        self.output_directory_magnetic_field = GeneralFunctions.create_folder_in_directory(self.output_directory,
                                                                                           "magnetic_field")

    def assign_magnetic_field_to_geometry(self):
        pass

    @staticmethod
    def magnetic_field_to_string(mag_field_dict):
        return "------------------------------------------------------ \
               \n Magnetic Field map in the created windings is: \n {} \n" \
               "------------------------------------------------------".format(mag_field_dict)
