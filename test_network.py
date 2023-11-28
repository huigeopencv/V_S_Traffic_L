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
ADDITIONAL_ENV_PARAMS = {
    # maximum acceleration of autonomous vehicles
    'max_accel': 3,
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
             lane_change_params=SumoLaneChangeParams(lane_change_mode=1621,),
             car_following_params=SumoCarFollowingParams(speed_mode="obey_safe_speed")
             )
vehicles.add("rl",
             acceleration_controller=(RLController, {}),
             lane_change_controller=(SimLaneChangeController, {}),
             lane_change_params=SumoLaneChangeParams(lane_change_mode=1621, ),
             car_following_params=SumoCarFollowingParams(speed_mode="obey_safe_speed")
             )
inflows = InFlows()
inflows.add(veh_type="human",
            edge="1",
            vehs_per_hour=1600,
            depart_lane="random",
            depart_speed="random",
            end="300",
            color="white")
inflows.add(veh_type="rl",
            edge="1",
            vehs_per_hour=400,
            depart_lane="random",
            depart_speed="random",
            end="300",
            color="red")
net_params=NetParams(inflows=inflows, additional_params=ADDITIONAL_NET_PARAMS)
env_params=EnvParams(horizon=3000, additional_params=ADDITIONAL_ENV_PARAMS)
sim_params=SumoParams(sim_step=0.1, render=True,emission_path='data')
traffic_lights=TrafficLightParams()
flow_params=dict(
    exp_tag="Bottleneck_VSL",
    env_name=TestEnv,
    network=BottleneckNetwork,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    # initial=initial_config,
    tls=traffic_lights,
)
exp=Experiment(flow_params)
_=exp.run(1)


