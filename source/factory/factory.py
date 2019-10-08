
import os
from source.factory.analysis_launcher import AnalysisLauncher

import source

from source.geometry.geometry_1D1D1D import GeometryMulti1D
from source.geometry.geometry_2D import Geometry2D

from source.ansys.ansys_1D import Ansys1D
from source.ansys.ansys_multiple_1D_skew_quad import AnsysMultiple1DSkewQuad
from source.ansys.ansys_multiple_1D_slab import AnsysMultiple1DSlab
from source.ansys.ansys_2D import Ansys2D

from source.material_properties.material_properties_nonlinear import MaterialsNonLinear
from source.material_properties.material_properties_linear import MaterialsLinear

from source.post_processor.quench_velocity.quench_velocity import QuenchFront
from source.post_processor.quench_velocity.quench_velocity_constant import QuenchFrontConst
from source.post_processor.quench_velocity.quench_velocity_numerical import QuenchFrontNum

from source.magnetic_field.magnetic_field_1D import MagneticField1D
from source.magnetic_field.magnetic_field_2D import MagneticField2D
from source.magnetic_field.magnetic_field_2D_static import MagneticField2DStatic
from source.magnetic_field.magnetic_field_2D_transient import MagneticField2DTransient

from source.solver.solver_quench_velocity import SolverQuenchVelocity
from source.solver.solver_heat_balance import SolverHeatBalance

from source.circuit.circuit_therm_analysis_no_circuit import CircuitThermalAnalysisNoCircuit
from source.circuit.circuit_electr_analysis_no_circuit import CircuitElectricAnalysisNoCircuit
from source.circuit.circuit_electric_analysis_with_circuit_transient import CircuitElectricAnalysisWithCircuitTransient
from source.circuit.circuit_electric_analysis_with_circuit_static import CircuitElectricAnalysisWithCircuitStatic

from source.solver.initial_temperature.initial_temperature_function import InitialTemperatureFunction
from source.solver.initial_temperature.initial_temperature_gaussian import InitialTemperatureGaussian
from source.solver.initial_temperature.initial_temperature_uniform import InitialTemperatureUniform
from source.solver.initial_temperature.initial_temperature_power_input import InitialTemperaturePowerInput

from source.pre_processor.pre_processor_quench_velocity import PreProcessorQuenchVelocity
from source.pre_processor.pre_processor_heat_balance import PreProcessorHeatBalance

from source.post_processor.post_processor_heat_balance import PostProcessorHeatBalance
from source.post_processor.post_processor_quench_velocity import PostProcessorQuenchVelocity

class Factory(AnalysisLauncher):

    def __init__(self, directory):
        AnalysisLauncher.__init__(self, directory)
        self.input_data = self.get_input_data_class()

    def get_input_data_class(self):
        """
        Converts .json file input into a class with subclasses
        """
        return self.convert_json_to_class_object(class_name="InputUser", json_filename='input_ansys_modelling.json')

    @staticmethod
    def get_source_directory():
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

    def get_geometry_class(self):
        if self.input_data.geometry_settings.dimensionality == "1D" or self.input_data.geometry_settings.dimensionality == "multiple_1D":
            return GeometryMulti1D(input_data=self.input_data, analysis_directory=self.get_ansys_scripts_directory())
        elif self.input_data.geometry_settings.dimensionality == "2D":
            return Geometry2D(input_data=self.input_data, analysis_directory=self.get_ansys_scripts_directory())
        else:
            raise ValueError("Class Geometry does not exist")

    def get_ansys_class(self):
        if self.input_data.geometry_settings.dimensionality == "1D":
            return Ansys1D(input_data=self.input_data, analysis_directory=self.get_ansys_scripts_directory())
        elif self.input_data.geometry_settings.dimensionality == "multiple_1D" and self.input_data.geometry_settings.type == "skew_quadrupole":
            return AnsysMultiple1DSkewQuad(input_data=self.input_data, analysis_directory=self.get_ansys_scripts_directory())
        elif self.input_data.geometry_settings.dimensionality == "multiple_1D" and self.input_data.geometry_settings.type == "slab":
            return AnsysMultiple1DSlab(input_data=self.input_data, analysis_directory=self.get_ansys_scripts_directory())
        elif self.input_data.geometry_settings.dimensionality == "2D":
            return Ansys2D(input_data=self.input_data, analysis_directory=self.get_ansys_scripts_directory())
        else:
            raise ValueError("The specified geometry type and dimensionality do not exist at the same time")

    def get_material_properties_class(self):
        """
        Chooses between linear and nonlinear material properties set in json file
        :return: Class with material properties
        """
        if self.input_data.material_settings.type == "linear":
            return MaterialsLinear(input_data=self.input_data)
        elif self.input_data.material_settings.type == "nonlinear":
            return MaterialsNonLinear(input_data=self.input_data)
        else:
            raise ValueError("Class MaterialProperties does not exist")

    def get_quench_velocity_class(self):
        """
        Chooses between QuenchFront classes calculating qv in different manners
        :return: Class QuenchFront
        """
        if self.input_data.analysis_type.input.v_quench_model == "constant":
            return QuenchFrontConst
        elif self.input_data.analysis_type.input.v_quench_model == "numerical":
            return QuenchFrontNum
        elif self.input_data.analysis_type.input.v_quench_model is None:
            return QuenchFront
        else:
            raise ValueError("Class QuenchFront does not exist")

    def get_magnetic_map_class(self):
        """
        Chooses between Classes with constant and non-constant magnetic field map
        :return: Class MagneticField
        """
        if self.input_data.magnetic_field_settings.type == "1D_constant":
            return MagneticField1D(input_data=self.input_data)
        elif self.input_data.magnetic_field_settings.type == "2D_constant":
            return MagneticField2D(input_data=self.input_data)
        elif self.input_data.magnetic_field_settings.type == "2D_static":
            return MagneticField2DStatic(input_data=self.input_data)
        elif self.input_data.magnetic_field_settings.type == "2D_transient":
            return MagneticField2DTransient(input_data=self.input_data)
        else:
            raise ValueError("Class MagneticField does not exist")

    def get_solver_type(self, ansys_commands, class_geometry, circuit, ic_temperature_class, mat_props, mag_map):
        if self.input_data.analysis_type.type == "v_quench_model":
            return SolverQuenchVelocity(ansys_commands=ansys_commands, class_geometry=class_geometry,
                                        input_data=self.input_data, circuit=circuit,
                                        ic_temperature_class=ic_temperature_class, mag_map=mag_map, mat_props=mat_props)
        elif self.input_data.analysis_type.type == "heat_balance":
            return SolverHeatBalance(ansys_commands=ansys_commands, class_geometry=class_geometry,
                                     input_data=self.input_data, circuit=circuit,
                                     ic_temperature_class=ic_temperature_class, mag_map=mag_map, mat_props=mat_props)
        else:
            raise ValueError("Class Solver does not exist")

    def get_circuit_class(self, ansys_commands, class_geometry):
        if not Factory.electric_ansys_elements:
            return CircuitThermalAnalysisNoCircuit(ansys_commands, class_geometry, input_data=self.input_data)
        else:
            if not Factory.build_electric_circuit:
                return CircuitElectricAnalysisNoCircuit(ansys_commands, class_geometry, input_data=self.input_data)
            else:
                if not Factory.transient_electric_analysis:
                    return CircuitElectricAnalysisWithCircuitStatic(ansys_commands, class_geometry, input_data=self.input_data)
                else:
                    return CircuitElectricAnalysisWithCircuitTransient(ansys_commands, class_geometry, input_data=self.input_data)

    def get_initial_temperature_class(self, ansys_commands, class_geometry, mat_props):
        if self.input_data.temperature_init_distribution.type == "gaussian_distribution":
            return InitialTemperatureGaussian(ansys_commands, class_geometry, input_data=self.input_data, mat_props=mat_props)
        elif self.input_data.temperature_init_distribution.type == "uniform":
            return InitialTemperatureUniform(ansys_commands, class_geometry, input_data=self.input_data, mat_props=mat_props)
        elif self.input_data.temperature_init_distribution.type == "power_input":
            return InitialTemperaturePowerInput(ansys_commands, class_geometry, input_data=self.input_data, mat_props=mat_props)
        elif self.input_data.temperature_init_distribution.type == "temperature_function":
            return InitialTemperatureFunction(ansys_commands, class_geometry, input_data=self.input_data, mat_props=mat_props)
        else:
            raise ValueError("The initial temperature distribution - is not well-defined. "
                             "\n Please check the user input file carefully.")

    def get_preprocessor_class(self, mat_props, ansys_commands):
        if self.input_data.analysis_type.type == "v_quench_model":
            return PreProcessorQuenchVelocity(mat_props, ansys_commands, self.input_data)
        elif self.input_data.analysis_type.type == "heat_balance":
            return PreProcessorHeatBalance(mat_props, ansys_commands, self.input_data)

    def get_postprocessor_class(self, class_geometry, ansys_commands, v_quench, solver):
        if self.input_data.analysis_type.type == "v_quench_model":
            return PostProcessorQuenchVelocity(class_geometry, ansys_commands, v_quench, solver, input_data=self.input_data)
        elif self.input_data.analysis_type.type == "heat_balance":
            return PostProcessorHeatBalance(class_geometry, ansys_commands, v_quench, solver, input_data=self.input_data)
        else:
            raise ValueError("Class PostProcessor was not properly defined - change the name of 'analysis type'")
