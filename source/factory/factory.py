
import os
from source.factory.general_functions import GeneralFunctions
from source.factory.analysis_launcher import AnalysisLauncher

import source

from source.geometry.geometry_1D1D1D import GeometryMulti1D
from source.geometry.geometry_2D import Geometry2D

from source.ansys.ansys_multiple_1D_skew_quad import AnsysMultiple1DSkewQuad
from source.ansys.ansys_multiple_1D_slab import AnsysMultiple1DSlab
from source.ansys.ansys_2D import Ansys2D

from source.post_processor.quench_velocity.quench_front import QuenchFront
from source.post_processor.quench_velocity.quench_front_constant import QuenchFrontConst
from source.post_processor.quench_velocity.quench_front_numerical import QuenchFrontNum

from source.magnetic_field.magnetic_field_constant import MagneticFieldConstant
from source.magnetic_field.magnetic_field_2D_static import MagneticField2DStatic
from source.magnetic_field.magnetic_field_2D_transient import MagneticField2DTransient

from source.solver.solver_quench_velocity import SolverQuenchVelocity
from source.solver.solver_heat_balance import SolverHeatBalance

from source.circuit.circuit_thermal_analysis_no_circuit import CircuitThermalAnalysisNoCircuit
from source.circuit.circuit_electric_analysis_no_circuit import CircuitElectricAnalysisNoCircuit
from source.circuit.circuit_electric_analysis_with_circuit import CircuitElectricAnalysisWithCircuit

from source.solver.initial_temperature.initial_temperature_function import InitialTemperatureFunction
from source.solver.initial_temperature.initial_temperature_gaussian import InitialTemperatureGaussian
from source.solver.initial_temperature.initial_temperature_uniform import InitialTemperatureUniform
from source.solver.initial_temperature.initial_temperature_power_input import InitialTemperaturePowerInput

from source.pre_processor.pre_processor_quench_velocity import PreProcessorQuenchVelocity
from source.pre_processor.pre_processor_heat_balance import PreProcessorHeatBalance

from source.post_processor.post_processor_heat_balance import PostProcessorHeatBalance
from source.post_processor.post_processor_quench_velocity import PostProcessorQuenchVelocity

from source.materials.material_properties import MaterialProperties
from source.materials.nb_ti_material_properties import NbTiMaterialProperties
from source.materials.cu_material_properties import CuMaterialProperties
from source.materials.g10_material_properties import G10MaterialProperties
from source.materials.insulation_linear_material_properties import InsulationLinearMaterialProperties
from source.materials.winding_linear_material_properties import WindingLinearMaterialProperties
from source.materials.nb_ti_jc_low_current import NbTiJcLowCurrent
from source.materials.nb_ti_jc_russenschuck import NbTiJcRussenschuck

class Factory(AnalysisLauncher, GeneralFunctions):

    def __init__(self, json_directory, json_filename):
        self.input_data = self.get_input_data_class(json_directory, json_filename)
        AnalysisLauncher.__init__(self, self.input_data, json_directory, json_filename)

    def get_input_data_class(self, json_directory, json_filename):
        """
        Converts .json file input into a class with subclasses
        """
        return AnalysisLauncher.convert_json_to_class_object(
            json_filename_directory=json_directory, json_filename=json_filename)

    @staticmethod
    def get_source_directory():
        """
        Returns the directory of the main repository with Python scripts
        :return: directory as string
        """
        return os.path.dirname(source.__file__)

    def get_ansys_scripts_directory(self):
        source_path = self.get_source_directory()
        if self.input_data.geometry_settings.dimensionality == "1D":
            return os.path.join(source_path, 'apdl_scripts', '1D')
        elif self.input_data.geometry_settings.dimensionality == "multiple_1D":
            return os.path.join(source_path, 'apdl_scripts', '1D_1D_1D')
        elif self.input_data.geometry_settings.dimensionality == "2D":
            return os.path.join(source_path, 'apdl_scripts', '2D')
        else:
            raise ValueError("Directory does not exist")

    def get_geometry_class(self, factory):
        """
        Returns the geometry Class instance
        :param factory: Class factory
        :return: Class
        """
        if self.input_data.geometry_settings.dimensionality == "1D" or \
                self.input_data.geometry_settings.dimensionality == "multiple_1D":
            return GeometryMulti1D(factory)
        elif self.input_data.geometry_settings.dimensionality == "2D":
            return Geometry2D(factory)
        else:
            raise ValueError("Class Geometry does not exist")

    def get_ansys_class(self, factory):
        """
        Returns the ANSYS Class instance
        :param factory: Class factory
        :return: Class
        """
        if self.input_data.geometry_settings.dimensionality == "multiple_1D" and \
                self.input_data.geometry_settings.type == "skew_quadrupole":
            return AnsysMultiple1DSkewQuad(factory, ansys_input_directory=self.get_ansys_scripts_directory())
        elif self.input_data.geometry_settings.dimensionality == "multiple_1D" and \
                self.input_data.geometry_settings.type == "slab":
            return AnsysMultiple1DSlab(factory, ansys_input_directory=self.get_ansys_scripts_directory())
        elif self.input_data.geometry_settings.dimensionality == "2D":
            return Ansys2D(factory, ansys_input_directory=self.get_ansys_scripts_directory())
        else:
            raise ValueError("The specified geometry type and dimensionality do not exist at the same time")

    def get_quench_velocity_class(self):
        """
        Chooses between QuenchFront classes calculating quench velocity in different manners
        :return: Class QuenchFront
        """
        quench_model_exists = hasattr(self.input_data.analysis_type.input, "v_quench_model")
        if quench_model_exists:
            if self.input_data.analysis_type.input.v_quench_model == "constant":
                return QuenchFrontConst
            elif self.input_data.analysis_type.input.v_quench_model == "numerical":
                return QuenchFrontNum
            else:
                raise ValueError("Class QuenchFront does not exist")
        else:
            return QuenchFront

    def get_magnetic_map_class(self, factory):
        """
        Chooses between Classes with constant and non-constant magnetic field map
        :return: Class MagneticField
        """
        if self.input_data.magnetic_field_settings.type == "constant":
            return MagneticFieldConstant(factory)
        elif self.input_data.magnetic_field_settings.type == "2D_static":
            return MagneticField2DStatic(factory)
        elif self.input_data.magnetic_field_settings.type == "2D_transient":
            return MagneticField2DTransient(factory)
        else:
            raise ValueError("Class MagneticField does not exist")

    def get_solver_type(self, factory, ansys_commands, class_geometry, circuit,
                        ic_temperature_class, mat_props, mag_map):
        if self.input_data.analysis_type.type == "quench_velocity":
            return SolverQuenchVelocity(ansys_commands=ansys_commands, class_geometry=class_geometry,
                                        circuit=circuit, factory=factory,
                                        ic_temperature_class=ic_temperature_class, mag_map=mag_map, mat_props=mat_props)
        elif self.input_data.analysis_type.type == "heat_balance":
            return SolverHeatBalance(ansys_commands=ansys_commands, class_geometry=class_geometry,
                                     factory=factory, circuit=circuit,
                                     ic_temperature_class=ic_temperature_class, mag_map=mag_map, mat_props=mat_props)
        else:
            raise ValueError("Class Solver does not exist")

    def get_circuit_class(self, factory, ansys_commands, class_geometry):
        if not self.input_data.circuit_settings.electric_ansys_elements:
            return CircuitThermalAnalysisNoCircuit(ansys_commands, class_geometry, factory)
        else:
            if not self.input_data.circuit_settings.build_electric_circuit:
                return CircuitElectricAnalysisNoCircuit(ansys_commands, class_geometry, factory)
            else:
                return CircuitElectricAnalysisWithCircuit(ansys_commands, class_geometry, factory)

    def get_initial_temperature_class(self, factory, ansys_commands, class_geometry, mat_props):
        if self.input_data.temperature_settings.type == "gaussian":
            return InitialTemperatureGaussian(ansys_commands, class_geometry, factory=factory, mat_props=mat_props)
        elif self.input_data.temperature_settings.type == "uniform":
            return InitialTemperatureUniform(ansys_commands, class_geometry, factory=factory, mat_props=mat_props)
        elif self.input_data.temperature_settings.type == "power_input":
            return InitialTemperaturePowerInput(ansys_commands, class_geometry, factory=factory, mat_props=mat_props)
        elif self.input_data.temperature_settings.type == "temperature_function":
            return InitialTemperatureFunction(ansys_commands, class_geometry, factory=factory, mat_props=mat_props)
        else:
            raise ValueError("The initial temperature distribution - is not well-defined. "
                             "\n Please check the user input file carefully.")

    def get_preprocessor_class(self, factory, mat_props, ansys_commands):
        if self.input_data.analysis_type.type == "quench_velocity":
            return PreProcessorQuenchVelocity(mat_props, ansys_commands, factory)
        elif self.input_data.analysis_type.type == "heat_balance":
            return PreProcessorHeatBalance(mat_props, ansys_commands, factory)
        else:
            raise ValueError("Please, type 'quench_velocity' or 'heat_balance' in analysis type.")

    def get_postprocessor_class(self, factory, class_geometry, ansys_commands, v_quench, solver):
        if self.input_data.analysis_type.type == "quench_velocity":
            return PostProcessorQuenchVelocity(class_geometry, ansys_commands, v_quench, solver, factory)
        elif self.input_data.analysis_type.type == "heat_balance":
            return PostProcessorHeatBalance(class_geometry, ansys_commands, v_quench, solver, factory)
        else:
            raise ValueError("Class PostProcessor was not properly defined - change the name of 'analysis type'")

    def get_superconductor_class(self, temperature_profile, output_directory_materials=None):
        """
        Returns a Class with superconductor material properties
        :param temperature_profile: 1D numpy array with temperatures at which the
        material properties should be evaluated
        :param output_directory_materials: output directory where material properties files should be saved as string,
        default as None
        :return: Class instance
        """
        if self.input_data.material_settings.type == "nonlinear":
            if self.input_data.material_settings.input.superconductor_name == "Nb-Ti":
                return NbTiMaterialProperties(
                    temperature_profile,
                    txt_output=self.input_data.material_settings.input.txt_data_output,
                    png_output=self.input_data.material_settings.input.png_data_output,
                    output_directory=output_directory_materials,
                    magnetic_field_list=self.input_data.material_settings.input.magnetic_field_value_list)
            else:
                raise ValueError("Material does not exist in the library.")
        elif self.input_data.material_settings.type == "linear":
            return WindingLinearMaterialProperties(
                temperature_profile,
                txt_output=self.input_data.material_settings.input.txt_data_output,
                png_output=self.input_data.material_settings.input.png_data_output,
                output_directory=output_directory_materials
            )
        else:
            raise ValueError("Type of the material does not exist.")

    def get_normal_conductor_class(self, temperature_profile, output_directory_materials=None):
        """
        Returns a Class with normal-conductor material properties
        :param temperature_profile: temperature_profile: 1D numpy array with temperatures at which the
        material properties should be evaluated
        :param output_directory_materials: output directory where material properties files should be saved as string,
        default as None
        :return: Class instance
        """
        if self.input_data.material_settings.type == "nonlinear":
            magnetic_field_value_list = self.input_data.material_settings.input.magnetic_field_value_list
            if self.input_data.material_settings.input.normal_conductor_name == "Cu":
                return CuMaterialProperties(
                    temperature_profile,
                    rrr=self.input_data.material_settings.input.rrr,
                    txt_output=self.input_data.material_settings.input.txt_data_output,
                    png_output=self.input_data.material_settings.input.png_data_output,
                    output_directory=output_directory_materials,
                    magnetic_field_list=magnetic_field_value_list)
            else:
                raise ValueError("Material does not exist in the library.")
        elif self.input_data.material_settings.type == "linear":
            return WindingLinearMaterialProperties(
                temperature_profile,
                txt_output=self.input_data.material_settings.input.txt_data_output,
                png_output=self.input_data.material_settings.input.png_data_output,
                output_directory=output_directory_materials)
        else:
            raise ValueError("Type of the material does not exist.")

    def get_insulation_class(self, temperature_profile, output_directory_materials):
        """
        Returns a Class with insulation material properties
        :param temperature_profile: temperature_profile: 1D numpy array with temperatures at which the
        material properties should be evaluated
        :param output_directory_materials: output directory where material properties files should be saved as string,
        default as None
        :return: Class instance
        """
        if self.input_data.material_settings.type == "nonlinear":
            if self.input_data.material_settings.input.insulation_name == "G10":
                return G10MaterialProperties(
                    temperature_profile,
                    txt_output=self.input_data.material_settings.input.txt_data_output,
                    png_output=self.input_data.material_settings.input.png_data_output,
                    output_directory=output_directory_materials)
            else:
                raise ValueError("Material does not exist in the library.")
        elif self.input_data.material_settings.type == "linear":
            return InsulationLinearMaterialProperties(
                temperature_profile,
                txt_output=self.input_data.material_settings.input.txt_data_output,
                png_output=self.input_data.material_settings.input.png_data_output,
                output_directory=output_directory_materials)
        else:
            raise ValueError("Type of the material does not exist.")

    def get_critical_current_density_class(self):
        if self.input_data.material_settings.input.current_density_formula == "low_current_jc":
            return NbTiJcLowCurrent()
        elif self.input_data.material_settings.input.current_density_formula == "russenschuck_jc":
            return NbTiJcRussenschuck()

    @staticmethod
    def get_material_properties_class(factory):
        """
        Returns a Class which is the engine for material properties evaluation
        :param factory: Class with input data instances from factory
        :return: Class with material properties evaluation engine
        """
        output_directory_materials = GeneralFunctions.create_folder_in_directory(factory.output_directory,
                                                                                 "material_properties")
        return MaterialProperties(factory, output_directory_materials)
