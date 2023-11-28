import numpy as np
from gym.spaces.box import Box
from gym.spaces.discrete import Discrete
from flow.core import rewards
# import the base Multi-agent environment
from flow.envs.multiagent.base import MultiEnv
class SharedMultiAgentEnv(MultiEnv):
    pass
def observation_space(self):
    """State space that is partially observed.
        Velocities and distance to intersections for nearby
        vehicles ('num_observed') from each direction.
        """
    tl_box = Box(
        low=0.,
        high=1,
        shape=(2 * 4 * self.num_observed),
        dtype=np.float32)
    return tl_box
def action_space(self):
    """See class definition."""
    if self.discrete:
            # each intersection is an agent, and the action is simply 0 or 1.
            # - 0 means no-change in the traffic light
            # - 1 means switch the direction
        return Discrete(2)
    else:
        return Box(low=0, high=1, shape=(1,), dtype=np.float32)
class SharedMultiAgentEnv(MultiEnv):
    def _apply_rl_actions(self, rl_actions):
        for agent_name in rl_actions:
            action = rl_actions[agent_name]
            # check if the action space is discrete
            # check if our timer has exceeded the yellow phase, meaning it
            # should switch to red
            if self.currently_yellow[tl_num] == 1:  # currently yellow
                self.last_change[tl_num] += self.sim_step
                if self.last_change[
                    tl_num] >= self.min_switch_time:  # check if our timer has exceeded the yellow phase, meaning it
                    # should switch to red
                    if self.direction[tl_num] == 0:
                        self.k.traffic_light.set_state(
                            node_id='center{}'.format(tl_num),
                            state="GrGr")
                    else:
                        self.k.traffic_light.set_state(
                            node_id='center{}'.format(tl_num),
                            state='rGrG')
                    self.currently_yellow[tl_num] = 0
            else:
                if action:
                    if self.direction[tl_num] == 0:
                        self.k.traffic_light.set_state(
                            node_id='center{}'.format(tl_num),
                            state='yryr')
                    else:
                        self.k.traffic_light.set_state(
                            node_id='center{}'.format(tl_num),
                            state='ryry')
                    self.last_change[tl_num] = 0.0
                    self.direction[tl_num] = not self.direction[tl_num]
                    self.currently_yellow[tl_num] = 1
    def get_state(self):
        """Observations for each intersection
        :return: dictionary which contains agent-wise observations as follows:
        - For the self.num_observed number of vehicles closest and incomingsp
        towards traffic light agent, gives the vehicle velocity and distance to
        intersection.
        """
        # Normalization factors
        max_speed = max(
            self.k.network.speed_limit(edge)
            for edge in self.k.network.get_edge_list())
        max_dist = max(grid_array["short_length"], grid_array["long_length"],
                       grid_array["inner_length"])
        # Observed vehicle information
        speeds = []
        dist_to_intersec = []
        for _, edges in self.network.node_mapping:
            local_speeds = []
            local_dists_to_intersec = []
            # .... More code here (removed for simplicity of example)
            # ....
            speeds.append(local_speeds)
            dist_to_intersec.append(local_dists_to_intersec)
        obs = {}
        for agent_id in self.k.traffic_light.get_ids():
            # .... More code here (removed for simplicity of example)
            # ....
            observation = np.array(np.concatenate(speeds, dist_to_intersec))
            obs.update({agent_id: observation})
        return obs
    def compute_reward(self, rl_actions, **kwargs):
        if rl_actions is None:
            return {}
        if self.env_params.evaluate:
            rew = -rewards.min_delay_unscaled(self)
        else:
            rew = -rewards.min_delay_unscaled(self) \
                  + rewards.penalize_standstill(self, gain=0.2)
        # each agent receives reward normalized by number of lights
        rew /= self.num_traffic_lights
        rews = {}
        for rl_id in rl_actions.keys():
            rews[rl_id] = rew
        return rews
class NonSharedMultiAgentEnv(MultiEnv):
    def _apply_rl_actions(self, rl_actions):
        # the names of all autonomous (RL) vehicles in the network
        agent_ids = [
            veh_id for veh_id in self.sorted_ids
            if veh_id in self.k.vehicle.get_rl_ids()
        ]
        # define different actions for different multi-agents
        av_action = rl_actions['av']
        adv_action = rl_actions['adversary']
        perturb_weight = self.env_params.additional_params['perturb_weight']
        rl_action = av_action + perturb_weight * adv_action
        # use the base environment method to convert actions into accelerations for the rl vehicles
        self.k.vehicle.apply_acceleration(agent_ids, rl_action)
    def get_state(self, **kwargs):
        state = np.array([[
            self.k.vehicle.get_speed(veh_id) / self.k.network.max_speed(),
            self.k.vehicle.get_x_by_id(veh_id) / self.k.network.length()
        ] for veh_id in self.sorted_ids])
        state = np.ndarray.flatten(state)
        return {'av': state, 'adversary': state}
    def compute_reward(self, rl_actions, **kwargs):
        if self.env_params.evaluate:
            reward = np.mean(self.k.vehicle.get_speed(
                self.k.vehicle.get_ids()))
            return {'av': reward, 'adversary': -reward}
        else:
            reward = rewards.desired_velocity(self, fail=kwargs['fail'])
            return {'av': reward, 'adversary': -reward}
from flow.envs.multiagent import MultiWaveAttenuationPOEnv
from flow.networks import MultiRingNetwork
from flow.core.params import SumoParams, EnvParams, NetParams, VehicleParams, InitialConfig
from flow.controllers import ContinuousRouter, IDMController, RLController
# time horizon of a single rollout
HORIZON = 3000
# Number of rings
NUM_RINGS = 1
vehicles = VehicleParams()
for i in range(NUM_RINGS):
    vehicles.add(
        veh_id='human_{}'.format(i),
        acceleration_controller=(IDMController, {
            'noise': 0.2
        }),
        routing_controller=(ContinuousRouter, {}),
        num_vehicles=21)
    vehicles.add(
        veh_id='rl_{}'.format(i),
        acceleration_controller=(RLController, {}),
        routing_controller=(ContinuousRouter, {}),
        num_vehicles=1)
flow_params = dict(
    # name of the experiment
    exp_tag='multiagent_ring_road',
    # name of the flow environment the experiment is running on
    env_name=MultiWaveAttenuationPOEnv,
    # name of the network class the experiment is running on
    network=MultiRingNetwork,
    # simulator that is used by the experiment
    simulator='traci',
    # sumo-related parameters (see flow.core.params.SumoParams)
    sim=SumoParams(
        sim_step=0.1,
        render=False,
    ),
    # environment related parameters (see flow.core.params.EnvParams)
    env=EnvParams(
        horizon=HORIZON,
        warmup_steps=750,
        additional_params={
            'max_accel': 1,
            'max_decel': 1,
            'ring_length': [230, 230],
            'target_velocity': 4
        },
    ),
    # network-related parameters
    net=NetParams(
        additional_params={
            'length': 230,
            'lanes': 1,
            'speed_limit': 30,
            'resolution': 40,
            'num_rings': NUM_RINGS
        },
    ),
    # vehicles to be placed in the network at the start of a rollout
    veh=vehicles,
    # parameters specifying the positioning of vehicles upon initialization/
    # reset
    initial=InitialConfig(bunching=20.0, spacing='custom'),
)
# 创建环境
from flow.utils.registry import make_create_env
from ray.tune.registry import register_env
create_env, env_name = make_create_env(params=flow_params, version=0)
# Register as rllib env
register_env(env_name, create_env)
test_env = create_env()
obs_space = test_env.observation_space
act_space = test_env.action_space
from ray.rllib.agents.ppo.ppo_policy import PPOTFPolicy
# 共享策略
def gen_policy():
    """Generate a policy in RLlib."""
    return PPOTFPolicy, obs_space, act_space, {}
# Setup PG with an ensemble of `num_policies` different policy graphs
POLICY_GRAPHS = {'av': gen_policy()}
def policy_mapping_fn(_):
    """Map a policy in RLlib."""
    return 'av'
POLICIES_TO_TRAIN = ['av']
# 非共享策略
def gen_policy():
    """Generate a policy in RLlib."""
    return PPOTFPolicy, obs_space, act_space, {}
# Setup PG with an ensemble of `num_policies` different policy graphs
POLICY_GRAPHS = {'av': gen_policy(), 'adversary': gen_policy()}
def policy_mapping_fn(agent_id):
    """Map a policy in RLlib."""
    return agent_id
