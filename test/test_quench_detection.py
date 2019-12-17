
import unittest
import numpy as np
import os
from source.physics.quench_velocity.quench_detection import QuenchDetect
from source.physics.quench_velocity.quench_front import QuenchFront
from source.geometry.geometry import Geometry

class VirtualGeometry(object):

    def __init__(self, division, filename, directory):
        self.coil_geometry = self.create_1d_coil_geometry(division, filename, directory)

    # methods for 1D analysis
    @staticmethod
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


class TestQuenchDetection(unittest.TestCase):

    NPOINTS = 101
    CWD = os.path.dirname(__file__)
    DIRECTORY = os.path.join(CWD, 'quench_detection')
    coil_data = None
    coil_geometry = None

    def setUp(self):
        self.class_geometry = VirtualGeometry(division=100, filename="File_Position.txt", directory=TestQuenchDetection.DIRECTORY)
        self.quench_detect = QuenchDetect(class_geometry=self.class_geometry, npoints=TestQuenchDetection.NPOINTS, input_data=None, testunit=True)

    def test_1_find_one_quench_zone(self):
        q_pos_vector = [QuenchFront(x_down=0.2, x_up=0.7, label=1, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True),
                        QuenchFront(x_down=4.2, x_up=4.7, label=2, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
            quench_fronts.front_up_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
        temperature_profile = Geometry.load_file(filename="1_find_one_quench_zone.txt", file_lines_length=TestQuenchDetection.NPOINTS, analysis_directory=TestQuenchDetection.DIRECTORY, npoints=TestQuenchDetection.NPOINTS)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile=temperature_profile, magnetic_field_map=None)
        expected_result = [[1.85, 3.05]]
        self.assertEqual(first=result, second=expected_result)

    def test_2_find_multiple_quench_zones(self):
        q_pos_vector = [QuenchFront(x_down=0.2, x_up=0.7, label=1, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True),
                        QuenchFront(x_down=4.2, x_up=4.7, label=2, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
            quench_fronts.front_up_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
        temperature_profile = Geometry.load_file(filename="2_find_multiple_quench_zones.txt", file_lines_length=TestQuenchDetection.NPOINTS, analysis_directory=TestQuenchDetection.DIRECTORY, npoints=TestQuenchDetection.NPOINTS)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile=temperature_profile, magnetic_field_map=None)
        expected_result = [[0.0, 0.0], [1.35, 1.4], [1.8, 1.8], [1.9, 1.9], [2.2, 2.7], [5.0, 5.0]]
        unittest.TestCase().assertEqual(first=result, second=expected_result)

    def test_3_find_multiple_quench_zones(self):
        q_pos_vector = [QuenchFront(x_down=0.3, x_up=0.6, label=1, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True),
                        QuenchFront(x_down=4.3, x_up=4.6, label=2, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
            quench_fronts.front_up_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
        temperature_profile = Geometry.load_file(filename="3_find_multiple_quench_zones.txt", file_lines_length=TestQuenchDetection.NPOINTS, analysis_directory=TestQuenchDetection.DIRECTORY, npoints=TestQuenchDetection.NPOINTS)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile=temperature_profile, magnetic_field_map=None)
        expected_result = [[0.0, 0.0], [1.35, 1.4], [1.8, 1.8], [1.9, 1.9], [2.2, 2.7], [5.0, 5.0]]
        unittest.TestCase().assertEqual(first=result, second=expected_result)

    def test_4_find_multiple_quench_zones(self):
        q_pos_vector = [QuenchFront(x_down=0.25, x_up=0.65, label=1, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True),
                        QuenchFront(x_down=4.25, x_up=4.65, label=2, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
            quench_fronts.front_up_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
        temperature_profile = Geometry.load_file(filename="4_find_multiple_quench_zones.txt", file_lines_length=TestQuenchDetection.NPOINTS, analysis_directory=TestQuenchDetection.DIRECTORY, npoints=TestQuenchDetection.NPOINTS)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile=temperature_profile, magnetic_field_map=None)
        expected_result = [[0.0, 0.0], [1.35, 1.4], [1.8, 1.8], [1.9, 1.9], [2.2, 2.7], [5.0, 5.0]]
        unittest.TestCase().assertEqual(first=result, second=expected_result)

    def test_5_find_multiple_quench_zones(self):
        q_pos_vector = [QuenchFront(x_down=0.25, x_up=0.65, label=1, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True),
                        QuenchFront(x_down=4.25, x_up=4.65, label=2, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
            quench_fronts.front_up_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
        temperature_profile = Geometry.load_file(filename="5_find_multiple_quench_zones.txt", file_lines_length=TestQuenchDetection.NPOINTS, analysis_directory=TestQuenchDetection.DIRECTORY, npoints=TestQuenchDetection.NPOINTS)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile=temperature_profile, magnetic_field_map=None)
        expected_result = [[0.0, 0.05], [1.35, 1.4], [1.8, 1.8], [1.9, 1.9], [2.2, 2.7], [4.95, 5.0]]
        unittest.TestCase().assertEqual(first=result, second=expected_result)

    def test_6_find_multiple_quench_zones(self):
        q_pos_vector = [QuenchFront(x_down=0.25, x_up=0.65, label=1, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True),
                        QuenchFront(x_down=4.2, x_up=4.65, label=3, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True),
                        QuenchFront(x_down=2.2, x_up=2.7, label=2, coil_geometry=self.coil_geometry,
                                    coil_data=self.coil_data, testunit=True)]
        for quench_fronts in q_pos_vector:
            quench_fronts.front_down_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
            quench_fronts.front_up_to_node(coil_length=self.class_geometry.coil_geometry, initial_search=True)
        temperature_profile = Geometry.load_file(filename="6_find_multiple_quench_zones.txt", file_lines_length=TestQuenchDetection.NPOINTS, analysis_directory=TestQuenchDetection.DIRECTORY, npoints=TestQuenchDetection.NPOINTS)
        result = self.quench_detect.detect_quench(input_quench_front_vector=q_pos_vector, temperature_profile=temperature_profile, magnetic_field_map=None)
        expected_result = [[0.0, 0.05], [1.35, 1.4], [1.8, 1.8], [1.9, 1.9], [4.95, 5.0]]
        unittest.TestCase().assertEqual(first=result, second=expected_result)
