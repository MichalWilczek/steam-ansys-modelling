
import os
import numpy as np


class Geometry:

    def __init__(self, file_directory):
        self.create_1d_imaginary_coil_length(file_position_directory=file_directory)
        self.create_node_dict_for_each_winding()

    # methods for 1D analysis
    @staticmethod
    def length_coil(division, filename, directory):
        """
        Returns array with length of coil at each node starting from the 1st node
        :param division: number of elements as integer
        :param filename: filename as string
        :param directory: analysis directory as string
        """
        os.chdir(directory)
        npoints = division + 1
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

    # methods for 2D/3D analyses
    def create_1d_imaginary_coil_length(self, file_position_directory):
        """
        Creates imaginary 1D coil length based on files: "Winding[number)" and "Node_Position"
        :param file_position_directory: full analysis directory as string
        """
        self.files_in_directory = Geometry.search_files_names_in_directory(directory=file_position_directory)
        self.list_windings_nodes = Geometry.find_files_with_windings_nodes(list_files=self.files_in_directory)
        self.dict_winding_nodes = Geometry.load_files_with_windings_nodes(winding_files=self.list_windings_nodes, directory=file_position_directory)
        self.file_node_position = Geometry.load_file_with_winding_nodes_position(directory=file_position_directory, filename="Node_Position.txt")
        self.center_plane_position = Geometry.calculate_windings_lengths(position_array=self.file_node_position, winding_set=self.dict_winding_nodes)
        self.coil_data = Geometry.calculate_coil_length_data(windings_lengths=self.center_plane_position)
        self.coil_length_1d = Geometry.retrieve_1d_imaginary_coil(coil_data=self.coil_data)
        self.node_map_sorted = Geometry.translate_3d_domain_into_1d_cable(coil_data=self.coil_data, winding_set=self.dict_winding_nodes)

    def create_node_dict_for_each_winding(self):
        """
        Creates dictionary with sorted list of node numbers belonging to each winding separately
        """
        self.winding_node_dict = {}
        for key in self.dict_winding_nodes:
            node_list = []
            value = self.dict_winding_nodes[key]
            for column in range(len(value[0, :])):
                plane_node_list = value[:, column]
                for node_number in plane_node_list:
                    if node_number != 0.0 or node_number != 0:
                        node_list.append(int(node_number))
            node_list.sort()
            self.winding_node_dict[key] = node_list

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
        winding_number = 1
        for file in winding_files:
            winding = np.loadtxt(file, dtype=int)
            winding_set["winding"+str(winding_number)] = winding
            winding_number += 1
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
    def calculate_average(list):
        """
        Returns the average of values given in the list
        :param list: list of float values
        :return: average of input values
        """
        return sum(list)/len(list)

    @staticmethod
    def calculate_windings_lengths(position_array, winding_set):
        """
        Calculates a centre of each node in Cartesian space
        :param position_array: numpy array with positions x,y,z of each node
        :param winding_set: dictionary which assigns nodes to each winding
        :return: dictionary which assigns a numpy array with mean x, y, z positions to each winding
        """
        winding_lengths = {}
        for key in winding_set:
            value = winding_set[key]
            winding_mean_pos_list = np.zeros((len(value[1, :]), 4))
            for i in range(len(value[1, :])):
                plane_node_list = value[:, i]
                n_pos_x_list = []
                n_pos_y_list = []
                n_pos_z_list = []
                for node_number in plane_node_list:
                    if node_number != 0.0 or node_number != 0:
                        node_pos_xyz = position_array[np.where(position_array[:, 0] == node_number)]
                        n_pos_x = node_pos_xyz[:, 1]
                        n_pos_y = node_pos_xyz[:, 2]
                        n_pos_z = node_pos_xyz[:, 3]
                        n_pos_x_list.append(n_pos_x)
                        n_pos_y_list.append(n_pos_y)
                        n_pos_z_list.append(n_pos_z)
                mean_pos_x = Geometry.calculate_average(n_pos_x_list)
                mean_pos_y = Geometry.calculate_average(n_pos_y_list)
                mean_pos_z = Geometry.calculate_average(n_pos_z_list)
                winding_mean_pos_list[i, 0] = i+1
                winding_mean_pos_list[i, 1] = mean_pos_x
                winding_mean_pos_list[i, 2] = mean_pos_y
                winding_mean_pos_list[i, 3] = mean_pos_z
            winding_lengths[key] = winding_mean_pos_list
        return winding_lengths

    @staticmethod
    def calculate_coil_length_data(windings_lengths):
        """
        Transforms x, y, z mean values of each node into 1D length of the entire coil
        :param windings_lengths: dictionary which assigns a numpy array with mean x, y, z positions to each winding
        :return: numpy array with 4 columns; 1-winding number as string, 2-plane number as integer,
                 3-ordered plane number along 1D coil length as integer, 4-imaginary 1D coil length as float
        """
        length = 0.0
        imaginary_node = 1
        coil_data = None
        for key in windings_lengths:
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
    def unique_rows(array):
        """
        Deletes repetitive rows with respect to one column
        :param array: numpy array
        :return: numpy float array without repetitions
        """
        array = np.ascontiguousarray(array, dtype=float)
        unique_a = np.unique(array.view([('', array.dtype)] * array.shape[1]))
        return unique_a.view(array.dtype).reshape((unique_a.shape[0], array.shape[1]))

    @staticmethod
    def retrieve_1d_imaginary_coil(coil_data):
        """
        Retrieves two last columns from coil_data numpy array
        :param coil_data: 4-column numpy array
        :return: Two-column numpy array without repetitions of its rows;
                 1-ordered plane number along 1D coil length as float, 2-imaginary 1D coil length as float
        """
        coil_length_1d = coil_data[:, 2:4]
        coil_length_1d = Geometry.unique_rows(coil_length_1d)
        coil_length_1d_sorted = coil_length_1d[coil_length_1d[:, 0].argsort()]
        return coil_length_1d_sorted

    def load_temperature_and_map_onto_1d_cable(self, directory, npoints, filename="Temperature_Data.txt"):
        """
        Loads temperature file with real nodes and maps it onto 1D cable length
        :param directory: full analysis directory as string
        :param npoints: number of nodes as integer in meshed ANSYS geometry
        :param filename: filename as string with temperature profile
        :returns: 2-column numpy array; 1-imaginary node number as float, 2-node temperature as float
        """
        temperature_profile = Geometry.load_file(analysis_directory=directory, npoints=npoints, filename=filename, file_lines_length=npoints)
        coil_temperature_1d = self.map_3d_max_temperature_into_1d_cable(temperature_profile=temperature_profile)
        return coil_temperature_1d

    @staticmethod
    def translate_3d_domain_into_1d_cable(coil_data, winding_set):
        """
        Creates numpy array which assigns each real node number to imaginary node number
        :param coil_data: 4-column numpy array; 1-winding number as string, 2-plane number as integer,
                          3-ordered plane number along 1D coil length as integer, 4-imaginary 1D coil length as float
        :param winding_set: dictionary which assigns nodes to each winding
        :return: 2-column numpy array sorted with respect to imaginary node numbers; 1-imaginary node numbers,
                 2-real node numbers
        """
        node_mapping = None
        for i in range(len(coil_data)):
            winding_number = coil_data[i, 0]
            winding_plane = int(float(coil_data[i, 1]))
            imaginary_node = int(float(coil_data[i, 2]))
            winding_nodes = winding_set[winding_number]
            winding_plane_nodes = winding_nodes[:, winding_plane-1]
            for j in range(len(winding_plane_nodes)):
                node_number = winding_plane_nodes[j]
                if node_number != 0:
                    temporary_list = [imaginary_node, winding_plane_nodes[j]]
                    if i == 0 and j == 0:
                        node_mapping = np.array(temporary_list)
                    else:
                        node_mapping = np.vstack((node_mapping, temporary_list))
        node_mapping_sorted = node_mapping[node_mapping[:, 0].argsort()]
        return node_mapping_sorted

    # functions for step-by-step analysis
    def map_3d_max_temperature_into_1d_cable(self, temperature_profile):
        """
        Finds maximum temperature at each plane of each winding and maps it onto 1D coil length
        :param temperature_profile: 2-column numpy array; 1-real node number as float, 2-real node temperature as float
        :return: 2-column numpy array; 1-imaginary node number as float, 2-node temperature as float
        """
        imaginary_1d_temperature = np.zeros((len(self.coil_length_1d), 2))
        for i in range(len(self.coil_length_1d)):
            node_list_for_imaginary_node = self.node_map_sorted[np.where(self.node_map_sorted[:, 0] == i+1)][:, 1]
            node_temperature_array = np.zeros((len(node_list_for_imaginary_node), 2))
            for j in range(len(node_list_for_imaginary_node)):
                node_temperature_array[j, 0] = node_list_for_imaginary_node[j]
                node_temperature_array[j, 1] = temperature_profile[np.where(temperature_profile[:, 0] == node_list_for_imaginary_node[j])][:, 1]
            imaginary_1d_temperature[i, 0] = self.node_map_sorted[i, 0]
            imaginary_1d_temperature[i, 1] = np.max(node_temperature_array[:, 1])
        return imaginary_1d_temperature

    def convert_imaginary_nodes_set_into_real_nodes(self, x_down_node, x_up_node):
        """
        Returns list with real quenched nodes
        :param x_down_node: quench down front node from imaginary set as integer
        :param x_up_node: quench up front node from imaginary set as integer
        :return: list of quenched real nodes
        """
        imaginary_1d_node_set = self.coil_data[:, 2]
        imaginary_1d_node_set = np.asfarray(imaginary_1d_node_set, float)
        quenched_coil_set = self.coil_data[(imaginary_1d_node_set[:] >= x_down_node) & (imaginary_1d_node_set[:] <= x_up_node)]
        real_nodes_list = []
        for i in range(len(quenched_coil_set)):
            temporary_key = quenched_coil_set[i, 0]
            temporary_column = int(float(quenched_coil_set[i, 1])) - 1
            real_nodes_in_imaginary_node = self.dict_winding_nodes[temporary_key][:, temporary_column]
            for node in real_nodes_in_imaginary_node:
                if node != 0.0 or node != 0:
                    node = int(node)
                    real_nodes_list.append(node)
        real_nodes_list.sort()
        return real_nodes_list

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
            while node_index_up < len(real_nodes_list)-1 and real_nodes_list[node_index_up+1]-real_nodes_list[node_index_up] == 1:
                node_index_up += 1
            nodes_selection_list.append([real_nodes_list[node_index_down], real_nodes_list[node_index_up]])
            node_index_down = node_index_up + 1
            node_index_up += 1
        return nodes_selection_list

    @staticmethod
    def file_length(filename, analysis_directory):
        """
        :param filename: filename with extension as string
        :param analysis_directory: string
        :return: number of rows in a file as integer
        """
        os.chdir(analysis_directory)
        with open(filename) as myfile:
            return int(len(myfile.readlines()))

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

    @staticmethod
    def load_parameter(directory, filename):
        """
        Returns the 1st row of txt file
        :param directory: full analysis directory as string
        :param filename: filename as string
        :return: parameter as float
        """
        full_filename = "{}".format(filename)
        full_path = "{}\\{}".format(directory, full_filename)
        text_file = open(full_path, "r")
        list1 = text_file.readlines()
        final_list = []
        for item in list1:
            item = float(item)
            final_list.append(item)
        return final_list[0]

    def create_node_list_for_bf(self):
        node_list_for_bf = {}
        for key in self.dict_winding_nodes:
            value = self.dict_winding_nodes[key]
            first_plane_nodes = value[:, 0]
            last_plane_nodes = value[:, np.ma.size(value, axis=1)-1]
            node_list_for_bf[key] = [first_plane_nodes, last_plane_nodes]
        return node_list_for_bf

    def create_node_list_to_couple_windings(self):
        node_list_for_bf = self.create_node_list_for_bf()
        coupling_node_list = []
        for i in range(len(node_list_for_bf)-1):
            one_coupling_node_list = []
            first_plane_nodes = node_list_for_bf["winding"+str(i+1)][1]
            second_plane_nodes = node_list_for_bf["winding"+str(i+2)][0]
            for node in first_plane_nodes:
                if node != 0.0 and node != 0:
                    one_coupling_node_list.append(int(node))
            for node in second_plane_nodes:
                if node != 0.0 and node != 0:
                    one_coupling_node_list.append(int(node))
            one_coupling_node_list.sort()
            coupling_node_list.append(one_coupling_node_list)
        return coupling_node_list

    def create_node_list_to_couple_interfaces(self):
        node_list_for_bf = self.create_node_list_for_bf()
        node_list_to_unselect = []
        for i in range(len(node_list_for_bf)):
            for node in node_list_for_bf["winding"+str(i+1)][0]:
                if node != 0.0 and node != 0:
                    node_list_to_unselect.append(int(node))
            for node in node_list_for_bf["winding"+str(i+1)][1]:
                if node != 0.0 and node != 0:
                    node_list_to_unselect.append(int(node))
        node_list_to_unselect.sort()
        return node_list_to_unselect

    def create_node_list_for_current(self):
        node_list_current = []
        for key in self.winding_node_dict:
            value = self.winding_node_dict[key]
            for index in range(len(value)):
                node_number = value[index]
                node_list_current.append(node_number)
        node_list_current.sort()
        return node_list_current

    def create_node_list_for_ground(self):
        node_list_for_bf = self.create_node_list_for_bf()
        nodes_list_for_ground = []
        for node in node_list_for_bf["winding"+str(len(node_list_for_bf))][1]:
            if node != 0.0 and node != 0:
                nodes_list_for_ground.append(int(node))
        return nodes_list_for_ground


# directory = "C:\\gitlab\\steam-ansys-modelling\\source\\APDL\\3D_Mapping_Input_Files"
# geo_ansys = Geometry(file_directory=directory)
#
# temperature_profile = geo_ansys.load_temperature_and_map_onto_1d_cable(npoints=5736, directory=directory)
# print(temperature_profile)
#
# list_real_nodes = geo_ansys.convert_imaginary_node_set_into_real_nodes(x_down_node=99, x_up_node=105)
# print(list_real_nodes)
