import numpy as np
import os
from source.geometry.geometry import Geometry

class Geometry1D(Geometry):

    def __init__(self, input_data, analysis_directory):
        Geometry.__init__(self, input_data, analysis_directory)
        self.coil_geometry = self.create_1d_coil_geometry()
        print("Geometry uploaded... \n________________")

    # methods for 1D analysis
    def create_1d_coil_geometry(self):
        """
        Returns array with length of coil at each node starting from the 1st node
        :param division: number of elements as integer
        :param filename: filename as string
        :param directory: analysis directory as string
        """
        division = self.factory.get_division_in_full_coil()
        filename = self.factory.filename_nodal_position()
        directory = self.directory()

        os.chdir(directory)
        npoints = division + 1
        length_array = np.zeros((npoints, 2))
        current_length = 0
        array = np.loadtxt(filename)
        for i in range(1, npoints):
            current_length += ((array[i, 1] - array[i - 1, 1]) ** 2 + (array[i, 2] - array[i - 1, 2]) ** 2 +
                               (array[i, 3] - array[i - 1, 3]) ** 2) ** 0.5
            length_array[i - 1, 0] = i
            length_array[i, 1] = current_length
        length_array[npoints - 1, 0] = npoints
        return length_array
