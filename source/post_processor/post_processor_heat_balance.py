
from source.post_processor.post_processor import PostProcessor
import numpy as np

class PostProcessorHeatBalance(PostProcessor):

    def __init__(self, class_geometry, ansys_commands, v_quench, solver, input_data):
        PostProcessor.__init__(self, class_geometry, ansys_commands, v_quench, solver, input_data)

    def check_quench_state(self):
        time_step = [self.time_step_vector[self.iteration[0]]][0]
        q_v_time_array = []
        quench_fronts = []
        quench_front_new = self.q_det.detect_quench(quench_fronts, self.temperature_profile,
                                                    magnetic_field_map=self.magnetic_map.im_short_mag_dict)
        if self.iteration[0] > 0:
            time_step = [self.time_step_vector[self.iteration[0]]][0]
            q_v_time_array = np.zeros((1, 3))
            if len(quench_front_new) > 0:
                pos_x_down = quench_front_new[0][0]
                pos_x_up = quench_front_new[0][1]
                q_length_up = abs(pos_x_up - self.factory.quench_init_position)
                q_length_down = abs(pos_x_down - self.factory.quench_init_position)
                q_vel = ((q_length_up + q_length_down) / 2.0) / time_step
                q_v_time_array[0, 0] = time_step
                q_v_time_array[0, 1] = q_length_down + q_length_up
                q_v_time_array[0, 2] = q_vel
            else:
                q_v_time_array[0, 0] = time_step
                q_v_time_array[0, 1] = 0.0
                q_v_time_array[0, 2] = 0.0

        # write down quench velocity
        if self.iteration[0] == 1:
            self.write_line_in_file(directory=self.directory, filename="Q_V_array.txt", mydata=q_v_time_array)
        elif self.iteration[0] > 1:
            self.write_line_in_file(directory=self.directory, filename="Q_V_array.txt", mydata=q_v_time_array,
                                    newfile=False)
        for qf in quench_front_new:
            self.quench_fronts = [self.qf(x_down=qf[0], x_up=qf[1], label=self.quench_label,
                                          class_geometry=self.geometry)]

    def estimate_coil_resistance(self):
        self.plot_resistive_voltage(self.calculate_coil_resistance())

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
                    wire_diameter=self.factory.STRAND_DIAMETER)
            coil_resistance += qf_resistance
        return coil_resistance

    def plot_resistive_voltage(self, coil_resistance):
        time_step = [self.time_step_vector[self.iteration[0]]][0]
        res_voltage = self.circuit.return_current_in_time_step() * coil_resistance
        self.plot_resistive_voltage_python(voltage=res_voltage,
                                           total_time=self.factory.time_total_simulation, time_step=time_step,
                                           iteration=self.iteration[0])
        res_voltage_array = np.zeros((1, 2))
        res_voltage_array[0, 0] = self.t[0]
        res_voltage_array[0, 1] = res_voltage
        if self.iteration[0] == 1:
            self.write_line_in_file(directory=self.plots.output_directory_resistive_voltage,
                                    filename="Res_Voltage.txt", mydata=res_voltage_array)
        else:
            self.write_line_in_file(directory=self.plots.output_directory_resistive_voltage,
                                    filename="Res_Voltage.txt", mydata=res_voltage_array,
                                    newfile=False)

    def make_gif(self):
        self.create_gif(plot_array=self.quench_temperature_plots, filename='video_temperature_distribution.gif',
                        directory=self.plots.output_directory_temperature)
