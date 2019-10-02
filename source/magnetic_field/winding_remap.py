
from source.magnetic_field.winding_remap_searcher import WindingRemapSearcher

class WindingRemap(WindingRemapSearcher):

    def __init__(self, input_data):
        self.factory = input_data
        self.start_winding = self.factory.winding_number_first_in_analysis
        self.end_winding = self.factory.winding_number_last_in_first_layer
        self.layers = self.factory.number_of_layers_in_analysis
        WindingRemapSearcher.__init__(self, number_of_layers=self.layers, number_of_windings_in_layer=self.factory.NUMBER_TURNS_IN_LAYER)

    def map_winding_list(self):
        """
        Creates a list of real winding numbers analyzed in the simulation
        :return: list of integers
        """
        map_main_list = []
        for j in range(self.start_winding, self.end_winding + 1):
            map_main_list.append(j)
        map_list = map_main_list

        for i in range(1, self.layers):
            new_layer_list = []
            for j in range(len(map_list)):
                layer = self.in_which_layer_is_winding(map_list[j])
                winding_in_layer = self.which_winding_in_layer(layer, winding_number=map_list[j])
                new_layer_list.append(self.neighbouring_winding_in_next_layer(map_list[j], winding_in_layer))
                map_main_list.append(self.neighbouring_winding_in_next_layer(map_list[j], winding_in_layer))
            map_list = new_layer_list
        map_main_list.sort()
        print("List of windings analyzed in geometry: {}".format(map_main_list))
        return map_main_list
