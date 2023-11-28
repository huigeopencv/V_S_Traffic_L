# 瓶颈！！！
# Import all of the necessary pieces of Flow to run the experiments
from flow.core.params import SumoParams, EnvParams, NetParams, InitialConfig, \
    InFlows, SumoLaneChangeParams, SumoCarFollowingParams
from flow.core.params import VehicleParams
from flow.core.params import TrafficLightParams
from flow.networks.bottleneck import BottleneckNetwork
from flow.controllers import SimLaneChangeController, ContinuousRouter, StaticLaneChanger
from flow.envs.bottleneck import BottleneckEnv
from flow.core.experiment import Experiment
import logging
def run_exp(flow_rate,
            scaling=1,
            disable_tb=True,
            disable_ramp_meter=True,
            n_crit=1000,
            feedback_coef=20):
    # Set up SUMO to render the results, take a time_step of 0.5 seconds per simulation step
    sim_params = SumoParams(
        sim_step=0.5,
        render=True,
        overtake_right=False,
        restart_instance=False,
        emission_path='data'
    )
    vehicles = VehicleParams()
    # Add a few vehicles to initialize the simulation. The vehicles have all lane changing enabled,
    # which is mode 1621
    vehicles.add(
        veh_id="human",
        lane_change_controller=(SimLaneChangeController, {}),
        routing_controller=(ContinuousRouter, {}),
        car_following_params=SumoCarFollowingParams(
            speed_mode=25,
        ),
        lane_change_params=SumoLaneChangeParams(
            lane_change_mode=1621,
        ),
        num_vehicles=1)
    # These are additional params that configure the bottleneck experiment. They are explained in more detail below.
    additional_env_params = {
        "target_velocity": 40,
        "max_accel": 1,
        "max_decel": 1,
        "lane_change_duration": 5,
        "add_rl_if_exit": False,
        "disable_tb": disable_tb,
        "disable_ramp_metering": disable_ramp_meter,
        "n_crit": n_crit,
        "feedback_coeff": feedback_coef,
    }
    # Set up the experiment to run for 1000 time steps i.e. 500 seconds (1000 * 0.5)
    env_params = EnvParams(
        horizon=1000, additional_params=additional_env_params)
    # Add vehicle inflows at the front of the bottleneck. They enter with a flow_rate number of vehicles
    # per hours and with a speed of 10 m/s
    inflow = InFlows()
    inflow.add(
        veh_type="human",
        edge="1",
        vehsPerHour=flow_rate,
        departLane="random",
        departSpeed=10)
    # Initialize the traffic lights. The meanings of disable_tb and disable_ramp_meter are discussed later.
    traffic_lights = TrafficLightParams()
    if not disable_tb:
        traffic_lights.add(node_id="2")
    if not disable_ramp_meter:
        traffic_lights.add(node_id="3")
    additional_net_params = {"scaling": scaling, "speed_limit": 23}
    net_params = NetParams(
        inflows=inflow,
        additional_params=additional_net_params)
    initial_config = InitialConfig(
        spacing="random",
        min_gap=5,
        lanes_distribution=float("inf"),
        edges_distribution=["2", "3", "4", "5"])
    flow_params = dict(
        exp_tag='bay_bridge_toll',
        env_name=BottleneckEnv,
        network=BottleneckNetwork,
        simulator='traci',
        sim=sim_params,
        env=env_params,
        net=net_params,
        veh=vehicles,
        initial=initial_config,
        tls=traffic_lights,
    )
    # number of time steps
    flow_params['env'].horizon = 1000
    exp = Experiment(flow_params)
    # run the sumo simulation
    _ = exp.run(1,convert_to_csv=True)
# run_exp(flow_rate=1000, scaling=1, disable_tb=True, disable_ramp_meter=True)
# run_exp(flow_rate=1000, scaling=2, disable_tb=True, disable_ramp_meter=True)
# run_exp(flow_rate=1400, scaling=1, disable_tb=True, disable_ramp_meter=True)
# run_exp(flow_rate=2400, scaling=1, disable_tb=True, disable_ramp_meter=True)
# run_exp(flow_rate=1000, scaling=1, disable_tb=False, disable_ramp_meter=True)
## An example of a good value of n_crit
run_exp(flow_rate=1000, scaling=1, disable_tb=True, disable_ramp_meter=False, n_crit=8)
## An example where n_crit is way too low
# run_exp(flow_rate=1000, scaling=1, disable_tb=True, disable_ramp_meter=False, n_crit=2)
## An example where n_crit is way too high
# run_exp(flow_rate=1000, scaling=1, disable_tb=True, disable_ramp_meter=False, n_crit=30)
## An example of a relatively stable feedback value
# run_exp(flow_rate=1000, scaling=1, disable_tb=False, disable_ramp_meter=False, n_crit=8, feedback_coef=20)
## An example of a feedback value that will cause the red time to swing wildly
# run_exp(flow_rate=1000, scaling=1, disable_tb=True, disable_ramp_meter=False, n_crit=8, feedback_coef=200)
## An example of a feedback value that will cause the red time to change too slowly
# run_exp(flow_rate=1000, scaling=1, disable_tb=True, disable_ramp_meter=False, n_crit=8, feedback_coef=1)





