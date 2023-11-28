# the TestEnv environment is used to simply simulate the network
from flow.envs import TestEnv
# the Experiment class is used for running simulations
from flow.core.experiment import Experiment
# all other imports are standard
from flow.core.params import VehicleParams
from flow.core.params import NetParams
from flow.core.params import InitialConfig
from flow.core.params import EnvParams
from flow.core.params import SumoParams
from flow.networks import Network
net_params = NetParams(
    osm_path='networks/bay_bridge.osm'
)
# create the remainding parameters
env_params = EnvParams()
sim_params = SumoParams(render=True)
initial_config = InitialConfig()
vehicles = VehicleParams()
vehicles.add('human', num_vehicles=100)
flow_params = dict(
    exp_tag='bay_bridge',
    env_name=TestEnv,
    network=Network,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    initial=initial_config,
)
# number of time steps
flow_params['env'].horizon = 1000
exp = Experiment(flow_params)
# run the sumo simulation
_ = exp.run(1)

