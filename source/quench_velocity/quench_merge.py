
class QuenchMerge(object):

    @staticmethod
    def quench_merge(quench_fronts, testunit=False):
        """
        :param quench_fronts: list of inherited QuenchFront objects
        """
        qf_sorted = QuenchMerge.sort_quench_fronts(quench_fronts=quench_fronts)
        QuenchMerge.print_quench_fronts(quench_fronts=qf_sorted)
        qf_merged = QuenchMerge.merge_quench_fronts(quench_fronts_sorted=qf_sorted, testunit=testunit)
        QuenchMerge.print_quench_fronts_after_merging(quench_fronts_merged=qf_merged)
        return qf_merged

    @staticmethod
    def sort_quench_fronts(quench_fronts):
        """
        :param quench_fronts: list of QuenchFront objects
        :return: list of QuenchFront objects sorted in increasing order with respect to x_down
        """
        quench_fronts_sorted = sorted(quench_fronts, key=lambda QuenchFront: QuenchFront.x_down)
        return quench_fronts_sorted

    @staticmethod
    def print_quench_fronts(quench_fronts):
        """
        Prints x_down, x_up and label of each object in list
        :param quench_fronts: list of QuenchFront objects
        """
        for qf in quench_fronts:
            print("{}: x_down = {}, x_up = {}".format(qf.label, qf.x_down, qf.x_up))

    @staticmethod
    def merge_quench_fronts(quench_fronts_sorted, testunit=False):
        """
        :param quench_fronts: list of sorted QuenchFront objects with respect to x_down
        :return: list of merged QuenchFront objects if previous fronts overlapped
        """
        quench_fronts_merged = []
        index = 0
        while index < len(quench_fronts_sorted):
            qf_outer = quench_fronts_sorted[index]
            qf_merged = None
            for j in range(index + 1, len(quench_fronts_sorted)):
                qf_inner = quench_fronts_sorted[j]
                is_overlap = qf_outer.check_overlap(qf_inner)
                is_set_included = qf_outer.check_set_included(qf_inner)
                to_be_merged = is_overlap or is_set_included
                print("Checking overlap of: {} and {}. The result is {}".format(
                      qf_outer.label, qf_inner.label, is_overlap))
                if to_be_merged:
                    qf_merged = qf_outer.merge(qf_inner, testunit)
                    qf_outer = qf_merged
                    index = j + 1

            if qf_merged is None:
                quench_fronts_merged.append(qf_outer)
                index = index + 1
            else:
                quench_fronts_merged.append(qf_merged)
        return quench_fronts_merged

    @staticmethod
    def print_quench_fronts_after_merging(quench_fronts_merged):
        """
        Prints x_down, x_up and label of each object in list after merging
        :param quench_fronts: list of new QuenchFront objects
        """
        for qfm in quench_fronts_merged:
            print("{}: x_down = {}, x_up = {}".format(qfm.label, qfm.x_down, qfm.x_up))
