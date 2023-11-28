"""Environment for training vehicles to reduce congestion in a merge."""

from flow.envs.multiagent.base import MultiEnv
from flow.core import rewards
from gym.spaces.box import Box
import numpy as np


ADDITIONAL_ENV_PARAMS = {
    # maximum acceleration for autonomous vehicles, in m/s^2
    "max_accel": 3,
    # maximum deceleration for autonomous vehicles, in m/s^2
    "max_decel": 3,
    # desired velocity for all vehicles in the network, in m/s
    "target_velocity": 25,
}


class MultiAgentMergePOEnv(MultiEnv):
    """Partially observable multi-agent merge environment.
    部分可观察的多代理合并环境。

    This environment is used to train autonomous vehicles to attenuate the
    formation and propagation of waves in an open merge network.
    该环境用于训练自动驾驶车辆，以衰减开放合并网络中波浪的形成和传播。

    Required from env_params:

    * max_accel: maximum acceleration for autonomous vehicles, in m/s^2
    * max_decel: maximum deceleration for autonomous vehicles, in m/s^2
    * target_velocity: desired velocity for all vehicles in the network, in m/s

    States
        The observation consists of the speeds and bumper-to-bumper headways of
        the vehicles immediately preceding and following autonomous vehicle, as
        well as the ego speed of the autonomous vehicles.
        观察包括自动驾驶车辆前后车辆的速度和保险杠间距，以及自动驾驶车辆的自我速度。

        In order to maintain a fixed observation size, when the number of AVs
        in the network is less than "num_rl", the extra entries are filled in
        with zeros. Conversely, if the number of autonomous vehicles is greater
        than "num_rl", the observations from the additional vehicles are not
        included in the state space.
        为了保持固定的观测大小，当网络中的AVs数量小于“num_rl”时，额外的条目用零填充。
        相反，如果自动驾驶车辆的数量大于“num_rl”，则状态空间中不包括来自其他车辆的观察结果。
    Actions
        The action space consists of a vector of bounded accelerations for each
        autonomous vehicle $i$. In order to ensure safety, these actions are
        bounded by failsafes provided by the simulator at every time step.
        动作空间由每个自动驾驶车辆$i$的有界加速度向量组成。为了确保安全，这些动作在每个时间步骤都受到模拟器提供的故障保护的限制。

        In order to account for variability in the number of autonomous
        vehicles, if n_AV < "num_rl" the additional actions provided by the
        agent are not assigned to any vehicle. Moreover, if n_AV > "num_rl",
        the additional vehicles are not provided with actions from the learning
        agent, and instead act as human-driven vehicles as well.
        为了说明自动驾驶车辆数量的可变性，如果n_AV<“num_rl”，则代理提供的附加操作不会分配给任何车辆。
        此外，如果n_AV>“num_rl”，则其他车辆不会被学习代理提供动作，而是充当人类驾驶的车辆。
    Rewards
        The reward function encourages proximity of the system-level velocity
        to a desired velocity, while slightly penalizing small time headways
        among autonomous vehicles.
        奖励功能鼓励系统级速度接近期望速度，同时稍微惩罚自动驾驶车辆之间的小时间间隔。
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

        # used for visualization: the vehicles behind and after RL vehicles
        # (ie the observed vehicles) will have a different color
        self.leader = []
        self.follower = []

        super().__init__(env_params, sim_params, network, simulator)

    @property
    def action_space(self):
        """See class definition."""
        return Box(
            low=-abs(self.env_params.additional_params["max_decel"]),
            high=self.env_params.additional_params["max_accel"],
            shape=(1,),
            dtype=np.float32)

    @property
    def observation_space(self):
        """See class definition."""
        return Box(low=-5, high=5, shape=(5,), dtype=np.float32)

    def _apply_rl_actions(self, rl_actions):
        """See class definition."""
        for rl_id in enumerate(self.k.vehicle.get_rl_ids()):
            if rl_id not in rl_actions.keys():
                # the vehicle just entered, so ignore
                continue
            self.k.vehicle.apply_acceleration(rl_id, rl_actions[rl_id])

    def get_state(self, rl_id=None, **kwargs):
        """See class definition."""
        observation = {}
        self.leader = []
        self.follower = []

        # normalizing constants
        max_speed = self.k.network.max_speed()
        max_length = self.k.network.length()

        for rl_id in self.k.vehicle.get_rl_ids():
            this_speed = self.k.vehicle.get_speed(rl_id)
            lead_id = self.k.vehicle.get_leader(rl_id)
            follower = self.k.vehicle.get_follower(rl_id)

            if lead_id in ["", None]:
                # in case leader is not visible
                lead_speed = max_speed
                lead_head = max_length
            else:
                self.leader.append(lead_id)
                lead_speed = self.k.vehicle.get_speed(lead_id)
                lead_head = self.k.vehicle.get_x_by_id(lead_id) \
                    - self.k.vehicle.get_x_by_id(rl_id) \
                    - self.k.vehicle.get_length(rl_id)

            if follower in ["", None]:
                # in case follower is not visible
                follow_speed = 0
                follow_head = max_length
            else:
                self.follower.append(follower)
                follow_speed = self.k.vehicle.get_speed(follower)
                follow_head = self.k.vehicle.get_headway(follower)

            observation[rl_id] = np.array([
                this_speed / max_speed,
                (lead_speed - this_speed) / max_speed,
                lead_head / max_length,
                (this_speed - follow_speed) / max_speed,
                follow_head / max_length
            ])

        return observation

    def compute_reward(self, rl_actions, **kwargs):
        """See class definition."""
        if self.env_params.evaluate:
            return np.mean(self.k.vehicle.get_speed(self.k.vehicle.get_ids()))
        else:
            # return a reward of 0 if a collision occurred
            if kwargs["fail"]:
                return 0

            # reward high system-level velocities
            cost1 = rewards.desired_velocity(self, fail=kwargs["fail"])

            # penalize small time headways
            cost2 = 0
            t_min = 1  # smallest acceptable time headway
            for rl_id in self.k.vehicle.get_rl_ids():
                lead_id = self.k.vehicle.get_leader(rl_id)
                if lead_id not in ["", None] \
                        and self.k.vehicle.get_speed(rl_id) > 0:
                    t_headway = max(
                        self.k.vehicle.get_headway(rl_id) /
                        self.k.vehicle.get_speed(rl_id), 0)
                    cost2 += min((t_headway - t_min) / t_min, 0)

            # weights for cost1 and cost2, respectively
            eta1, eta2 = 1.00, 0.10

            reward = max(eta1 * cost1 + eta2 * cost2, 0)
            return {key: reward for key in self.k.vehicle.get_rl_ids()}

    def additional_command(self):
        """See parent class.

        This method defines which vehicles are observed for visualization
        purposes.
        观察前后方的车辆
        """
        for veh_id in self.leader + self.follower:
            self.k.vehicle.set_observed(veh_id)

    def reset(self, new_inflow_rate=None):
        """See parent class.

        In addition, a few variables that are specific to this class are
        emptied before they are used by the new rollout.
        此外，一些特定于该类的变量在被新卷展栏使用之前被清空。
        """
        self.leader = []
        self.follower = []
        return super().reset()
