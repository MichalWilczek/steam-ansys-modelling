
import unittest
from quench_velocity import QuenchFront
from quench_merge import QuenchMerge


def sort_quench_fronts(quench_fronts):
    quench_fronts_sorted = sorted(quench_fronts, key=lambda QuenchFront: QuenchFront.x_down)
    return quench_fronts_sorted


class TestQuenchMerge(unittest.TestCase):

    def test_set_overlapping_and_included(self):
        quench_fronts = [QuenchFront(10.0, 30.0, "1"), QuenchFront(70.0, 80.0, "2"), QuenchFront(40.0, 50.0, "3"), QuenchFront(20.0, 60.0, "4")]
        result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)

        expected_result = [QuenchFront(10.0, 60.0, "1_4_3"), QuenchFront(70.0, 80.0, "2")]
        expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)

        for res in range(len(result)):
            self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
            self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)

    def test_set_included_four_times(self):
        quench_fronts = [QuenchFront(10.0, 80.0, "1"), QuenchFront(30.0, 60.0, "2"), QuenchFront(20.0, 70.0, "3"), QuenchFront(40.0, 50.0, "4")]
        result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)

        expected_result = [QuenchFront(10.0, 80.0, "1_3_2_4")]
        expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)

        for res in range(len(result)):
            self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
            self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)

    def test_set_included_three_times_one_overlapping_over_all_sets(self):
        quench_fronts = [QuenchFront(10.0, 80.0, "1"), QuenchFront(30.0, 60.0, "2"), QuenchFront(20.0, 70.0, "3"),
                         QuenchFront(40.0, 50.0, "4")]
        result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)

        expected_result = [QuenchFront(10.0, 80.0, "2_3_1_4")]
        expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)

        for res in range(len(result)):
            self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
            self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)

    def test_set_included_four_times_each_doubled(self):
        quench_fronts = [QuenchFront(30.0, 50.0, "1"), QuenchFront(10.0, 70.0, "2"),
                QuenchFront(20.0, 60.0, "3"), QuenchFront(40.0, 80.0, "4"),
                QuenchFront(30.0, 50.0, "5"), QuenchFront(10.0, 70.0, "6"),
                QuenchFront(20.0, 60.0, "7"), QuenchFront(40.0, 80.0, "8")]
        result = QuenchMerge.quench_merge(quench_fronts=quench_fronts)

        expected_result = [QuenchFront(10.0, 80.0, "2_6_3_7_1_5_4_8")]
        expected_result_sorted = sort_quench_fronts(quench_fronts=expected_result)

        for res in range(len(result)):
            self.assertEqual(result[res].x_down, expected_result_sorted[res].x_down)
            self.assertEqual(result[res].x_up, expected_result_sorted[res].x_up)

