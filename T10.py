# 信号灯！！！
from flow.core.params import NetParams
from flow.networks.traffic_light_grid import TrafficLightGridNetwork
from flow.core.params import TrafficLightParams
from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams, \
    InFlows, SumoCarFollowingParams
from flow.core.params import VehicleParams
from gym.spaces.box import Box
from gym.spaces import Tuple
from gym.spaces.discrete import Discrete
import numpy as np
from flow.core import rewards
inner_length = 300
long_length = 500
short_length = 300
n = 2 # rows
m = 3 # columns
num_cars_left = 20
num_cars_right = 20
num_cars_top = 20
num_cars_bot = 20
tot_cars = (num_cars_left + num_cars_right) * m \
    + (num_cars_top + num_cars_bot) * n
grid_array = {"short_length": short_length, "inner_length": inner_length,
              "long_length": long_length, "row_num": n, "col_num": m,
              "cars_left": num_cars_left, "cars_right": num_cars_right,
              "cars_top": num_cars_top, "cars_bot": num_cars_bot}
tl_logic = TrafficLightParams()
nodes = ["center0", "center1", "center2", "center3", "center4", "center5"]
phases = [{"duration": "31", "state": "GrGr"},
          {"duration": "6", "state": "yryr"},
          {"duration": "31", "state": "rGrG"},
          {"duration": "6", "state": "ryry"}]
for node_id in nodes:
    tl_logic.add(node_id, tls_type="static", programID="1", offset=None, phases=phases)
additional_net_params = {"grid_array": grid_array, "speed_limit": 35,
                         "horizontal_lanes": 1, "vertical_lanes": 1,
                         "traffic_lights": True}
net_params = NetParams(additional_params=additional_net_params)
network = TrafficLightGridNetwork(name="grid",
                            vehicles=VehicleParams(),
                            net_params=net_params,
                            initial_config=InitialConfig(),
                            traffic_lights=tl_logic)
# 静态交通灯
tl_logic = TrafficLightParams(baseline=False)
phases = [{"duration": "31", "state": "GrGr"},
          {"duration": "6", "state": "yryr"},
          {"duration": "31", "state": "rGrG"},
          {"duration": "6", "state": "ryry"}]
tl_logic.add("center0", phases=phases, programID=1)
# 自动信号灯，可根据交通流情况自行安排信号周期
tl_logic = TrafficLightParams(baseline=False)
phases = [{"duration": "31", "minDur": "8", "maxDur": "45", "state": "GrGr"},
          {"duration": "6", "minDur": "3", "maxDur": "6", "state": "yryr"},
          {"duration": "31", "minDur": "8", "maxDur": "45", "state": "rGrG"},
          {"duration": "6", "minDur": "3", "maxDur": "6", "state": "ryry"}]
tl_logic.add("center1",
             tls_type="actuated",
             programID="1",
             phases=phases,
             maxGap=5.0,
             detectorGap=0.9,
             showDetectors=False)
tl_logic.add("center2",
             tls_type="actuated")
# 基线自动信号灯
tl_type = "actuated"
program_id = 1
max_gap = 3.0
detector_gap = 0.8
show_detectors = True
phases = [{"duration": "31", "minDur": "8", "maxDur": "45", "state": "GrGr"},
        {"duration": "6", "minDur": "3", "maxDur": "6", "state": "yryr"},
        {"duration": "31", "minDur": "8", "maxDur": "45", "state": "rGrG"},
        {"duration": "6", "minDur": "3", "maxDur": "6", "state": "ryry"}]
tl_logic = TrafficLightParams(baseline=True)
additional_net_params = {"grid_array": grid_array,
                         "speed_limit": 35,
                         "horizontal_lanes": 1,
                         "vertical_lanes": 1,
                         "traffic_lights": True,
                         "tl_logic": tl_logic}
# RL 控制的信号灯
additional_net_params = {"speed_limit": 35, "grid_array": grid_array,
                         "horizontal_lanes": 1, "vertical_lanes": 1,
                         "traffic_lights": True}
# # keeps track of the last time the traffic lights in an intersection were allowed to change
# # (the last time the lights were allowed to change from a red-green state to a red-yellow state).
# self.last_change = np.zeros((self.rows * self.cols, 1))
# # keeps track of the direction of the intersection (the direction that is currently being allowed
# # to flow. 0 indicates flow from top to bottom, and 1 indicates flow from left to right.)
# self.direction = np.zeros((self.rows * self.cols, 1))
# # value of 1 indicates that the intersection is in a red-yellow state (traffic lights are red for
# # one way (e.g. north-south), while the traffic lights for the other way (e.g. west-east) are yellow.
# # 0 indicates that the intersection is in a red-green state.
# self.currently_yellow = np.zeros((self.rows * self.cols, 1))
additional_env_params = {"target_velocity": 50, "switch_time": 3.0}
@property
def action_space(self):
    if self.discrete:
        return Discrete(2 ** self.num_traffic_lights)
    else:
        return Box(
                low=0,
                high=1,
                shape=(self.num_traffic_lights,),
                dtype=np.float32)
@property
def observation_space(self):
    speed = Box(
            low=0,
            high=1,
            shape=(self.initial_vehicles.num_vehicles,),
            dtype=np.float32)
    dist_to_intersec = Box(
            low=0.,
            high=np.inf,
            shape=(self.initial_vehicles.num_vehicles,),
            dtype=np.float32)
    edge_num = Box(
            low=0.,
            high=1,
            shape=(self.initial_vehicles.num_vehicles,),
            dtype=np.float32)
    traffic_lights = Box(
            low=0.,
            high=1,
            shape=(3 * self.rows * self.cols,),
            dtype=np.float32)
    return Tuple((speed, dist_to_intersec, edge_num, traffic_lights))
def get_state(self):
    # compute the normalizers
        grid_array = self.net_params.additional_params["grid_array"]
        max_dist = max(grid_array["short_length"],
                       grid_array["long_length"],
                       grid_array["inner_length"])
        # get the state arrays
        speeds = [
            self.k.vehicle.get_speed(veh_id) / self.k.network.max_speed()
            for veh_id in self.k.vehicle.get_ids()
        ]
        dist_to_intersec = [
            self.get_distance_to_intersection(veh_id) / max_dist
            for veh_id in self.k.vehicle.get_ids()
        ]
        edges = [
            self._convert_edge(self.k.vehicle.get_edge(veh_id)) /
            (self.k.network.network.num_edges - 1)
            for veh_id in self.k.vehicle.get_ids()
        ]
        state = [
            speeds, dist_to_intersec, edges,
            self.last_change.flatten().tolist(),
            self.direction.flatten().tolist(),
            self.currently_yellow.flatten().tolist()
        ]
        return np.array(state)
def compute_reward(self, rl_actions, **kwargs):
    return - rewards.min_delay_unscaled(self) - rewards.boolean_action_penalty(rl_actions >= 0.5, gain=1.0)
def _apply_rl_actions(self, rl_actions):
        """See class definition."""
        # check if the action space is discrete
        if self.discrete:
            # convert single value to list of 0's and 1's
            rl_mask = [int(x) for x in list('{0:0b}'.format(rl_actions))]
            rl_mask = [0] * (self.num_traffic_lights - len(rl_mask)) + rl_mask
        else:
            # convert values less than 0.5 to zero and above 0.5 to 1. 0
            # indicates that we should not switch the direction, and 1 indicates
            # that switch should happen
            rl_mask = rl_actions > 0.5
        # Loop through the traffic light nodes
        for i, action in enumerate(rl_mask):
            if self.currently_yellow[i] == 1:  # currently yellow
                # Code to change from yellow to red
                self.last_change[i] += self.sim_step
                # Check if our timer has exceeded the yellow phase, meaning it
                # should switch to red
                if self.last_change[i] >= self.min_switch_time:
                    if self.direction[i] == 0:
                        self.k.traffic_light.set_state(
                            node_id='center{}'.format(i),
                            state="GrGr")
                    else:
                        self.k.traffic_light.set_state(
                            node_id='center{}'.format(i),
                            state='rGrG')
                    self.currently_yellow[i] = 0
            else:
                # Code to change to yellow
                if action:
                    if self.direction[i] == 0:
                        self.k.traffic_light.set_state(
                            node_id='center{}'.format(i),
                            state='yryr')
                    else:
                        self.k.traffic_light.set_state(
                            node_id='center{}'.format(i),
                            state='ryry')
                self.last_change[i] = 0.0
                self.direction[i] = not self.direction[i]
                self.currently_yellow[i] = 1
