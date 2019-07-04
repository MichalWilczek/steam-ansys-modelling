
import unittest
import os
from source.quench_detection import QuenchDetect
from source.quench_velocity import QuenchFront
from source.geometry import Geometry


class TestQuenchDetection(unittest.TestCase):
    NPOINTS = 101
    CWD = os.path.dirname(__file__)
    DIRECTORY = os.path.join(CWD, 'quench_detection')

    def setUp(self):
        self.coil_geometry = Geometry.length_coil(division=100, filename="File_Position.txt",
                                             directory=TestQuenchDetection.DIRECTORY)
        self.quench_detect = QuenchDetect(coil_length=self.coil_geometry, directory=TestQuenchDetection.DIRECTORY, npoints=TestQuenchDetection.NPOINTS)

    def test_1_find_one_quench_zone(self):
        q_pos_vector = [QuenchFront(x_down=0.2, x_up=0.7, label=1), QuenchFront(x_down=4.2, x_up=4.7, label=2)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.coil_geometry)
            quench_fronts.front_up_to_node(coil_length=self.coil_geometry)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile_file="test_1_find_one_quench_zone.txt")
        expected_result = [[1.85, 3.05]]
        self.assertEqual(first=result, second=expected_result)

    def test_2_find_multiple_quench_zones(self):
        q_pos_vector = [QuenchFront(x_down=0.2, x_up=0.7, label=1), QuenchFront(x_down=4.2, x_up=4.7, label=2)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.coil_geometry)
            quench_fronts.front_up_to_node(coil_length=self.coil_geometry)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile_file="test_2_find_multiple_quench_zones.txt")
        expected_result = [[0.0, 0.0], [1.35, 1.4], [1.8, 1.8], [1.9, 1.9], [2.2, 2.7], [5.0, 5.0]]
        unittest.TestCase().assertEqual(first=result, second=expected_result)

    def test_3_find_multiple_quench_zones(self):
        q_pos_vector = [QuenchFront(x_down=0.3, x_up=0.6, label=1), QuenchFront(x_down=4.3, x_up=4.6, label=2)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.coil_geometry)
            quench_fronts.front_up_to_node(coil_length=self.coil_geometry)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile_file="test_3_find_multiple_quench_zones.txt")
        expected_result = [[0.0, 0.0], [1.35, 1.4], [1.8, 1.8], [1.9, 1.9], [2.2, 2.7], [5.0, 5.0]]
        unittest.TestCase().assertEqual(first=result, second=expected_result)

    def test_4_find_multiple_quench_zones(self):
        q_pos_vector = [QuenchFront(x_down=0.25, x_up=0.65, label=1), QuenchFront(x_down=4.25, x_up=4.65, label=2)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.coil_geometry)
            quench_fronts.front_up_to_node(coil_length=self.coil_geometry)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile_file="test_4_find_multiple_quench_zones.txt")
        expected_result = [[0.0, 0.0], [1.35, 1.4], [1.8, 1.8], [1.9, 1.9], [2.2, 2.7], [5.0, 5.0]]
        unittest.TestCase().assertEqual(first=result, second=expected_result)

    def test_5_find_multiple_quench_zones(self):
        q_pos_vector = [QuenchFront(x_down=0.25, x_up=0.65, label=1), QuenchFront(x_down=4.25, x_up=4.65, label=2)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.coil_geometry)
            quench_fronts.front_up_to_node(coil_length=self.coil_geometry)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile_file="test_5_find_multiple_quench_zones.txt")
        expected_result = [[0.0, 0.05], [1.35, 1.4], [1.8, 1.8], [1.9, 1.9], [2.2, 2.7], [4.95, 5.0]]
        unittest.TestCase().assertEqual(first=result, second=expected_result)

    def test_6_find_multiple_quench_zones(self):
        q_pos_vector = [QuenchFront(x_down=0.25, x_up=0.65, label=1), QuenchFront(x_down=4.2, x_up=4.65, label=3), QuenchFront(x_down=2.2, x_up=2.7, label=2)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.coil_geometry)
            quench_fronts.front_up_to_node(coil_length=self.coil_geometry)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile_file="test_6_find_multiple_quench_zones.txt")
        expected_result = [[0.0, 0.05], [1.35, 1.4], [1.8, 1.8], [1.9, 1.9], [4.95, 5.0]]
        unittest.TestCase().assertEqual(first=result, second=expected_result)
