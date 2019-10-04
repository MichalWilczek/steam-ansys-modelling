
import unittest
import numpy as np
from source.solver.initial_temperature.initial_temperature_gaussian import InitialTemperatureGaussian

class TestInitialTemperatureGaussian(unittest.TestCase):

    def test_refine_gaussian_array_input_above_t_critical(self):
        # exemplary numpy array
        array = np.zeros((10, 2))
        nnum = 1
        for i in range(len(array[:, 0])):
            array[i, 0] = nnum
            array[i, 1] = 1.9
            nnum += 1
        array[6, 1] = 5.0
        array[7, 1] = 5.0

        # theoretical result of the function
        refined_array = np.zeros((2, 2))
        refined_array[0, 0] = 7
        refined_array[1, 0] = 8
        refined_array[0, 1] = 5.0
        refined_array[1, 1] = 5.0

        # comparison of all values in array to compare
        self.assertEqual(refined_array[0, 0], InitialTemperatureGaussian.refine_gaussian_array_input_above_t_critical(array, 1.9)[0, 0])
        self.assertEqual(refined_array[1, 0], InitialTemperatureGaussian.refine_gaussian_array_input_above_t_critical(array, 1.9)[1, 0])
        self.assertEqual(refined_array[0, 1], InitialTemperatureGaussian.refine_gaussian_array_input_above_t_critical(array, 1.9)[0, 1])
        self.assertEqual(refined_array[1, 1], InitialTemperatureGaussian.refine_gaussian_array_input_above_t_critical(array, 1.9)[1, 1])



