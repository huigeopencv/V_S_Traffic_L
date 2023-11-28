# 匝道汇入！！！！
# 匝道汇入网络
# from flow.networks import MergeNetwork
# from flow.core.params import VehicleParams
# from flow.controllers import IDMController
# from flow.core.params import SumoCarFollowingParams
# # create an empty vehicles object
# vehicles = VehicleParams()
# # add some vehicles to this object of type "human"
# vehicles.add("human",
#              acceleration_controller=(IDMController, {}),
#              car_following_params=SumoCarFollowingParams(
#                  speed_mode="obey_safe_speed",
#                  # we use the speed mode "obey_safe_speed" for better dynamics at the merge
#              ),
#              num_vehicles=20)
# from flow.core.params import InFlows
# inflow = InFlows()
# inflow.add(veh_type="human",
#            edge="inflow_highway",
#            vehs_per_hour=2000)
# inflow.add(veh_type="human",
#            edge="inflow_merge",
#            vehs_per_hour=100)
# from flow.networks.merge import ADDITIONAL_NET_PARAMS
# from flow.core.params import NetParams
# additional_net_params = ADDITIONAL_NET_PARAMS.copy()
# # make the part of the highway after the merge longer
# additional_net_params['post_merge_length'] = 350
# # make the number of lanes on the highway be just one
# additional_net_params['highway_lanes'] = 1
# net_params = NetParams(inflows=inflow,  # our inflows
#                        additional_params=additional_net_params)
# from flow.core.params import SumoParams, EnvParams, InitialConfig
# from flow.envs.ring.accel import AccelEnv, ADDITIONAL_ENV_PARAMS
# from flow.core.experiment import Experiment
# sim_params = SumoParams(render=True,
#                          sim_step=0.2)
# env_params = EnvParams(additional_params=ADDITIONAL_ENV_PARAMS)
# initial_config = InitialConfig()
# flow_params = dict(
#     exp_tag='merge-example',
#     env_name=AccelEnv,
#     network=MergeNetwork,
#     simulator='traci',
#     sim=sim_params,
#     env=env_params,
#     net=net_params,
#     veh=vehicles,
#     initial=initial_config,
# )
# # number of time steps
# flow_params['env'].horizon = 10000
# exp = Experiment(flow_params)
# # run the sumo simulation
# _ = exp.run(1)




from flow.core.experiment import Experiment
from flow.core.params import NetParams, EnvParams, InitialConfig, InFlows, \
                             VehicleParams, SumoParams, SumoCarFollowingParams, SumoLaneChangeParams
from flow.controllers import IDMController
from flow.networks import MergeNetwork
from flow.networks.merge import ADDITIONAL_NET_PARAMS
from flow.envs.ring.accel import AccelEnv, ADDITIONAL_ENV_PARAMS
# create a vehicle type
vehicles = VehicleParams()
vehicles.add("human",
             acceleration_controller=(IDMController, {}),
             car_following_params=SumoCarFollowingParams(
                 speed_mode="obey_safe_speed"),
             lane_change_params=SumoLaneChangeParams(lane_change_mode=1621,))
# create the inflows
inflows = InFlows()
# inflow for (1)
# 车辆颜色是个问题，无法改动
inflows.add(veh_type="human",
            edge="inflow_highway",
            vehs_per_hour=2000,
            depart_lane="random",
            depart_speed="random",
            color="white",)
# inflow for (2)
inflows.add(veh_type="human",
            edge="inflow_highway",
            vehs_per_hour=200,
            depart_lane="random",  # right lane
            depart_speed="random",
            color="green",)
# inflow for (3)
inflows.add(veh_type="human",
            edge="inflow_merge",
            vehs_per_hour=300,
            depart_speed="random",
            color="green")
# modify the network accordingly to instructions
# (the available parameters can be found in flow/networks/merge.py)
additional_net_params = ADDITIONAL_NET_PARAMS.copy()
additional_net_params['post_merge_length'] = 3000  # this is just for visuals
additional_net_params['highway_lanes'] = 2
additional_net_params['merge_lanes'] = 1
# setup and run the simulation
net_params = NetParams(inflows=inflows,
                       additional_params=additional_net_params)
sim_params = SumoParams(render="drgb", force_color_update=True, sim_step=0.2)
# sim_params.force_color_update = False
# sim_params.color_by_speed = True
env_params = EnvParams(additional_params=ADDITIONAL_ENV_PARAMS)
initial_config = InitialConfig()
flow_params = dict(
    exp_tag='merge-example',
    env_name=AccelEnv,
    network=MergeNetwork,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    initial=initial_config,
)
# number of time steps
flow_params['env'].horizon = 10000
exp = Experiment(flow_params)
# run the sumo simulation
_ = exp.run(1)

