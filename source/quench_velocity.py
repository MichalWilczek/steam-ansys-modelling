
from source.nodes_search import SearchNodes


class QuenchFront:
    def __init__(self, x_down, x_up, label):
        """
        :param x_down: bottom position of quench front in [m]
        :param x_up: top position of quench front in [m]
        :param label: assigned number to QuenchFront as string
        """

        self.q_v = 0.5            # [m/s]
        self.x_down = x_down
        self.x_up = x_up
        self.x_centre = (x_up+x_down)/2.0
        self.label = label

        self.x_up_node = None
        self.x_down_node = None
        self.x_up_previous_node = None
        self.x_down_previous_node = None

    def calculate_quench_front_position(self, t_step, min_length, max_length):
        self.calculate_q_front_pos_down(t_step=t_step, min_length=min_length)
        self.calculate_q_front_pos_up(t_step=t_step, max_length=max_length)
        self.position_to_string()

    def convert_quench_front_to_nodes(self, coil_length):
        self.front_down_to_node(coil_length=coil_length)
        self.front_up_to_node(coil_length=coil_length)
        self.node_to_string()

    def position_to_string(self):
        return "{}: x_down = {}, x_up = {}".format(self.label, self.x_down, self.x_up)

    def node_to_string(self):
        return "{}: x_down_node = {}, x_up_node = {}".format(self.label, self.x_down_node, self.x_up_node)

    def calculate_q_front_pos_up(self, t_step, max_length):
        """
        :param t_step: time step as float
        :param max_length: max length of the coil as float
        :return: quench front position in meters in upper direction as float
        """
        if self.x_up == max_length:
            return self.x_up
        else:
            self.x_up = self.x_up + self.q_v * t_step
            if self.x_up > max_length:
                self.x_up = max_length
            return self.x_up

    def calculate_q_front_pos_down(self, t_step, min_length):
        """
        :param t_step: time step as float
        :param max_length: max length of the coil as float
        :return: quench front position in meters in lower direction as float
        """
        if self.x_down == min_length:
            return self.x_down
        else:
            self.x_down = self.x_down - self.q_v * t_step
            if self.x_down < min_length:
                self.x_down = min_length
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

    def merge(self, qf):
        """
        :param qf: QuenchFront object
        :return: New quench QuenchFront object merged from quench front and qf
        """
        x_down_new = min(self.x_down, qf.x_down)
        x_up_new = max(self.x_up, qf.x_up)
        return QuenchFront(x_down_new, x_up_new, str(self.label) + "_" + str(qf.label))

    def front_down_to_node(self, coil_length):
        """
        :return: lower quench front boundary as node number
        """
        if self.x_down_node is None:
            self.x_down_node = SearchNodes(coil_length=coil_length).search_init_node(position=self.x_down)
        else:
            self.x_down_node = SearchNodes(coil_length=coil_length).search_node_down(right=self.x_down_previous_node, quench_length=self.x_down)
        self.x_down_previous_node = self.x_down_node
        return self.x_down_node

    def front_up_to_node(self, coil_length):
        """
        :return: upper quench front boundary as node number
        """
        if self.x_up_node is None:
            # requires less computing power but x_down_node needs to be calculated first
            self.x_up_node = SearchNodes(coil_length=coil_length).search_node_up(left=self.x_down_node, quench_length=self.x_up)
            # optional method independent of x_down node:
            # self.x_up_node = SearchNodes().search_init_node(position=self.x_up)
        else:
            self.x_up_node = SearchNodes(coil_length=coil_length).search_node_up(left=self.x_up_previous_node, quench_length=self.x_up)
        self.x_up_previous_node = self.x_up_node
        return self.x_up_node
