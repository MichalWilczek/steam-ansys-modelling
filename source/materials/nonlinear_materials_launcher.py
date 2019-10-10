
from source.materials.materials import Materials
from source.post_processor.plots import Plots
from source.factory.general_functions import GeneralFunctions


class MaterialsLauncher(Materials, GeneralFunctions):

    def __init__(self, factory):
        Materials.__init__(self, factory)
        self.input_data = factory.input_data


    def extract_data_for_multiple_1D_case(self):
        min_magnetic_field_value = self.input_data.magnetic_field_settings.input.min_magnetic_field_value
        max_magnetic_field_value = self.input_data.magnetic_field_settings.input.max_magnetic_field_value


    def extract_data_from_nbti(self):
        pass



    def extract_data_for_1D_case(self):
        magnetic_field_value = self.input_data.magnetic_field_settings.input.magnetic_field_value

        # Insulator properties
        g10_cp = self.calculate_g10_cp()
        g10_k = self.calculate_g10_therm_cond()
        g10_diffusivity = self.calculate_g10_thermal_diffusivity()
        GeneralFunctions.save_array(self.output_directory_materials, "cv_nist.txt", g10_cp)
        GeneralFunctions.save_array(self.output_directory_materials, "g10_k.txt", g10_k)
        GeneralFunctions.save_array(self.output_directory_materials, "g10_diffusivity.txt", g10_diffusivity)

        # Superconductor properties
        nb_ti_cp = self.calculate_nbti_cp(magnetic_field=magnetic_field_value)
        GeneralFunctions.save_array(self.output_directory_materials,
                                    "nb_ti_cp_mag_value_{}.txt".format(magnetic_field_value), nb_ti_cp)

        # Non-superconductor properties
        cu_cp = self.calculate_cu_cp()
        cu_k = self.calculate_cu_thermal_cond(magnetic_field=magnetic_field_value, rrr=self.rrr)
        cu_diffusivity = self.calculate_cu_thermal_diffusivity()
        cu_resistivity = self.calculate_cu_rho(magnetic_field=magnetic_field_value, rrr=self.rrr)
        GeneralFunctions.save_array(self.output_directory_materials, "cu_cp.txt", cu_cp)
        GeneralFunctions.save_array(self.output_directory_materials,
                                    "cu_k_mag_value_{}.txt".format(magnetic_field_value), cu_k)
        GeneralFunctions.save_array(self.output_directory_materials,
                                    "cu_resistivity_mag_value_{}.txt".format(magnetic_field_value), cu_resistivity)

        # Strand equivalent properties
        strand_eq_cp = self.calculate_winding_eq_cp(magnetic_field_value)
        strand_eq_diffusivity = self.calculate_strand_thermal_diffusivity(
            magnetic_field=magnetic_field_value, rrr=self.rrr)
        GeneralFunctions.save_array(self.output_directory_materials,
                                    "strand_eq_cp_mag_value_{}.txt".format(magnetic_field_value), strand_eq_cp)
        GeneralFunctions.save_array(self.output_directory_materials,
                                    "strand_eq_diffusivity_mag_value_{}.txt".format(magnetic_field_value), strand_eq_diffusivity)

        if self.input_data.analysis_settings.create_plots_in_output:

            # Insulator properties
            Plots.plot_material_properties(
                directory=self.output_directory_materials, filename="cv_nist.png",
                array=g10_cp, y_axis_name="volumetric heat capacity - G10, " + r'$\frac{J}{K m^3}$')
            Plots.plot_material_properties(
                directory=self.output_directory_materials, filename="g10_k.png",
                array=g10_k, y_axis_name="thermal conductivity - G10, " + r'$\frac{W}{K m}$')
            Plots.plot_material_properties(
                directory=self.output_directory_materials, filename="g10_diffusivity.png",
                array=g10_diffusivity, y_axis_name="thermal diffusivity - G10, " + r'$\frac{m^2}{s}$')

            # Superconductor properties
            Plots.plot_material_properties(
                directory=self.output_directory_materials, filename="nb_ti_cp.png",
                array=nb_ti_cp, y_axis_name="volumetric heat capacity - Nb-Ti, " + r'$\frac{J}{K m^3}$')

            # Non-superconductor properties
            Plots.plot_material_properties(
                directory=self.output_directory_materials, filename="cu_cp.png",
                array=cu_cp, y_axis_name="volumetric heat capacity - Cu, " + r'$\frac{J}{K m^3}$')
            Plots.plot_material_properties(
                directory=self.output_directory_materials, filename="cu_k.png",
                array=cu_k, y_axis_name="thermal conductivity - Cu, " + r'$\frac{W}{K m}$')
            Plots.plot_material_properties(
                directory=self.output_directory_materials, filename="cu_resistivity.png",
                array=cu_resistivity, y_axis_name="resistivity - Cu, " + r'$\frac{m^2}{s}$')
            Plots.plot_material_properties(
                directory=self.output_directory_materials, filename="cu_diffusivity.png",
                array=cu_diffusivity, y_axis_name="thermal diffusivity - Cu, " + r'$\frac{m^2}{s}$')

            # Strand equivalent properties
            Plots.plot_material_properties(
                directory=self.output_directory_materials, filename="strand_equivalent_cp.png",
                array=strand_eq_cp, y_axis_name="volumetric heat capacity - Strand, " + r'$\frac{J}{K m^3}$')
            Plots.plot_material_properties(
                directory=self.output_directory_materials, filename="strand_equivalent_diffusivity.png",
                array=strand_eq_diffusivity, y_axis_name="thermal diffusivity - Strand, " + r'$\frac{m^2}{s}$')
