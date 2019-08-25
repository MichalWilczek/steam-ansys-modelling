
from source.nodes_search import SearchNodes
import numpy as np


class QuenchFront(object):

    def __init__(self, x_down, x_up, label, coil_geometry, coil_data):
        """
        :param x_down: bottom position of quench front in [m]
        :param x_up: top position of quench front in [m]
        :param label: assigned number to QuenchFront as string
        """
        self.x_down = x_down
        self.x_up = x_up
        self.x_centre = (x_up+x_down)/2.0
        self.label = label
        self.coil_geometry = coil_geometry
        self.coil_data = coil_data
        self.x_down_node = self.front_down_to_node(self.coil_geometry, initial_search=True)
        self.x_up_node = self.front_up_to_node(self.coil_geometry, initial_search=True)
        self.x_up_previous_node = self.x_down_node
        self.x_down_previous_node = self.x_up_node
        self.front_down_winding_numbers = self.define_front_down_winding_number(self.coil_data)
        self.front_up_winding_numbers = self.define_front_up_winding_number(self.coil_data)

    def calculate_quench_front_position(self, q_length_down, q_length_up, min_length, max_length):
        """
        Calculates position of quench at each time step and prints the data
        :param t_step: time step as float
        :param min_length: max length of the coil as float
        :param max_length: max length of the coil as float
        """
        self.calculate_q_front_pos_down(q_length_down, min_coil_length=min_length)
        self.calculate_q_front_pos_up(q_length_up, max_coil_length=max_length)
        self.position_to_string()

    def convert_quench_front_to_nodes(self, coil_length):
        """
        Converts quench front position to nodes
        :param coil_length: imaginary 1D coil geometry
        """
        self.front_down_to_node(coil_length=coil_length)
        self.front_up_to_node(coil_length=coil_length)
        self.node_to_string()

    def find_front_winding_numbers(self, coil_data):
        self.define_front_down_winding_number(coil_data=coil_data)
        self.define_front_up_winding_number(coil_data=coil_data)
        self.winding_to_string()

    def position_to_string(self):
        return "quench front no {}: x_down = {}, x_up = {}".format(self.label, self.x_down, self.x_up)

    def node_to_string(self):
        return "quench front no {}: x_down_node = {}, x_up_node = {}".format(self.label, self.x_down_node, self.x_up_node)

    def winding_to_string(self):
        return "quench front no {}: x_down_node is in {}, x_up_node is in {}".format(
            self.label, self.front_down_winding_numbers, self.front_up_winding_numbers)

    def calculate_q_front_pos_up(self, q_length, max_coil_length):
        """
        :param t_step: time step as float
        :param max_length: max length of the coil as float
        :return: quench front position in meters in upper direction as float
        """
        if self.x_up == max_coil_length:
            return self.x_up
        else:
            self.x_up = self.x_up + q_length
            if self.x_up > max_coil_length:
                self.x_up = max_coil_length
            return self.x_up

    def calculate_q_front_pos_down(self, q_length, min_coil_length):
        """
        :param t_step: time step as float
        :param min_length: max length of the coil as float
        :return: quench front position in meters in lower direction as float
        """
        if self.x_down == min_coil_length:
            return self.x_down
        else:
            self.x_down = self.x_down - q_length
            if self.x_down < min_coil_length:
                self.x_down = min_coil_length
            return self.x_down

    def is_position_in_front(self, position):
        """
        :param position: position in meters as float
        :return: True if the position is in the quench front, False otherwise
        """
        return (position >= self.x_down) and (position <= self.x_up)

    def check_set_included(self, qf):
        """
        :param qf: QuenchFront object
        :return: True if QuenchFront object is included in the quench front, False otherwise
        """
        is_x_down_inside = (self.x_down <= qf.x_down) and (self.x_down <= qf.x_up)
        is_x_up_inside = (self.x_up >= qf.x_down) and (self.x_up >= qf.x_up)
        return is_x_down_inside and is_x_up_inside

    def check_overlap(self, qf):
        """
        :param qf: QuenchFront object
        :return: True if QuenchFront object overlaps with the quench front, False otherwise
        """
        is_x_down_inside = (self.x_down >= qf.x_down) and (self.x_down <= qf.x_up)
        is_x_up_inside = (self.x_up >= qf.x_down) and (self.x_up <= qf.x_up)
        return is_x_down_inside or is_x_up_inside

    def front_down_to_node(self, coil_length, initial_search=False):
        """
        Returns the down front node of imaginary 1D coil
        :param coil_length: Two-column numpy array without repetitions of its rows;
                 1-ordered plane number along 1D coil length as float, 2-imaginary 1D coil length as float
        :param initial_search: False (default) if the node was already searched in previous steps
        :return: lower quench front boundary as node number
        """
        if initial_search:
            self.x_down_node = SearchNodes.search_init_node(position=self.x_down, coil_length=coil_length)
        else:
            self.x_down_node = SearchNodes.search_node_down(right=self.x_down_previous_node, quench_length=self.x_down,
                                                            coil_length=coil_length)
        self.x_down_previous_node = self.x_down_node
        return self.x_down_node

    def front_up_to_node(self, coil_length, initial_search=False):
        """
        Returns the up front node of imaginary 1D coil
        :param coil_length: Two-column numpy array without repetitions of its rows;
                 1-ordered plane number along 1D coil length as float, 2-imaginary 1D coil length as float
        :param initial_search: False (default) if the node was already searched in previous steps
        :return: upper quench front boundary as node number
        """
        if initial_search:
            self.x_up_node = SearchNodes.search_init_node(position=self.x_up, coil_length=coil_length)
        else:
            self.x_up_node = SearchNodes.search_node_up(left=self.x_up_previous_node, quench_length=self.x_up,
                                                        coil_length=coil_length)
        self.x_up_previous_node = self.x_up_node
        return self.x_up_node

    def define_front_up_winding_number(self, coil_data):
        """
        Returns winding numbers which the front up node belongs to
        :param coil_data: numpy array with 4 columns; 1-winding number as string, 2-plane number as integer,
                 3-ordered plane number along 1D coil length as integer, 4-imaginary 1D coil length as float
        :return: list of winding numbers as string
        """
        self.front_up_winding_numbers = []
        imaginary_1d_node_set = coil_data[:, 2]
        imaginary_1d_node_set = np.asfarray(imaginary_1d_node_set, float)
        coil_data_front = coil_data[(imaginary_1d_node_set[:] == self.x_up_node)]
        for i in range(len(coil_data_front[:, 0])):
            self.front_up_winding_numbers.append(coil_data_front[i, 0])
        return self.front_up_winding_numbers

    def define_front_down_winding_number(self, coil_data):
        """
        Returns winding numbers which the front down node belongs to
        :param coil_data: numpy array with 4 columns; 1-winding number as string, 2-plane number as integer,
                 3-ordered plane number along 1D coil length as integer, 4-imaginary 1D coil length as float
        :return: list of winding numbers as string
        """
        self.front_down_winding_numbers = []
        imaginary_1d_node_set = coil_data[:, 2]
        imaginary_1d_node_set = np.asfarray(imaginary_1d_node_set, float)
        coil_data_front = coil_data[(imaginary_1d_node_set[:] == self.x_down_node)]
        for i in range(len(coil_data_front[:, 0])):
            self.front_down_winding_numbers.append(coil_data_front[i, 0])
        return self.front_down_winding_numbers
