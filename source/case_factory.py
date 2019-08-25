
from source.geometry_1D import Geometry1D
from source.geometry_1D_1D import Geometry1D1D
from source.geometry_2D import Geometry2D

from source.ansys_1D import AnsysCommands1D
from source.ansys_1D_1D import AnsysCommands1D1D
from source.ansys_1D_1D_1D import AnsysCommands1D1D1D
from source.ansys_2D import AnsysCommands2D
from source.factory import AnalysisBuilder

from source.material_properties_nonlinear import MaterialsNonLinear
from source.material_properties_linear import MaterialsLinear

from source.quench_velocity_constant import QuenchFrontConst
from source.quench_velocity_numerical import QuenchFrontNum

from source.magnetic_field_mapping_const import MagneticMapConst
from source.magnetic_field_mapping_non_const import MagneticMapNonConst

class CaseFactory(AnalysisBuilder):

    def get_geometry_class(self):
        dimensionality = self.get_dimensionality()
        if dimensionality == "1D":
            return Geometry1D()
        elif dimensionality == "1D_1D" or dimensionality == "1D_1D_1D":
            return Geometry1D1D()
        elif dimensionality == "2D":
            return Geometry2D()
        else:
            raise ValueError(dimensionality)

    def get_ansys_class(self):
        dimensionality = self.get_dimensionality()
        if dimensionality == "1D":
            return AnsysCommands1D()
        elif dimensionality == "1D_1D":
            return AnsysCommands1D1D()
        elif dimensionality == "1D_1D_1D":
            return AnsysCommands1D1D1D()
        elif dimensionality == "2D":
            return AnsysCommands2D()
        else:
            raise ValueError(dimensionality)

    def get_material_properties_class(self):
        """
        Chooses between linear and nonlinear material properties set in json file
        :return: Class with material properties
        """
        material_option = self.get_material_properties_type()
        if material_option == "linear":
            return MaterialsLinear()
        elif material_option == "nonlinear":
            return MaterialsNonLinear()
        else:
            raise ValueError("Class MaterialProperties does not exist")

    def get_quench_velocity_class(self):
        """
        Chooses between QuenchFront classes calculating qv in different manners
        :return: Class QuenchFront
        """
        qv_model = self.get_quench_velocity_model()
        if qv_model == "constant":
            return QuenchFrontConst
        elif qv_model == "numerical":
            return QuenchFrontNum
        else:
            raise ValueError("Class QuenchFront does not exist")

    def get_magnetic_map_class(self, winding_list):
        """
        Chooses between Classes with constant and non-constant magnetic field map
        :return: Class MagneticMap
        """
        mag_model = self.get_magnetic_map_model()
        if mag_model == "constant":
            return MagneticMapConst(windings_in_geometry=winding_list)
        elif mag_model == "nonconstant":
            return MagneticMapNonConst(windings_in_geometry=winding_list)
        else:
            raise ValueError("Class MagneticMap does not exist")

