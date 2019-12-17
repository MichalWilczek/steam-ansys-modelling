
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

    # @staticmethod
    # def search_node_up(left, quench_length, coil_length, epsilon=0.000001, step_control=100):
    #     """
    #     Uses jump and binary searches to find upper node number of propagating quench front
    #     :param left: previous quench position, node number
    #     :param quench_length: current quench position in [m]
    #     :param coil_length: coil length numpy array; 1st column - node number, 2nd column position in [m]
    #     :param epsilon: searching error as float (optional)
    #     :param step_control: int (optional)
    #     :return: current quench position (up), node number
    #     """
    #     # check erroneous input data for quench length
    #     if quench_length > coil_length[len(coil_length)-1, 1]:
    #         raise Exception("ERROR - search_node_up - quench exceeds the coil length;"
    #                         " the results might be erroneous.")
    #     elif quench_length < coil_length[left-1, 1] and left-1 > 0:
    #         raise Exception("ERROR - search_node_up - init. quench node is further"
    #                         " than the input quench length; the results might be erroneous.")
    #     # check erroneous input data for left boundary
    #     if left > len(coil_length):
    #         raise Exception("ERROR - search_node_up - left boundary node exceeds the number of nodes;"
    #                         " the results might be erroneous.")
    #     if left-1 < coil_length[0, 1]:
    #         raise Exception("ERROR - search_node_up - left boundary node is lower than"
    #                         " the minimum node number; the results might be erroneous.")
    #     num_guesses_jump = 0
    #     left = round(left-1)
    #     right = left
    #     while coil_length[right, 1] < quench_length:
    #         left = right
    #         right += step_control
    #         num_guesses_jump += 1
    #         if right > len(coil_length) - 1:
    #             right = len(coil_length) - 1
    #         if num_guesses_jump == 5:
    #             num_guesses_jump = 0
    #             step_control = 2*step_control
    #     guess = round((left+right)/2)
    #     guess_epsilon = None
    #     while abs(coil_length[guess, 1] - quench_length) >= epsilon:
    #         # what if epsilon is to small for the mesh
    #         if guess == guess_epsilon:
    #             # compare which border is closer
    #             if abs(coil_length[right, 1] - quench_length) < abs(coil_length[left, 1] - quench_length):
    #                 return right+1
    #             else:
    #                 return left+1
    #         # apply standard binary search
    #         if coil_length[guess, 1] < quench_length:
    #             left = guess
    #         else:
    #             right = guess
    #         guess_epsilon = guess
    #         guess = round((left + right) / 2)
    #
    #     # counting nodes in ansys_interface starts from 1
    #     return guess + 1
    #
    # @staticmethod
    # def search_node_down(right, quench_length, coil_length, epsilon=0.000001, step_control=100):
    #     """
    #     Uses jump and binary searches to find bottom node number of propagating quench front
    #     :param right: previous quench position, node number
    #     :param quench_length: current quench position in [m]
    #     :param coil_length: coil length numpy array; 1st column - node number, 2nd column position in [m]
    #     :param epsilon: searching error as float (optional)
    #     :param step_control: int (optional)
    #     :return: current quench position (down), node number
    #     """
    #     # check erroneous input data for quench length
    #     if quench_length > coil_length[right - 1, 1]:
    #         raise Exception("ERROR - search_node_down - init. quench node is below the value"
    #                         " of the input quench length; the results might be erroneous.")
    #     elif quench_length < coil_length[0, 1]:
    #         raise Exception("ERROR - search_node_down - quench is below the coil length;"
    #                         " the results might be erroneous.")
    #     # check erroneous input data for left boundary
    #     if right > len(coil_length):
    #         raise Exception("ERROR - search_node_up - right boundary node the number of nodes;"
    #                         " the results might be erroneous.")
    #     if right-1 < coil_length[0, 1]:
    #         raise Exception("ERROR - search_node_up - right boundary node is lower than"
    #                         " the minimum node number; the results might be erroneous.")
    #     num_guesses_jump = 0
    #     right = round(right-1)
    #     left = right
    #     while coil_length[left, 1] > quench_length:
    #         right = left
    #         left -= step_control
    #         num_guesses_jump += 1
    #         if left < coil_length[0, 1]:
    #             left = int(coil_length[0, 1])
    #         if num_guesses_jump == 5:
    #             num_guesses_jump = 0
    #             step_control = 2*step_control
    #     guess = round((left+right)/2)
    #     guess_epsilon = None
    #     while abs(coil_length[guess, 1] - quench_length) >= epsilon:
    #         # what if epsilon is to small for the mesh
    #         if guess == guess_epsilon:
    #             # compare which border is closer
    #             if abs(coil_length[right, 1] - quench_length) < abs(coil_length[left, 1] - quench_length):
    #                 return right+1
    #             else:
    #                 return left+1
    #         # apply standard binary search
    #         if coil_length[guess, 1] < quench_length:
    #             left = guess
    #         else:
    #             right = guess
    #         guess_epsilon = guess
    #         guess = round((left + right) / 2)
    #
    #     # counting nodes in ansys_interface starts from 1
    #     return guess + 1
