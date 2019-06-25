from variables import Variables
import os
import numpy as np


class Geometry:

    def __init__(self):
        self.division = Variables().division
        self.filename = Variables().coil_geometry_name
        self.analysis_directory = Variables().analysis_directory

    def length_coil(self):
        """
        returns an array with a length of the coil at each node starting from the 1st node
        """

        os.chdir(self.analysis_directory)
        npoints = self.division + 1
        length_array = np.zeros((npoints, 2))
        current_length = 0
        array = np.loadtxt(self.filename)

        for i in range(1, npoints):
            current_length += ((array[i, 1] - array[i - 1, 1]) ** 2 + (array[i, 2] - array[i - 1, 2]) ** 2 +
                               (array[i, 3] - array[i - 1, 3]) ** 2) ** 0.5
            # changed 22/05/2019
            # length_array[i, 0] = i
            length_array[i - 1, 0] = i
            length_array[i, 1] = current_length
        length_array[npoints - 1, 0] = npoints

        return length_array