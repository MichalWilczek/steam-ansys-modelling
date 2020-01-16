
from scipy import interpolate
import numpy as np

class InterpolationFunctions(object):

    @staticmethod
    def interpolate_linear_1d_function(x, y):
        """
        Interpolate a 1-D function.
        x and y are arrays of values used to approximate some function f: y = f(x)
        """
        return interpolate.interp1d(x, y, kind="linear")

    @staticmethod
    def interpolate_linear_2d_function(x, y, z):
        """
        Interpolate over a 2-D grid.
        x, y and z are arrays of values used to approximate some function f: z = f(x, y).
        """
        return interpolate.interp2d(x, y, z, kind="linear")

    @staticmethod
    def interpolate_linear_3d_function(x, y, z, data):
        return interpolate.RegularGridInterpolator((x, y, z), data)

    @staticmethod
    def get_value_from_linear_1d_interpolation(f_interpolation, x):
        array = np.array([x])
        return f_interpolation(array)[0]

    @staticmethod
    def get_value_from_linear_2d_interpolation(f_interpolation, x, y):
        x = np.array([x])
        y = np.array([y])
        return f_interpolation(x, y)[0]

    @staticmethod
    def get_value_from_linear_3d_interpolation(f_interpolation, x, y, z):
        array = np.array([x, y, z])
        return f_interpolation(array)[0]

