
import os
import numpy as np
from source.factory.general_functions import GeneralFunctions

class Geometry(GeneralFunctions):

    def __init__(self, factory):
        self.input_data = factory.input_data
        self.directory = factory.directory
        self.output_directory = factory.output_directory
        self.output_directory_geometry = GeneralFunctions.create_folder_in_directory(self.output_directory,
                                                                                     "geometry_output")

    @staticmethod
    def number_of_im_nodes_per_winding(dict_im_nodes):
        return len(dict_im_nodes["winding1"])

    @staticmethod
    def retrieve_quenched_winding_numbers_from_quench_fronts(coil_data, x_down_node, x_up_node):
        """
        Returns number of windings that contains the given quench front
        :param coil_data: 4-column numpy array; 1st column: winding number, 2nd column: real node number,
        3rd column: imaginary node number, 4th column: length at the given imaginary node number
        :param x_down_node: imaginary lower front of quench front as integer
        :param x_up_node: imaginary upper front of quench front as integer
        :return: list of integers indicating winding numbers
        """
        windings = []
        imaginary_1d_node_set = coil_data[:, 2]
        imaginary_1d_node_set = np.asfarray(imaginary_1d_node_set, float)
        quenched_coil_set = coil_data[(imaginary_1d_node_set[:] >= x_down_node) &
                                      (imaginary_1d_node_set[:] <= x_up_node)]
        windings.append(quenched_coil_set[0, 0])
        windings.append(quenched_coil_set[len(quenched_coil_set[:, 0])-1, 0])
        winding_numbers = []
        for name in windings:
            number = int(float(name[7:]))
            winding_numbers.append(number)
        quenched_winding_numbers = []
        if winding_numbers[1] - winding_numbers[0] >= 1:
            for i in range(winding_numbers[0], winding_numbers[1]+1):
                quenched_winding_numbers.append(i)
        else:
            quenched_winding_numbers.append(winding_numbers[0])
        return quenched_winding_numbers

    @staticmethod
    def retrieve_node_set_from_imaginary_node_number(coil_data, dict_planes_nodes, imaginary_node):
        """
        Returns a list of sorted real node numbers belonging to the imaginary node
        :param coil_data: 4-column numpy array; 1st column: winding number, 2nd column: real node number,
        3rd column: imaginary node number, 4th column: length at the given imaginary node number
        :param dict_planes_nodes: dictionary of dictionaries with windings as the first key and plane as the second
        :param imaginary_node: imaginary node number as string
        :return: list of real node numbers
        """
        imaginary_1d_node_set = coil_data[:, 2]
        imaginary_1d_node_set = np.asfarray(imaginary_1d_node_set, float)
        coil_set = coil_data[(imaginary_1d_node_set[:] == imaginary_node)]
        nodes_set = []
        for i in range(len(coil_set[:, 0])):
            winding_number = coil_set[i, 0]
            if GeneralFunctions.check_if_string_is_float(coil_set[i, 1]):
                number = str(int(float(coil_set[i, 1])))
                plane_number = "plane" + number
            else:
                plane_number = "plane" + str(coil_set[i, 1])
            nodes_set.append(dict_planes_nodes[winding_number][plane_number])
        nodes_set = GeneralFunctions.flatten_list(nodes_set)
        nodes_set.sort()
        return nodes_set

    @staticmethod
    def create_dict_with_nodes_in_planes_in_each_winding(dict_planes_nodes, dict_winding_nodes_insul):
        """
        Returns dictionary describing position of nodes in each plane
        :param dict_planes_nodes: dictionary with magnet nodes positioned at each plane
        :param dict_winding_nodes_insul: dictionary with magnet nodes belonging to each winding
        :return: dictionary of dictionaries with windings as the first key and plane as the second
        """
        dict_in_dict_temp = {}
        for key_nodes_insul in dict_winding_nodes_insul:
            winding_nodes_insul = dict_winding_nodes_insul[key_nodes_insul]
            dict_temp = {}
            for key_planes_nodes in dict_planes_nodes:
                planes_nodes = dict_planes_nodes[key_planes_nodes]
                if planes_nodes.ndim == 0:
                    nodes = [int(planes_nodes)]
                else:
                    nodes = list(set(winding_nodes_insul) & set(planes_nodes))
                dict_temp[key_planes_nodes] = nodes
            dict_in_dict_temp[key_nodes_insul] = dict_temp
        return dict_in_dict_temp

    def load_files_with_windings_nodes(self, winding_files, directory, key_word):
        """
        Assigns a node number matrix (n x m in which n-plane number and m-node numbers in each winding)to each winding
        :param winding_files: list of files with windings' nodes numbers as integers
        :param directory: full analysis output_directory as string
        :param key_word: word to be used as a key for dictionary (as string)
        :return: dictionary which assigns nodes to each winding
        """
        os.chdir(directory)
        winding_set = {}
        for file in winding_files:
            filename, extension = file.split('.')
            winding_number_list = []
            for letter in filename:
                if GeneralFunctions.check_if_string_is_float(letter):
                    winding_number_list.append(letter)

            winding_number = int("".join(winding_number_list))
            winding = np.loadtxt(file, dtype=int)
            winding_set[key_word+str(winding_number)] = winding
        return winding_set

    @staticmethod
    def load_file_with_winding_nodes_position(directory, filename):
        """
        Loads the files with x,y,z position of each node in Cartesian coordinate system
        :param directory: full analysis output_directory as string
        :param filename: filename with nodes positions as string
        :return: numpy array with 4 columns; 1-node number as float, 2-position x, 3-position y, 4- position z
        """
        os.chdir(directory)
        position_array = np.loadtxt(filename, dtype=float)
        return position_array

    @staticmethod
    def calculate_coil_length_data(windings_lengths, number_of_windings):
        """
        Transforms x, y, z mean values of each node into 1D length of the entire coil
        :param windings_lengths: dictionary which assigns a numpy array with mean x, y, z positions to each winding
        :param number_of_windings: number of windings in geometry as integer
        :return: numpy array with 4 columns; 1-winding number as string, 2-plane number as integer,
                 3-ordered plane number along 1D coil length as integer, 4-imaginary 1D coil length as float
        """
        length = 0.0
        imaginary_node = 1
        coil_data = None
        for i in range(1, number_of_windings+1):
            key = 'winding' + str(i)
            value = windings_lengths[key]

            for j in range(1, len(value)):
                temporary_list = [key, int(value[j-1, 0]), imaginary_node, length]
                imaginary_node += 1
                if j == 1 and key == "winding1":
                    coil_data = np.array(temporary_list)
                else:
                    coil_data = np.vstack((coil_data, temporary_list))
                length += ((value[j, 1] - value[j - 1, 1]) ** 2 + (value[j, 2] - value[j - 1, 2]) ** 2 + (
                            value[j, 3] - value[j - 1, 3]) ** 2) ** 0.5
                if j == len(value)-1:
                    temporary_list = [key, value[j, 0], imaginary_node, length]
                    coil_data = np.vstack((coil_data, temporary_list))
        return coil_data

    @staticmethod
    def create_dict_with_imaginary_nodes(windings_lengths, number_of_windings):
        """
        :param windings_lengths: dictionary which assigns a numpy array with x, y, z positions to each winding
        :param number_of_windings: number of windings as integer
        :return: 4-column numpy array; 1st column: winding number, 2nd column: real node number,
        3rd column: imaginary node number, 4th column: length at the given imaginary node number
        """
        imaginary_node = 1
        coil_data = {}
        for i in range(1, number_of_windings+1):
            key = 'winding' + str(i)
            value = windings_lengths[key]
            imaginary_node_list = []
            for j in range(1, len(value)):
                imaginary_node_list.append(imaginary_node)
                imaginary_node += 1
                if j == len(value) - 1:
                    imaginary_node_list.append(imaginary_node)
            coil_data[key] = imaginary_node_list
        return coil_data

    @staticmethod
    def delete_repetitive_rows(array):
        """
        Deletes repetitive rows with respect to one column
        :param array: numpy array
        :return: numpy float array without repetitions
        """
        array = np.ascontiguousarray(array, dtype=float)
        unique_a = np.unique(array.view([('', array.dtype)] * array.shape[1]))
        return unique_a.view(array.dtype).reshape((unique_a.shape[0], array.shape[1]))

    @staticmethod
    def retrieve_1d_imaginary_coil(directory, coil_data):
        """
        Retrieves two last columns from coil_data numpy array
        :param directory: .txt file directory as string
        :param coil_data: 4-column numpy array; 1st column: winding number, 2nd column: real node number,
        3rd column: imaginary node number, 4th column: length at the given imaginary node number
        :return: Two-column numpy array without repetitions of its rows;
                 1-ordered plane number along 1D coil length as float, 2-imaginary 1D coil length as float
        """
        coil_length_1d = coil_data[:, 2:4]
        coil_length_1d = Geometry.delete_repetitive_rows(coil_length_1d)
        coil_length_1d_sorted = coil_length_1d[coil_length_1d[:, 0].argsort()]
        GeneralFunctions.save_array(directory=directory, filename="Im_Coil_Length.txt", array=coil_length_1d_sorted)
        return coil_length_1d_sorted

    @staticmethod
    def load_1d_temperature(directory, npoints, filename="Temperature_Data.txt"):
        """
        Loads file with nodal temperature results
        :param directory: output_directory of the file as string
        :param npoints: number of nodes in geometry as integer
        :param filename: filename as string; default: "Temperature_Data.txt"
        """
        return GeneralFunctions.load_file(directory=directory, npoints=npoints, filename=filename)

    @staticmethod
    def prepare_ansys_nodes_selection_list(real_nodes_list):
        """
        Transforms list of quenched nodes into sublists defining lower and upper boundaries of number sequences
        :param real_nodes_list: list of quenched real nodes
        :returns: list of lists
        """
        nodes_selection_list = []
        node_index_down = 0
        node_index_up = 0
        while node_index_up < len(real_nodes_list):
            while node_index_up < len(real_nodes_list)-1 \
                    and real_nodes_list[node_index_up+1]-real_nodes_list[node_index_up] == 1:
                node_index_up += 1
            nodes_selection_list.append([real_nodes_list[node_index_down], real_nodes_list[node_index_up]])
            node_index_down = node_index_up + 1
            node_index_up += 1
        return nodes_selection_list

    @staticmethod
    def load_ansys_output_one_line_txt_file(directory, filename):
        """
        Returns the 1st row of txt file
        :param directory: full analysis output_directory as string
        :param filename: filename as string
        :return: parameter as float
        """
        path = os.path.join(directory, filename)
        text_file = open(path, "r")
        list1 = text_file.readlines()
        final_list = []
        for item in list1:
            item = float(item)
            final_list.append(item)
        return final_list[0]
