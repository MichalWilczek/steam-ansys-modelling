import os
import numpy as np
path = 'C:\\1_MIT_modelling\ANSYS\\5_1D_multiple_quench_initiation\\approach_2\\APDL'


class Geometry:

    def __init__(self):
        self.division = 100

    def length_coil(self, path_file, filename):
        """
        returns an array with a length of the coil at each node starting from the 1st node
        """

        os.chdir(path_file)
        npoints = self.division + 1
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


class OptimSearch:

    def __init__(self, coil_length, epsilon):
        self.coil_length = coil_length
        self.epsilon = epsilon

    def search_init_node(self, position):
        """
        :param position: initial quench position, [m]
        :return: initial quench position, node number
        """
        # check if position is in the coil region
        if position > coil_length[len(coil_length) - 1, 1]:
            try:
                raise Exception("ERROR - search_init_node - init. quench position"
                                " is further than the coil length.")
            except Exception as inst:
                print(inst.args)
        elif position-1 < coil_length[0, 1]:
            try:
                raise Exception("ERROR - module algorithms - init. quench position"
                                " is below the start of the coil length.")
            except Exception as inst:
                print(inst.args)

        guess_epsilon = None
        num_guesses = 0
        left = 0
        right = len(self.coil_length)-1
        guess = round((left + right)/2)
        while abs(self.coil_length[guess, 1] - position) > self.epsilon:
            if guess == guess_epsilon:
                # compare which border is closer
                if abs(self.coil_length[right, 1] - position) < abs(self.coil_length[left, 1] - position):
                    guess = right
                else:
                    guess = left
                break
            if self.coil_length[guess, 1] < position:
                left = guess
                num_guesses += 1
            else:
                right = guess
                num_guesses += 1
            guess_epsilon = guess
            guess = round((left + right)/2)
        print("number of guesses = {}".format(num_guesses))

        # counting nodes in ansys starts from 1
        return guess + 1

    def search_node_up(self, left, quench_length, step_control=100):
        """
        :param left: previous quench position, node number
        :param quench_length: current quench position, [m]
        :param step_control: int (optional)
        :return: current quench position (up), node number
        """
        # check erroneous input data for quench length
        if quench_length > coil_length[len(coil_length)-1, 1]:
            try:
                raise Exception("ERROR - search_node_up - quench exceeds the coil length;"
                                " the results might be erroneous.")
            except Exception as inst:
                print(inst.args)
        elif quench_length < coil_length[left-1, 1] and left-1 > 0:
             try:
                raise Exception("ERROR - search_node_up - init. quench node is further"
                                " than the input quench length; the results might be erroneous.")
             except Exception as inst:
                 print(inst.args)
        # check erroneous input data for left boundary
        if left > len(coil_length):
            try:
                raise Exception("ERROR - search_node_up - left boundary node exceeds the number of nodes;"
                                " the results might be erroneous.")
            except Exception as inst:
                print(inst.args)
        if left-1 < coil_length[0, 1]:
            try:
                raise Exception("ERROR - search_node_up - left boundary node is lower than"
                                " the minimum node number; the results might be erroneous.")
            except Exception as inst:
                print(inst.args)

        num_guesses_jump = 0
        left = round(left-1)
        right = left
        while self.coil_length[right, 1] < quench_length:
            left = right
            right += step_control
            num_guesses_jump += 1
            if right > len(coil_length) - 1:
                right = len(coil_length) - 1
            if num_guesses_jump == 5:
                num_guesses_jump = 0
                step_control = 2*step_control
        guess = round((left+right)/2)
        guess_epsilon = None
        num_guesses_binary_search = 0
        while abs(self.coil_length[guess, 1] - quench_length) >= self.epsilon:
            # what if epsilon is to small for the mesh
            if guess == guess_epsilon:
                # compare which border is closer
                if abs(self.coil_length[right, 1] - quench_length) < abs(self.coil_length[left, 1] - quench_length):
                    guess = right
                else:
                    guess = left
                break
            # apply standard binary search
            if self.coil_length[guess, 1] < quench_length:
                left = guess
                num_guesses_binary_search += 1
            else:
                right = guess
                num_guesses_binary_search += 1
            guess_epsilon = guess
            guess = round((left + right) / 2)
        num_guesses = num_guesses_jump + num_guesses_binary_search
        print("number of guesses = {}".format(num_guesses))

        # counting nodes in ansys starts from 1
        return guess + 1

    def search_node_down(self, right, quench_length, step_control=100):
        """
        :param right: previous quench position, node number
        :param quench_length: current quench position, [m]
        :param step_control: int (optional)
        :return: current quench position (down), node number
        """
        # check erroneous input data for quench length
        if quench_length > coil_length[right - 1, 1]:
            try:
                raise Exception("ERROR - search_node_down - init. quench node is below the value"
                                " of the input quench length; the results might be erroneous.")
            except Exception as inst:
                print(inst.args)
        elif quench_length < coil_length[0, 1]:
             try:
                raise Exception("ERROR - search_node_down - quench is below the coil length;"
                                " the results might be erroneous.")
             except Exception as inst:
                 print(inst.args)

        # check erroneous input data for left boundary
        if right > len(coil_length):
            try:
                raise Exception("ERROR - search_node_up - right boundary node the number of nodes;"
                                " the results might be erroneous.")
            except Exception as inst:
                print(inst.args)
        if right-1 < coil_length[0, 1]:
            try:
                raise Exception("ERROR - search_node_up - right boundary node is lower than"
                                " the minimum node number; the results might be erroneous.")
            except Exception as inst:
                print(inst.args)

        num_guesses_jump = 0
        right = round(right-1)
        left = right
        while self.coil_length[left, 1] > quench_length:
            right = left
            left -= step_control
            num_guesses_jump += 1
            if left < self.coil_length[0, 1]:
                left = int(self.coil_length[0, 1])
            if num_guesses_jump == 5:
                num_guesses_jump = 0
                step_control = 2*step_control
        guess = round((left+right)/2)
        guess_epsilon = None
        num_guesses_binary_search = 0
        while abs(self.coil_length[guess, 1] - quench_length) >= self.epsilon:
            # what if epsilon is to small for the mesh
            if guess == guess_epsilon:
                # compare which border is closer
                if abs(self.coil_length[right, 1] - quench_length) < abs(self.coil_length[left, 1] - quench_length):
                    guess = right
                else:
                    guess = left
                break
            # apply standard binary search
            if self.coil_length[guess, 1] < quench_length:
                left = guess
                num_guesses_binary_search += 1
            else:
                right = guess
                num_guesses_binary_search += 1
            guess_epsilon = guess
            guess = round((left + right) / 2)
        num_guesses = num_guesses_jump + num_guesses_binary_search
        print("number of guesses = {}".format(num_guesses))

        # counting nodes in ansys starts from 1
        return guess + 1

geo = Geometry()
coil_length = geo.length_coil(path, 'File_Position_101nodes_1m.inp')


# test 1 : search_init_node()
# series 1:
# epsilon=0.001 (one order of magnitude lower than mesh quality)
# position = [0, 0.2001, 0.5001, 0.8001, 1]
# optim_test = OptimSearch(epsilon=0.001, coil_length=coil_length)
# node_init = optim_test.search_init_node(position=0)
# node_init = optim_test.search_init_node(position=0.2001)
# node_init = optim_test.search_init_node(position=0.5001)
# node_init = optim_test.search_init_node(position=0.8001)
# node_init = optim_test.search_init_node(position=1)
# print("Initial node = {}".format(node_init))

# series 2:
# epsilon=0.0000001 (much lower !!!)
# position = [0, 0.2001, 0.5001, 0.8001, 1] + [-1, 5]; 5: value further than coil length
# optim_test = OptimSearch(epsilon=0.0000001, coil_length=coil_length)
# node_init = optim_test.search_init_node(position=-1)
# node_init = optim_test.search_init_node(position=0)
# node_init = optim_test.search_init_node(position=0.2001)
# node_init = optim_test.search_init_node(position=0.5001)
# node_init = optim_test.search_init_node(position=0.8001)
# node_init = optim_test.search_init_node(position=1)
# node_init = optim_test.search_init_node(position=5)
# print("Initial node = {}".format(node_init))


# test 2 : search_node_up()
# series 1:
# optim_test = OptimSearch(epsilon=0.0000001, coil_length=coil_length)
# node_up = optim_test.search_node_up(left=-10, quench_length=0.5912, step_control=1)
# node_up = optim_test.search_node_up(left=0, quench_length=0.5912, step_control=1)
# node_up = optim_test.search_node_up(left=1, quench_length=0.5912, step_control=1)
# node_up = optim_test.search_node_up(left=30, quench_length=0.5912, step_control=1)
# node_up = optim_test.search_node_up(left=90, quench_length=0.5912, step_control=1)
# node_up = optim_test.search_node_up(left=101, quench_length=0.5912, step_control=1)

# series 2:
# node_up = optim_test.search_node_up(left=-10, quench_length=0.5912, step_control=200)
# node_up = optim_test.search_node_up(left=0, quench_length=0.5912, step_control=200)
# node_up = optim_test.search_node_up(left=1, quench_length=0.5912, step_control=200)
# node_up = optim_test.search_node_up(left=30, quench_length=0.5912, step_control=200)
# node_up = optim_test.search_node_up(left=90, quench_length=0.5912, step_control=200)
# node_up = optim_test.search_node_up(left=101, quench_length=0.5912, step_control=200)
# node_up = optim_test.search_node_up(left=301, quench_length=0.5912, step_control=200)
# print("Node up = {}".format(node_up))


# test 3 :search_node_down()
# series 1:
# optim_test = OptimSearch(epsilon=0.0000001, coil_length=coil_length)
# node_down = optim_test.search_node_down(right=-10, quench_length=0.1235, step_control=1)
# node_down = optim_test.search_node_down(right=0, quench_length=0.1235, step_control=1)
# node_down = optim_test.search_node_down(right=1, quench_length=0.1235, step_control=1)
# node_down = optim_test.search_node_down(right=30, quench_length=0.1235, step_control=1)
# node_down = optim_test.search_node_down(right=90, quench_length=0.1235, step_control=1)
# node_down = optim_test.search_node_down(right=101, quench_length=0.1235, step_control=1)
# node_down = optim_test.search_node_down(right=301, quench_length=0.1235, step_control=1)
#
# # series 2:
# node_down = optim_test.search_node_down(right=-10, quench_length=0.1235, step_control=200)
# node_down = optim_test.search_node_down(right=0, quench_length=0.1235, step_control=200)
# node_down = optim_test.search_node_down(right=1, quench_length=0.1235, step_control=200)
# node_down = optim_test.search_node_down(right=30, quench_length=0.1235, step_control=200)
# node_down = optim_test.search_node_down(right=90, quench_length=0.1235, step_control=200)
# node_down = optim_test.search_node_down(right=101, quench_length=0.1235, step_control=200)
# node_down = optim_test.search_node_down(right=301, quench_length=0.1235, step_control=200)
# print("Node down = {}".format(node_down))

