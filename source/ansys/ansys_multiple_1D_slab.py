
from source.ansys.ansys_multiple_1D import AnsysMultiple1D
import time
import math

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

    def input_insulation_material_properties(self, class_mat):
        """
        Inputs material properties for the insulation, in this case G10
        """
        self.enter_preprocessor()
        element_number = 2*self.factory.number_of_windings + 1
        self.define_element_type(element_number=element_number, element_name="link33")
        insulation_area = self.calculate_effective_insulation_area()
        self.define_element_constant(element_number=element_number, element_constant=insulation_area)
        self.define_element_density(element_number=element_number, value=class_mat.g10_dens)
        g10_therm_cond = class_mat.calculate_g10_therm_cond()
        g10_cp = class_mat.calculate_g10_cp()

        for j in range(len(g10_therm_cond[:, 0])):
            self.define_temperature_for_material_property(table_placement=j+1, temperature=g10_therm_cond[j, 0])
            self.define_element_conductivity(element_number=element_number, value=g10_therm_cond[j, 1])
            self.define_element_heat_capacity(element_number=element_number, value=g10_cp[j, 1])

    def calculate_effective_insulation_area(self):
        # if self.factory.number_of_windings != 1:
        #     eff_side = (self.factory.winding_side + math.pi * self.factory.strand_diameter/4.0)/2.0
        #     winding_total_length = 2.0*self.factory.coil_short_side + 2.0*self.factory.coil_long_side
        #     total_insulation_area = eff_side * winding_total_length
        #     number_divisions_in_winding = (2.0 * self.factory.division_long_side + 2.0 * self.factory.division_short_side)
        #     elem_ins_area = total_insulation_area / (number_divisions_in_winding+1.0)
        #     elem_ins_area_meters = elem_ins_area * 10.0**(-6.0)
        #     return elem_ins_area_meters
        # else:
        #     return 1.0
        return 1.0
