import os
from ansys_corba import CORBA
from source.ansys_commands.ansys_table import Table
from source.initial_temperature.polynomial_fit import Polynomials
from source.general_functions import GeneralFunctions
import time

class AnsysCommands(GeneralFunctions):

    def __init__(self, input_data, analysis_directory):
        self.factory = input_data
        self.analysis_directory = analysis_directory
        os.chdir(self.analysis_directory)
        with open('aaS_MapdlID.txt', 'r') as f:
            aasMapdlKey = f.read()
        self.mapdl = CORBA.ORB_init().string_to_object(aasMapdlKey)

    def input_point_mass_material_properties(self, class_mat, elem_volume):
        self.enter_preprocessor()
        element_number = 2 * self.factory.number_of_windings() + 2
        self.define_element_type(element_number=element_number, element_name="mass71")
        self.define_element_constant(element_number=element_number, element_constant=elem_volume)
        self.define_keyopt(element_number, keyopt_1=3, keyopt_2=0)  # real constant interpreted as volume with density and specific heat defined as material properties
        self.define_keyopt(element_number, keyopt_1=4, keyopt_2=0)  # heat generation independent of temperature

        res_cp = class_mat.calculate_cu_cp()
        for j in range(len(res_cp[:, 0])):
            self.define_temperature_for_material_property(table_placement=j+1, temperature=res_cp[j, 0])
            self.define_element_heat_capacity(element_number=element_number, value=res_cp[j, 1])
        return element_number

    def input_heat_generation_curve(self, class_mat, magnetic_field):
        self.enter_preprocessor()
        heat_gen_array = class_mat.create_heat_gen_profile(magnetic_field, wire_diameter=self.factory.STRAND_DIAMETER, current=self.factory.current_init)
        filename = "HGEN_Table"
        filename_path = self.analysis_directory + "\\" + filename
        hgen = Table(filename_path, ext='.inp')
        hgen.load('hgen_table', heat_gen_array[:, 1], [heat_gen_array[:, 0]])
        hgen.write(['HGEN'])
        self.wait_for_process_to_finish(hgen)
        hgen.close()
        self.input_file(filename=filename, extension="inp")

    def input_heat_generation_table(self, class_mat, magnetic_field):
        self.enter_preprocessor()
        heat_gen_array = class_mat.create_heat_gen_profile(magnetic_field, wire_diameter=self.factory.STRAND_DIAMETER, current=self.factory.current_init)
        self.create_dim_table(dim_name="heatgen", dim_type="table", size1=len(heat_gen_array[:, 0]), size2=1, size3=1, name1="temp")
        self.fill_dim_table(dim_name="heatgen", row=0, column=1, value=0.0)
        for i in range(len(heat_gen_array[:, 0])):
            self.fill_dim_table(dim_name="heatgen", row=i+1, column=0, value=heat_gen_array[i, 0])
            self.fill_dim_table(dim_name="heatgen", row=i+1, column=1, value=heat_gen_array[i, 1])

    def input_heat_generation_table_winding(self, class_mat, magnetic_field, winding_number):
        self.enter_preprocessor()
        heat_gen_array = class_mat.create_heat_gen_profile(magnetic_field, wire_diameter=self.factory.STRAND_DIAMETER, current=self.factory.current_init)
        dim_name = "heatgen_"+winding_number
        self.create_dim_table(dim_name=dim_name, dim_type="table", size1=len(heat_gen_array[:, 0]), size2=1, size3=1, name1="temp")
        self.fill_dim_table(dim_name=dim_name, row=0, column=1, value=0.0)
        for i in range(len(heat_gen_array[:, 0])):
            self.fill_dim_table(dim_name=dim_name, row=i+1, column=0, value=heat_gen_array[i, 0])
            self.fill_dim_table(dim_name=dim_name, row=i+1, column=1, value=heat_gen_array[i, 1])

    def input_heat_generation_on_windings(self, winding_number):
        dim_name = "%heatgen_" + winding_number[7:] + "%"
        self.set_heat_generation_in_nodes(node_number="all", value=dim_name)

    def input_heat_flow_table(self, number_windings_heated=1.0, scaling_factor=1.0):
        self.enter_preprocessor()
        heat_flow_array = Polynomials.extract_meas_power_function()
        self.create_dim_table(dim_name="heat_flow", dim_type="table", size1=len(heat_flow_array), size2=1, size3=1, name1="time")
        self.fill_dim_table(dim_name="heat_flow", row=0, column=1, value=0.0)
        for i in range(len(heat_flow_array[:, 0])):
            self.fill_dim_table(dim_name="heat_flow", row=i + 1, column=0, value=heat_flow_array[i, 0])
            self.fill_dim_table(dim_name="heat_flow", row=i + 1, column=1, value=(heat_flow_array[i, 1]/number_windings_heated)*scaling_factor)

    # functions responsible for deleting unnecessary ansys files
    def delete_old_files(self):
        """
        Deletes unnecessary files saved during previous analyses
        """
        self.delete_file(directory=self.analysis_directory, filename='Variable_Input.inp')
        self.delete_file(directory=self.analysis_directory, filename='File_Position.txt')
        self.delete_file(directory=self.analysis_directory, filename='Process_Finished.txt')

    @staticmethod
    def create_variable_table_method(directory):
        """
        Creates a Class object
        :param directory: analysis_directory as string
        :return: Class for creation of ANSYS files
        """
        filename = directory
        filename += '/Variable_Input'
        extension = 'inp'
        return Table(filename, ext=('.' + extension))

    @staticmethod
    def wait_for_process_to_finish(data):
        """
        Writes down in the opened file the APDL commands to create the file named "Process_Finished.txt"
        :param data: Class object to create APDL commands .txt file
        """
        data.write_text('*cfopen,Process_Finished,txt')  # for reading purposes between ansys and python
        data.write_text('*vwrite,1')
        data.write_text('(1(ES16.7))')
        data.write_text('*cfclose')

    def variable_file_invariable_input(self, data):
        """
        :param data: Class object to create APDL commands .txt file
        Creates an input file with parameters used by ANSYS
        """
        data.write_text('/clear')
        data.write_text('/title,Quench_Analysis_' + self.factory.dimensionality)
        data.write_text('/prep7')
        data.write_text('/nerr,999999999999')
        data.write_text('/graphics,power')
        data.write_text('/show,png')
        data.write_text('electric_analysis={}'.format(self.change_boolean_into_integer(self.factory.electric_ansys_elements)))

    @staticmethod
    def wait_python(filename, directory, file_length=1):
        """
        Makes Python wait until process in ANSYS is finished
        :param directory:
        :param filename: filename as string given by ANSYS when it finishes processing
        :param file_length: number of rows in filename as integer
        """
        exists = False
        while exists is False:
            exists = os.path.isfile(directory+"\\"+filename)
            if exists and GeneralFunctions.file_length(filename, analysis_directory=directory) == file_length:
                os.chdir(directory)
                with open('Process_Finished.txt', 'r') as f:
                    file_input = int(float(f.read()))
                if file_input == 1:
                    f.close()
                    break
                else:
                    exists = False
            else:
                exists = False

    @staticmethod
    def delete_file(filename, directory):
        """
        Deletes file in directory
        :param directory: analysis directory as string
        :param filename: filename to delete as string
        """
        full_filename = "{}.".format(filename)
        full_path = "{}\\{}".format(directory, full_filename)
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            print("Error: {} file not found".format(full_filename))

    def select_nodes_list(self, nodes_list):
        """
        Selects a set of nodes from given list of nodes
        :param nodes_list: list of lists with lower and higher node to be selected in a set
        """
        for i in range(len(nodes_list)):
            if i == 0:
                print(self.mapdl.executeCommandToString("nsel,s,node,,{},{}".format(nodes_list[i][0], nodes_list[i][1])))
            else:
                print(self.mapdl.executeCommandToString("nsel,a,node,,{},{}".format(nodes_list[i][0], nodes_list[i][1])))

    def unselect_nodes_list(self, nodes_list):
        """
        Selects a set of nodes from given list of nodes
        :param nodes_list: list of lists with lower and higher node to be selected in a set
        """
        for i in range(len(nodes_list)):
            self.mapdl.executeCommand("nsel,u,node,,{},{}".format(nodes_list[i][0], nodes_list[i][1]))

    # not needed anymore
    def set_gaussian_initial_temperature_distribution(self, gaussian_temperature_distr):
        """
        Sets initial temperature to all nodes according to gaussian distribution curve
        :param gaussian_temperature_distr: temperature distribution numpy array; 1st column: node number as integer,
         2nd column: temperature as float
        """
        self.allsel()
        for i in range(len(gaussian_temperature_distr[:, 0])):
            node_number = gaussian_temperature_distr[i, 0]
            temperature = gaussian_temperature_distr[i, 1]
            self.mapdl.executeCommandToString("ic,{},temp,{}".format(node_number, temperature))

    # general commands
    def create_dim_table(self, dim_name, dim_type, name1, size1, size2=" ", size3=" "):
        self.mapdl.executeCommand("*dim,{},{},{},{},{},{}".format(dim_name, dim_type, size1, size2, size3, name1))

    def fill_dim_table(self, dim_name, row, column, value):
        self.mapdl.executeCommand("{}({},{})={}".format(dim_name, row, column, value))

    def clear_all(self):
        self.mapdl.executeCommand("/clear,all,")

    def select_nodes(self, node_down, node_up):
        self.mapdl.executeCommand("nsel,s,node,,{},{}".format(node_down, node_up))

    def select_elem_from_nodes(self):
        self.mapdl.executeCommand("esln,s,1,all")

    def allsel(self):
        print(self.mapdl.executeCommandToString("allsel"))

    def allsel_below(self, domain):
        print(self.mapdl.executeCommandToString("allsel,below,{}".format(domain)))

    def input_file(self, filename, extension, add_directory=" "):
        print(self.mapdl.executeCommandToString(
            "/input,{},{},{}\\{}".format(filename, extension, self.analysis_directory, add_directory)))
        self.wait_python(filename='Process_Finished.txt', directory=self.analysis_directory)
        time.sleep(1)
        self.delete_file(filename='Process_Finished.txt', directory=self.analysis_directory)
        print("File uploaded... \n________________")

    def terminate_analysis(self):
        self.mapdl.terminate()

    def save_analysis(self):
        print(self.mapdl.executeCommandToString("save"))

    def set_dof(self, dof):
        print(self.mapdl.executeCommandToString("dof,{}".format(dof)))

    # coupling commands
    def couple_nodes(self, dof):
        """
        Couples all nodes in previously defined set
        :param dof: 'volt' for voltage or 'temp' for temperature dof
        """
        self.mapdl.executeCommand("cp,next,{},all".format(dof))

    def couple_interface(self, dof):
        self.mapdl.executeCommand("cpintf,{},".format(dof))

    # restart commands
    def save_parameters(self, filename='parameter_file', extension='txt'):
        print(self.mapdl.executeCommandToString("parsav,all,{},{},".format(filename, extension)))

    def load_parameters(self, filename='parameter_file', extension='txt'):
        print(self.mapdl.executeCommandToString("parres,new,{},{},".format(filename, extension)))

    def restart_analysis(self):
        print(self.mapdl.executeCommandToString("antype,,rest,,,continue"))

    # preprocessor commands`
    def define_temperature_for_material_property(self, table_placement, temperature):
        self.mapdl.executeCommand('mptemp,{},{}'.format(table_placement, temperature))

    def define_element_type(self, element_number, element_name):
        self.mapdl.executeCommand('et,{},{}'.format(element_number, element_name))

    def define_element_type_with_keyopt(self, element_number, element_name, keyopt):
        self.mapdl.executeCommand('et,{},{},{}'.format(element_number, element_name, keyopt))

    def define_keyopt(self, element_number, keyopt_1, keyopt_2):
        self.mapdl.executeCommand('keyopt,{},{},{}'.format(element_number, keyopt_1, keyopt_2))

    def define_element_constant(self, element_number, element_constant):
        self.mapdl.executeCommand('r,{},{}'.format(element_number, element_constant))

    def define_element_constants(self, element_number, constant1, constant2):
        self.mapdl.executeCommand('r,{},{},{}'.format(element_number, constant1, constant2))

    def define_element_density(self, element_number, value):
        self.mapdl.executeCommand('mp,dens,{},{}'.format(element_number, value))

    def define_element_conductivity(self, element_number, value, direction="kxx"):
        self.mapdl.executeCommand('mpdata,{},{},,{}'.format(direction, element_number, value))

    def define_element_heat_capacity(self, element_number, value):
        self.mapdl.executeCommand('mpdata,c,{},,{}'.format(element_number, value))

    def define_element_resistivity(self, element_number, value, direction="rsvx"):
        self.mapdl.executeCommand('mpdata,{},{},,{}'.format(direction, element_number, value))

    def enter_preprocessor(self):
        print(self.mapdl.executeCommandToString('/prep7'))

    def modify_material_type(self, element_number):
        print("Material type was modfied")
        self.mapdl.executeCommand("emodif,all,type,{}".format(element_number))

    def modify_material_constant(self, constant_number):
        print("Material constant was modified")
        self.mapdl.executeCommand("emodif,all,real,{}".format(constant_number))

    def modify_material_number(self, material_number):
        print("Material number was modified")
        self.mapdl.executeCommand("emodif,all,mat,{}".format(material_number))

    # solver processor commands
    def enter_solver(self):
        print(self.mapdl.executeCommandToString("/solu"))

    def set_time_step(self, time_step, iteration):
        """
        Sets time step and creates APDL variable "time_step" used for further post-processing plotting
        :param time_step: time step as float
        :param iteration: current analysis iteration as integer
        """
        print(self.mapdl.executeCommandToString("time_step={}".format(iteration)))
        print(self.mapdl.executeCommandToString("time,{}".format(time_step)))

    def set_initial_temperature(self, temperature):
        self.allsel()
        print(self.mapdl.executeCommandToString("ic,all,temp,{}".format(temperature)))

    def set_quench_temperature(self, q_temperature):
        print(self.mapdl.executeCommandToString("ic,all,temp,{}".format(q_temperature)))

    def set_current(self, node_number, value):
        self.mapdl.executeCommand("f,{},amps,{}".format(node_number, value))

    def set_ground(self, node_number, value):
        self.mapdl.executeCommand("d,{},volt,{}".format(node_number, value))

    def set_heat_generation_in_elements(self, element_number, value):
        self.mapdl.executeCommand("bfe,{},hgen,,{}".format(element_number, value))

    def set_heat_generation_in_nodes(self, node_number, value):
        self.mapdl.executeCommand("bf,{},hgen,{}".format(node_number, value))

    def set_heat_flow_into_nodes(self, value):
        self.mapdl.executeCommand("f,all,heat,{}".format(value))

    def start_solution(self):
        self.allsel()
        print(self.mapdl.executeCommandToString('solve'))

    def set_load_in_solver(self, dof, value):
        print(self.mapdl.executeCommandToString("d, all, {}, {}".format(dof, value)))

    def set_ansys_time_step_settings(self, init_time_step, min_time_step, max_time_step):
        print(self.mapdl.executeCommandToString('deltim,{},{},{}').format(init_time_step, min_time_step, max_time_step))

    def set_analysis_setting(self):
        print(self.mapdl.executeCommandToString('antype,4'))
        print(self.mapdl.executeCommandToString('trnopt,full'))
        print(self.mapdl.executeCommandToString('kbc,1'))
        print(self.mapdl.executeCommandToString('eqslv,sparse'))
        print(self.mapdl.executeCommandToString('bcsoption,,default'))
        print(self.mapdl.executeCommandToString('lumpm,0'))
        print(self.mapdl.executeCommandToString('autots,on'))
        print(self.mapdl.executeCommandToString('solcontrol,on,on'))
        print(self.mapdl.executeCommandToString('neqit,1000'))
        print(self.mapdl.executeCommandToString('lnsrch,on'))
        print(self.mapdl.executeCommandToString('rescontrol,define,none,none,1'))
        print(self.mapdl.executeCommandToString('tintp,,,,1'))   # switches T calculation from trapezoidal integration (default) into backward Euler formulation

    # postprocessor commands
    def create_file(self, filename, extension):
        print(self.mapdl.executeCommandToString("*cfopen,{},{}".format(filename, extension)))

    def close_file(self):
        print(self.mapdl.executeCommandToString('*cfclose'))

    def set_do_loop(self, min_value, max_value, increase=1):
        self.mapdl.executeCommand("*do,i,{},{},{}".format(min_value, max_value, increase))

    def end_do_loop(self):
        self.mapdl.executeCommand('*enddo')
