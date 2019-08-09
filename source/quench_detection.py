
import numpy as np
from source.factory import AnalysisDirectory, AnalysisBuilder


class QuenchDetect:

    MAGNETIC_FIELD_STRENGTH = 2.88

    def __init__(self, coil_length, npoints, directory=None):
        """
        :param coil_length:
        :param directory: analysis_directory as string
        :param npoints: number of nodes in geometry as integer
        """
        self.coil_length = coil_length
        self.factory = AnalysisBuilder()
        self.npoints = npoints

        if directory is None:
            self.analysis_directory = AnalysisDirectory().get_directory(self.factory.get_dimensionality())
        else:
            self.analysis_directory = directory

    def detect_quench(self, input_quench_front_vector, temperature_profile, magnetic_field=MAGNETIC_FIELD_STRENGTH):
        """
        :param input_quench_front_vector: list of QuenchFront objects
        :param temperature_profile_file: file with nodal temperature as string
        :param magnetic_field: magnetic fields strength value as float
        :return: list of new quench fronts positions in meters
        """
        input_quench_front_vector_sorted = QuenchDetect.sort_input_quench_front_vector(input_quench_front_vector)
        critical_temperature = QuenchDetect.calculate_critical_temperature(magnetic_field=magnetic_field)
        temperature_profile_sliced = QuenchDetect.slice_temperature_profile(input_quench_front_vector=input_quench_front_vector_sorted, temperature_profile=temperature_profile)
        temp_profile_sliced_quench_detection = QuenchDetect.find_quenched_nodes(sliced_temperature_profile=temperature_profile_sliced, critical_temperature=critical_temperature)
        new_quenched_fronts_before_rejection = QuenchDetect.find_new_quench_fronts(quenched_nodes=temp_profile_sliced_quench_detection)
        new_quench_fronts_list = QuenchDetect.create_new_quench_fronts_list(input_quench_front_vector=input_quench_front_vector_sorted, new_quench_fronts=new_quenched_fronts_before_rejection)
        new_quench_fronts_list_without_repetitions = QuenchDetect.find_repetitive_fronts(new_quench_fronts_list)
        new_quench_fronts_sorted = QuenchDetect.define_final_new_quench_fronts(fronts_list=new_quench_fronts_list_without_repetitions, new_quench_fronts_nodes=new_quenched_fronts_before_rejection)
        quench_fronts_position = QuenchDetect.search_quench_length(coil_length=self.coil_length, new_quench_fronts_nodes=new_quench_fronts_sorted)
        return quench_fronts_position

    @staticmethod
    def sort_input_quench_front_vector(input_quench_front_vector):
        """
        :param input_quench_front_vector: list of QuenchFront objects
        :return: list of QuenchFront objects sorted from lowest x_down to highest x_down
        """
        return sorted(input_quench_front_vector, key=lambda QuenchFront: QuenchFront.x_down)

    @staticmethod
    def calculate_critical_temperature(magnetic_field=MAGNETIC_FIELD_STRENGTH):
        """
        :param magnetic_field: magnetic field strength as float
        :return: critical temperature as float
        """
        critical_temperature_0 = 9.2              # [K]
        critical_magnetic_field_0 = 14.5          # [T]
        critical_temperature = critical_temperature_0*(1.0-magnetic_field/critical_magnetic_field_0)**0.59
        return critical_temperature

    @staticmethod
    def slice_temperature_profile(input_quench_front_vector, temperature_profile):
        """
        :param input_quench_front_vector: list of QuenchFront objects
        :param temperature_profile: temperature profile as numpy array
        :return: list of non-quenched zones as numpy arrays
        """
        node_down_list = []
        for items in input_quench_front_vector:
            node_down_list.append(items.x_down_node)
        node_up_list = []
        for items in input_quench_front_vector:
            node_up_list.append(items.x_up_node)

        sliced_temperature_profile = []
        if len(input_quench_front_vector) != 0:
            for i in range(len(input_quench_front_vector) + 1):
                if i == 0:
                    sliced_temperature_profile.append(temperature_profile[0:(node_down_list[i]-1), :])
                elif i == len(input_quench_front_vector):
                    sliced_temperature_profile.append(temperature_profile[(node_up_list[i-1]):(len(temperature_profile)), :])
                else:
                    sliced_temperature_profile.append(temperature_profile[(node_up_list[i-1]):(node_down_list[i]-1), :])
            print("Number of zones to check for quench is: {}".format(len(sliced_temperature_profile)))
        else:
            sliced_temperature_profile.append(temperature_profile)
        return sliced_temperature_profile

    @staticmethod
    def find_quenched_nodes(sliced_temperature_profile, critical_temperature):
        """
        :param sliced_temperature_profile: list of non-quenched zones as numpy arrays
        :param critical_temperature: critical temperature as float
        :return: list quenched nodes as numpy arrays
        """
        quenched_nodes = []
        for each_zone in sliced_temperature_profile:
            temporary_quenched_nodes = each_zone[np.where(each_zone[:, 1] >= critical_temperature)]
            if len(temporary_quenched_nodes) != 0:
                quenched_nodes.append(temporary_quenched_nodes)
        return quenched_nodes

    @staticmethod
    def find_new_quench_fronts(quenched_nodes):
        """
        :param quenched_nodes: list quenched nodes as numpy arrays
        :return: list of lists in each of which there is lower and upper node of new quench fronts
        """
        new_quench_fronts = []
        for quenched_nodes_sliced_profiles in quenched_nodes:
            x_up_node = 0
            x_down_node = 0
            while x_up_node < len(quenched_nodes_sliced_profiles):
                while x_up_node < len(quenched_nodes_sliced_profiles)-1 and quenched_nodes_sliced_profiles[x_up_node+1][0] - quenched_nodes_sliced_profiles[x_up_node][0] == 1:
                        x_up_node += 1
                new_quench_fronts.append([int(quenched_nodes_sliced_profiles[x_down_node][0]),
                                          int(quenched_nodes_sliced_profiles[x_up_node][0])])
                x_down_node = x_up_node + 1
                x_up_node += 1
        return new_quench_fronts

    @staticmethod
    def create_new_quench_fronts_list(input_quench_front_vector, new_quench_fronts):
        """
        :param input_quench_front_vector: list of QuenchFront objects
        :param new_quench_fronts: list of lists in each of which there is lower and upper node of new quench fronts
        :return: list of indices of new quench fronts which are directly neighboring with existing quench fronts
        """
        initial_quench_fronts = []
        for items in input_quench_front_vector:
            initial_quench_fronts.append([items.x_down_node, items.x_up_node])
        fronts_to_delete = []
        for i in range(len(initial_quench_fronts)):
            for j in range(len(new_quench_fronts)):
                if abs(initial_quench_fronts[i][0] - new_quench_fronts[j][1]) == 1:
                    fronts_to_delete.append(j)
        for i in range(len(initial_quench_fronts)):
            for j in range(len(new_quench_fronts)):
                if abs(initial_quench_fronts[i][1] - new_quench_fronts[j][0]) == 1:
                    fronts_to_delete.append(j)
        return fronts_to_delete

    @staticmethod
    def find_repetitive_fronts(duplicate):
        """
        Removes repeating indices in the list of indices
        :param duplicate: list of indices of new quench fronts which are directly neighboring with existing quench fronts
        :return: list of indices of new quench fronts to delete without repetitions
        """
        final_list = []
        for num in duplicate:
            if num not in final_list:
                final_list.append(num)
        return final_list

    @staticmethod
    def define_final_new_quench_fronts(fronts_list, new_quench_fronts_nodes):
        """
        :param fronts_list: list of indices of new quench fronts to delete without repetitions
        :param new_quench_fronts_nodes: list of lists in each of which there is lower and upper node of new quench fronts
        :return: list of new quench fronts without the ones neighboring with the existing ones
        """
        fronts_list.sort()
        fronts_list.reverse()
        print("Number of quench fronts faster than current quench fronts: {}".format(len(fronts_list)))
        for i in range(len(fronts_list)):
            new_quench_fronts_nodes.remove(new_quench_fronts_nodes[fronts_list[i]])
        print("New quench fronts [nodes]: {}".format(new_quench_fronts_nodes))
        return new_quench_fronts_nodes

    @staticmethod
    def search_quench_length(coil_length, new_quench_fronts_nodes):
        """
        :param coil_length: length of coil for each node as numpy array
        :param new_quench_fronts_nodes: list of final new quench fronts
        :return: list of position of new quench fronts
        """
        new_quench_node_list = new_quench_fronts_nodes
        new_quench_length_list = []
        for sublist in new_quench_node_list:
            new_x_down = coil_length[sublist[0]-1][1]
            new_x_up = coil_length[sublist[1]-1][1]
            print("New quench zone; x_down= {}, x_up= {}".format(new_x_down, new_x_up))
            new_quench_length_list.append([new_x_down, new_x_up])
        return new_quench_length_list
