
import os
import numpy as np


class Geometry:

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
    @staticmethod
    def create_1d_imaginary_coil_length(file_position_directory):
        files_in_directory = Geometry.search_files_names_in_directory(directory=file_position_directory)
        list_windings_nodes = Geometry.find_files_with_windings_nodes(list_files=files_in_directory)
        dict_winding_nodes = Geometry.load_files_with_windings_nodes(winding_files=list_windings_nodes, directory=file_position_directory)
        file_node_position = Geometry.load_file_with_winding_nodes_position(directory=file_position_directory, filename="Node_Position.txt")
        center_plane_position = Geometry.calculate_windings_lengths(position_array=file_node_position, winding_set=dict_winding_nodes)
        coil_data = Geometry.calculate_coil_length_data(windings_lengths=center_plane_position)
        coil_length_1d = Geometry.retrieve_1d_imaginary_coil(coil_data=coil_data)
        return coil_length_1d

    @staticmethod
    def create_1d_imaginary_temperature_profile(directory, npoints=5736, filename="Temperature_Data.txt"):
        files_in_directory = Geometry.search_files_names_in_directory(directory=directory)
        list_windings_nodes = Geometry.find_files_with_windings_nodes(list_files=files_in_directory)
        dict_winding_nodes = Geometry.load_files_with_windings_nodes(winding_files=list_windings_nodes, directory=directory)
        file_node_position = Geometry.load_file_with_winding_nodes_position(directory=directory, filename="Node_Position.txt")
        center_plane_position = Geometry.calculate_windings_lengths(position_array=file_node_position, winding_set=dict_winding_nodes)
        coil_data = Geometry.calculate_coil_length_data(windings_lengths=center_plane_position)
        coil_length_1d = Geometry.retrieve_1d_imaginary_coil(coil_data=coil_data)
        node_map = Geometry.translate_3d_domain_into_1d_cable(coil_data=coil_data, winding_set=dict_winding_nodes)
        temperature_profile = Geometry.load_file(directory=directory, npoints=npoints, filename=filename)
        coil_temperature_1d = Geometry.map_3d_max_temperature_into_1d_cable(node_mapping=node_map, temperature_profile=temperature_profile, coil_1d=coil_length_1d)
        return coil_temperature_1d

    @staticmethod
    def convert_imaginary_quench_front_up_into_real_nodes(file_position_directory, previous_x_up_node=20, x_up_node=50):
        files_in_directory = Geometry.search_files_names_in_directory(directory=file_position_directory)
        list_windings_nodes = Geometry.find_files_with_windings_nodes(list_files=files_in_directory)
        dict_winding_nodes = Geometry.load_files_with_windings_nodes(winding_files=list_windings_nodes, directory=file_position_directory)
        file_node_position = Geometry.load_file_with_winding_nodes_position(directory=file_position_directory, filename="Node_Position.txt")
        center_plane_position = Geometry.calculate_windings_lengths(position_array=file_node_position, winding_set=dict_winding_nodes)
        coil_data = Geometry.calculate_coil_length_data(windings_lengths=center_plane_position)

        imaginary_1d_node_set = coil_data[:, 2]



        print(type(coil_data[1,0]))
        quenched_coil_set = coil_data[np.where(imaginary_1d_node_set[:] == previous_x_up_node)]
        # each_zone[np.where(each_zone[:, 1] >= critical_temperature)]

        print(np.where(coil_data[:, 2] == previous_x_up_node))
        quenched_coil_set = coil_data[np.where(coil_data[:, 2] == previous_x_up_node)]
        # quenched_coil_set = coil_data[np.where(coil_data[:, 2] >= previous_x_up_node and coil_data[:, 2]<=x_up_node)]
        quenched_nodes = []
        for i in range(len(quenched_coil_set)):
            real_nodes_in_imaginary_node = dict_winding_nodes[temporary_key][:, i]
            temporary_key = quenched_coil_set[i, 0]
            # for j in range(len(real_nodes_in_imaginary_node):







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
    def retrieve_1d_imaginary_coil(coil_data):
        coil_length_1d = coil_data[:, 2:4]
        coil_length_1d = Geometry.unique_rows(coil_length_1d)
        coil_length_1d_sorted = coil_length_1d[coil_length_1d[:, 0].argsort()]
        return coil_length_1d_sorted

    @staticmethod
    def unique_rows(a):
        a = np.ascontiguousarray(a, dtype=float)
        unique_a = np.unique(a.view([('', a.dtype)] * a.shape[1]))
        return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))

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

    @staticmethod
    def map_3d_max_temperature_into_1d_cable(node_mapping, temperature_profile, coil_1d):
        imaginary_1d_temperature = np.zeros((len(coil_1d), 2))
        for i in range(len(coil_1d)):
            node_list_for_imaginary_node = node_mapping[np.where(node_mapping[:, 1] == i+1)][:, 0]
            node_temperature_array = np.zeros((len(node_list_for_imaginary_node), 2))
            for j in range(len(node_list_for_imaginary_node)):
                node_temperature_array[j, 0] = node_list_for_imaginary_node[j]
                node_temperature_array[j, 1] = temperature_profile[np.where(temperature_profile[:, 0] == node_list_for_imaginary_node[j])][:, 1]
            imaginary_1d_temperature[i, 0] = node_mapping[i, 0]
            imaginary_1d_temperature[i, 1] = np.max(node_temperature_array[:, 1])
        return imaginary_1d_temperature


directory = "C:\\gitlab\\steam-ansys-modelling\\source\\APDL\\3D_Mapping_Input_Files"
coil_data = Geometry.create_1d_imaginary_coil_length(file_position_directory=directory)
print(coil_data)

temperature_profile = Geometry.create_1d_imaginary_temperature_profile(directory=directory)
print(temperature_profile)

quenched_nodes_up = Geometry.convert_imaginary_quench_front_up_into_real_nodes(file_position_directory=directory)
print(quenched_nodes_up)