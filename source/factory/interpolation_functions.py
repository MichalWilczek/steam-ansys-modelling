
from scipy import interpolate
import numpy as np

class InterpolationFunctions(object):

    @staticmethod
    def interpolate_linear_function(x, y):
        return interpolate.interp1d(x, y, kind="linear")

    @staticmethod
    def get_value_from_linear_1d_interpolation(f_interpolation, x):
        array = np.array([x])
        return f_interpolation(array)[0]

