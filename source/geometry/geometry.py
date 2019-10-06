
import os
import numpy as np

class Geometry(object):

    def __init__(self, input_data, analysis_directory):
        self.factory = input_data
        self.directory = analysis_directory

    @staticmethod
    def number_of_im_nodes_per_winding(dict_im_nodes):
        return len(dict_im_nodes["winding1"])

    @staticmethod
    def make_one_list_from_list_of_lists(list_of_lists):
        """
        Creates one single list out of lists of lists
        :param list_of_lists: list of lists
        :return: one list
        """
        flat_list = []
        for list in list_of_lists:
            for item in list:
                flat_list.append(item)
        return flat_list

    @staticmethod
    def remove_repetitive_values_from_list(mylist):
        """
        Removes repetitve values from list
        :param mylist: list
        :return: list without repetitions
        """
        return list(dict.fromkeys(mylist))

    @staticmethod
    def retrieve_quenched_winding_numbers_from_quench_fronts(coil_data, x_down_node, x_up_node):
        """
        Returns number of windings that containt the given quench front
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

    # functions for objects creation inside of Class
    @staticmethod
    def search_files_names_in_directory(directory):
        """
        :param directory: full analysis directory as string
        :return: list of file names as strings
        """
        list_files = os.listdir(directory)
        return list_files

    @staticmethod
    def find_files_with_windings_nodes(list_files):
        """
        :param list_files: list of file names as strings
        :return: list of files as strings with "Winding" in their names
        """
        list_winding_files = []
        for files in list_files:
            if "Winding" in files:
                list_winding_files.append(files)
        return list_winding_files

    @staticmethod
    def load_files_with_windings_nodes(winding_files, directory):
        """
        Assigns a node number matrix (n x m in which n-plane number and m-node numbers in each winding)to each winding
        :param winding_files: list of files with windings' nodes numbers as integers
        :param directory: full analysis directory as string
        :return: dictionary which assigns nodes to each winding
        """
        os.chdir(directory)
        winding_set = {}
        for file in winding_files:
            winding_text_chunk = file[8:]
            winding_number, extension = winding_text_chunk.split('.')
            winding = np.loadtxt(file, dtype=int)
            winding_set["winding"+winding_number] = winding
        return winding_set

    @staticmethod
    def load_file_with_winding_nodes_position(directory, filename):
        """
        Loads the files with x,y,z position of each node in Cartesian coordinate system
        :param directory: full analysis directory as string
        :param filename: filename with nodes positions as string
        :return: numpy array with 4 columns; 1-node number as float, 2-position x, 3-position y, 4- position z
        """
        os.chdir(directory)
        position_array = np.loadtxt(filename, dtype=float)
        return position_array

    @staticmethod
    def calculate_average(float_objects_in_list):
        """
        Returns the average of values given in the list
        :param float_objects_in_list: list of float values
        :return: average of input values
        """
        return sum(float_objects_in_list) / len(float_objects_in_list)

    @staticmethod
    def calculate_coil_length_data(windings_lengths, number_of_windings):
        """
        Transforms x, y, z mean values of each node into 1D length of the entire coil
        :param windings_lengths: dictionary which assigns a numpy array with mean x, y, z positions to each winding
        :return: numpy array with 4 columns; 1-winding number as string, 2-plane number as integer,
                 3-ordered plane number along 1D coil length as integer, 4-imaginary 1D coil length as float
        """
        length = 0.0
        imaginary_node = 1
        coil_data = None
        for i in range(1, number_of_windings+1):
            key = 'winding' + str(i)
            value = windings_lengths[key]
            for i in range(1, len(value)):
                temporary_list = [key, int(value[i-1, 0]), imaginary_node, length]
                imaginary_node += 1
                if i == 1 and key == "winding1":
                    coil_data = np.array(temporary_list)
                else:
                    coil_data = np.vstack((coil_data, temporary_list))
                length += ((value[i, 1] - value[i - 1, 1]) ** 2 + (value[i, 2] - value[i - 1, 2]) ** 2 + (
                            value[i, 3] - value[i - 1, 3]) ** 2) ** 0.5
                if i == len(value)-1:
                    temporary_list = [key, value[i, 0], imaginary_node, length]
                    coil_data = np.vstack((coil_data, temporary_list))
        return coil_data

    @staticmethod
    def create_dict_with_imaginary_nodes(windings_lengths, number_of_windings):
        """
        TO BE ADDED !!!
        :param windings_lengths: dictionary which assigns a numpy array with x, y, z positions to each winding
        :param number_of_windings: number of windings as integer
        :return:
        """
        imaginary_node = 1
        coil_data = {}
        for i in range(1, number_of_windings+1):
            key = 'winding' + str(i)
            value = windings_lengths[key]
            imaginary_node_list = []
            for i in range(1, len(value)):
                imaginary_node_list.append(imaginary_node)
                imaginary_node += 1
                if i == len(value) - 1:
                    imaginary_node_list.append(imaginary_node)
            coil_data[key] = imaginary_node_list
        return coil_data

    @staticmethod
    def unique_rows(array):
        """
        Deletes repetitive rows with respect to one column
        :param array: numpy array
        :return: numpy float array without repetitions
        """
        array = np.ascontiguousarray(array, dtype=float)
        unique_a = np.unique(array.view([('', array.dtype)] * array.shape[1]))
        return unique_a.view(array.dtype).reshape((unique_a.shape[0], array.shape[1]))

    def retrieve_1d_imaginary_coil(self, coil_data):
        """
        Retrieves two last columns from coil_data numpy array
        :param coil_data: 4-column numpy array
        :return: Two-column numpy array without repetitions of its rows;
                 1-ordered plane number along 1D coil length as float, 2-imaginary 1D coil length as float
        """
        coil_length_1d = coil_data[:, 2:4]
        coil_length_1d = Geometry.unique_rows(coil_length_1d)
        coil_length_1d_sorted = coil_length_1d[coil_length_1d[:, 0].argsort()]
        self.save_array(directory=self.directory, filename="Im_Coil_Length.txt", array=coil_length_1d_sorted)
        return coil_length_1d_sorted

    @staticmethod
    def load_1d_temperature(directory, npoints, filename="Temperature_Data.txt"):
        """
        Loads file with nodal temperature results
        :param directory: directory of the file as string
        :param npoints: number of nodes in geometry as integer
        :param filename: filename as string; default: "Temperature_Data.txt"
        """
        return Geometry.load_file(analysis_directory=directory, npoints=npoints, filename=filename, file_lines_length=npoints)

    @staticmethod
    def save_array(directory, filename, array):
        """
        Saves array as txt file
        :param directory: directory to save file as string
        :param filename: filename to be created as string
        :param array: array to be saved
        """
        array_filename = directory + "\\" + filename
        np.savetxt(array_filename, array)

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
    def load_file(filename, file_lines_length, analysis_directory, npoints):
        """
        Works if number of rows in the file corresponds to number of nodes in geometry
        :param filename: filename with extension as string
        :param file_lines_length: number of rows in the file as integer
        :param analysis_directory: string
        :param npoints: number of nodes in geometry as integer
        :return: temperature profile as numpy array
        """
        loaded_file = None
        os.chdir(analysis_directory)
        exists = False
        while exists is False:
            exists = os.path.isfile(filename)
            if exists and file_lines_length == npoints:
                loaded_file = np.loadtxt(filename)
            else:
                exists = False
        return loaded_file

    def load_parameter(self, filename):
        """
        Returns the 1st row of txt file
        :param directory: full analysis directory as string
        :param filename: filename as string
        :return: parameter as float
        """
        full_filename = "{}".format(filename)
        full_path = "{}\\{}".format(self.directory, full_filename)
        text_file = open(full_path, "r")
        list1 = text_file.readlines()
        final_list = []
        for item in list1:
            item = float(item)
            final_list.append(item)
        return final_list[0]
