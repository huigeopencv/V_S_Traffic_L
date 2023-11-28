# """Script containing the TraCI simulation kernel class."""
#
# from flow.core.kernel.simulation import KernelSimulation
# from flow.core.util import ensure_dir
# import flow.config as config
# import traci.constants as tc
# import traci
# import traceback
# import os
# import time
# import logging
# import subprocess
# import signal
# import csv
import pynverse
# import numpy as np
# pre_merge_length= 500
# merge_length = 100
# # Number of retries on restarting SUMO before giving up
# RETRIES_ON_ERROR = 10
# Kp=0.002
# q_c=[0]*5000
# o_max=0.414
# global m
# m=0
# x=[0,0.0013,0.0032,0.00507814,0.00722536,0.00856738,0.0107146,0.0117882,0.0131302,0.015,0.0158,0.016,0.0163,0.0165,0.01742,0.0183,0.0194,0.0205,0.0223,0.02655,0.03621,0.04749,0.052317,0.0606376,0.0654688,0.07,0.0746,0.0804994,0.085867,0.0891,0.0961,0.101435,0.1063,0.12,0.12546]
# y=[0,0.051,0.1,0.1487,0.184585,0.225585,0.266585,0.28965,0.315273,0.346,0.37677,0.38,0.39,0.396,0.4165,0.41,0.40,0.39,0.38,0.376774,0.3614,0.3486,0.34474,0.337,0.3268,0.32,0.3127,0.289648,0.276836,0.273,0.24865,0.24,0.2141,0.165,0.1402]
# parameter=np.polyfit(x,y,5)
# y1=np.poly1d(parameter)
# class TraCISimulation(KernelSimulation):
#     """Sumo simulation kernel.
#
#     Extends flow.core.kernel.simulation.KernelSimulation
#
#     Attributes
#     ----------
#     sumo_proc : subprocess.Popen
#         contains the subprocess.Popen instance used to start traci
#         包含子进程。用于启动traci的Popen实例
#     sim_step : float
#         seconds per simulation step
#     emission_path : str or None
#         Path to the folder in which to create the emissions output. Emissions
#         output is not generated if this value is not specified
#     time : float
#         used to internally keep track of the simulation time
#         用于内部跟踪模拟时间
#     stored_data : dict <str, dict <float, dict <str, Any>>>
#         a dict object used to store additional data if an emission file is
#         provided. The first key corresponds to the name of the vehicle, the
#         second corresponds to the time the sample was issued, and the final
#         keys represent the additional data stored at every given time for every
#         vehicle, and consists of the following keys:
#         如果提供了发射文件，则用于存储附加数据的dict对象。
#         第一把钥匙与车辆名称相对应，第二把钥匙与发放样品的时间相对应，最后一把钥匙代表每辆车在每个给定时间存储的附加数据，由以下钥匙组成：
#
#         * acceleration (no noise): the accelerations issued to the vehicle,
#           excluding noise
#         * acceleration (requested): the requested acceleration by the vehicle,
#           including noise
#         * acceleration (actual): the actual acceleration by the vehicle,
#           collected by computing the difference between the speeds of the
#           vehicle and dividing it by the sim_step term
#           车辆的实际加速度，通过计算车辆速度之间的差值并将其除以simstep项来收集
#     """
#
#     def __init__(self, master_kernel):
#         """Instantiate the sumo simulator kernel.
#
#         Parameters
#         ----------
#         master_kernel : flow.core.kernel.Kernel
#             the higher level kernel (used to call methods from other
#             sub-kernels)
#         """
#         KernelSimulation.__init__(self, master_kernel)
#
#         self.sumo_proc = None
#         self.sim_step = None
#         self.emission_path = None
#         self.time = 0
#         self.stored_data = dict()
#
#     def pass_api(self, kernel_api):
#         """See parent class.
#
#         Also initializes subscriptions.
#         """
#         KernelSimulation.pass_api(self, kernel_api)
#
#         # subscribe some simulation parameters needed to check for entering,
#         # exiting, and colliding vehicles
#         self.kernel_api.simulation.subscribe([
#             tc.VAR_DEPARTED_VEHICLES_IDS,
#             tc.VAR_ARRIVED_VEHICLES_IDS,
#             tc.VAR_TELEPORT_STARTING_VEHICLES_IDS,
#             tc.VAR_TIME_STEP,
#             tc.VAR_DELTA_T,
#             tc.VAR_LOADED_VEHICLES_NUMBER,
#             tc.VAR_DEPARTED_VEHICLES_NUMBER,
#             tc.VAR_ARRIVED_VEHICLES_NUMBER
#         ])
#
#     def simulation_step(self):
#         """See parent class."""
#         self.kernel_api.simulationStep()
#
#     # global m
#     def update(self, reset):
#         """See parent class."""
#         if reset:
#             self.time = 0
#         else:
#             self.time += self.sim_step
#             global m
#             m+=1
#
#         # Collect the additional data to store in the emission file.
#         if self.emission_path is not None:
#             kv = self.master_kernel.vehicle
#             # m_occ = self.master_kernel.network.get_laststep_occupancy('center')
#
#             m_speed = self.master_kernel.network.get_laststep_meanspeed('4')
#             d_2 = self.master_kernel.network.get_laststep_vehiclenum('4') / (500 * 2)
#             flow_1 = m_speed*d_2
#             t = round(self.time, 2)
#             if t not in self.stored_data.keys():
#                 self.stored_data[t] = dict()
#             self.stored_data[t].update({
#                 "flow_1": (self.master_kernel.network.get_laststep_vehiclenum('4') / (500 * 2))*abs(self.master_kernel.network.get_laststep_meanspeed('4')),
#                 "m_speed" : self.master_kernel.network.get_laststep_meanspeed('4'),
#                 "num" : self.master_kernel.network.get_laststep_vehiclenum('4'),
#                 "density": self.master_kernel.network.get_laststep_vehiclenum('4') / (500 * 2),
#             })
#
#             # 上游车辆流量
#             d_1 = self.master_kernel.network.get_laststep_meanspeed('3')
#             d_3 = self.master_kernel.network.get_laststep_vehiclenum('3')/(140*4)
#             d = abs(d_1)*d_3
#             # VSL控制
#             q_c[m] = q_c[m-1]+Kp*(o_max-d)
#             y1=lambda x:4.676e5*x**5-1.702e5*x**4+2.325*x**3-1482*x**2+41.63*x-0.01581
#             # 用到的函数，速度，车辆数（求解密度），veh/m*m/s==veh/s即得到车流量信息
#             # if m_speed<15 :
#             #     if q_c[m]>0.154723 and q_c[m]<0.4043:
#             #         v = q_c[m]/(pynverse.inversefunc(y1, y_values=q_c[m], domain=[0.02, 0.12]))
#             #         self.master_kernel.network.set_max_speed('2', v)
#             #         self.master_kernel.network.set_max_speed('3', v)
#             #
#             #         print(v)
# # # # # # 2023.03.09.17.45修改traci进行VSL的实施控制！！！！！！！！！！！
#
#             # for veh_id in self.master_kernel.vehicle.get_ids():
#             #     t = round(self.time, 2)
#             #
#             #     # some miscellaneous pre-processing 一些杂项预处理
#             #     position = kv.get_2d_position(veh_id)
#             #
#             #     # Make sure dictionaries corresponding to the vehicle and time are available.
#             #     # 确保与车辆和时间相对应的词典可用
#             #     if veh_id not in self.stored_data.keys():
#             #         self.stored_data[veh_id] = dict()
#             #     if t not in self.stored_data[veh_id].keys():
#             #         self.stored_data[veh_id][t] = dict()
#             #
#             #     # Add the speed, position, and lane data.
#             #     self.stored_data[veh_id][t].update({
#             #         "speed": kv.get_speed(veh_id),
#             #         "lane_number": kv.get_lane(veh_id),
#             #         "edge_id": kv.get_edge(veh_id),
#             #         "relative_position": kv.get_position(veh_id),
#             #         "x": position[0],
#             #         "y": position[1],
#             #         "headway": kv.get_headway(veh_id),
#             #         "leader_id": kv.get_leader(veh_id),
#             #         "follower_id": kv.get_follower(veh_id),
#             #         "leader_rel_speed":
#             #             kv.get_speed(kv.get_leader(veh_id))
#             #             - kv.get_speed(veh_id),
#             #         "target_accel_with_noise_with_failsafe":
#             #             kv.get_accel(veh_id, noise=True, failsafe=True),
#             #         "target_accel_no_noise_no_failsafe":
#             #             kv.get_accel(veh_id, noise=False, failsafe=False),
#             #         "target_accel_with_noise_no_failsafe":
#             #             kv.get_accel(veh_id, noise=True, failsafe=False),
#             #         "target_accel_no_noise_with_failsafe":
#             #             kv.get_accel(veh_id, noise=False, failsafe=True),
#             #         "realized_accel":
#             #             kv.get_realized_accel(veh_id),
#             #         "road_grade": kv.get_road_grade(veh_id),
#             #         "distance": kv.get_distance(veh_id),
#             #     })
#
#     # def update(self, reset):
#     #         """See parent class."""
#     #         if reset:
#     #             self.time = 0
#     #         else:
#     #             self.time += self.sim_step
#     #
#     #         # Collect the additional data to store in the emission file.
#     #         if self.emission_path is not None:
#     #             kv = self.master_kernel.vehicle
#     #             # m_occ = self.master_kernel.network.get_laststep_occupancy('center')
#     #
#
#                 # m_speed = self.master_kernel.network.get_laststep_meanspeed('4')
#                 # d_2 = self.master_kernel.network.get_laststep_vehiclenum('4') / (280 * 2)
#                 # flow_1 = m_speed * d_2
#                 # t = round(self.time, 2)
#                 # self.stored_data[t].update({
#                 #     "flow_1": flow_1,
#                 #     "density": d_2,
#                 # })
#     #
#     #             # # # # # 2023.03.09.17.45修改traci进行VSL的实施控制！！！！！！！！！！！
#     #
#     #             for veh_id in self.master_kernel.vehicle.get_ids():
#     #                 t = round(self.time, 2)
#     #
#     #                 # some miscellaneous pre-processing 一些杂项预处理
#     #                 position = kv.get_2d_position(veh_id)
#     #
#     #                 # Make sure dictionaries corresponding to the vehicle and time are available.
#     #                 # 确保与车辆和时间相对应的词典可用
#     #                 if veh_id not in self.stored_data.keys():
#     #                     self.stored_data[veh_id] = dict()
#     #                 if t not in self.stored_data[veh_id].keys():
#     #                     self.stored_data[veh_id][t] = dict()
#     #
#     #                 # Add the speed, position, and lane data.
#     #                 self.stored_data[veh_id][t].update({
#     #                     "speed": kv.get_speed(veh_id),
#     #                     "lane_number": kv.get_lane(veh_id),
#     #                     "edge_id": kv.get_edge(veh_id),
#     #                     "relative_position": kv.get_position(veh_id),
#     #                     "x": position[0],
#     #                     "y": position[1],
#     #                     "headway": kv.get_headway(veh_id),
#     #                     "leader_id": kv.get_leader(veh_id),
#     #                     "follower_id": kv.get_follower(veh_id),
#     #                     "leader_rel_speed":
#     #                         kv.get_speed(kv.get_leader(veh_id))
#     #                         - kv.get_speed(veh_id),
#     #                     "target_accel_with_noise_with_failsafe":
#     #                         kv.get_accel(veh_id, noise=True, failsafe=True),
#     #                     "target_accel_no_noise_no_failsafe":
#     #                         kv.get_accel(veh_id, noise=False, failsafe=False),
#     #                     "target_accel_with_noise_no_failsafe":
#     #                         kv.get_accel(veh_id, noise=True, failsafe=False),
#     #                     "target_accel_no_noise_with_failsafe":
#     #                         kv.get_accel(veh_id, noise=False, failsafe=True),
#     #                     "realized_accel":
#     #                         kv.get_realized_accel(veh_id),
#     #                     "road_grade": kv.get_road_grade(veh_id),
#     #                     "distance": kv.get_distance(veh_id),
#     #                 })
#
#     def close(self):
#         """See parent class."""
#         # Save the emission data to a csv.
#         if self.emission_path is not None:
#             self.save_emission()
#
#         self.kernel_api.close()
#
#     def check_collision(self):
#         """See parent class."""
#         return self.kernel_api.simulation.getStartingTeleportNumber() != 0
#
#     def start_simulation(self, network, sim_params):
#         """Start a sumo simulation instance.
#
#         This method performs the following operations:
#
#         1. It collect the simulation step size and the emission path
#            information. If an emission path is specifies, it ensures that the
#            path exists.
#         2. It also uses the configuration files created by the network class to
#            initialize a sumo instance.
#         3. Finally, It initializes a traci connection to interface with sumo
#            from Python and returns the connection.
#         """
#         # Save the simulation step size (for later use).
#         self.sim_step = sim_params.sim_step
#
#         # Update the emission path term.
#         self.emission_path = sim_params.emission_path
#         if self.emission_path is not None:
#             ensure_dir(self.emission_path)
#
#         error = None
#         for _ in range(RETRIES_ON_ERROR):
#             try:
#                 # port number the sumo instance will be run on
#                 port = sim_params.port
#
#                 sumo_binary = "sumo-gui" if sim_params.render is True \
#                     else "sumo"
#
#                 # command used to start sumo
#                 sumo_call = [
#                     sumo_binary, "-c", network.cfg,
#                     "--remote-port", str(sim_params.port),
#                     "--num-clients", str(sim_params.num_clients),
#                     "--step-length", str(sim_params.sim_step)
#                 ]
#
#                 # use a ballistic integration step (if request)
#                 if sim_params.use_ballistic:
#                     sumo_call.append("--step-method.ballistic")
#
#                 # ignore step logs (if requested)
#                 if sim_params.no_step_log:
#                     sumo_call.append("--no-step-log")
#
#                 # add the lateral resolution of the sublanes 添加子线的横向分辨率 (if requested)
#                 if sim_params.lateral_resolution is not None:
#                     sumo_call.append("--lateral-resolution")
#                     sumo_call.append(str(sim_params.lateral_resolution))
#
#                 if sim_params.overtake_right:
#                     sumo_call.append("--lanechange.overtake-right")
#                     sumo_call.append("true")
#
#                 # specify a simulation seed (if requested)
#                 if sim_params.seed is not None:
#                     sumo_call.append("--seed")
#                     sumo_call.append(str(sim_params.seed))
#
#                 if not sim_params.print_warnings:
#                     sumo_call.append("--no-warnings")
#                     sumo_call.append("true")
#
#                 # set the time it takes for a gridlock teleport to occur
#                 sumo_call.append("--time-to-teleport")
#                 sumo_call.append(str(int(sim_params.teleport_time)))
#
#                 # check collisions at intersections
#                 sumo_call.append("--collision.check-junctions")
#                 sumo_call.append("true")
#
#                 logging.info(" Starting SUMO on port " + str(port))
#                 logging.debug(" Cfg file: " + str(network.cfg))
#                 if sim_params.num_clients > 1:
#                     logging.info(" Num clients are" +
#                                  str(sim_params.num_clients))
#                 logging.debug(" Emission file: " + str(self.emission_path))
#                 logging.debug(" Step length: " + str(sim_params.sim_step))
#
#                 # Opening the I/O thread to SUMO
#                 self.sumo_proc = subprocess.Popen(
#                     sumo_call,
#                     stdout=subprocess.DEVNULL
#                 )
#
#                 # wait a small period of time for the subprocess to activate
#                 # before trying to connect with traci
#                 if os.environ.get("TEST_FLAG", 0):
#                     time.sleep(0.1)
#                 else:
#                     time.sleep(config.SUMO_SLEEP)
#
#                 traci_connection = traci.connect(port, numRetries=100)
#                 traci_connection.setOrder(0)
#                 traci_connection.simulationStep()
#
#                 return traci_connection
#             except Exception as e:
#                 print("Error during start: {}".format(traceback.format_exc()))
#                 error = e
#                 self.teardown_sumo()
#         raise error
#
#     def teardown_sumo(self):
#         """Kill the sumo subprocess instance."""
#         try:
#             os.killpg(self.sumo_proc.pid, signal.SIGTERM)
#         except Exception as e:
#             print("Error during teardown: {}".format(e))
#
#     def save_emission(self, run_id=0):
#         """Save any collected emission data to a csv file.
#
#         If not data was collected, nothing happens. Moreover, any internally
#         stored data by this class is clear whenever data is stored.
#         如果没有收集到数据，什么也不会发生。此外，每当存储数据时，此类内部存储的任何数据都是清晰的。可以在交互模式下单击各个轨迹，在控制台上打印车辆Id
#
#         Parameters
#         ----------
#         run_id : int
#             the rollout number, appended to the name of the emission file. Used
#             to store emission files from multiple rollouts run sequentially.
#         """
#         # If there is no stored data, ignore this operation. This is to ensure
#         # that data isn't deleted if the operation is called twice.
#         if len(self.stored_data) == 0:
#             return
#
#         # Get a csv name for the emission file.
#         name = "{}-{}_emission.csv".format(
#             self.master_kernel.network.network.name, run_id)
#
#         # The name of all stored data-points (excluding id and time)
#         stored_ids = [
#             "flow_1",
#             "m_speed",
#             "num",
#             "density",
#             # "speed",
#             # "headway",
#             # "leader_id",
#             # "target_accel_with_noise_with_failsafe",
#             # "target_accel_no_noise_no_failsafe",
#             # "target_accel_with_noise_no_failsafe",
#             # "target_accel_no_noise_with_failsafe",
#             # "realized_accel",
#             # "road_grade",
#             # "edge_id",
#             # "lane_number",
#             # "distance",
#             # "relative_position",
#             # "follower_id",
#             # "leader_rel_speed",
#         ]
#
#         # Update the stored data to push to the csv file.更新存储的数据以推送到csv文件。
#         # final_data = {"time": [], "id": []}
#         final_data = {"time": []}
#
#         final_data.update({key: [] for key in stored_ids})
#
#         for t in self.stored_data.keys():
#             final_data['time'].append(t)
#             # final_data['id'].append(veh_id)
#             for key in stored_ids:
#                 final_data[key].append(self.stored_data[t][key])
#         # for veh_id in self.stored_data.keys():
#         #     for t in self.stored_data[veh_id].keys():
#         #         final_data['time'].append(t)
#         #         final_data['id'].append(veh_id)
#         #         for key in stored_ids:
#         #             final_data[key].append(self.stored_data[veh_id][t][key])
#
#         with open(os.path.join(self.emission_path, name), "w") as f:
#             print(os.path.join(self.emission_path, name), self.emission_path)
#             writer = csv.writer(f, delimiter=',')
#             writer.writerow(final_data.keys())
#             writer.writerows(zip(*final_data.values()))
#
#         # Clear all memory from the stored data. This is useful if this
#         # function is called in between resets.
#         self.stored_data.clear()
#     # def save_emission(self, run_id=0):
#     #     """Save any collected emission data to a csv file.
#     #
#     #     If not data was collected, nothing happens. Moreover, any internally
#     #     stored data by this class is clear whenever data is stored.
#     #     如果没有收集到数据，什么也不会发生。此外，每当存储数据时，此类内部存储的任何数据都是清晰的。可以在交互模式下单击各个轨迹，在控制台上打印车辆Id
#     #
#     #     Parameters
#     #     ----------
#     #     run_id : int
#     #         the rollout number, appended to the name of the emission file. Used
#     #         to store emission files from multiple rollouts run sequentially.
#     #     """
#     #     # If there is no stored data, ignore this operation. This is to ensure
#     #     # that data isn't deleted if the operation is called twice.
#     #     if len(self.stored_data) == 0:
#     #         return
#     #
#     #     # Get a csv name for the emission file.
#     #     name = "{}-{}_emission.csv".format(
#     #         self.master_kernel.network.network.name, run_id)
#     #
#     #     # The name of all stored data-points (excluding id and time)
#     #     stored_ids = [
#     #         "x",
#     #         "y",
#     #         "speed",
#     #         "headway",
#     #         "leader_id",
#     #         "target_accel_with_noise_with_failsafe",
#     #         "target_accel_no_noise_no_failsafe",
#     #         "target_accel_with_noise_no_failsafe",
#     #         "target_accel_no_noise_with_failsafe",
#     #         "realized_accel",
#     #         "road_grade",
#     #         "edge_id",
#     #         "lane_number",
#     #         "distance",
#     #         "relative_position",
#     #         "follower_id",
#     #         "leader_rel_speed",
#     #     ]
#     #
#     #     # Update the stored data to push to the csv file.更新存储的数据以推送到csv文件。
#     #     final_data = {"time": [], "id": []}
#     #     final_data.update({key: [] for key in stored_ids})
#     #
#     #     for veh_id in self.stored_data.keys():
#     #         for t in self.stored_data[veh_id].keys():
#     #             final_data['time'].append(t)
#     #             final_data['id'].append(veh_id)
#     #             for key in stored_ids:
#     #                 final_data[key].append(self.stored_data[veh_id][t][key])
#     #
#     #     with open(os.path.join(self.emission_path, name), "w") as f:
#     #         print(os.path.join(self.emission_path, name), self.emission_path)
#     #         writer = csv.writer(f, delimiter=',')
#     #         writer.writerow(final_data.keys())
#     #         writer.writerows(zip(*final_data.values()))
#     #
#     #     # Clear all memory from the stored data. This is useful if this
#     #     # function is called in between resets.
#     #     self.stored_data.clear()

"""Script containing the TraCI simulation kernel class."""

from flow.core.kernel.simulation import KernelSimulation
from flow.core.util import ensure_dir
import flow.config as config
import traci.constants as tc
import traci
import traceback
import os
import time
import logging
import subprocess
import signal
import csv

import numpy as np
# Number of retries on restarting SUMO before giving up
# 放弃前重启 SUMO 的重试次数
RETRIES_ON_ERROR = 10
Kp=0.002
q_c=[0]*5000
o_max=0.5228
global m
m=0

# x=[0,0.0013,0.0032,0.00507814,0.00722536,0.00856738,0.0107146,0.0117882,0.0131302,0.015,0.0158,0.016,0.0163,0.0165,0.01742,0.0183,0.0194,0.0205,0.0223,0.02655,0.03621,0.04749,0.052317,0.0606376,0.0654688,0.07,0.0746,0.0804994,0.085867,0.0891,0.0961,0.101435,0.1063,0.12,0.12546]
# y=[0,0.051,0.1,0.1487,0.184585,0.225585,0.266585,0.28965,0.315273,0.346,0.37677,0.38,0.39,0.396,0.4165,0.41,0.40,0.39,0.38,0.376774,0.3614,0.3486,0.34474,0.337,0.3268,0.32,0.3127,0.289648,0.276836,0.273,0.24865,0.24,0.2141,0.165,0.1402]
# parameter=np.polyfit(x,y,5)
# y1=np.poly1d(parameter)
x=[0,0.01,0.0145,0.02,0.0232,0.02674,0.032,0.05329,0.06656,0.0775,0.0867,0.094,0.1]
y=[0,0.254,0.3678,0.464,0.502,0.5228,0.5,0.34,0.32,0.31,0.29,0.25,0.196]
parameter=np.polyfit(x,y,5)
p=np.poly1d(parameter)
# print(p)
# print (0.35128858)/(pynverse.inversefunc(p, y_values=0.35128858, domain=[0.024, 0.11]))
y1=p(x)
class TraCISimulation(KernelSimulation):
    """Sumo simulation kernel.

    Extends flow.core.kernel.simulation.KernelSimulation

    Attributes
    ----------
    sumo_proc : subprocess.Popen
        contains the subprocess.Popen instance used to start traci
        包含用于启动 traci 的 subprocess.Popen 实例
    sim_step : float
        seconds per simulation step
        每个模拟步骤的秒数
    emission_path : str or None
        Path to the folder in which to create the emissions output. Emissions
        output is not generated if this value is not specified
        在其中创建排放量输出的文件夹的路径。 如果未指定此值，则不会生成排放量输出
    time : float
        used to internally keep track of the simulation time
        用于在内部跟踪仿真时间
    stored_data : dict <str, dict <float, dict <str, Any>>>
        a dict object used to store additional data if an emission file is
        provided. The first key corresponds to the name of the vehicle, the
        second corresponds to the time the sample was issued, and the final
        keys represent the additional data stored at every given time for every
        vehicle, and consists of the following keys:
        如果提供了输出文件，则用于存储附加数据的 dict 对象。 第一个键对应车辆的名称，第二个键对应样本发布时间，
        最后一个键代表每辆车在每个给定时间存储的附加数据，由以下键组成：

        * acceleration (no noise): the accelerations issued to the vehicle,
          excluding noise
        * acceleration (requested): the requested acceleration by the vehicle,
          including noise
        * acceleration (actual): the actual acceleration by the vehicle,
          collected by computing the difference between the speeds of the
          vehicle and dividing it by the sim_step term
    """

    def __init__(self, master_kernel):
        """Instantiate the sumo simulator kernel. 实例化SUMO模拟器内核。

        Parameters
        ----------
        master_kernel : flow.core.kernel.Kernel
            the higher level kernel (used to call methods from other
            sub-kernels)
        """
        KernelSimulation.__init__(self, master_kernel)

        self.sumo_proc = None
        self.sim_step = None
        self.emission_path = None
        self.time = 0
        self.stored_data = dict()
        self.stored_data_1 = dict()

    def pass_api(self, kernel_api):
        """See parent class.

        Also initializes subscriptions.
        """
        KernelSimulation.pass_api(self, kernel_api)

        # subscribe some simulation parameters needed to check for entering,
        # exiting, and colliding vehicles
        # 订阅一些需要检查进入、退出和碰撞车辆的模拟参数
        self.kernel_api.simulation.subscribe([
            tc.VAR_DEPARTED_VEHICLES_IDS,
            tc.VAR_ARRIVED_VEHICLES_IDS,
            tc.VAR_TELEPORT_STARTING_VEHICLES_IDS,
            tc.VAR_TIME_STEP,
            tc.VAR_DELTA_T,
            tc.VAR_LOADED_VEHICLES_NUMBER,
            tc.VAR_DEPARTED_VEHICLES_NUMBER,
            tc.VAR_ARRIVED_VEHICLES_NUMBER
        ])

    def simulation_step(self):
        """See parent class."""
        self.kernel_api.simulationStep()

    def update(self, reset):
        """See parent class."""
        global m
        if reset:
            self.time = 0
        else:
            self.time += self.sim_step
            m+=1


        # Collect the additional data to store in the emission file.
        # 收集附加数据以存储在输出文件中。
        if self.emission_path is not None:
            kv = self.master_kernel.vehicle
            m_speed = self.master_kernel.network.get_laststep_meanspeed('4')
            d_2 = self.master_kernel.network.get_laststep_vehiclenum('4') / (500 * 2)
            flow_1 = m_speed * d_2
            t = round(self.time, 2)
            if t not in self.stored_data_1.keys():
                self.stored_data_1[t] = dict()
            self.stored_data_1[t].update({
                "flow_1": (self.master_kernel.network.get_laststep_vehiclenum('4') / (500 * 2)) * abs(
                    self.master_kernel.network.get_laststep_meanspeed('4')),
                "m_speed": self.master_kernel.network.get_laststep_meanspeed('4'),
                "num": self.master_kernel.network.get_laststep_vehiclenum('4'),
                "density": self.master_kernel.network.get_laststep_vehiclenum('4') / (500 * 2),
            })
            # 上游车辆流量
            d_1 = self.master_kernel.network.get_laststep_meanspeed('5')
            d_3 = self.master_kernel.network.get_laststep_vehiclenum('5')/(250)
            d = abs(d_1)*d_3
            # print(d)
                        # VSL控制
            q_c[m] = q_c[m-1]+Kp*(o_max-d)
            y1 = lambda x:-1.283e+06*x**5 + 2.606e+05*x**4 - 1.279e+04*x**3 - 360.6*x**2 + 33.66*x - 0.009375
            # print(q_c)
            #
            # # 用到的函数，速度，车辆数（求解密度），veh/m*m/s==veh/s即得到车流量信息
            if m_speed < 11:
                if q_c[m] > 0.183 and q_c[m] < 0.510237:
                    mmm = pynverse.inversefunc(y1, y_values=q_c[m], domain=[0.031371, 0.1], accuracy=1)#031371
                    # print(mmm)
                    v = q_c[m]/(mmm)
                    # self.master_kernel.network.set_max_speed('2', v)
                    # self.master_kernel.network.set_max_speed('3', v)
                    # 2023.11.24进行服从率的修改实验
                    for vsl_id in self.master_kernel.vehicle.get_vsl_ids():
                        if kv.get_road_id(vsl_id ) =="3":
                            print(vsl_id)
                            kv.set_max_speed(vsl_id, v)
                        else:
                            kv.set_max_speed(vsl_id, 30)
            # if q_c[m] > 0.183 and q_c[m] < 0.513217:
            #     mmm = pynverse.inversefunc(y1, y_values=q_c[m], domain=[0.031371, 0.1])
            #     # print(mmm)
            #     v = q_c[m] / (mmm)
            #     self.master_kernel.network.set_max_speed('2', v)
            #     # self.master_kernel.network.set_max_speed('3', v)
            #     print(v)
            for veh_id in self.master_kernel.vehicle.get_ids():
                t = round(self.time, 2)

                # some miscellaneous pre-processing
                position = kv.get_2d_position(veh_id)

                # Make sure dictionaries corresponding to the vehicle and
                # time are available.
                # 确保车辆和时间对应的词典可用。
                if veh_id not in self.stored_data.keys():
                    self.stored_data[veh_id] = dict()
                if t not in self.stored_data[veh_id].keys():
                    self.stored_data[veh_id][t] = dict()

                # Add the speed, position, and lane data.
                self.stored_data[veh_id][t].update({
                    "speed": kv.get_speed(veh_id),
                    "lane_number": kv.get_lane(veh_id),
                    "edge_id": kv.get_edge(veh_id),
                    "relative_position": kv.get_position(veh_id),
                    "x": position[0],
                    "y": position[1],
                    "headway": kv.get_headway(veh_id),
                    "leader_id": kv.get_leader(veh_id),
                    "follower_id": kv.get_follower(veh_id),
                    "leader_rel_speed":
                        kv.get_speed(kv.get_leader(veh_id))
                        - kv.get_speed(veh_id),
                    "target_accel_with_noise_with_failsafe":
                        kv.get_accel(veh_id, noise=True, failsafe=True),
                    "target_accel_no_noise_no_failsafe":
                        kv.get_accel(veh_id, noise=False, failsafe=False),
                    "target_accel_with_noise_no_failsafe":
                        kv.get_accel(veh_id, noise=True, failsafe=False),
                    "target_accel_no_noise_with_failsafe":
                        kv.get_accel(veh_id, noise=False, failsafe=True),
                    "realized_accel":
                        kv.get_realized_accel(veh_id),
                    "road_grade": kv.get_road_grade(veh_id),
                    "distance": kv.get_distance(veh_id),
                })

    def close(self):
        """See parent class."""
        # Save the emission data to a csv.
        if self.emission_path is not None:
            self.save_emission()

        self.kernel_api.close()

    def check_collision(self):
        """See parent class."""
        return self.kernel_api.simulation.getStartingTeleportNumber() != 0

    def start_simulation(self, network, sim_params):
        """Start a sumo simulation instance.

        This method performs the following operations:

        1. It collect the simulation step size and the emission path
           information. If an emission path is specifies, it ensures that the
           path exists.
           它收集仿真步长和输出路径信息。 如果指定了输出路径，它会确保该路径存在。
        2. It also uses the configuration files created by the network class to
           initialize a sumo instance.
           它还使用网络类创建的配置文件来初始化SUMO实例。
        3. Finally, It initializes a traci connection to interface with sumo
           from Python and returns the connection.
           最后，它初始化一个 traci 连接以与来自 Python 的 sumo 接口并返回连接。
        """
        # Save the simulation step size (for later use).
        self.sim_step = sim_params.sim_step

        # Update the emission path term.
        self.emission_path = sim_params.emission_path
        if self.emission_path is not None:
            ensure_dir(self.emission_path)

        error = None
        for _ in range(RETRIES_ON_ERROR):
            try:
                # port number the sumo instance will be run on
                port = sim_params.port

                sumo_binary = "sumo-gui" if sim_params.render is True \
                    else "sumo"

                # command used to start sumo
                sumo_call = [
                    sumo_binary, "-c", network.cfg,
                    "--remote-port", str(sim_params.port),
                    "--num-clients", str(sim_params.num_clients),
                    "--step-length", str(sim_params.sim_step)
                ]

                # use a ballistic integration step (if request)
                if sim_params.use_ballistic:
                    sumo_call.append("--step-method.ballistic")

                # ignore step logs (if requested)
                if sim_params.no_step_log:
                    sumo_call.append("--no-step-log")

                # add the lateral resolution of the sublanes (if requested)
                if sim_params.lateral_resolution is not None:
                    sumo_call.append("--lateral-resolution")
                    sumo_call.append(str(sim_params.lateral_resolution))

                if sim_params.overtake_right:
                    sumo_call.append("--lanechange.overtake-right")
                    sumo_call.append("true")

                # specify a simulation seed (if requested)
                if sim_params.seed is not None:
                    sumo_call.append("--seed")
                    sumo_call.append(str(sim_params.seed))

                if not sim_params.print_warnings:
                    sumo_call.append("--no-warnings")
                    sumo_call.append("true")

                # set the time it takes for a gridlock teleport to occur
                sumo_call.append("--time-to-teleport")
                sumo_call.append(str(int(sim_params.teleport_time)))

                # check collisions at intersections
                sumo_call.append("--collision.check-junctions")
                sumo_call.append("true")

                logging.info(" Starting SUMO on port " + str(port))
                logging.debug(" Cfg file: " + str(network.cfg))
                if sim_params.num_clients > 1:
                    logging.info(" Num clients are" +
                                 str(sim_params.num_clients))
                logging.debug(" Emission file: " + str(self.emission_path))
                logging.debug(" Step length: " + str(sim_params.sim_step))

                # Opening the I/O thread to SUMO
                self.sumo_proc = subprocess.Popen(
                    sumo_call,
                    stdout=subprocess.DEVNULL
                )

                # wait a small period of time for the subprocess to activate
                # before trying to connect with traci
                if os.environ.get("TEST_FLAG", 0):
                    time.sleep(0.1)
                else:
                    time.sleep(config.SUMO_SLEEP)

                traci_connection = traci.connect(port, numRetries=100)
                traci_connection.setOrder(0)
                traci_connection.simulationStep()

                return traci_connection
            except Exception as e:
                print("Error during start: {}".format(traceback.format_exc()))
                error = e
                self.teardown_sumo()
        raise error

    def teardown_sumo(self):
        """Kill the sumo subprocess instance."""
        """杀死 sumo 子进程实例。"""
        try:
            os.killpg(self.sumo_proc.pid, signal.SIGTERM)
        except Exception as e:
            print("Error during teardown: {}".format(e))

    def save_emission(self, run_id=0):
        """Save any collected emission data to a csv file.

        If not data was collected, nothing happens. Moreover, any internally
        stored data by this class is clear whenever data is stored.
        如果没有收集到数据，什么也不会发生。此外，每当存储数据时，此类内部存储的任何数据都是清晰的。可以在交互模式下单击各个轨迹，在控制台上打印车辆Id

        Parameters
        ----------
        run_id : int
            the rollout number, appended to the name of the emission file. Used
            to store emission files from multiple rollouts run sequentially.
        """
        # If there is no stored data, ignore this operation. This is to ensure
        # that data isn't deleted if the operation is called twice.
        if len(self.stored_data) == 0:
            return
        if len(self.stored_data_1) == 0:
            return
        # Get a csv name for the emission file.
        name = "{}-{}_emission.csv".format(
            self.master_kernel.network.network.name, run_id)
        name_1 = "{}-{}_speed_emission.csv".format(
            self.master_kernel.network.network.name, run_id)

        # The name of all stored data-points (excluding id and time)
        stored_ids_1 = [
            "flow_1",
            "m_speed",
            "num",
            "density",
            # "speed",
            # "headway",
            # "leader_id",
            # "target_accel_with_noise_with_failsafe",
            # "target_accel_no_noise_no_failsafe",
            # "target_accel_with_noise_no_failsafe",
            # "target_accel_no_noise_with_failsafe",
            # "realized_accel",
            # "road_grade",
            # "edge_id",
            # "lane_number",
            # "distance",
            # "relative_position",
            # "follower_id",
            # "leader_rel_speed",
        ]
        stored_ids = [
            "speed",
            "headway",
            "leader_id",
            "target_accel_with_noise_with_failsafe",
            "target_accel_no_noise_no_failsafe",
            "target_accel_with_noise_no_failsafe",
            "target_accel_no_noise_with_failsafe",
            "realized_accel",
            "road_grade",
            "edge_id",
            "lane_number",
            "distance",
            "relative_position",
            "follower_id",
            "leader_rel_speed",
        ]



        # Update the stored data to push to the csv file.更新存储的数据以推送到csv文件。
        final_data = {"time": [], "id": []}
        final_data_1 = {"time": []}

        final_data.update({key: [] for key in stored_ids})
        final_data_1.update({key: [] for key in stored_ids_1})


        for t in self.stored_data_1.keys():
            final_data_1['time'].append(t)
            # final_data['id'].append(veh_id)
            for key in stored_ids_1:
                final_data_1[key].append(self.stored_data_1[t][key])
        for veh_id in self.stored_data.keys():
            for t in self.stored_data[veh_id].keys():
                final_data['time'].append(t)
                final_data['id'].append(veh_id)
                for key in stored_ids:
                    final_data[key].append(self.stored_data[veh_id][t][key])

        with open(os.path.join(self.emission_path, name), "w") as f:
            print(os.path.join(self.emission_path, name), self.emission_path)
            writer = csv.writer(f, delimiter=',')
            writer.writerow(final_data.keys())
            writer.writerows(zip(*final_data.values()))

        with open(os.path.join(self.emission_path, name_1), "w") as f:
            print(os.path.join(self.emission_path, name_1), self.emission_path)
            writer = csv.writer(f, delimiter=',')
            writer.writerow(final_data_1.keys())
            writer.writerows(zip(*final_data_1.values()))

        # Clear all memory from the stored data. This is useful if this
        # function is called in between resets.
        self.stored_data.clear()
        self.stored_data_1.clear()

    # def save_emission(self, run_id=0):
    #     """Save any collected emission data to a csv file.
    #
    #     If not data was collected, nothing happens. Moreover, any internally
    #     stored data by this class is clear whenever data is stored.
    #
    #     Parameters
    #     ----------
    #     run_id : int
    #         the rollout number, appended to the name of the emission file. Used
    #         to store emission files from multiple rollouts run sequentially.
    #     """
    #     # If there is no stored data, ignore this operation. This is to ensure
    #     # that data isn't deleted if the operation is called twice.
    #     # 如果没有存储数据，则忽略此操作。这是为了确保如果操作被调用两次，数据不会被删除。
    #     if len(self.stored_data) == 0:
    #         return
    #
    #     # Get a csv name for the emission file.
    #     name = "{}-{}_emission.csv".format(
    #         self.master_kernel.network.network.name, run_id)
    #
    #     # The name of all stored data-points (excluding id and time)
    #     stored_ids = [
    #         "x",
    #         "y",
    #         "speed",
    #         "headway",
    #         "leader_id",
    #         "target_accel_with_noise_with_failsafe",
    #         "target_accel_no_noise_no_failsafe",
    #         "target_accel_with_noise_no_failsafe",
    #         "target_accel_no_noise_with_failsafe",
    #         "realized_accel",
    #         "road_grade",
    #         "edge_id",
    #         "lane_number",
    #         "distance",
    #         "relative_position",
    #         "follower_id",
    #         "leader_rel_speed",
    #     ]
    #
    #     # Update the stored data to push to the csv file.
    #     final_data = {"time": [], "id": []}
    #     final_data.update({key: [] for key in stored_ids})
    #
    #     for veh_id in self.stored_data.keys():
    #         for t in self.stored_data[veh_id].keys():
    #             final_data['time'].append(t)
    #             final_data['id'].append(veh_id)
    #             for key in stored_ids:
    #                 final_data[key].append(self.stored_data[veh_id][t][key])
    #
    #     with open(os.path.join(self.emission_path, name), "w") as f:
    #         print(os.path.join(self.emission_path, name), self.emission_path)
    #         writer = csv.writer(f, delimiter=',')
    #         writer.writerow(final_data.keys())
    #         writer.writerows(zip(*final_data.values()))
    #
    #     # Clear all memory from the stored data. This is useful if this
    #     # function is called in between resets.
    #     self.stored_data.clear()







