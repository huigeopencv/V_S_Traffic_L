"""Environment used to train vehicles to improve traffic on a highway."""
import numpy as np
from gym.spaces.box import Box
from flow.core.rewards import desired_velocity
from flow.envs.multiagent.base import MultiEnv


ADDITIONAL_ENV_PARAMS = {
    # maximum acceleration of autonomous vehicles
    'max_accel': 1,
    # maximum deceleration of autonomous vehicles
    'max_decel': 1,
    # desired velocity for all vehicles in the network, in m/s
    "target_velocity": 25
}


class MultiAgentHighwayPOEnv(MultiEnv):
    """Partially observable multi-agent environment for an highway with ramps.
    “”“带有匝道的高速公路的部分可观察的多智能体环境。
    This environment is used to train autonomous vehicles to attenuate the
    formation and propagation of waves in an open highway network.
    该环境用于训练自动驾驶车辆，以减弱开放公路网络中波浪的形成和传播。
    The highway can contain an arbitrary number of entrance and exit ramps, and
    is intended to be used with the HighwayRampsNetwork network.
    公路可包含任意数量的入口和出口匝道，并与HighwayRampsNetwork网络一起使用。
    The policy is shared among the agents, so there can be a non-constant
    number of RL vehicles throughout the simulation.
    该策略在智能体之间共享，因此在整个仿真过程中，RL车辆的数量可以是非恒定的。
    Required from env_params:

    * max_accel: maximum acceleration for autonomous vehicles, in m/s^2
    * max_decel: maximum deceleration for autonomous vehicles, in m/s^2
    * target_velocity: desired velocity for all vehicles in the network, in m/s

    The following states, actions and rewards are considered for one autonomous
    vehicle only, as they will be computed in the same way for each of them.
    以下状态、行动和奖励仅考虑一辆自动驾驶汽车，因为它们将以相同的方式计算。
    States
        The observation consists of the speeds and bumper-to-bumper headways of
        the vehicles immediately preceding and following autonomous vehicle, as
        well as the speed of the autonomous vehicle.
        观察包括自动驾驶车辆前后车辆的速度和保险杠间距，以及自动驾驶车辆的速度。
    Actions
        The action consists of an acceleration, bound according to the
        environment parameters, as well as three values that will be converted
        into probabilities via softmax to decide of a lane change (left, none
        or right).
        该动作包括根据环境参数绑定的加速度，以及三个值，这些值将通过softmax转换为概率，以决定车道变化（左、无或右）。
    Rewards
        The reward function encourages proximity of the system-level velocity
        to a desired velocity specified in the environment parameters, while
        slightly penalizing small time headways among autonomous vehicles.
        奖励功能鼓励系统级速度接近环境参数中指定的期望速度，同时稍微惩罚自动驾驶车辆之间的小时间间隔。
    Termination
        A rollout is terminated if the time horizon is reached or if two
        vehicles collide into one another.
        如果到达时间范围或两辆车相撞，则卷展将终止。
    """

    def __init__(self, env_params, sim_params, network, simulator='traci'):
        for p in ADDITIONAL_ENV_PARAMS.keys():
            if p not in env_params.additional_params:
                raise KeyError(
                    'Environment parameter "{}" not supplied'.format(p))

        super().__init__(env_params, sim_params, network, simulator)

    @property
    def observation_space(self):
        """See class definition."""
        return Box(-float('inf'), float('inf'), shape=(5,), dtype=np.float32)

    @property
    def action_space(self):
        """See class definition."""
        return Box(
            low=-np.abs(self.env_params.additional_params['max_decel']),
            high=self.env_params.additional_params['max_accel'],
            shape=(1,),  # (4,),
            dtype=np.float32)

    def _apply_rl_actions(self, rl_actions):
        """See class definition."""
        # in the warmup steps, rl_actions is None
        if rl_actions:
            for rl_id, actions in rl_actions.items():
                accel = actions[0]

                # lane_change_softmax = np.exp(actions[1:4])
                # lane_change_softmax /= np.sum(lane_change_softmax)
                # lane_change_action = np.random.choice([-1, 0, 1],
                #                                       p=lane_change_softmax)

                self.k.vehicle.apply_acceleration(rl_id, accel)
                # self.k.vehicle.apply_lane_change(rl_id, lane_change_action)

    def get_state(self):
        """See class definition."""
        obs = {}

        # normalizing constants
        max_speed = self.k.network.max_speed()
        max_length = self.k.network.length()

        for rl_id in self.k.vehicle.get_rl_ids():
            # 获取当前车辆速度
            this_speed = self.k.vehicle.get_speed(rl_id)
            # 获取该车前方车辆
            lead_id = self.k.vehicle.get_leader(rl_id)
            # 获取该车后方车辆
            follower = self.k.vehicle.get_follower(rl_id)

            if lead_id in ["", None]:
                # in case leader is not visible
                # 防止没有前车，然后就可以正常行驶
                lead_speed = max_speed
                lead_head = max_length
            else:
                # 如果有前车，获取前车的速度及距离
                lead_speed = self.k.vehicle.get_speed(lead_id)
                lead_head = self.k.vehicle.get_headway(lead_id)

            if follower in ["", None]:
                # in case follower is not visible
                # 没有跟车的情况
                follow_speed = 0
                follow_head = max_length
            else:
                # 有跟车的情况
                follow_speed = self.k.vehicle.get_speed(follower)
                follow_head = self.k.vehicle.get_headway(follower)
            # 观测数据有以下五个组成
            observation = np.array([
                this_speed / max_speed,
                (lead_speed - this_speed) / max_speed,
                lead_head / max_length,
                (this_speed - follow_speed) / max_speed,
                follow_head / max_length
            ])
            # 将每个智能体的观测数据储存起来
            obs.update({rl_id: observation})

        return obs

    def compute_reward(self, rl_actions, **kwargs):
        """See class definition."""
        # in the warmup steps
        # 神经网络在刚开始训练的时候是非常不稳定的，因此刚开始的学习率应当设置得很低很低，这样可以保证网络能够具有良好的收敛性。
        # 但是较低的学习率会使得训练过程变得非常缓慢，因此这里会采用以较低学习率逐渐增大至较高学习率的方式实现网络训练的“热身”阶段
        if rl_actions is None:
            return {}

        rewards = {}
        for rl_id in self.k.vehicle.get_rl_ids():
            if self.env_params.evaluate:
                # reward is speed of vehicle if we are in evaluation mode
                # 如果我们处于评估模式，奖励是车辆的速度
                reward = self.k.vehicle.get_speed(rl_id)
            elif kwargs['fail']:
                # reward is 0 if a collision occurred
                # 碰撞发生时，奖励为0
                reward = 0
            else:
                # reward high system-level velocities
                # 奖励高系统级速度
                cost1 = desired_velocity(self, fail=kwargs['fail'])

                # penalize small time headways
                # 惩罚小时间间隔
                cost2 = 0
                t_min = 1  # smallest acceptable time headway 最小可接受时间间隔
                # 获取该车前方的车辆
                lead_id = self.k.vehicle.get_leader(rl_id)
                if lead_id not in ["", None] \
                        and self.k.vehicle.get_speed(rl_id) > 0:
                # 如果前方车辆存在而且当前车辆的速度大于0
                    t_headway = max(
                        self.k.vehicle.get_headway(rl_id) /
                        self.k.vehicle.get_speed(rl_id), 0)
                    cost2 += min((t_headway - t_min) / t_min, 0)

                # weights for cost1, cost2, and cost3, respectively
                eta1, eta2 = 1.00, 0.10

                reward = max(eta1 * cost1 + eta2 * cost2, 0)

            rewards[rl_id] = reward
        return rewards

    def additional_command(self):
        """See parent class.

        Define which vehicles are observed for visualization purposes.
        定义为了可视化目的观察哪些车辆。
        此处是观察前后方车辆的程序
        """
        # specify observed vehicles
        for rl_id in self.k.vehicle.get_rl_ids():
            # leader
            lead_id = self.k.vehicle.get_leader(rl_id)
            if lead_id:
                self.k.vehicle.set_observed(lead_id)
            # follower
            follow_id = self.k.vehicle.get_follower(rl_id)
            if follow_id:
                self.k.vehicle.set_observed(follow_id)
