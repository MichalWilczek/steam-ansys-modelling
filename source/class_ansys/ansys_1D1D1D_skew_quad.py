
from source.class_ansys.ansys_1D1D1D import AnsysMulti1D

class AnsysMulti1DSkewQuad(AnsysMulti1D):

    def input_geometry(self, filename='1D_1D_1D_Geometry_quadrupole'):
        """
        Inputs prepared file with geometry to ANSYS environment
        :param filename: geometry file name as string
        """
        print("________________ \nAnsys geometry is being uploaded...")
        self.input_file(filename=filename, extension='inp', add_directory='Input_Files')
