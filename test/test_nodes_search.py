
import os
import unittest
import numpy as np
from source.physics.quench_velocity.nodes_search import SearchNodes


# methods for 1D analysis
def create_1d_coil_geometry(division, filename, directory):
    """
    Returns array with length of coil at each node starting from the 1st node
    :param division: number of elements as integer
    :param filename: filename as string
    :param directory: analysis output_directory as string
    """
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

class TestSearchNodes(unittest.TestCase):

    CWD = os.path.dirname(__file__)
    DIRECTORY = os.path.join(CWD, 'nodes_search')
    LARGE_STEP_CONTROL = 100
    SMALL_STEP_CONTROL = 1
    LARGE_EPSILON = 0.001
    SMALL_EPSILON = 0.0000001

    def setUp(self):
        self.coil_geometry = create_1d_coil_geometry(division=100, filename="File_Position_101nodes_1m.txt", directory=TestSearchNodes.DIRECTORY)

    # tests for function search_init_node
    def test_search_init_node_large_epsilon(self):
        position = [0.0, 0.2001, 0.5001, 0.8001, 1.0]
        expected_result = [1, 21, 51, 81, 101]
        for x in range(len(position)):
            result = SearchNodes.search_init_node(position=position[x], coil_length=self.coil_geometry, epsilon=TestSearchNodes.LARGE_EPSILON)
            self.assertEqual(result, expected_result[x])

    def test_search_init_node_small_epsilon(self):
        position = [0.0, 0.2001, 0.5001, 0.8001, 1.0]
        expected_result = [1, 21, 51, 81, 101]
        for x in range(len(position)):
            result = SearchNodes.search_init_node(position=position[x], coil_length=self.coil_geometry, epsilon=TestSearchNodes.SMALL_EPSILON)
            self.assertEqual(result, expected_result[x])

    def test_search_init_node_error_position_negative(self):
        position_negative = -1.0
        with self.assertRaises(Exception):
            SearchNodes.search_init_node(position=position_negative, coil_length=self.coil_geometry, epsilon=TestSearchNodes.LARGE_EPSILON)
            SearchNodes.search_init_node(position=position_negative, coil_length=self.coil_geometry, epsilon=TestSearchNodes.SMALL_EPSILON)

    def test_search_init_node_error_position_larger_than_coil(self):
        position_above_coil_length = 5000000.0
        with self.assertRaises(Exception):
            SearchNodes.search_init_node(position=position_above_coil_length, coil_length=self.coil_geometry, epsilon=TestSearchNodes.LARGE_EPSILON)
            SearchNodes.search_init_node(position=position_above_coil_length, coil_length=self.coil_geometry, epsilon=TestSearchNodes.SMALL_EPSILON)
