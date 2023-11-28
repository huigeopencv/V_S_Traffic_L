from flow.networks import MergeNetwork
from flow.envs import AccelEnv as myEnv
from flow.envs.test import TestEnv
from flow.envs.merge import MergePOEnv
# from flow.envs.multiagent import MultiAgentHighwayPOEnv, MultiAgentMergePOEnv
from free_ramp_env1 import MultiAgentHighwayPOEnv
import json
import ray
from ray.rllib.agents.registry import get_agent_class
from ray.tune import run_experiments
from ray.tune.registry import register_env
from flow.utils.registry import make_create_env
from flow.utils.rllib import FlowParamsEncoder
from flow.controllers import IDMController, ContinuousRouter, RLController,SimLaneChangeController,StaticLaneChanger
from flow.core.experiment import Experiment
from flow.core.params import NetParams, EnvParams, InitialConfig, InFlows, \
                             VehicleParams, SumoParams, SumoCarFollowingParams, TrafficLightParams, \
                            SumoLaneChangeParams
initial_config=InitialConfig(spacing="uniform",perturbation=1, bunching=20,)
# 1，结果可视化的实现
# 2，可视化程序的阅读
# 3，对单个车的控制是具体怎么个意思，是在全局只有一辆车受控还是在拥堵区域内有一辆被控制
# 4，论文的阅读
# 具体做法方向，
# time horizon of a single rollout
HORIZON = 1500
# number of rollouts per training iteration
N_ROLLOUTS = 20
# number of parallel workers
N_CPUS = 16
ADDITIONAL_NET_PARAMS = {
    # length of the merge edge
    "merge_length": 100,
    # length of the highway leading to the merge
    "pre_merge_length": 500,
    # length of the highway past the merge
    "post_merge_length": 3000,
    # number of lanes in the merge
    "merge_lanes": 1,
    # number of lanes in the highway
    "highway_lanes": 2,
    # max speed limit of the network
    "speed_limit": 30,
}
ADDITIONAL_ENV_PARAMS = {
    # maximum acceleration for autonomous vehicles, in m/s^2
    "max_accel": 3,
    # maximum deceleration for autonomous vehicles, in m/s^2
    "max_decel": 3,
    # desired velocity for all vehicles in the network, in m/s
    "target_velocity": 25,
    # maximum number of controllable vehicles in the network
    # "num_rl": 200,
}
vehicles=VehicleParams()
vehicles.add("human",
             acceleration_controller=(IDMController, {}),
             lane_change_controller=(SimLaneChangeController, {}),
             lane_change_params=SumoLaneChangeParams(lane_change_mode=1621,),
             car_following_params=SumoCarFollowingParams(speed_mode="obey_safe_speed"))
vehicles.add("rl",
             acceleration_controller=(RLController, {}),
             lane_change_controller=(SimLaneChangeController, {}),
             lane_change_params=SumoLaneChangeParams(lane_change_mode=1621, ),
             car_following_params=SumoCarFollowingParams(speed_mode="obey_safe_speed"))
inflows = InFlows()
# 车辆颜色是个问题，无法改动
inflows.add(veh_type="human",
            edge="inflow_highway",
            vehs_per_hour=2400,
            depart_lane="random",
            depart_speed="random",
            color="white",
            )
inflows.add(veh_type="rl",
            edge="inflow_highway",
            vehs_per_hour=600,
            depart_lane="random",
            depart_speed="random",
            color="red")
inflows.add(veh_type="human",
            edge="inflow_merge",
            vehs_per_hour=300,
            depart_speed="random",
            color="green")
env_params = EnvParams(horizon=HORIZON, warmup_steps=100, clip_actions=False, additional_params=ADDITIONAL_ENV_PARAMS)
net_params = NetParams(inflows=inflows, additional_params=ADDITIONAL_NET_PARAMS)
sim_params = SumoParams(sim_step=0.2, render=False, restart_instance=True, emission_path='data')
traffic_lights = TrafficLightParams()
flow_params = dict(
    exp_tag="free_ramp_example",
    env_name=MultiAgentHighwayPOEnv,
    network=MergeNetwork,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    initial=initial_config,
    # tls=traffic_lights,
)
# exp = Experiment(flow_params)
# _ = exp.run(1)
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
    config["num_gpus"] = 1


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
# rl_ids = myEnv.k.vehicle.get_rl_ids()

ray.init(num_cpus=N_CPUS + 1)
trials = run_experiments({
    flow_params["exp_tag"]: {
        "run": alg_run,
        "env": gym_name,
        "config": {**config},
        "checkpoint_freq": 20,
        "checkpoint_at_end": True,
        "max_failures": 999,
        "stop": {"training_iteration": 1000, },
    }
})








