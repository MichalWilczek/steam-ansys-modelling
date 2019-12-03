
from source.factory.general_functions import GeneralFunctions


class WindingRemapSearch(GeneralFunctions):

    def __init__(self, number_of_layers, number_of_windings_in_layer):
        self._number_of_layers = number_of_layers
        self._number_of_windings_in_layer = number_of_windings_in_layer

    @staticmethod
    def list_of_windings_to_analyse_without_repetitions(list_of_lists):
        one_list = GeneralFunctions.flatten_list(list_of_lists)
        return GeneralFunctions.remove_repetitive_values_from_list(one_list)

    def list_of_neighbouring_windings(self, winding_number):
        """
        Returns list with numbers of neighbouring windings of the one given as a param + param
        :param winding_number: winding number as integer
        :return: list of numbers
        """
        if winding_number > self._number_of_layers*self._number_of_windings_in_layer:
            raise ValueError("Given winding number is to high with respect to analysed geometry!")
        winding_list = []
        neigh1 = self.neighbouring_windings_in_the_same_layer(winding_number)
        neigh2 = self.neighbouring_windings_in_diff_layer(winding_number)
        for item in neigh1:
            winding_list.append(item)
        for item in neigh2:
            winding_list.append(item)
        winding_list.append(winding_number)
        winding_list.sort()
        return winding_list

    def in_which_layer_is_winding(self, winding_number):
        """
        Returns the layer number where the given winding number is placed
        :param winding_number: winding number as integer
        :return: layer number as integer
        """
        i = self._number_of_windings_in_layer
        layer_counter = 1
        while winding_number > i:
            i += self._number_of_windings_in_layer
            layer_counter += 1
        return layer_counter

    def first_winding_of_given_layer(self, layer):
        """
        Returns the number of the 1st winding number in a given layer
        :param layer: layer as integer
        :return: winding number as integer
        """
        return (layer-1)*self._number_of_windings_in_layer + 1

    def last_winding_of_given_layer(self, layer):
        """
        Returns the number of the last winding number in a given layer
        :param layer: layer as integer
        :return: winding number as integer
        """
        return layer*self._number_of_windings_in_layer

    def neighbouring_windings_in_the_same_layer(self, winding_number):
        """
        Returns number of windings which are neighboring with the given winding
        :param winding_number: winding number as integer
        :return: list of neigbhouring windings
        """
        neighbouring_windings = []
        layer = self.in_which_layer_is_winding(winding_number)
        first = self.first_winding_of_given_layer(layer)
        last = self.last_winding_of_given_layer(layer)

        if winding_number != first:
            neighbouring_windings.append(winding_number-1)
        if winding_number != last:
            neighbouring_windings.append(winding_number+1)
        return neighbouring_windings

    def which_winding_in_layer(self, layer, winding_number):
        """
        Returns the number which corresponds to the nth number of the set (layer)
        :param layer: layer number as integer
        :param winding_number: winding number as integer
        :return: nth number of the set as integer
        """
        return winding_number - self.first_winding_of_given_layer(layer)

    @staticmethod
    def neighbouring_winding_in_previous_layer(winding, which_winding_in_layer):
        """
        Returns the neighbouring number of the winding from previous layer
        :param winding: winding number as integer
        :param which_winding_in_layer: nth number of the set as integer
        :return: neighbouring winding number as integer
        """
        return winding - (2*which_winding_in_layer + 1)

    def neighbouring_winding_in_next_layer(self, winding, which_winding_in_layer):
        """
        Returns the neighbouring number of the winding from next layer
        :param winding: winding number as integer
        :param which_winding_in_layer: nth number of the set as integer
        :return: neighbouring winding number as integer
        """
        return winding + (2*(self._number_of_windings_in_layer-which_winding_in_layer) - 1)

    def neighbouring_windings_in_diff_layer(self, winding_number):
        """
        Returns all winding numbers neighbouring with given winding but not laying in the same layer
        :param winding_number: winding number as integer
        :return: neighbouring winding numbers as list
        """
        neighbouring_windings = []
        layer = self.in_which_layer_is_winding(winding_number)
        winding_in_layer = self.which_winding_in_layer(layer, winding_number=winding_number)
        if layer != 1:
            neighbouring_windings.append(self.neighbouring_winding_in_previous_layer(winding_number, winding_in_layer))
        if layer != self._number_of_layers:
            neighbouring_windings.append(self.neighbouring_winding_in_next_layer(winding_number, winding_in_layer))
        return neighbouring_windings
