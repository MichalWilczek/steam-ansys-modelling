

class Variables:

    def __init__(self):

        # variables for ansys input command
        self.prep7 = '/prep7'
        self.solu = '/solu'
        self.post1 = '/post1'
        self.title = '/title,' + 'quench_analysis'
        self.error = '/nerr,' + str(999999999999)
        self.division = 25000       # 50 nodes/m
        self.npoints = self.division+1
        self.coil_length = 500        # [m]

        self.q_v = 10.0                     # [m/s]
        self.quench_init_pos = 25.0          # [m]
        self.quench_init_length = 0.05      # [m]
        self.total_time = 5.0               # [s]
        self.time_division = 1000.0
        self.time_step = self.total_time / self.time_division

        self.coil_geometry_name = "File_Position.inp"
        self.analysis_directory = "C:\\1_MIT_modelling\ANSYS\\5_1D_multiple_quench_initiation\\APDL"

        # variables for ansys boundary/initial conditions
        self.current = 100  # [A]
        self.T_initial = 1.9  # [K]
        self.T_quench = 8.8  # [K]
        self.T_peak = 20  # [K]

        self.init_x_up = self.quench_init_pos + self.quench_init_length
        self.init_x_down = self.quench_init_pos - self.quench_init_length

    def time_vector(self):
        vector = []

        i = self.time_step
        while i <= self.total_time:
            vector.append(i)
            i += self.time_step
        return vector

    def quench_pos_vector(self, delay=0.5):
        time_vector = self.time_vector()
        vector = []
        subvector = [self.init_x_down, self.init_x_up]
        vector.append(subvector)
        j = (self.init_x_down+self.init_x_up)/2.0 + 25.0
        for i in range(len(self.time_vector()) - 1):
            if round(time_vector[i], 7) - delay == 0:
                subvector = [self.init_x_down + j, self.init_x_up + j]
                j += 50       # [m]
                delay += 0.5  # [s]
            else:
                subvector = [0, 0]
            vector.append(subvector)
        print(vector)
        return vector