
import os
import unittest
from source.nodes_search import SearchNodes
from source.geometry import Geometry


class TestSearchNodes(unittest.TestCase):

    CWD = os.path.dirname(__file__)
    DIRECTORY = os.path.join(CWD, 'nodes_search')
    LARGE_STEP_CONTROL = 100
    SMALL_STEP_CONTROL = 1
    LARGE_EPSILON = 0.001
    SMALL_EPSILON = 0.0000001

    def setUp(self):
        self.coil_geometry = Geometry.length_coil(division=100, filename="File_Position_101nodes_1m.txt", directory=TestSearchNodes.DIRECTORY)
        # series of tests with epsilon one order of magnitude lower than mesh quality
        self.search_nodes_large_epsilon = SearchNodes(coil_length=self.coil_geometry, epsilon=TestSearchNodes.LARGE_EPSILON)
        # series of tests with epsilon five orders of magnitude lower than mesh quality
        self.search_nodes_small_epsilon = SearchNodes(coil_length=self.coil_geometry, epsilon=TestSearchNodes.SMALL_EPSILON)

    # tests for function search_init_node
    def test_search_init_node_large_epsilon(self):
        position = [0.0, 0.2001, 0.5001, 0.8001, 1.0]
        expected_result = [1, 21, 51, 81, 101]
        for x in range(len(position)):
            result = self.search_nodes_large_epsilon.search_init_node(position=position[x])
            self.assertEqual(result, expected_result[x])

    def test_search_init_node_small_epsilon(self):
        position = [0.0, 0.2001, 0.5001, 0.8001, 1.0]
        expected_result = [1, 21, 51, 81, 101]
        for x in range(len(position)):
            result = self.search_nodes_small_epsilon.search_init_node(position=position[x])
            self.assertEqual(result, expected_result[x])

    def test_search_init_node_error_position_negative(self):
        position_negative = -1.0
        with self.assertRaises(Exception):
            self.search_nodes_large_epsilon.search_init_node(position=position_negative)
            self.search_nodes_small_epsilon.search_init_node(position=position_negative)

    def test_search_init_node_error_position_larger_than_coil(self):
        position_above_coil_length = 5000000.0
        with self.assertRaises(Exception):
            self.search_nodes_large_epsilon.search_init_node(position=position_above_coil_length)
            self.search_nodes_small_epsilon.search_init_node(position=position_above_coil_length)

    # tests for function search_node_up
    def test_search_node_up_small_step_control(self, quench_length=0.5912, step_control=SMALL_STEP_CONTROL):
        starting_node = [1, 30]
        expected_result = 60
        for sn in starting_node:
            result_small_epsilon = self.search_nodes_small_epsilon.search_node_up(left=sn, quench_length=quench_length, step_control=step_control)
            result_large_epsilon = self.search_nodes_large_epsilon.search_node_up(left=sn, quench_length=quench_length, step_control=step_control)
            self.assertEqual(first=result_small_epsilon, second=expected_result)
            self.assertEqual(first=result_large_epsilon, second=expected_result)

    def test_search_node_up_small_step_control_exceptions(self, quench_length=0.5912, step_control=SMALL_STEP_CONTROL):
        starting_node = [-10, 0, 90, 101]
        for sn in starting_node:
            with self.assertRaises(Exception):
                self.search_nodes_small_epsilon.search_node_up(left=sn, quench_length=quench_length, step_control=step_control)
                self.search_nodes_large_epsilon.search_node_up(left=sn, quench_length=quench_length, step_control=step_control)

    def test_search_node_up_large_step_control(self, quench_length=0.5912, step_control=LARGE_STEP_CONTROL):
        starting_node = [1, 30]
        expected_result = 60
        for sn in starting_node:
            result_small_epsilon = self.search_nodes_small_epsilon.search_node_up(left=sn, quench_length=quench_length, step_control=step_control)
            result_large_epsilon = self.search_nodes_large_epsilon.search_node_up(left=sn, quench_length=quench_length, step_control=step_control)
            self.assertEqual(first=result_small_epsilon, second=expected_result)
            self.assertEqual(first=result_large_epsilon, second=expected_result)

    def test_search_node_up_large_step_control_exceptions(self, quench_length=0.5912, step_control=LARGE_STEP_CONTROL):
        starting_node = [-10, 0, 90, 101]
        for sn in starting_node:
            with self.assertRaises(Exception):
                self.search_nodes_small_epsilon.search_node_up(left=sn, quench_length=quench_length, step_control=step_control)
                self.search_nodes_large_epsilon.search_node_up(left=sn, quench_length=quench_length, step_control=step_control)

    # tests for function search_node_down
    def test_search_node_down_small_step_control(self, quench_length=0.1235, step_control=SMALL_STEP_CONTROL):
        starting_node = [30, 90, 101]
        expected_result = 13
        for sn in starting_node:
            result_small_epsilon = self.search_nodes_small_epsilon.search_node_down(right=sn, quench_length=quench_length, step_control=step_control)
            result_large_epsilon = self.search_nodes_large_epsilon.search_node_down(right=sn, quench_length=quench_length, step_control=step_control)
            self.assertEqual(first=result_small_epsilon, second=expected_result)
            self.assertEqual(first=result_large_epsilon, second=expected_result)

    def test_search_node_down_small_step_control_exceptions(self, quench_length=0.1235, step_control=SMALL_STEP_CONTROL):
        starting_node = [-10, 0, 1, 50000000]
        for sn in starting_node:
            with self.assertRaises(Exception):
                self.search_nodes_small_epsilon.search_node_down(right=sn, quench_length=quench_length, step_control=step_control)
                self.search_nodes_large_epsilon.search_node_down(right=sn, quench_length=quench_length, step_control=step_control)

    def test_search_node_down_large_step_control(self, quench_length=0.1234, step_control=LARGE_STEP_CONTROL):
        starting_node = [30, 90, 101]
        expected_result = 13
        for sn in starting_node:
            result_small_epsilon = self.search_nodes_small_epsilon.search_node_down(right=sn, quench_length=quench_length, step_control=step_control)
            result_large_epsilon = self.search_nodes_large_epsilon.search_node_down(right=sn, quench_length=quench_length, step_control=step_control)
            self.assertEqual(first=result_small_epsilon, second=expected_result)
            self.assertEqual(first=result_large_epsilon, second=expected_result)

    def test_search_node_down_large_step_control_exceptions(self, quench_length=0.1234, step_control=LARGE_STEP_CONTROL):
        starting_node = [-10, 0, 1, 50000000]
        for sn in starting_node:
            with self.assertRaises(Exception):
                self.search_nodes_small_epsilon.search_node_down(right=sn, quench_length=quench_length, step_control=step_control)
                self.search_nodes_large_epsilon.search_node_down(right=sn, quench_length=quench_length, step_control=step_control)

