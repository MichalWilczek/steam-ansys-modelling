from source.geometry_1D import Geometry1D
from source.geometry_1D_1D import Geometry1D1D
from source.geometry_2D import Geometry2D

from source.ansys_1D import AnsysCommands1D
from source.ansys_1D_1D import AnsysCommands1D1D
from source.ansys_2D import AnsysCommands2D
from source.factory import AnalysisBuilder


class CaseFactory(AnalysisBuilder):

    def get_geometry_class(self):
        dimensionality = self.get_dimensionality()
        if dimensionality == "1D":
            return Geometry1D()
        elif dimensionality == "1D_1D":
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
        elif dimensionality == "2D":
            return AnsysCommands2D()
        else:
            raise ValueError(dimensionality)