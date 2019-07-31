import numpy as np
from source.geometry import Geometry

class Geometry1D1D(Geometry):

    def __init__(self):
        Geometry.__init__(self)
        self.create_1d_coil_geometry()
        self.winding_node_dict = self.create_node_dict_for_each_winding()
        self.coil_geometry = self.coil_length_1d
        print("Geometry uploaded... \n________________")

    # methods for analysis 1D+1D
    def create_1d_coil_geometry(self):
        """
        Creates imaginary 1D coil length based on files: "Winding[number)" and "Node_Position"
        """
        files_in_directory = Geometry.search_files_names_in_directory(directory=self.directory)
        list_windings_nodes = Geometry.find_files_with_windings_nodes(list_files=files_in_directory)
        self.dict_winding_nodes = Geometry.load_files_with_windings_nodes(winding_files=list_windings_nodes, directory=self.directory)
        self.file_node_position = Geometry.load_file_with_winding_nodes_position(directory=self.directory, filename="Node_Position.txt")
        self.center_plane_position = self.calculate_windings_lengths(position_array=self.file_node_position, winding_set=self.dict_winding_nodes)
        self.coil_data = Geometry.calculate_coil_length_data(windings_lengths=self.center_plane_position, number_of_windings=self.factory.get_number_of_windings())
        self.coil_length_1d = Geometry.retrieve_1d_imaginary_coil(coil_data=self.coil_data)
        self.node_map_sorted = self.translate_domain_into_1d_cable(coil_data=self.coil_data, winding_set=self.dict_winding_nodes)

    def create_node_dict_for_each_winding(self):
        """
        Creates dictionary with sorted list of node numbers belonging to each winding separately
        """
        winding_node_dict = {}
        for key in self.dict_winding_nodes:
            node_list = []
            value = self.dict_winding_nodes[key]
            for i in range(len(value)):
                node_number = value[i]
                if node_number != 0.0 or node_number != 0:
                    node_list.append(int(node_number))
            node_list.sort()
            winding_node_dict[key] = node_list
        return winding_node_dict

    @staticmethod
    def calculate_windings_lengths(position_array, winding_set):
        """
        Calculates a centre of each node in Cartesian space
        :param position_array: numpy array with positions x,y,z of each node
        :param winding_set: dictionary which assigns nodes to each winding
        :return: dictionary which assigns a numpy array with x, y, z positions to each winding
        """
        winding_lengths = {}
        for key in winding_set:
            value = winding_set[key]
            winding_pos_list = np.zeros((len(value), 4))
            for i in range(len(value)):
                node_number = value[i]
                n_pos_x_list = []
                n_pos_y_list = []
                n_pos_z_list = []
                if node_number != 0.0 or node_number != 0:
                    node_pos_xyz = position_array[np.where(position_array[:, 0] == node_number)]
                    n_pos_x = node_pos_xyz[:, 1]
                    n_pos_y = node_pos_xyz[:, 2]
                    n_pos_z = node_pos_xyz[:, 3]
                    n_pos_x_list.append(n_pos_x)
                    n_pos_y_list.append(n_pos_y)
                    n_pos_z_list.append(n_pos_z)
                winding_pos_list[i, 0] = i + 1
                winding_pos_list[i, 1] = n_pos_x
                winding_pos_list[i, 2] = n_pos_y
                winding_pos_list[i, 3] = n_pos_z
            winding_lengths[key] = winding_pos_list
        return winding_lengths

    @staticmethod
    def translate_domain_into_1d_cable(coil_data, winding_set):
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

            # if i == 101:
            #     print("Hello")

            winding_number = coil_data[i, 0]
            winding_plane = int(float(coil_data[i, 1]))
            imaginary_node = int(float(coil_data[i, 2]))
            winding_nodes = winding_set[winding_number]
            node_number = winding_nodes[winding_plane-1]
            if node_number != 0:
                temporary_list = [imaginary_node, node_number]
                if i == 0:
                    node_mapping = np.array(temporary_list)
                else:
                    node_mapping = np.vstack((node_mapping, temporary_list))
        node_mapping_sorted = node_mapping[node_mapping[:, 0].argsort()]
        return node_mapping_sorted

    def create_node_list_for_bf(self):
        node_list_for_bf = {}
        for key in self.dict_winding_nodes:
            value = self.dict_winding_nodes[key]
            first_plane_nodes = value[0]
            last_plane_nodes = value[np.ma.size(value)-1]
            node_list_for_bf[key] = [first_plane_nodes, last_plane_nodes]
        return node_list_for_bf

    def create_node_list_to_couple_windings(self):
        node_list_for_bf = self.create_node_list_for_bf()
        coupling_node_list = []
        for i in range(len(node_list_for_bf)-1):
            one_coupling_node_list = []
            first_plane_node = node_list_for_bf["winding"+str(i+1)][1]
            second_plane_node = node_list_for_bf["winding"+str(i+2)][0]
            if first_plane_node != 0.0 and first_plane_node != 0:
                one_coupling_node_list.append(int(first_plane_node))
            if second_plane_node != 0.0 and second_plane_node != 0:
                one_coupling_node_list.append(int(second_plane_node))
            one_coupling_node_list.sort()
            coupling_node_list.append(one_coupling_node_list)
        return coupling_node_list

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
        node = node_list_for_bf["winding"+str(len(node_list_for_bf))][1]
        if node != 0.0 and node != 0:
            nodes_list_for_ground.append(int(node))
        return nodes_list_for_ground

    # functions for step-by-step analysis
    def map_temperature_into_1d_cable(self, temperature_profile):
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
                node_temperature_array[j, 1] = temperature_profile[np.where(temperature_profile[:, 0] ==
                                                                            node_list_for_imaginary_node[j])][:, 1]
            imaginary_1d_temperature[i, 0] = self.node_map_sorted[i, 1]
            imaginary_1d_temperature[i, 1] = np.max(node_temperature_array[:, 1])
        return imaginary_1d_temperature

    def load_temperature_and_map_onto_1d_cable(self, directory, npoints, filename="Temperature_Data.txt"):
        """
        Loads temperature file with real nodes and maps it onto 1D cable length
        :param directory: full analysis directory as string
        :param npoints: number of nodes as integer in meshed ANSYS geometry
        :param filename: filename as string with temperature profile
        :returns: 2-column numpy array; 1-imaginary node number as float, 2-node temperature as float
        """
        temperature_profile = Geometry.load_file(analysis_directory=directory, npoints=npoints, filename=filename, file_lines_length=npoints)
        coil_temperature_1d = self.map_temperature_into_1d_cable(temperature_profile=temperature_profile)
        return coil_temperature_1d

    def convert_imaginary_nodes_set_into_real_nodes_1d_1d(self, x_down_node, x_up_node):
        """
        Returns list with real quenched nodes
        :param x_down_node: quench down front node from imaginary set as integer
        :param x_up_node: quench up front node from imaginary set as integer
        :return: list of quenched real nodes
        """
        imaginary_1d_node_set = self.coil_data[:, 2]
        imaginary_1d_node_set = np.asfarray(imaginary_1d_node_set, float)
        quenched_coil_set = self.coil_data[(imaginary_1d_node_set[:] >= x_down_node) &
                                           (imaginary_1d_node_set[:] <= x_up_node)]
        real_nodes_list = []
        for i in range(len(quenched_coil_set)):
            temporary_key = quenched_coil_set[i, 0]
            temporary_column = int(float(quenched_coil_set[i, 1])) - 1
            real_node_in_imaginary_node = self.dict_winding_nodes[temporary_key][temporary_column]
            if real_node_in_imaginary_node != 0.0 or real_node_in_imaginary_node != 0:
                real_nodes_list.append(real_node_in_imaginary_node)
        real_nodes_list.sort()
        return real_nodes_list
