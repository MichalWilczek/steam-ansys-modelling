
class Time:

    @staticmethod
    def linear_time_stepping(time_step, total_time):
        """
        Returns at time vector for simulation with constant time step
        :param time_step: time step as float
        :param total_time: total simulation time as float
        :return: list of time steps
        """
        vector = []
        i = time_step
        while i <= total_time:
            vector.append(i)
            i += time_step
        return vector
