# ring网络，可用于创建具有不同长度的可变车道和车辆数量的环形道路
from flow.networks.ring import RingNetwork
# 车辆信息，可通过类中的get方法收集有关观察和奖励函数的信息
from flow.core.params import VehicleParams
# 跟车模型：车辆加速行为
from flow.controllers.car_following_models import IDMController
# 对于封闭的网络，该控制器用于永久将所有车辆重新路由到初始设定路线
from flow.controllers.routing_controllers import ContinuousRouter
# 网络特定的参数，长度，车道数，路的速度限制，分辨率
from flow.networks.ring import ADDITIONAL_NET_PARAMS
# 用于特定网络的参数，用于定义网络的形状和属性
from flow.core.params import NetParams
# 指定在仿真开始时影响车辆在网络中定位的参数，可用于限制车辆原本占据的边数和数量，也提供一种增加起始位置随机性的手段
from flow.core.params import InitialConfig
# 用于描述交通信号灯在网络中的位置和类型
from flow.core.params import TrafficLightParams
# 该环境可用于在具有静态数量车辆的完全可观察网络中训练可变数量的车辆
from flow.envs.ring.accel import AccelEnv
# 制定SUMO仿真步骤长度和是否呈现GUI
from flow.core.params import SumoParams
# 基本用于特定的环境的参数设置
from flow.envs.ring.accel import ADDITIONAL_ENV_PARAMS
# 指定影响训练过程或者网络中各组件动态的环境和实验特定参数
from flow.core.params import EnvParams
# 设置实验，开始仿真
from flow.core.experiment import Experiment
# print(ADDITIONAL_NET_PARAMS)
# 道路名称
name="ring_example"
# 此类的初始配置描述了每次模拟时网络中车辆数量，车辆属性
vehicles=VehicleParams()
# 通过add方法添加车辆
import os
vehicles.add("human",
             acceleration_controller=(IDMController,{}),
             routing_controller=(ContinuousRouter,{}),
             num_vehicles=20)
ADDITIONAL_NET_PARAMS = {
    # length of the ring road
    "length": 230,
    # number of lanes
    "lanes": 2,
    # speed limit for all edges
    "speed_limit": 30,
    # resolution of the curves on the ring
    "resolution": 40
}
net_params=NetParams(additional_params=ADDITIONAL_NET_PARAMS)
# 车辆初始化设置，为给网络中的车辆系统引入较小的初始干扰，将perturbation设置为1
initial_config=InitialConfig(spacing="uniform",perturbation=1)
traffic_lights=TrafficLightParams()
# 步长为0.1，True表示显示GUI，最后一个是数据输出路径
sim_params=SumoParams(sim_step=0.1,render=True,emission_path='data')
env_params=EnvParams(additional_params=ADDITIONAL_ENV_PARAMS)
flow_params=dict(
    exp_tag="ring_example",
    env_name=AccelEnv,
    network=RingNetwork,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    initial=initial_config,
    tls=traffic_lights,
)
# 仿真的步数

flow_params['env'].horizon = 3000
exp = Experiment(flow_params)
emission_location = os.path.join(exp.env.sim_params.emission_path, exp.env.network.name)
print(emission_location)

_ = exp.run(1,convert_to_csv=True)





