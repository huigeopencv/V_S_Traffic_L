# # import the base environment class
# # Env提供运行和修改SUMO仿真的接口
# from flow.envs import Env
# import numpy as np
# # define the environment class, and inherit properties from the base environment class
# class myEnv(Env):
#     pass
# 该参数用于储存有关路网中AVS的最大加减速信息
# ADDITIONAL_ENV_PARAMS = {
#     "max_accel": 1,
#     "max_decel": 1,
# }
# action空间定义了RL智能体提供的动作的数量和范围，使用OpenAI gym来定义范围，则用到了gym.spaces中的几个对象
# Box用于定义值的有界数组
# Tuple对象允许用户将对个Box对象组合在一起
# from gym.spaces.box import Box
# from gym.spaces import Tuple
# class myEnv(myEnv):
#     @property
# 动作由一个N元素的刘表组成，（N是AVS的数量），上下分别以max_accel和max_decel为界
#     def action_space(self):
#         num_actions = self.initial_vehicles.num_rl_vehicles
#         accel_ub = self.env_params.additional_params["max_accel"]
#         accel_lb = - abs(self.env_params.additional_params["max_decel"])
#         return Box(low=accel_lb,
#                    high=accel_ub,
#                    shape=(num_actions,))
# 观测空间提供RL智能体可从环境中观察信息的类型和数量
#     @property
#     def observation_space(self):
#         return Box(
#             low=0,
#             high=float("inf"),
#             shape=(2*self.initial_vehicles.num_vehicles,),
#         )
# apply_rl_actions将RL智能体指定的命令转化为在仿真中执行的实际操作
#     def _apply_rl_actions(self, rl_actions):
#         # the names of all autonomous (RL) vehicles in the network
#         rl_ids = self.k.vehicle.get_rl_ids()
#         # use the base environment method to convert actions into accelerations for the rl vehicles
#         self.k.vehicle.apply_acceleration(rl_ids, rl_actions)
# # self.k.vehicle提供当前路网中所有车辆的状态信息
# # self.k.traffic_light提供红绿灯的状态信息
# # self.k.network网络上的信息，不像车辆和交通信号灯是静态的
# get_state方法从环境中提取特征，然后作为输入提供给RL智能体提供的策略
#     def get_state(self, **kwargs):
#         # the get_ids() method is used to get the names of all vehicles in the network
#         ids = self.k.vehicle.get_ids()
#         # we use the get_absolute_position method to get the positions of all vehicles
#         pos = [self.k.vehicle.get_x_by_id(veh_id) for veh_id in ids]
#         # we use the get_speed method to get the velocities of all vehicles
#         vel = [self.k.vehicle.get_speed(veh_id) for veh_id in ids]
#         # the speeds and positions are concatenated to produce the state
#         return np.concatenate((pos, vel))
#     def compute_reward(self, rl_actions, **kwargs):
#         # the get_ids() method is used to get the names of all vehicles in the network
#         ids = self.k.vehicle.get_ids()
#         # we next get a list of the speeds of all vehicles in the network
#         speeds = self.k.vehicle.get_speed(ids)
#         # finally, we return the average of all these speeds as the reward
#         return np.mean(speeds)
# from flow.controllers import IDMController, ContinuousRouter
# from flow.core.experiment import Experiment
# from flow.core.params import SumoParams, EnvParams, \
#     InitialConfig, NetParams
# from flow.core.params import VehicleParams
# from flow.networks.ring import RingNetwork, ADDITIONAL_NET_PARAMS
# sim_params = SumoParams(sim_step=0.1, render=True)
# vehicles = VehicleParams()
# vehicles.add(veh_id="idm",
#              acceleration_controller=(IDMController, {}),
#              routing_controller=(ContinuousRouter, {}),
#              num_vehicles=22)
# env_params = EnvParams(additional_params=ADDITIONAL_ENV_PARAMS)
# additional_net_params = ADDITIONAL_NET_PARAMS.copy()
# net_params = NetParams(additional_params=additional_net_params)
# initial_config = InitialConfig(bunching=20)
# flow_params = dict(
#     exp_tag='ring',
#     env_name=myEnv,  # using my new environment for the simulation
#     network=RingNetwork,
#     simulator='traci',
#     sim=sim_params,
#     env=env_params,
#     net=net_params,
#     veh=vehicles,
#     initial=initial_config,
# )
# # number of time steps
# flow_params['env'].horizon = 1500
# exp = Experiment(flow_params)
# # run the sumo simulation
# _ = exp.run(1)



# 新建的环境应该放在flow.envs文件夹中，作为一个单独的py文件，然后这样导入以在OpenAI gym中注册环境
from flow.envs import AccelEnv as myEnv
import json
import ray
from ray.rllib.agents.registry import get_agent_class
from ray.tune import run_experiments
from ray.tune.registry import register_env
from flow.networks.ring import RingNetwork, ADDITIONAL_NET_PARAMS
from flow.utils.registry import make_create_env
from flow.utils.rllib import FlowParamsEncoder
from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams, VehicleParams, SumoCarFollowingParams
from flow.controllers import RLController, IDMController, ContinuousRouter
# time horizon of a single rollout
HORIZON = 1500
# number of rollouts per training iteration
N_ROLLOUTS = 20
# number of parallel workers
N_CPUS = 1
# We place one autonomous vehicle and 22 human-driven vehicles in the network
vehicles = VehicleParams()
vehicles.add(
    veh_id="human",
    acceleration_controller=(IDMController, {"noise": 0.2}),
    car_following_params=SumoCarFollowingParams(min_gap=0),
    routing_controller=(ContinuousRouter, {}),
    num_vehicles=18)
vehicles.add(
    veh_id="rl",
    acceleration_controller=(RLController, {}),
    # acceleration_controller=(IDMController, {}),
    routing_controller=(ContinuousRouter, {}),
    num_vehicles=4)
flow_params = dict(
    # name of the experiment
    exp_tag="stabilizing_the_ring",
    # name of the flow environment the experiment is running on
    env_name=myEnv,  # <------ here we replace the environment with our new environment
    # name of the network class the experiment is running on
    network=RingNetwork,
    # simulator that is used by the experiment
    simulator='traci',
    # sumo-related parameters (see flow.core.params.SumoParams)
    sim=SumoParams(sim_step=0.1, render=False,),
    # environment related parameters (see flow.core.params.EnvParams)
    env=EnvParams(
        horizon=HORIZON,
        warmup_steps=750,
        clip_actions=False,
        additional_params={
            "target_velocity": 20,
            "sort_vehicles": False,
            "max_accel": 1,
            "max_decel": 1,
        },
    ),
    # network-related parameters (see flow.core.params.NetParams and the
    # network's documentation or ADDITIONAL_NET_PARAMS component)
    net=NetParams(additional_params=ADDITIONAL_NET_PARAMS.copy()),
    # vehicles to be placed in the network at the start of a rollout (see
    # flow.core.params.VehicleParams)
    veh=vehicles,
    # parameters specifying the positioning of vehicles upon initialization/
    # reset (see flow.core.params.InitialConfig)
    initial=InitialConfig(bunching=20,),
)
def setup_exps():
    """Return the relevant components of an RLlib experiment.
    Returns
    -------
    str
        name of the training algorithm
    str
        name of the gym environment to be trained
    dict
        training configuration parameters
    """
    alg_run = "PPO"
    agent_cls = get_agent_class(alg_run)
    config = agent_cls._default_config.copy()
    config["num_workers"] = N_CPUS
    config["train_batch_size"] = HORIZON * N_ROLLOUTS
    config["gamma"] = 0.999  # discount rate
    config["model"].update({"fcnet_hiddens": [3, 3]})
    config["use_gae"] = True
    config["lambda"] = 0.97
    config["kl_target"] = 0.02
    config["num_sgd_iter"] = 10
    config['clip_actions'] = False  # FIXME(ev) temporary ray bug
    config["horizon"] = HORIZON
    # save the flow params for replay
    flow_json = json.dumps(
        flow_params, cls=FlowParamsEncoder, sort_keys=True, indent=4)
    config['env_config']['flow_params'] = flow_json
    config['env_config']['run'] = alg_run
    create_env, gym_name = make_create_env(params=flow_params, version=0)
    # Register as rllib env
    register_env(gym_name, create_env)
    return alg_run, gym_name, config
alg_run, gym_name, config = setup_exps()
ray.init(num_cpus=N_CPUS + 1)

trials = run_experiments({
    flow_params["exp_tag"]: {
        "run": alg_run,
        "env": gym_name,
        "config": {**config},
        "checkpoint_freq": 20,
        "checkpoint_at_end": True,
        "max_failures": 999,
        "stop": {"training_iteration": 200, },
    }
})


