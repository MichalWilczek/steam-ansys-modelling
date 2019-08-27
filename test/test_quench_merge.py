
import unittest
from source.quench_velocity_constant import QuenchFrontConst
from source.quench_velocity_numerical import QuenchFrontNum
from source.quench_merge import QuenchMerge


def sort_quench_fronts(quench_fronts):
    quench_fronts_sorted = sorted(quench_fronts, key=lambda QuenchFront: QuenchFront.x_down)
    return quench_fronts_sorted


class TestQuenchMerge(unittest.TestCase):

    coil_geometry = None
    coil_data = None

    def test_set_overlapping_and_included_QuenchFrontConst(self):

        QuenchFront = QuenchFrontConst
        quench_fronts = [QuenchFront(10.0, 30.0, "1", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(70.0, 80.0, "2", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(40.0, 50.0, "3", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(20.0, 60.0, "4", self.coil_geometry, self.coil_data, testunit=True)]
        result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)

        expected_result = [QuenchFront(10.0, 60.0, "1_4_3", self.coil_geometry, self.coil_data, testunit=True),
                           QuenchFront(70.0, 80.0, "2", self.coil_geometry, self.coil_data, testunit=True)]
        expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)

        for res in range(len(result)):
            self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
            self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)

    def test_set_included_four_times_QuenchFrontConst(self):
        QuenchFront = QuenchFrontConst
        quench_fronts = [QuenchFront(10.0, 80.0, "1", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(30.0, 60.0, "2", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(20.0, 70.0, "3", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(40.0, 50.0, "4", self.coil_geometry, self.coil_data, testunit=True)]
        result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)

        expected_result = [QuenchFront(10.0, 80.0, "1_3_2_4", self.coil_geometry, self.coil_data, testunit=True)]
        expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)

        for res in range(len(result)):
            self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
            self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)

    def test_set_included_three_times_one_overlapping_over_all_sets_QuenchFrontConst(self):
        QuenchFront = QuenchFrontConst
        quench_fronts = [QuenchFront(10.0, 80.0, "1", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(30.0, 60.0, "2", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(20.0, 70.0, "3", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(40.0, 50.0, "4", self.coil_geometry, self.coil_data, testunit=True)]
        result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)

        expected_result = [QuenchFront(10.0, 80.0, "2_3_1_4", self.coil_geometry, self.coil_data, testunit=True)]
        expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)

        for res in range(len(result)):
            self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
            self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)

    def test_set_included_four_times_each_doubled_QuenchFrontConst(self):
        QuenchFront = QuenchFrontConst
        quench_fronts = [QuenchFront(30.0, 50.0, "1", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(10.0, 70.0, "2", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(20.0, 60.0, "3", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(40.0, 80.0, "4", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(30.0, 50.0, "5", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(10.0, 70.0, "6", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(20.0, 60.0, "7", self.coil_geometry, self.coil_data, testunit=True),
                         QuenchFront(40.0, 80.0, "8", self.coil_geometry, self.coil_data, testunit=True)]
        result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)

        expected_result = [QuenchFront(10.0, 80.0, "2_6_3_7_1_5_4_8", self.coil_geometry, self.coil_data, testunit=True)]
        expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)

        for res in range(len(result)):
            self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
            self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)

    # def test_set_overlapping_and_included_QuenchFrontNum(self):
    #
    #     QuenchFront = QuenchFrontNum
    #     quench_fronts = [QuenchFront(10.0, 30.0, "1", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(70.0, 80.0, "2", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(40.0, 50.0, "3", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(20.0, 60.0, "4", self.coil_geometry, self.coil_data, testunit=True)]
    #     result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)
    #
    #     expected_result = [QuenchFront(10.0, 60.0, "1_4_3", self.coil_geometry, self.coil_data, testunit=True),
    #                        QuenchFront(70.0, 80.0, "2", self.coil_geometry, self.coil_data, testunit=True)]
    #     expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)
    #
    #     for res in range(len(result)):
    #         self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
    #         self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)
    #
    # def test_set_included_four_times_QuenchFrontNum(self):
    #     QuenchFront = QuenchFrontNum
    #     quench_fronts = [QuenchFront(10.0, 80.0, "1", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(30.0, 60.0, "2", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(20.0, 70.0, "3", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(40.0, 50.0, "4", self.coil_geometry, self.coil_data, testunit=True)]
    #     result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)
    #
    #     expected_result = [QuenchFront(10.0, 80.0, "1_3_2_4", self.coil_geometry, self.coil_data, testunit=True)]
    #     expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)
    #
    #     for res in range(len(result)):
    #         self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
    #         self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)
    #
    # def test_set_included_three_times_one_overlapping_over_all_sets_QuenchFrontNum(self):
    #     QuenchFront = QuenchFrontNum
    #     quench_fronts = [QuenchFront(10.0, 80.0, "1", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(30.0, 60.0, "2", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(20.0, 70.0, "3", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(40.0, 50.0, "4", self.coil_geometry, self.coil_data, testunit=True)]
    #     result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)
    #
    #     expected_result = [QuenchFront(10.0, 80.0, "2_3_1_4", self.coil_geometry, self.coil_data, testunit=True)]
    #     expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)
    #
    #     for res in range(len(result)):
    #         self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
    #         self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)
    #
    # def test_set_included_four_times_each_doubled_QuenchFrontNum(self):
    #     QuenchFront = QuenchFrontNum
    #     quench_fronts = [QuenchFront(30.0, 50.0, "1", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(10.0, 70.0, "2", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(20.0, 60.0, "3", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(40.0, 80.0, "4", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(30.0, 50.0, "5", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(10.0, 70.0, "6", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(20.0, 60.0, "7", self.coil_geometry, self.coil_data, testunit=True),
    #                      QuenchFront(40.0, 80.0, "8", self.coil_geometry, self.coil_data, testunit=True)]
    #     result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)
    #
    #     expected_result = [QuenchFront(10.0, 80.0, "2_6_3_7_1_5_4_8", self.coil_geometry, self.coil_data, testunit=True)]
    #     expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)
    #
    #     for res in range(len(result)):
    #         self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
    #         self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)

