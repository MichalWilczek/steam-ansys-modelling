import os
import numpy as np
path = 'C:\\1_MIT_modelling\ANSYS\\5_1D_multiple_quench_initiation\\approach_2\\APDL'


class Variables:

    def __init__(self):

        self.quench_init_pos = 0.3          # [m]
        self.quench_init_length = 0.01      # [m]
        self.total_time = 0.01  # [s]
        self.time_division = 9.0
        self.time_step = self.total_time / self.time_division

    def time_vector(self):
        vector = []

        i = self.time_step
        while i <= self.total_time:
            vector.append(i)
            i += self.time_step
        return vector

    def quench_pos_vector(self):
        vector = []
        subvector = [self.quench_init_pos, self.quench_init_length]
        vector.append(subvector)
        j = self.quench_init_pos
        for i in range(len(self.time_vector()) - 1):
            subvector = [self.quench_init_pos + j, self.quench_init_length]
            vector.append(subvector)
            j += 0.2
        return vector


class Geometry:

    def __init__(self):
        self.division = 3000

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


class QuenchFront:
    def __init__(self, x_q_pos, q_length, label):
        self.q_v = 10                         # [m/s]
        self.x_down = x_q_pos - q_length      # [m]
        self.x_up = x_q_pos + q_length        # [m]
        self.label = label

    def to_string(self):
        return "{}: x_down = {}, x_up = {}".format(self.label, self.x_down, self.x_up)

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
        return QuenchFront((x_up_new+x_down_new)/2, (x_up_new-x_down_new)/2, str(self.label)+"_"+str(qf.label))


geo = Geometry()
var = Variables()
coil_length = geo.length_coil(path, 'File_Position.inp')
min_coil_length = coil_length[0, 1]
max_coil_length = coil_length[len(coil_length)-1, 1]

time = var.time_vector()                    # user's time stepping vector
q_pos_vector = var.quench_pos_vector()      # temporary quench position vector before T verification is created
quench_fronts = []

for i in range(len(time)):

    print("iteration number: {} \n ____".format(i))
    t = time[i]
    # left separate for ansys commands
    if i == 0:
        quench_fronts.append(QuenchFront(x_q_pos=q_pos_vector[i][0], q_length=q_pos_vector[i][1], label=i))
        quench_fronts[0].calculate_q_front_pos_up(t, max_coil_length)
        quench_fronts[0].calculate_q_front_pos_down(t, min_coil_length)

    else:
        # find new quench locations
        q_pos_new = q_pos_vector[i]
        if not any(quench_front.is_position_in_front(q_pos_new[0]) for quench_front in quench_fronts):
            quench_fronts.append(QuenchFront(x_q_pos=q_pos_vector[i][0], q_length=q_pos_vector[i][1], label=i))

        # calculate quench propagation
        for qf in quench_fronts:
            qf.calculate_q_front_pos_up(t, max_coil_length)
            qf.calculate_q_front_pos_down(t, min_coil_length)

        # what if quench fronts meet
        # list sorted with increasing x_down
        quench_fronts_sorted = sorted(quench_fronts, key=lambda QuenchFront: QuenchFront.x_down)
        for qf in quench_fronts_sorted:
            print("label: {}, x_down = {}, x_up = {}".format(qf.label, qf.x_down, qf.x_up))

        # merging procedure
        quench_fronts_merged = []
        index = 0
        while index < len(quench_fronts_sorted):
            qfOuter = quench_fronts_sorted[index]
            qf_merged = None
            for j in range(index + 1, len(quench_fronts_sorted)):
                qfInner = quench_fronts_sorted[j]
                isOverlap = qfOuter.check_overlap(qfInner)
                isSetIncluded = qfOuter.check_set_included(qfInner)
                to_be__merged = isOverlap or isSetIncluded
                print("Checking overlap of: {} and {}. The result is {}".format(qfOuter.label, qfInner.label, isOverlap))
                if to_be__merged:
                    qf_merged = qfOuter.merge(qfInner)
                    qfOuter = qf_merged
                    index = j + 1
        
            if qf_merged is None:
                quench_fronts_merged.append(qfOuter)
                index = index + 1
            else:
                quench_fronts_merged.append(qf_merged)

        print("\nSituation after merging:")
        for qfm in quench_fronts_merged:
            print(qfm.to_string())
        print("______")

        # set new number of non-merged quench waves
        quench_fronts = quench_fronts_merged

