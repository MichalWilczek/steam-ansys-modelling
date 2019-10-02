
from source.ansys_commands.ansys_multiple_1D import AnsysMultiple1D
import time

class AnsysMultiple1DSlab(AnsysMultiple1D):

    def create_variable_file(self):
        """
        Creates an input file with parameters used by ANSYS
        """
        data = self.create_variable_table_method(self.analysis_directory)
        self.variable_file_invariable_input(data)
        data.write_text('number_of_windings =' + str(self.factory.number_of_windings))
        data.write_text('number_of_windings_in_reel =' + str(self.factory.number_of_windings_in_layer))
        data.write_text('elem_per_line =' + str(1))

        data.write_text('transverse_dimension_winding =' + str(self.calculate_insulation_length()))
        data.write_text('transverse_division_insulation =' + str(self.factory.transverse_division_insulation))

        # variables required when a slab (not magnet) geometry is considered
        data.write_text('division_per_winding = ' + str(self.factory.division_per_winding))
        data.write_text('length_per_winding = ' + str(self.factory.length_per_winding))

        self.wait_for_process_to_finish(data)
        time.sleep(2)

    def input_geometry(self, filename='1D_1D_1D_Geometry_slab'):
        """
        Inputs prepared file with geometry to ANSYS environment
        :param filename: geometry file name as string
        """
        print("________________ \nAnsys geometry is being uploaded...")
        self.input_file(filename=filename, extension='inp', add_directory='Input_Files')
