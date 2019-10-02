
import os

from source.input.input_user_general import InputUserGeneral
from source.input.input_skew_quadrupole import InputSkewQuadrupole
from source.input.input_user_analysis_1D import InputUserAnalysis1D
from source.input.input_user_analysis_multiple_1D import InputUserAnalysisMultiple1D
from source.input.input_user_analysis_2D import InputUserAnalysis2D
# from source.input.input_user_analysis_slab import InputUserAnalysisSlab

from source.geometry.geometry_1D import Geometry1D
from source.geometry.geometry_1D1D1D import GeometryMulti1D
from source.geometry.geometry_2D import Geometry2D

from source.ansys_commands.ansys_1D import Ansys1D
from source.ansys_commands.ansys_multiple_1D_skew_quad import AnsysMultiple1DSkewQuad
from source.ansys_commands.ansys_multiple_1D_slab import AnsysMultiple1DSlab
from source.ansys_commands.ansys_2D import Ansys2D

from source.material_properties.material_properties_nonlinear import MaterialsNonLinear
from source.material_properties.material_properties_linear import MaterialsLinear

from source.quench_velocity.quench_velocity_constant import QuenchFrontConst
from source.quench_velocity.quench_velocity_numerical import QuenchFrontNum

from source.magnetic_field.magnetic_field_1D import MagneticField1D
from source.magnetic_field.magnetic_field_2D import MagneticField2D
from source.magnetic_field.magnetic_field_2D_static import MagneticField2DStatic
from source.magnetic_field.magnetic_field_2D_transient import MagneticField2DTransient

from source.solver.solver_quench_velocity import SolverQuenchVelocity
from source.solver.solver_heat_balance import SolverHeatBalance

from source.circuit.circuit_transient import CircuitTransient
from source.circuit.circuit_no_transient import CircuitNoTransient

from source.initial_temperature.initial_temperature_function import InitialTemperatureFunction
from source.initial_temperature.initial_temperature_gaussian import InitialTemperatureGaussian
from source.initial_temperature.initial_temperature_uniform import InitialTemperatureUniform
from source.initial_temperature.initial_temperature_power_input import InitialTemperaturePowerInput

class Factory(InputUserGeneral):

    @staticmethod
    def get_directory():
        if Factory.dimensionality == "1D":
            return Factory.directory_1d()
        elif Factory.dimensionality == "multiple_1D":
            return Factory.directory_multiple_1d()
        elif Factory.dimensionality == "2D":
            return Factory.directory_2d()
        else:
            raise ValueError("Directory does not exist")

    @staticmethod
    def define_main_path():
        cwd = os.path.dirname(__file__)
        return cwd

    @staticmethod
    def directory_1d():
        source = Factory.define_main_path()
        path = os.path.join(source, 'APDL', '1D')
        return path

    @staticmethod
    def directory_multiple_1d():
        source = Factory.define_main_path()
        path = os.path.join(source, 'APDL', '1D_1D_1D')
        return path

    @staticmethod
    def directory_2d():
        source = Factory.define_main_path()
        path = os.path.join(source, 'APDL', '2D')
        return path

    @staticmethod
    def create_class(*args):
        class CustomisedClass(*args):
            pass
        return CustomisedClass

    @staticmethod
    def get_input_data_class():
        if Factory.dimensionality == "1D":
            if Factory.geometry_type == "slab":
                return Factory.create_class(InputUserGeneral, InputUserAnalysis1D)
            elif Factory.geometry_type == "skew_quadrupole":
                return Factory.create_class(InputUserGeneral, InputUserAnalysis1D, InputSkewQuadrupole)
        elif Factory.dimensionality == "multiple_1D":
            if Factory.geometry_type == "slab":
                return Factory.create_class(InputUserGeneral, InputUserAnalysisMultiple1D)
            elif Factory.geometry_type == "skew_quadrupole":
                return Factory.create_class(InputUserGeneral, InputUserAnalysisMultiple1D, InputSkewQuadrupole)
        elif Factory.dimensionality == "2D":
            if Factory.geometry_type == "slab":
                return Factory.create_class(InputUserGeneral, InputUserAnalysis2D)
            elif Factory.geometry_type == "skew_quadrupole":
                return Factory.create_class(InputUserGeneral, InputUserAnalysis2D, InputSkewQuadrupole)
        else:
            raise ValueError("Input data are not sufficient to run the analysis")

    @staticmethod
    def get_geometry_class():
        if Factory.dimensionality == "1D" or Factory.dimensionality == "multiple_1D":
            return GeometryMulti1D(input_data=Factory.get_input_data_class(),
                                   analysis_directory=Factory.get_directory())
        elif Factory.dimensionality == "2D":
            return Geometry2D(input_data=Factory.get_input_data_class(),
                              analysis_directory=Factory.get_directory())
        else:
            raise ValueError("Class Geometry does not exist")

    @staticmethod
    def get_ansys_class():
        if Factory.dimensionality == "1D":
            return Ansys1D(input_data=Factory.get_input_data_class(),
                           analysis_directory=Factory.get_directory())
        elif Factory.dimensionality == "multiple_1D" and Factory.geometry_type == "skew_quadrupole":
            return AnsysMultiple1DSkewQuad(input_data=Factory.get_input_data_class(),
                                           analysis_directory=Factory.get_directory())
        elif Factory.dimensionality == "multiple_1D" and Factory.geometry_type == "slab":
            return AnsysMultiple1DSlab(input_data=Factory.get_input_data_class(),
                                       analysis_directory=Factory.get_directory())
        elif Factory.dimensionality == "2D":
            return Ansys2D(input_data=Factory.get_input_data_class(),
                           analysis_directory=Factory.get_directory())
        else:
            raise ValueError(Factory.dimensionality)

    @staticmethod
    def get_material_properties_class():
        """
        Chooses between linear and nonlinear material properties set in json file
        :return: Class with material properties
        """
        if Factory.material_properties_type == "linear":
            return MaterialsLinear(input_data=Factory.get_input_data_class())
        elif Factory.material_properties_type == "nonlinear":
            return MaterialsNonLinear(input_data=Factory.get_input_data_class())
        else:
            raise ValueError("Class MaterialProperties does not exist")

    @staticmethod
    def get_quench_velocity_class():
        """
        Chooses between QuenchFront classes calculating qv in different manners
        :return: Class QuenchFront
        """
        if Factory.v_quench_model == "constant":
            return QuenchFrontConst
        elif Factory.v_quench_model == "numerical":
            return QuenchFrontNum
        else:
            raise ValueError("Class QuenchFront does not exist")

    @staticmethod
    def get_magnetic_map_class():
        """
        Chooses between Classes with constant and non-constant magnetic field map
        :return: Class MagneticField
        """
        if Factory.magnetic_map_model == "1D_constant":
            return MagneticField1D(input_data=Factory.get_input_data_class())
        elif Factory.magnetic_map_model == "2D_constant":
            return MagneticField2D(input_data=Factory.get_input_data_class())
        elif Factory.magnetic_map_model == "2D_static":
            return MagneticField2DStatic(input_data=Factory.get_input_data_class())
        elif Factory.magnetic_map_model == "2D_transient":
            return MagneticField2DTransient(input_data=Factory.get_input_data_class())
        else:
            raise ValueError("Class MagneticField does not exist")

    @staticmethod
    def get_solver_type(ansys_commands, class_geometry, circuit):
        if Factory.analysis_type == "v_quench_model":
            return SolverQuenchVelocity(ansys_commands, class_geometry, input_data=Factory.get_input_data_class(),
                                        circuit=circuit)
        elif Factory.analysis_type == "heat_balance":
            return SolverHeatBalance(ansys_commands, class_geometry, input_data=Factory.get_input_data_class(),
                                     circuit=circuit)
        else:
            raise ValueError("Class Solver does not exist")

    @staticmethod
    def get_circuit_class(ansys_commands, class_geometry):
        if Factory.transient_electric_analysis:
            return CircuitTransient(ansys_commands, class_geometry, input_data=Factory.get_input_data_class())
        else:
            return CircuitNoTransient(ansys_commands, class_geometry, input_data=Factory.get_input_data_class())

    @staticmethod
    def get_initial_temperature_class(ansys_commands, class_geometry):
        if Factory.temperature_init_distr == "gaussian_distribution":
            return InitialTemperatureGaussian(ansys_commands, class_geometry, input_data=Factory.get_input_data_class())
        elif Factory.temperature_init_distr == "uniform":
            return InitialTemperatureUniform(ansys_commands, class_geometry, input_data=Factory.get_input_data_class())
        elif Factory.temperature_init_distr == "power_input":
            return InitialTemperaturePowerInput(ansys_commands, class_geometry, input_data=Factory.get_input_data_class())
        elif Factory.temperature_init_distr == "temperature_function":
            return InitialTemperatureFunction(ansys_commands, class_geometry, input_data=Factory.get_input_data_class())
        else:
            raise ValueError("The initial temperature distribution - is not well-defined. "
                             "\n Please check the user input file carefully.")








