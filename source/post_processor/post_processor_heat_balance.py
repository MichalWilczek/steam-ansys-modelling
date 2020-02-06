
from source.post_processor.plots import Plots
from source.post_processor.post_processor import PostProcessor
import numpy as np
import os

class PostProcessorHeatBalance(PostProcessor):

    def __init__(self, class_geometry, ansys_commands, v_quench, solver, input_data):
        PostProcessor.__init__(self, class_geometry, ansys_commands, v_quench, solver, input_data)
        init_quench_pos = self.define_initial_quench_position()
        self.quench_fronts = [self.qf(x_down=init_quench_pos[0],
                                      x_up=init_quench_pos[1],
                                      label=self.quench_label,
                                      class_geometry=self.geometry)]

    def define_initial_quench_position(self):
        x_down = self.input_data.analysis_settings.quench_init_position - \
            self.input_data.analysis_settings.quench_init_length/2.0
        x_up = self.input_data.analysis_settings.quench_init_position + \
            self.input_data.analysis_settings.quench_init_length/2.0

        if x_down < self.min_coil_length:
            x_down = 0.0
        if x_up > self.max_coil_length:
            x_up = self.max_coil_length
        return x_down, x_up

    def check_quench_state(self):
        self.check_quench_state_heat_balance()

    def check_quench_state_heat_balance(self):

        time_step = [self.time_step_vector[self.iteration[0]]][0] - [self.time_step_vector[self.iteration[0]-1]][0]
        time = [self.time_step_vector[self.iteration[0]]][0]
        q_v_time_array = []
        quench_fronts = []
        quench_front_new = self.q_det.detect_quench(quench_fronts, self.temperature_profile,
                                                    magnetic_field_map=self.magnetic_map.im_short_mag_dict)
        if self.iteration[0] > 0:
            q_v_time_array = np.zeros((1, 3))
            if len(quench_front_new) > 0:
                pos_x_down = quench_front_new[0][0]
                pos_x_up = quench_front_new[0][1]

                q_length_up = abs(pos_x_up - self.quench_fronts[0].x_up)
                q_length_down = abs(pos_x_down - self.quench_fronts[0].x_down)

                if q_length_up == 0.0:
                    q_vel = q_length_down / time_step
                elif q_length_down == 0.0:
                    q_vel = q_length_up / time_step
                else:
                    q_vel = ((q_length_up + q_length_down) / 2.0) / time_step

                q_v_time_array[0, 0] = time
                q_v_time_array[0, 1] = q_length_down + q_length_up
                q_v_time_array[0, 2] = q_vel
            else:
                q_v_time_array[0, 0] = time
                q_v_time_array[0, 1] = 0.0
                q_v_time_array[0, 2] = 0.0

        self.write_down_quench_velocity_to_file(q_v_time_array)
        for qf in quench_front_new:
            self.quench_fronts = [self.qf(x_down=qf[0], x_up=qf[1], label=self.quench_label,
                                          class_geometry=self.geometry)]

    def write_down_quench_velocity_to_file(self, q_v_time_array):
        if self.iteration[0] == 1:
            os.chdir(self.plots.output_directory_quench_state)
            with open('quench_velocity.txt', 'a') as file:
                file.write('t, s;                    L_quench, m;             v_quench, m/s\n')
            Plots.write_line_in_file(directory=self.plots.output_directory_quench_state,
                                     filename="quench_velocity.txt", mydata=q_v_time_array, newfile=False)
        elif self.iteration[0] > 1:
            Plots.write_line_in_file(directory=self.plots.output_directory_quench_state,
                                     filename="quench_velocity.txt", mydata=q_v_time_array,
                                     newfile=False)

    def estimate_resistive_voltage(self):
        self.resistive_voltage = self.calculate_resistive_voltage()
        self.write_down_resistive_voltage_to_file(self.resistive_voltage)
        self.plot_resistive_voltage()

    def calculate_resistive_voltage(self):
        coil_resistance = self.calculate_coil_resistance()
        return coil_resistance * self.circuit.return_current_in_time_step()

    def calculate_coil_resistance(self):
        quenched_winding_list = []
        for qf in self.quench_fronts:
            # position transformation into nodes
            qf.convert_quench_front_to_nodes(self.geometry.coil_geometry)
            quenched_winding_list.append(self.geometry.retrieve_quenched_winding_numbers_from_quench_fronts(
                coil_data=self.geometry.coil_data, x_down_node=qf.x_down_node, x_up_node=qf.x_up_node))

        coil_resistance = 0.0
        for qf in self.quench_fronts:
            qf_resistance = 0.0
            quench_dict = self.geometry.retrieve_winding_numbers_and_quenched_nodes(
                x_down_node=qf.x_down_node, x_up_node=qf.x_up_node)
            for key in quench_dict:
                winding_number = int(float(key[7:]))
                mag_field = self.magnetic_map.im_short_mag_dict["winding" + str(winding_number)]
                n_down = quench_dict["winding" + str(winding_number)][0]
                n_up = quench_dict["winding" + str(winding_number)][1]
                qf_resistance = self.mat_props.calculate_qf_resistance(
                    qf_down=n_down, qf_up=n_up, im_temp_profile=self.temperature_profile,
                    im_coil_geom=self.geometry.coil_geometry, mag_field=mag_field,
                    wire_diameter=self.input_data.geometry_settings.type_input.strand_diameter)
            coil_resistance += qf_resistance
        return coil_resistance

    def make_gif(self):
        Plots.create_gif(plot_array=self.quench_temperature_plots, filename='video_temperature_profile.gif',
                         directory=self.plots.output_directory_temperature)
