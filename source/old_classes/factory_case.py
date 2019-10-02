
from source.factory import AnalysisBuilder

from source.class_geometry.geometry_1D import Geometry1D
from source.class_geometry.geometry_1D1D1D import GeometryMulti1D
from source.class_geometry.geometry_2D import Geometry2D

from source.class_ansys.ansys_1D import Ansys1D
from source.class_ansys.ansys_1D1D1D_skew_quad import AnsysMulti1DSkewQuad
from source.class_ansys.ansys_1D1D1D_slab import AnsysMulti1DSlab
from source.class_ansys.ansys_2D import Ansys2D

from source.class_material_properties.material_properties_nonlinear import  MaterialsNonLinear
from source.class_material_properties.material_properties_linear import MaterialsLinear

from source.class_quench_velocity.quench_velocity_constant import QuenchFrontConst
from source.class_quench_velocity.quench_velocity_numerical import QuenchFrontNum

from source.class_magnetic_field.magnetic_field_mapping_const import MagneticMapConst
from source.class_magnetic_field.magnetic_field_mapping_non_const import MagneticMapNonConst

class CaseFactory(AnalysisBuilder):

    def get_geometry_class(self):
        dimensionality = self.get_dimensionality()
        if dimensionality == "1D" or dimensionality == "1D_1D_1D":
            return GeometryMulti1D()
        elif dimensionality == "2D":
            return Geometry2D()
        else:
            raise ValueError(dimensionality)

    def get_ansys_class(self):
        dimensionality = self.get_dimensionality()
        geometry_type = self.get_geometry_type()
        magnet_type = self.get_magnet_type()
        if dimensionality == "1D":
            return Ansys1D()
        elif dimensionality == "1D_1D_1D" and geometry_type == "magnet" and magnet_type == "skew_quadrupole":
            return AnsysMulti1DSkewQuad()
        elif dimensionality == "1D_1D_1D" and geometry_type == "slab":
            return AnsysMulti1DSlab()
        elif dimensionality == "2D":
            return Ansys2D()
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

    def get_magnetic_map_class(self, winding_list, **kwargs):
        """
        Chooses between Classes with constant and non-constant magnetic field map
        :return: Class MagneticField
        """
        mag_model = self.get_magnetic_map_model()
        if mag_model == "constant":
            return MagneticMapConst(windings_in_geometry=winding_list, **kwargs)
        elif mag_model == "nonconstant":
            return MagneticMapNonConst(windings_in_geometry=winding_list)
        else:
            raise ValueError("Class MagneticField does not exist")

