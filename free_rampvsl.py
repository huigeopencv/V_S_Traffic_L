from flow.core.params import NetParams
from flow.core.params import VehicleParams
from flow.core.params import InitialConfig
from flow.networks import MiniCityNetwork
# from flow.networks import BayBridgeNetwork
# from flow.networks import BayBridgeTollNetwork
from flow.networks import BottleneckNetwork
from flow.networks import FigureEightNetwork
from flow.networks import HighwayNetwork
# 有点奇怪，没有匝道，只有主路
# from flow.networks import HighwayRampsNetwork
# from flow.networks import MergeNetwork
from flow.networks import MultiRingNetwork
from flow.networks import RingNetwork
# from flow.networks import TrafficLightGridNetwork
# from flow.networks import I210SubNetwork
from flow.envs.multiagent import MultiAgentHighwayPOEnv
from flow.core.params import SumoParams
from flow.controllers.car_following_models import IDMController
from flow.controllers.routing_controllers import ContinuousRouter
from flow.core.experiment import Experiment
from flow.core.params import EnvParams
from flow.envs.test import TestEnv
from numpy import pi
from flow.core.params import TrafficLightParams
# initial_config=InitialConfig(spacing="uniform",perturbation=1)
from flow.controllers import IDMController, ContinuousRouter, RLController,SimLaneChangeController,StaticLaneChanger
from flow.core.experiment import Experiment
from flow.core.params import NetParams, EnvParams, InitialConfig, InFlows, \
                             VehicleParams, SumoParams, SumoCarFollowingParams, TrafficLightParams, SumoLaneChangeParams
HORIZON=1500
ADDITIONAL_ENV_PARAMS = {
    # maximum acceleration of autonomous vehicles
    'max_accel': 4,
    # maximum deceleration of autonomous vehicles
    'max_decel': 7.5,
    # desired velocity for all vehicles in the network, in m/s
    "target_velocity": 30
}

ADDITIONAL_NET_PARAMS = {
    # the factor multiplying number of lanes.
    "scaling": 1,
    # edge speed limit
    'speed_limit': 30
}
vehicles=VehicleParams()
vehicles.add("human",
             acceleration_controller=(IDMController, {}),
             lane_change_controller=(SimLaneChangeController, {}),
             # lane_change_params=SumoLaneChangeParams(lane_change_mode=1621,),
             # HDVs的跟车模型参数
             car_following_params=SumoCarFollowingParams(speed_mode="right_of_way", accel=4, decel=7.5, tau=1.5),
             )
vehicles.add("rl",
             acceleration_controller=(RLController, {}),
             lane_change_controller=(SimLaneChangeController, {}),
             # lane_change_params=SumoLaneChangeParams(lane_change_mode=1621, ),
             # CAVs的跟车模型参数
             car_following_params=SumoCarFollowingParams(speed_mode="right_of_way", accel=4, decel=7.5, min_gap=1.0, sigma=0, impatience=0, tau=0.5),
             )
vehicles.add("vsl",
             acceleration_controller=(IDMController, {}),
             lane_change_controller=(SimLaneChangeController, {}),
             # lane_change_params=SumoLaneChangeParams(lane_change_mode=1621,),
             # HDVs的跟车模型参数
             car_following_params=SumoCarFollowingParams(speed_mode="right_of_way", accel=4, decel=7.5, tau=1.5),
             color='green'
             )
inflows = InFlows()
inflows.add(veh_type="human",
            edge="1",
            vehs_per_hour=1000,
            depart_lane="random",
            depart_speed="random",
            end="300",
            )
# inflows.add(veh_type="rl",
#             edge="1",
#             vehs_per_hour=2000,
#             depart_lane="random",
#             depart_speed="random",
#             end="300",
#             color="red")
inflows.add(veh_type="vsl",
            edge="1",
            vehs_per_hour=1500,
            depart_lane="random",
            depart_speed="random",
            end="300",
            )
env_params = EnvParams(horizon=HORIZON, clip_actions=False, additional_params=ADDITIONAL_ENV_PARAMS)
net_params = NetParams(inflows=inflows, additional_params=ADDITIONAL_NET_PARAMS)
sim_params = SumoParams(sim_step=0.2, render=True, restart_instance=False, emission_path='data')
traffic_lights = TrafficLightParams()
flow_params = dict(
    exp_tag="Bottleneck_vsl",
    env_name=TestEnv,
    network=BottleneckNetwork,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    # initial=initial_config,
    # tls=traffic_lights,
)
flow_params['env'].horizon = HORIZON
exp = Experiment(flow_params)
_ = exp.run(1, convert_to_csv=True)








