
import os
import numpy as np


class Geometry:

    def __init__(self, file_directory):
        self.create_1d_imaginary_coil_length(file_position_directory=file_directory)

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
        self.files_in_directory = Geometry.search_files_names_in_directory(directory=file_position_directory)
        self.list_windings_nodes = Geometry.find_files_with_windings_nodes(list_files=self.files_in_directory)
        self.dict_winding_nodes = Geometry.load_files_with_windings_nodes(winding_files=self.list_windings_nodes, directory=file_position_directory)
        self.file_node_position = Geometry.load_file_with_winding_nodes_position(directory=file_position_directory, filename="Node_Position.txt")
        self.center_plane_position = Geometry.calculate_windings_lengths(position_array=self.file_node_position, winding_set=self.dict_winding_nodes)
        self.coil_data = Geometry.calculate_coil_length_data(windings_lengths=self.center_plane_position)
        self.coil_length_1d = Geometry.retrieve_1d_imaginary_coil(coil_data=self.coil_data)
        self.node_map_sorted = Geometry.translate_3d_domain_into_1d_cable(coil_data=self.coil_data, winding_set=self.dict_winding_nodes)

    # functions for objects creation inside of Class
    @staticmethod
    def search_files_names_in_directory(directory):
        list_files = os.listdir(directory)
        return list_files

    @staticmethod
    def find_files_with_windings_nodes(list_files):
        list_winding_files = []
        for files in list_files:
            if "Winding" in files:
                list_winding_files.append(files)
        return list_winding_files

    @staticmethod
    def load_files_with_windings_nodes(winding_files, directory):
        os.chdir(directory)
        winding_set = {}
        winding_number = 1
        for file in winding_files:
            winding = np.loadtxt(file)
            winding_set["winding"+str(winding_number)] = winding
            winding_number += 1
        return winding_set

    @staticmethod
    def load_file_with_winding_nodes_position(directory, filename):
        os.chdir(directory)
        position_array = np.loadtxt(filename)
        return position_array

    @staticmethod
    def calculate_average(list):
        return sum(list)/len(list)

    @staticmethod
    def calculate_windings_lengths(position_array, winding_set):
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

        length = 0.0
        imaginary_node = 1
        coil_data = None
        for key in windings_lengths:
            value = windings_lengths[key]
            for i in range(1, len(value)):
                temporary_list = [key, value[i-1, 0], imaginary_node, length]
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
    def unique_rows(a):
        a = np.ascontiguousarray(a, dtype=float)
        unique_a = np.unique(a.view([('', a.dtype)] * a.shape[1]))
        return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))

    @staticmethod
    def retrieve_1d_imaginary_coil(coil_data):
        coil_length_1d = coil_data[:, 2:4]
        coil_length_1d = Geometry.unique_rows(coil_length_1d)
        coil_length_1d_sorted = coil_length_1d[coil_length_1d[:, 0].argsort()]
        return coil_length_1d_sorted

    @staticmethod
    def translate_3d_domain_into_1d_cable(coil_data, winding_set):
        node_mapping = None
        for i in range(len(coil_data)):
            winding_number = coil_data[i, 0]
            winding_plane = coil_data[i, 1]
            winding_plane = np.asfarray(winding_plane, int)
            imaginary_node = coil_data[i, 2]
            winding_nodes = winding_set[winding_number]
            winding_plane_nodes = winding_nodes[:, int(winding_plane-1)]
            for j in range(len(winding_plane_nodes)):
                node_number = int(winding_plane_nodes[j])
                if node_number != 0:
                    temporary_list = [int(winding_plane_nodes[j]), int(imaginary_node)]
                    if i == 0 and j == 0:
                        node_mapping = np.array(temporary_list)
                    else:
                        node_mapping = np.vstack((node_mapping, temporary_list))
        node_mapping_sorted = node_mapping[node_mapping[:, 0].argsort()]
        return node_mapping_sorted

    # functions for step-by-step analysis
    def map_3d_max_temperature_into_1d_cable(self, temperature_profile):
        imaginary_1d_temperature = np.zeros((len(self.coil_length_1d), 2))
        for i in range(len(self.coil_length_1d)):
            node_list_for_imaginary_node = self.node_map_sorted[np.where(self.node_map_sorted[:, 1] == i+1)][:, 0]
            node_temperature_array = np.zeros((len(node_list_for_imaginary_node), 2))
            for j in range(len(node_list_for_imaginary_node)):
                node_temperature_array[j, 0] = node_list_for_imaginary_node[j]
                node_temperature_array[j, 1] = temperature_profile[np.where(temperature_profile[:, 0] == node_list_for_imaginary_node[j])][:, 1]
            imaginary_1d_temperature[i, 0] = self.node_map_sorted[i, 0]
            imaginary_1d_temperature[i, 1] = np.max(node_temperature_array[:, 1])
        return imaginary_1d_temperature

    def create_1d_imaginary_temperature_profile(self, directory, npoints=5736, filename="Temperature_Data.txt"):
        temperature_profile = Geometry.load_file(directory=directory, npoints=npoints, filename=filename)
        coil_temperature_1d = self.map_3d_max_temperature_into_1d_cable(temperature_profile=temperature_profile)
        return coil_temperature_1d

    def convert_imaginary_quench_front_up_into_real_nodes(self, previous_x_up_node=150, x_up_node=200):
        imaginary_1d_node_set = self.coil_data[:, 2]
        imaginary_1d_node_set = np.asfarray(imaginary_1d_node_set, float)
        quenched_coil_set = self.coil_data[(imaginary_1d_node_set[:] >= previous_x_up_node) & (imaginary_1d_node_set[:] <= x_up_node)]
        real_nodes_list = []
        for i in range(len(quenched_coil_set)):
            temporary_key = quenched_coil_set[i, 0]
            temporary_column = int(quenched_coil_set[i, 2]) - 1
            real_nodes_in_imaginary_node = self.dict_winding_nodes[temporary_key][:, temporary_column]
            for node in real_nodes_in_imaginary_node:
                if node != 0.0 or node != 0:
                    node = int(node)
                    real_nodes_list.append(node)
        real_nodes_list.sort()
        return real_nodes_list

    def convert_imaginary_quench_front_down_into_real_nodes(self, previous_x_down_node=50, x_down_node=20):
        imaginary_1d_node_set = self.coil_data[:, 2]
        imaginary_1d_node_set = np.asfarray(imaginary_1d_node_set, float)
        quenched_coil_set = self.coil_data[(imaginary_1d_node_set[:] >= x_down_node) & (imaginary_1d_node_set[:] <= previous_x_down_node)]
        real_nodes_list = []
        for i in range(len(quenched_coil_set)):
            temporary_key = quenched_coil_set[i, 0]
            temporary_column = int(quenched_coil_set[i, 2]) - 1
            real_nodes_in_imaginary_node = self.dict_winding_nodes[temporary_key][:, temporary_column]
            for node in real_nodes_in_imaginary_node:
                if node != 0.0 or node != 0:
                    node = int(node)
                    real_nodes_list.append(node)
        real_nodes_list.sort()
        return real_nodes_list

    @staticmethod
    def prepare_ansys_nodes_selection_list(real_nodes_list):
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
    def file_length(filename):
        """
        Reads number of files in file
        :param filename: filename to read as string
        """
        myfile = open(filename)
        return int(len(myfile.readlines()))

    @staticmethod
    def load_file(directory, npoints, filename):
        """
        Loads file as numpy array if its number of rows corresponds to number of nodes in geometry
        :param directory: analysis directory as string
        :param npoints: number of nodes in defined geometry
        :param filename: filename as string, 'Temperature_Data.txt' set as default
        """
        full_filename = "{}".format(filename)
        full_path = "{}\\{}".format(directory, full_filename)
        temp_distr = None
        exists = False
        while exists is False:
            exists = os.path.isfile(full_path)
            if exists and Geometry.file_length(full_filename) == npoints:
                os.chdir(directory)
                f = open(full_filename, 'r')
                temp_distr = np.loadtxt(f)
                f.close()
            else:
                exists = False
        return temp_distr

    def create_node_list_for_bf(self):
        node_list_for_bf = {}
        for key in self.dict_winding_nodes:
            value = self.dict_winding_nodes[key]
            first_plane_nodes = value[:, 0]
            last_plane_nodes = value[:, np.ma.size(value, axis=1)-1]
            node_list_for_bf[key] = [first_plane_nodes, last_plane_nodes]
        return node_list_for_bf

    def create_node_list_to_couple(self):
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

    def create_node_list_for_current(self):
        node_list_for_bf = self.create_node_list_for_bf()
        nodes_list_for_current = []
        for node in node_list_for_bf["winding1"][0]:
            if node != 0.0 and node != 0:
                nodes_list_for_current.append(int(node))
        return nodes_list_for_current

    def create_node_list_for_ground(self):
        node_list_for_bf = self.create_node_list_for_bf()
        nodes_list_for_ground = []
        for node in node_list_for_bf["winding"+str(len(node_list_for_bf)-1)][0]:
            if node != 0.0 and node != 0:
                nodes_list_for_ground.append(int(node))
        return nodes_list_for_ground


directory = "C:\\gitlab\\steam-ansys-modelling\\source\\APDL\\3D_Mapping_Input_Files"
geo_ansys = Geometry(file_directory=directory)

temperature_profile = geo_ansys.create_1d_imaginary_temperature_profile(directory=directory)
print(temperature_profile)

quenched_nodes_up = geo_ansys.convert_imaginary_quench_front_up_into_real_nodes()
print(quenched_nodes_up)

quenched_nodes_down = geo_ansys.convert_imaginary_quench_front_down_into_real_nodes()
print(quenched_nodes_down)

nodes_up_ansys_list = geo_ansys.prepare_ansys_nodes_selection_list(real_nodes_list=quenched_nodes_up)
nodes_down_ansys_list = geo_ansys.prepare_ansys_nodes_selection_list(real_nodes_list=quenched_nodes_down)

print(nodes_up_ansys_list)
print("_______________")
print(nodes_down_ansys_list)

list_nodes = geo_ansys.create_node_list_to_couple()
list_nodes_current = geo_ansys.create_node_list_for_current()
list_nodes_ground = geo_ansys.create_node_list_for_ground()
print("_______________")