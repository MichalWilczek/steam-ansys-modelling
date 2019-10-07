
import os
import json
from collections import namedtuple
from six import with_metaclass

from source.input.input_user import InputUser
# from source.input.input_slab import InputSlab
# from source.input.input_user_skew_quadrupole import InputUserSkewQuadrupole
# from source.input.input_user_1D import InputUser1D
# from source.input.input_user_multiple_1D import InputUserMultiple1D
# from source.input.input_user_2D import InputUser2D

from source.geometry.geometry_1D1D1D import GeometryMulti1D
from source.geometry.geometry_2D import Geometry2D

from source.ansys_commands.ansys_1D import Ansys1D
from source.ansys_commands.ansys_multiple_1D_skew_quad import AnsysMultiple1DSkewQuad
from source.ansys_commands.ansys_multiple_1D_slab import AnsysMultiple1DSlab
from source.ansys_commands.ansys_2D import Ansys2D

from source.material_properties.material_properties_nonlinear import MaterialsNonLinear
from source.material_properties.material_properties_linear import MaterialsLinear

from source.processor_post.quench_velocity.quench_velocity import QuenchFront
from source.processor_post.quench_velocity.quench_velocity_constant import QuenchFrontConst
from source.processor_post.quench_velocity.quench_velocity_numerical import QuenchFrontNum

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

from source.processor_pre.pre_processor_quench_velocity import PreProcessorQuenchVelocity
from source.processor_pre.pre_processor_heat_balance import PreProcessorHeatBalance

from source.processor_post.post_processor_heat_balance import PostProcessorHeatBalance
from source.processor_post.post_processor_quench_velocity import PostProcessorQuenchVelocity

class Factory(InputUser):

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
        path = os.path.join(source, 'apdl_scripts', '1D')
        return path

    @staticmethod
    def directory_multiple_1d():
        source = Factory.define_main_path()
        path = os.path.join(source, 'apdl_scripts', '1D_1D_1D')
        return path

    @staticmethod
    def directory_2d():
        source = Factory.define_main_path()
        path = os.path.join(source, 'apdl_scripts', '2D')
        return path

    @staticmethod
    def create_class(*args):
        class CustomisedClass(*args):
            pass
        return CustomisedClass

    @staticmethod
    def convert_json_to_class_object(class_name, json_filename):
        with open(json_filename) as json_file:
            data = json.load(json_file, object_hook=lambda d: namedtuple(class_name, d.keys())(*d.values()))
        return data

    @staticmethod
    def get_input_data_class(ansys_analysis_directory):

        input_json_directory = os.path.join(ansys_analysis_directory, 'analysis_input', 'input_json')
        os.chdir(input_json_directory)
        inp_1 = Factory.convert_json_to_class_object(class_name="InputUser", json_filename='input_user.json')
        inp_2 = Factory.convert_json_to_class_object(class_name="InputUserSkewQuadrupole", json_filename='input_user_skew_quadrupole.json')

        # print(InputUser)
        # print("----")
        # print(inp_1)
        # print("----")
        # print(inp_2)

        print(type(inp_1))
        class_inp_2 = Factory.create_class(inp_1, inp_2)
        print(inp_1.__dict__)

        class_inp = Factory.create_class(type(inp_1).__doc__, type(inp_2).__doc__)
        print(class_inp.magnetic_map_model)
        # print(class_inp)

        if InputUser.dimensionality == "1D":
            InputUser1D = Factory.convert_json_to_class_object(class_name="InputUser1D", json_filename='input_user_1D.json')
            if InputUser.geometry_type == "slab":
                InputUserSlab = Factory.convert_json_to_class_object(class_name="InputUserSlab", json_filename='input_user_slab.json')
                return Factory.create_class(InputUser, InputUser1D, InputUserSlab)
            elif InputUser.geometry_type == "skew_quadrupole":
                InputUserSkewQuadrupole = Factory.convert_json_to_class_object(class_name="InputUserSkewQuadrupole", json_filename='input_user_skew_quadrupole.json')
                return Factory.create_class(InputUser, InputUser1D, InputUserSkewQuadrupole)

        elif InputUser.dimensionality == "multiple_1D":
            InputUserMultiple1D = Factory.convert_json_to_class_object(class_name="InputUserMultiple1D", json_filename='input_user_multiple_1D.json')
            if InputUser.geometry_type == "slab":
                InputUserSlab = Factory.convert_json_to_class_object(class_name="InputUserSlab", json_filename='input_user_slab.json')
                return Factory.create_class(InputUser, InputUserMultiple1D, InputUserSlab)
            elif InputUser.geometry_type == "skew_quadrupole":
                InputUserSkewQuadrupole = Factory.convert_json_to_class_object(class_name="InputUserSkewQuadrupole", json_filename='input_user_skew_quadrupole.json')
                return Factory.create_class(InputUser, InputUserMultiple1D, InputUserSkewQuadrupole)

        elif InputUser.dimensionality == "2D":
            InputUser2D = Factory.convert_json_to_class_object(class_name="InputUser2D", json_filename='input_user_2D.json')
            if InputUser.geometry_type == "slab":
                InputUserSlab = Factory.convert_json_to_class_object(class_name="InputUserSlab", json_filename='input_user_slab.json')
                return Factory.create_class(InputUser, InputUser2D, InputUserSlab)
            elif InputUser.geometry_type == "skew_quadrupole":
                InputUserSkewQuadrupole = Factory.convert_json_to_class_object(class_name="InputUserSkewQuadrupole", json_filename='input_user_skew_quadrupole.json')
                return Factory.create_class(InputUser, InputUser2D, InputUserSkewQuadrupole)
        else:
            raise ValueError("Input data are not sufficient to run the analysis")


        # if Factory.dimensionality == "1D":
        #     if Factory.geometry_type == "slab":
        #         return Factory.create_class(InputUser, InputUser1D, InputSlab)
        #     elif Factory.geometry_type == "skew_quadrupole":
        #         return Factory.create_class(InputUser, InputUser1D, InputUserSkewQuadrupole)
        # elif Factory.dimensionality == "multiple_1D":
        #     if Factory.geometry_type == "slab":
        #         return Factory.create_class(InputUser, InputUserMultiple1D, InputSlab)
        #     elif Factory.geometry_type == "skew_quadrupole":
        #         return Factory.create_class(InputUser, InputUserMultiple1D, InputUserSkewQuadrupole)
        # elif Factory.dimensionality == "2D":
        #     if Factory.geometry_type == "slab":
        #         return Factory.create_class(InputUser, InputUser2D, InputSlab)
        #     elif Factory.geometry_type == "skew_quadrupole":
        #         return Factory.create_class(InputUser, InputUser2D, InputUserSkewQuadrupole)
        # else:
        #     raise ValueError("Input data are not sufficient to run the analysis")

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
        elif Factory.v_quench_model is None:
            return QuenchFront
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
    def get_solver_type(ansys_commands, class_geometry, circuit, ic_temperature_class, mat_props, mag_map):
        if Factory.analysis_type == "v_quench_model":
            return SolverQuenchVelocity(ansys_commands=ansys_commands, class_geometry=class_geometry,
                                        input_data=Factory.get_input_data_class(), circuit=circuit,
                                        ic_temperature_class=ic_temperature_class, mag_map=mag_map, mat_props=mat_props)
        elif Factory.analysis_type == "heat_balance":
            return SolverHeatBalance(ansys_commands=ansys_commands, class_geometry=class_geometry,
                                     input_data=Factory.get_input_data_class(), circuit=circuit,
                                     ic_temperature_class=ic_temperature_class, mag_map=mag_map, mat_props=mat_props)
        else:
            raise ValueError("Class Solver does not exist")

    @staticmethod
    def get_circuit_class(ansys_commands, class_geometry):
        if not Factory.electric_ansys_elements:
            return CircuitThermalAnalysisNoCircuit(ansys_commands, class_geometry, input_data=Factory.get_input_data_class())
        else:
            if not Factory.build_electric_circuit:
                return CircuitElectricAnalysisNoCircuit(ansys_commands, class_geometry, input_data=Factory.get_input_data_class())
            else:
                if not Factory.transient_electric_analysis:
                    return CircuitElectricAnalysisWithCircuitStatic(ansys_commands, class_geometry, input_data=Factory.get_input_data_class())
                else:
                    return CircuitElectricAnalysisWithCircuitTransient(ansys_commands, class_geometry, input_data=Factory.get_input_data_class())

    @staticmethod
    def get_initial_temperature_class(ansys_commands, class_geometry, mat_props):
        if Factory.temperature_init_distr == "gaussian_distribution":
            return InitialTemperatureGaussian(ansys_commands, class_geometry, input_data=Factory.get_input_data_class(), mat_props=mat_props)
        elif Factory.temperature_init_distr == "uniform":
            return InitialTemperatureUniform(ansys_commands, class_geometry, input_data=Factory.get_input_data_class(), mat_props=mat_props)
        elif Factory.temperature_init_distr == "power_input":
            return InitialTemperaturePowerInput(ansys_commands, class_geometry, input_data=Factory.get_input_data_class(), mat_props=mat_props)
        elif Factory.temperature_init_distr == "temperature_function":
            return InitialTemperatureFunction(ansys_commands, class_geometry, input_data=Factory.get_input_data_class(), mat_props=mat_props)
        else:
            raise ValueError("The initial temperature distribution - is not well-defined. "
                             "\n Please check the user input file carefully.")

    @staticmethod
    def get_preprocessor_class(mat_props, ansys_commands, input_data):
        if Factory.analysis_type == "v_quench_model":
            return PreProcessorQuenchVelocity(mat_props, ansys_commands, input_data)
        elif Factory.analysis_type == "heat_balance":
            return PreProcessorHeatBalance(mat_props, ansys_commands, input_data)

    @staticmethod
    def get_postprocessor_class(class_geometry, ansys_commands, v_quench, solver):
        if Factory.analysis_type == "v_quench_model":
            return PostProcessorQuenchVelocity(class_geometry, ansys_commands, v_quench, solver, input_data=Factory.get_input_data_class())
        elif Factory.analysis_type == "heat_balance":
            return PostProcessorHeatBalance(class_geometry, ansys_commands, v_quench, solver, input_data=Factory.get_input_data_class())
        else:
            raise ValueError("Class PostProcessor was not properly defined - change the name of 'analysis type'")
