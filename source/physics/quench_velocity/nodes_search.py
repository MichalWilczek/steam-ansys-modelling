
class SearchNodes(object):

    @staticmethod
    def search_init_node(position, coil_length, epsilon=0.000001):
        """
        Uses binary search to find initial quench node
        :param position: initial quench position in [m]
        :param coil_length: coil length numpy array; 1st column - node number, 2nd column position in [m]
        :param epsilon: searching error as float (optional)
        :return: initial quench position, node number
        """
        # check if position is in the coil region
        if position > coil_length[len(coil_length) - 1, 1]:
            raise Exception("ERROR - search_init_node - init. quench position"
                            " is further than the coil length.")
        elif position < coil_length[0, 1]:
            raise Exception("ERROR - search_init_node - init. quench position"
                            " is below the start of the coil length.")
        guess_epsilon = None
        left = 0
        right = len(coil_length)-1
        guess = round((left + right)/2)
        while abs(coil_length[guess, 1] - position) > epsilon:
            if guess == guess_epsilon:
                # compare which border is closer
                if abs(coil_length[right, 1] - position) < abs(coil_length[left, 1] - position):
                    return right+1
                else:
                    return left+1
            if coil_length[guess, 1] < position:
                left = guess
            else:
                right = guess
            guess_epsilon = guess
            guess = round((left + right)/2)

        # counting nodes in ansys_interface starts from 1
        return guess + 1

    @staticmethod
    def search_node_up(left, quench_length, coil_length, epsilon=0.000001, step_control=100):
        return SearchNodes.search_init_node(position=quench_length, coil_length=coil_length)

    @staticmethod
    def search_node_down(right, quench_length, coil_length, epsilon=0.000001, step_control=100):
        return SearchNodes.search_init_node(position=quench_length, coil_length=coil_length)
