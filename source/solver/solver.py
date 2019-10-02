
# from source.factory import Factory
from source.solver.model_input import ModelInput

class Solver(ModelInput):

    def __init__(self, ansys_commands, class_geometry, input_data):
        # self.temperature_ic = Factory.get_initial_temperature_class(ansys_commands, class_geometry)
        self.geometry = class_geometry
        self.ansys_commands = ansys_commands
        self.factory = input_data
        self.iteration = 1

        self.time_step_vector = ModelInput.linear_time_stepping(time_division=self.factory.time_step_cosimulation,
                                                                total_time=self.factory.time_total_simulation)

    def time_to_string(self):
        print("iteration number: {} \n time step: {} \n ______________".format(self.iteration,
                                                                               self.time_step_vector[self.iteration]))

    def couple_nodes_in_analysis(self):
        nodes_to_couple_windings_list = self.geometry.create_node_list_to_couple_windings()
        for nodes_list in nodes_to_couple_windings_list:
            nodes_to_select_ansys = self.geometry.prepare_ansys_nodes_selection_list(real_nodes_list=nodes_list)
            self.ansys_commands.select_nodes_list(nodes_list=nodes_to_select_ansys)
            self.ansys_commands.couple_nodes(dof="temp")
            self.ansys_commands.couple_nodes(dof="volt")

    def enter_solver_settings(self):
        self.ansys_commands.enter_solver()
        self.time_to_string()
        self.ansys_commands.set_analysis_settings()
        self.ansys_commands.set_ansys_time_step_settings(min_time_step=self.factory.time_step_min_ansys,
                                                         max_time_step=self.factory.time_step_max_ansys,
                                                         init_time_step=self.factory.time_step_min_ansys)

    def set_time_step(self):
        self.ansys_commands.set_time_step(time_step=self.time_step_vector[self.iteration], iteration=0)

    def set_initial_temperature(self):
        self.temperature_ic.set_initial_temperature()

    def set_time_step_temperature(self):
        self.temperature_ic.set_temperature_in_time_step(iteration=self.iteration)

    def solve(self):
        self.ansys_commands.input_solver()



