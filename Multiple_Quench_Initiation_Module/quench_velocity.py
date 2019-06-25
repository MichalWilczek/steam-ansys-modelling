from variables import Variables
from algorithms import SearchNodes


class QuenchFront:
    def __init__(self, x_down, x_up, label):

        self.q_v = Variables().q_v            # [m/s]
        self.x_down = x_down
        self.x_up = x_up
        self.x_centre = (x_up+x_down)/2.0

        self.label = label

        self.x_up_node = None
        self.x_down_node = None
        self.x_up_previous_node = None
        self.x_down_previous_node = None

    def to_string(self):
        return "{}: x_down = {}, x_up = {}".format(self.label, self.x_down, self.x_up)

    def to_string_node(self):
        return "{}: x_down_node = {}, x_up_node = {}".format(self.label, self.x_down_node, self.x_up_node)

    def calculate_q_front_pos_up(self, t_step, max_length):
        if self.x_up == max_length:
            return self.x_up
        else:
            self.x_up = self.x_up + self.q_v * t_step
            if self.x_up > max_length:
                self.x_up = max_length
            return self.x_up

    def calculate_q_front_pos_down(self, t_step, min_length):
        if self.x_down == min_length:
            return self.x_down
        else:
            self.x_down = self.x_down - self.q_v * t_step
            if self.x_down < min_length:
                self.x_down = min_length
            return self.x_down

    def is_position_in_front(self, position):
        return (position >= self.x_down) and (position <= self.x_up)

    def check_set_included(self, qf):
        is_x_down_inside = (self.x_down <= qf.x_down) and (self.x_down <= qf.x_up)
        is_x_up_inside = (self.x_up >= qf.x_down) and (self.x_up >= qf.x_up)
        return is_x_down_inside and is_x_up_inside

    def check_overlap(self, qf):
        is_x_down_inside = (self.x_down >= qf.x_down) and (self.x_down <= qf.x_up)
        is_x_up_inside = (self.x_up >= qf.x_down) and (self.x_up <= qf.x_up)
        return is_x_down_inside or is_x_up_inside

    def merge(self, qf):
        x_down_new = min(self.x_down, qf.x_down)
        x_up_new = max(self.x_up, qf.x_up)
        return QuenchFront(x_down_new, x_up_new, str(self.label) + "_" + str(qf.label))

    def front_down_to_node(self):
        if self.x_down_node is None:
            self.x_down_node = SearchNodes().search_init_node(position=self.x_down)
        else:
            self.x_down_node = SearchNodes().search_node_down(right=self.x_down_previous_node, quench_length=self.x_down)
        self.x_down_previous_node = self.x_down_node
        return self.x_down_node

    def front_up_to_node(self):
        if self.x_up_node is None:
            # requires less computing power but x_down_node needs to be calculated first
            self.x_up_node = SearchNodes().search_node_up(left=self.x_down_node, quench_length=self.x_up)
            # optional method independent of x_down node:
            # self.x_up_node = SearchNodes().search_init_node(position=self.x_up)
        else:
            self.x_up_node = SearchNodes().search_node_up(left=self.x_up_previous_node, quench_length=self.x_up)
        self.x_up_previous_node = self.x_up_node
        return self.x_up_node