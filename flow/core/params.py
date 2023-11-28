"""Objects that define the various meta-parameters of an experiment."""

import logging
import collections

from flow.utils.flow_warnings import deprecated_attribute
from flow.controllers.car_following_models import SimCarFollowingController
from flow.controllers.rlcontroller import RLController
from flow.controllers.lane_change_controllers import SimLaneChangeController


SPEED_MODES = {
    "aggressive": 0,
    "obey_safe_speed": 1,
    "no_collide": 7,
    "right_of_way": 25,
    "all_checks": 31
}

LC_MODES = {
    "no_lc_safe": 512,
    "no_lc_aggressive": 0,
    "sumo_default": 1621,
    "no_strategic_aggressive": 1108,
    "no_strategic_safe": 1620,
    "only_strategic_aggressive": 1,
    "only_strategic_safe": 513,
    "no_cooperative_aggressive": 1105,
    "no_cooperative_safe": 1617,
    "only_cooperative_aggressive": 4,
    "only_cooperative_safe": 516,
    "no_speed_gain_aggressive": 1093,
    "no_speed_gain_safe": 1605,
    "only_speed_gain_aggressive": 16,
    "only_speed_gain_safe": 528,
    "no_right_drive_aggressive": 1045,
    "no_right_drive_safe": 1557,
    "only_right_drive_aggressive": 64,
    "only_right_drive_safe": 576
}

# Traffic light defaults
PROGRAM_ID = 1
MAX_GAP = 3.0
DETECTOR_GAP = 0.6
SHOW_DETECTORS = True


class TrafficLightParams:
    """Base traffic light.
    该类用于在网络中放置红绿灯，并描述这些红绿灯的状态。 此外，该类还支持通过 TraCI 修改某些灯的状态。

    This class is used to place traffic lights in the network and describe
    the state of these traffic lights. In addition, this class supports
    modifying the states of certain lights via TraCI.
    """

    def __init__(self, baseline=False):
        """Instantiate base traffic light.

        Attributes
        ----------
        baseline: bool
        """
        # traffic light xml properties
        self.__tls_properties = dict()

        # all traffic light parameters are set to default baseline values
        self.baseline = baseline

    def add(self,
            node_id,
            tls_type="static",
            programID=10,
            offset=None,
            phases=None,
            maxGap=None,
            detectorGap=None,
            showDetectors=None,
            file=None,
            freq=None):
        """Add a traffic light component to the network.
        将交通灯组件添加到网络中。

        When generating networks using xml files, using this method to add a
        traffic light will explicitly place the traffic light in the requested
        node of the generated network.
        使用xml文件生成网络时，使用该方法添加红绿灯会明确地将红绿灯放置在生成网络的请求节点中。

        If traffic lights are not added here but are already present in the
        network (e.g. through a prebuilt net.xml file), then the traffic light
        class will identify and add them separately.
        如果此处未添加红绿灯但已存在于网络中（例如通过预构建的 net.xml 文件），则红绿灯类将单独识别并添加它们。

        Parameters
        ----------
        node_id : str
            name of the node with traffic lights
        tls_type : str, optional
            type of the traffic light (see Note)
        programID : str, optional
            id of the traffic light program (see Note)
        offset : int, optional
            initial time offset of the program
        phases : list  of dict, optional
            list of phases to be followed by the traffic light, defaults
            to default sumo traffic light behavior. Each element in the list
            must consist of a dict with two keys:

            * "duration": length of the current phase cycle (in sec)
            * "state": string consist the sequence of states in the phase
            * "minDur": optional
                The minimum duration of the phase when using type actuated
            * "maxDur": optional
                The maximum duration of the phase when using type actuated

        maxGap : int, optional
            describes the maximum time gap between successive vehicle that will
            cause the current phase to be prolonged, **used for actuated
            traffic lights**
        detectorGap : int, optional
            used for actuated traffic lights
            determines the time distance between the (automatically generated)
            detector and the stop line in seconds (at each lanes maximum
            speed), **used for actuated traffic lights**
        showDetectors : bool, optional
            toggles whether or not detectors are shown in sumo-gui, **used for
            actuated traffic lights**
        file : str, optional
            which file the detector shall write results into
        freq : int, optional
            the period over which collected values shall be aggregated

        Note
        ----
        For information on defining traffic light properties, see:
        http://sumo.dlr.de/wiki/Simulation/Traffic_Lights#Defining_New_TLS-Programs
        """
        # prepare the data needed to generate xml files
        self.__tls_properties[node_id] = {"id": node_id, "type": tls_type}

        if programID:
            self.__tls_properties[node_id]["programID"] = programID

        if offset:
            self.__tls_properties[node_id]["offset"] = offset

        if phases:
            self.__tls_properties[node_id]["phases"] = phases

        if tls_type == "actuated":
            # Required parameters
            self.__tls_properties[node_id]["max-gap"] = \
                maxGap if maxGap else MAX_GAP
            self.__tls_properties[node_id]["detector-gap"] = \
                detectorGap if detectorGap else DETECTOR_GAP
            self.__tls_properties[node_id]["show-detectors"] = \
                showDetectors if showDetectors else SHOW_DETECTORS

            # Optional parameters
            if file:
                self.__tls_properties[node_id]["file"] = file

            if freq:
                self.__tls_properties[node_id]["freq"] = freq

    def get_properties(self):
        """Return traffic light properties.
        返回红绿灯属性。

        This is meant to be used by the generator to import traffic light data
        to the .net.xml file
        这意味着生成器将使用它来将交通灯数据导入 .net.xml 文件
        """
        return self.__tls_properties

    def actuated_default(self):
        """Return the default values for an actuated network.
        返回驱动网络的默认值。

        An actuated network is a network for a system where
        all junctions are actuated traffic lights.
        驱动网络是所有交叉点都是驱动交通信号灯的系统的网络。

        Returns
        -------
        tl_logic : dict
            traffic light logic
        """
        tl_type = "actuated"
        program_id = 1
        max_gap = 3.0
        detector_gap = 0.8
        show_detectors = True
        phases = [{
            "duration": "31",
            "minDur": "8",
            "maxDur": "45",
            "state": "GrGr"
        }, {
            "duration": "6",
            "minDur": "3",
            "maxDur": "6",
            "state": "yryr"
        }, {
            "duration": "31",
            "minDur": "8",
            "maxDur": "45",
            "state": "rGrG"
        }, {
            "duration": "6",
            "minDur": "3",
            "maxDur": "6",
            "state": "ryry"
        }]

        return {
            "tl_type": str(tl_type),
            "program_id": str(program_id),
            "max_gap": str(max_gap),
            "detector_gap": str(detector_gap),
            "show_detectors": show_detectors,
            "phases": phases
        }


class VehicleParams:
    """Base vehicle class.

    This is used to describe the state of all vehicles in the network.
    State information on the vehicles for a given time step can be set or
    retrieved from this class.
    这用于描述网络中所有车辆的状态。 可以从此类中设置或检索给定时间步长的车辆状态信息。
    """

    def __init__(self):
        """Instantiate the base vehicle class."""
        self.ids = []  # ids of all vehicles

        # vehicles: Key = Vehicle ID, Value = Dictionary describing the vehicle
        # Ordered dictionary used to keep neural net inputs in order
        self.__vehicles = collections.OrderedDict()

        #: total number of vehicles in the network
        self.num_vehicles = 0
        #: int : number of rl vehicles in the network
        self.num_rl_vehicles = 0
        #: int : number of unique types of vehicles in the network
        self.num_types = 0
        #: list of str : types of vehicles in the network
        self.types = []

        #: dict (str, str) : contains the parameters associated with each type
        #: of vehicle
        self.type_parameters = dict()

        #: dict (str, int) : contains the minGap attribute of each type of
        #: vehicle
        self.minGap = dict()

        #: list : initial state of the vehicles class, used for serialization
        #: purposes
        self.initial = []

    def add(self,
            veh_id,
            acceleration_controller=(SimCarFollowingController, {}),
            lane_change_controller=(SimLaneChangeController, {}),
            routing_controller=None,
            initial_speed=0,
            num_vehicles=0,
            car_following_params=None,
            lane_change_params=None,
            color=None):
        """Add a sequence of vehicles to the list of vehicles in the network.

        Parameters
        ----------
        veh_id : str
            base vehicle ID for the vehicles (will be appended by a number)
        acceleration_controller : tup, optional
            1st element: flow-specified acceleration controller
            2nd element: controller parameters (may be set to None to maintain
            default parameters)
        lane_change_controller : tup, optional
            1st element: flow-specified lane-changer controller
            2nd element: controller parameters (may be set to None to maintain
            default parameters)
        routing_controller : tup, optional
            1st element: flow-specified routing controller
            2nd element: controller parameters (may be set to None to maintain
            default parameters)
        initial_speed : float, optional
            initial speed of the vehicles being added (in m/s)
        num_vehicles : int, optional
            number of vehicles of this type to be added to the network
        car_following_params : flow.core.params.SumoCarFollowingParams
            Params object specifying attributes for Sumo car following model.
        lane_change_params : flow.core.params.SumoLaneChangeParams
            Params object specifying attributes for Sumo lane changing model.
        """
        if car_following_params is None:
            # FIXME: depends on simulator
            car_following_params = SumoCarFollowingParams()

        if lane_change_params is None:
            # FIXME: depends on simulator
            lane_change_params = SumoLaneChangeParams()

        type_params = {}
        type_params.update(car_following_params.controller_params)
        type_params.update(lane_change_params.controller_params)

        # This dict will be used when trying to introduce new vehicles into
        # the network via a Flow. It is passed to the vehicle kernel object
        # during environment instantiation.
        self.type_parameters[veh_id] = \
            {"acceleration_controller": acceleration_controller,
             "lane_change_controller": lane_change_controller,
             "routing_controller": routing_controller,
             "initial_speed": initial_speed,
             "car_following_params": car_following_params,
             "lane_change_params": lane_change_params}

        if color:
            type_params['color'] = color
            self.type_parameters[veh_id]['color'] = color

        # TODO: delete?
        self.initial.append({
            "veh_id":
                veh_id,
            "acceleration_controller":
                acceleration_controller,
            "lane_change_controller":
                lane_change_controller,
            "routing_controller":
                routing_controller,
            "initial_speed":
                initial_speed,
            "num_vehicles":
                num_vehicles,
            "car_following_params":
                car_following_params,
            "lane_change_params":
                lane_change_params
        })

        # This is used to return the actual headways from the vehicles class.
        # It is passed to the vehicle kernel class during environment
        # instantiation.
        self.minGap[veh_id] = type_params["minGap"]

        for i in range(num_vehicles):
            v_id = veh_id + '_%d' % i

            # add the vehicle to the list of vehicle ids
            self.ids.append(v_id)

            self.__vehicles[v_id] = dict()

            # specify the type
            self.__vehicles[v_id]["type"] = veh_id

            # update the number of vehicles
            self.num_vehicles += 1
            if acceleration_controller[0] == RLController:
                self.num_rl_vehicles += 1

        # increase the number of unique types of vehicles in the network, and
        # add the type to the list of types
        self.num_types += 1
        self.types.append({"veh_id": veh_id, "type_params": type_params})

    def get_type(self, veh_id):
        """Return the type of a specified vehicle.

        Parameters
        ----------
        veh_id : str
            vehicle ID whose type the user is querying
        """
        return self.__vehicles[veh_id]["type"]


class SimParams(object):
    """Simulation-specific parameters.

    All subsequent parameters of the same type must extend this.

    Attributes
    ----------
    sim_step : float optional
        seconds per simulation step; 0.1 by default
        每个模拟步骤的秒数； 默认为 0.1
    render : str or bool, optional
        specifies whether to visualize the rollout(s)
        指定是否可视化卷展栏

        * False: no rendering
        * True: delegate rendering to sumo-gui for back-compatibility
        * "gray": static grayscale rendering, which is good for training
        * "dgray": dynamic grayscale rendering
        * "rgb": static RGB rendering
        * "drgb": dynamic RGB rendering, which is good for visualization

    restart_instance : bool, optional
        specifies whether to restart a simulation upon reset. Restarting
        the instance helps avoid slowdowns cause by excessive inflows over
        large experiment runtimes, but also require the gui to be started
        after every reset if "render" is set to True.
        指定是否在重置时重新启动模拟。 重新启动实例有助于避免因大型实验运行时的过多流入而导致的减速，但如果“render”设置为 True，则还需要在每次重置后启动 gui。
    emission_path : str, optional
        Path to the folder in which to create the emissions output.
        Emissions output is not generated if this value is not specified
        在其中创建排放量输出的文件夹的路径。 如果未指定此值，则不会生成排放量输出
    save_render : bool, optional
        specifies whether to save rendering data to disk
        指定是否将渲染数据保存到磁盘
    sight_radius : int, optional
        sets the radius of observation for RL vehicles (meter)
        设置 RL 车辆的观察半径（米）
    show_radius : bool, optional
        specifies whether to render the radius of RL observation
        指定是否渲染RL观察的半径
    pxpm : int, optional
        specifies rendering resolution (pixel / meter)
        指定渲染分辨率（像素/米）
    force_color_update : bool, optional
        whether or not to automatically color vehicles according to their types
        是否根据类型自动为车辆着色
    """

    def __init__(self,
                 sim_step=0.1,
                 render=False,
                 restart_instance=False,
                 emission_path=None,
                 save_render=False,
                 sight_radius=25,
                 show_radius=False,
                 pxpm=2,
                 force_color_update=False):
        """Instantiate SimParams."""
        self.sim_step = sim_step
        self.render = render
        self.restart_instance = restart_instance
        self.emission_path = emission_path
        self.save_render = save_render
        self.sight_radius = sight_radius
        self.pxpm = pxpm
        self.show_radius = show_radius
        self.force_color_update = force_color_update


class AimsunParams(SimParams):
    """Aimsun-specific simulation parameters.

    Extends SimParams.

    Attributes
    ----------
    sim_step : float optional
        seconds per simulation step; 0.1 by default
    render : str or bool, optional
        specifies whether to visualize the rollout(s)

        * False: no rendering
        * True: delegate rendering to sumo-gui for back-compatibility
        * "gray": static grayscale rendering, which is good for training
        * "dgray": dynamic grayscale rendering
        * "rgb": static RGB rendering
        * "drgb": dynamic RGB rendering, which is good for visualization

    restart_instance : bool, optional
        specifies whether to restart a simulation upon reset. Restarting
        the instance helps avoid slowdowns cause by excessive inflows over
        large experiment runtimes, but also require the gui to be started
        after every reset if "render" is set to True.
    emission_path : str, optional
        Path to the folder in which to create the emissions output.
        Emissions output is not generated if this value is not specified
    save_render : bool, optional
        specifies whether to save rendering data to disk
    sight_radius : int, optional
        sets the radius of observation for RL vehicles (meter)
    show_radius : bool, optional
        specifies whether to render the radius of RL observation
    pxpm : int, optional
        specifies rendering resolution (pixel / meter)
    network_name : str, optional
        name of the network generated in Aimsun.
    experiment_name : str, optional
        name of the experiment generated in Aimsun
    replication_name : str, optional
        name of the replication generated in Aimsun. When loading
        an Aimsun template, this parameter must be set to the name
        of the replication to be run by the simulation; in this case,
        the network_name and experiment_name parameters are not
        necessary as they will be obtained from the replication name.
    centroid_config_name : str, optional
        name of the centroid configuration to load in Aimsun. This
        parameter is only used when loading an Aimsun template,
        not when generating one.
    subnetwork_name : str, optional
        name of the subnetwork to load in Aimsun. This parameter is not
        used when generating a network; it can be used when loading an
        Aimsun template containing a subnetwork in order to only load
        the objects contained in this subnetwork. If set to None or if the
        specified subnetwork does not exist, the whole network will be loaded.
    """

    def __init__(self,
                 sim_step=0.1,
                 render=False,
                 restart_instance=False,
                 emission_path=None,
                 save_render=False,
                 sight_radius=25,
                 show_radius=False,
                 pxpm=2,
                 # set to match Flow_Aimsun.ang's scenario name
                 network_name="Dynamic Scenario 866",
                 # set to match Flow_Aimsun.ang's experiment name
                 experiment_name="Micro SRC Experiment 867",
                 # set to match Flow_Aimsun.ang's replication name
                 replication_name="Replication 870",
                 centroid_config_name=None,
                 subnetwork_name=None):
        """Instantiate AimsunParams."""
        super(AimsunParams, self).__init__(
            sim_step, render, restart_instance, emission_path, save_render,
            sight_radius, show_radius, pxpm)
        self.network_name = network_name
        self.experiment_name = experiment_name
        self.replication_name = replication_name
        self.centroid_config_name = centroid_config_name
        self.subnetwork_name = subnetwork_name


class SumoParams(SimParams):
    """Sumo-specific simulation parameters.

    Extends SimParams.

    These parameters are used to customize a sumo simulation instance upon
    initialization. This includes passing the simulation step length,
    specifying whether to use sumo's gui during a run, and other features
    described in the Attributes below.
    这些参数用于在初始化时自定义SUMO模拟实例。 这包括传递模拟步长、指定是否在运行期间使用 sumo 的 gui，以及下面属性中描述的其他功能。

    Attributes
    ----------
    port : int, optional
        Port for Traci to connect to; finds an empty port by default
    sim_step : float optional
        seconds per simulation step; 0.1 by default
    emission_path : str, optional
        Path to the folder in which to create the emissions output.
        Emissions output is not generated if this value is not specified
    lateral_resolution : float, optional
        width of the divided sublanes within a lane, defaults to None (i.e.
        no sublanes). If this value is specified, the vehicle in the
        network cannot use the "LC2013" lane change model.
        车道内划分的子线的宽度，默认为None（无子线）。如果指定了该值，则网络中的车辆不能使用“LC2013”变道模型。
    no_step_log : bool, optional
        specifies whether to add sumo's step logs to the log file, and
        print them into the terminal during runtime, defaults to True
        指定是否将sumo的步骤日志添加到日志文件中，并在运行时将其打印到终端中，默认为True
    render : str or bool, optional
        specifies whether to visualize the rollout(s)

        * False: no rendering
        * True: delegate rendering to sumo-gui for back-compatibility
        * "gray": static grayscale rendering, which is good for training
        *“gray”：静态灰度渲染，有利于训练
        * "dgray": dynamic grayscale rendering
        *“dgray”：动态灰度渲染
        * "rgb": static RGB rendering
        *“rgb”：静态rgb渲染
        * "drgb": dynamic RGB rendering, which is good for visualization
        *“drgb”：动态RGB渲染，有利于可视化

    save_render : bool, optional
        specifies whether to save rendering data to disk
        指定是否将渲染数据保存到磁盘
    sight_radius : int, optional
        sets the radius of observation for RL vehicles (meter)
        设置RL车辆的观察半径（米）
    show_radius : bool, optional
        specifies whether to render the radius of RL observation
        指定是否渲染RL观测半径
    pxpm : int, optional
        specifies rendering resolution (pixel / meter)
        指定渲染分辨率（像素/米）
    force_color_update : bool, optional
        whether or not to automatically color vehicles according to their types
        是否根据车辆类型自动为车辆上色
    overtake_right : bool, optional
        whether vehicles are allowed to overtake on the right as well as the left
        是否允许车辆在右侧和左侧超车
    seed : int, optional
        seed for sumo instance
        SUMO实例种子
    restart_instance : bool, optional
        specifies whether to restart a sumo instance upon reset. Restarting
        the instance helps avoid slowdowns cause by excessive inflows over
        large experiment runtimes, but also require the gui to be started
        after every reset if "render" is set to True.
        指定重置时是否重新启动SUMO实例。重新启动实例有助于避免大型实验运行时过多的流入导致的速度减慢，
        但如果“render”设置为True，则还需要在每次重置后启动gui。
    print_warnings : bool, optional
        If set to false, this will silence sumo warnings on the stdout
    teleport_time : int, optional
        If negative, vehicles don't teleport in gridlock. If positive,
        they teleport after teleport_time seconds
        如果是否定的，车辆就不会在交通堵塞的情况下传送。如果是肯定的，则在传送时间秒后传送
    num_clients : int, optional
        Number of clients that will connect to Traci
    color_by_speed : bool
        whether to color the vehicles by the speed they are moving at the current time step
        是否根据车辆在当前时间步长的移动速度为车辆上色
    use_ballistic: bool, optional
        If true, use a ballistic integration step instead of an euler step
        如果为真，则使用弹道积分步骤而不是欧拉步骤
    """

    def __init__(self,
                 port=None,
                 sim_step=0.1,
                 emission_path=None,
                 lateral_resolution=None,
                 no_step_log=True,
                 render=False,
                 save_render=False,
                 sight_radius=25,
                 show_radius=False,
                 pxpm=2,
                 force_color_update=False,
                 overtake_right=False,
                 seed=None,
                 restart_instance=False,
                 print_warnings=True,
                 teleport_time=-1,
                 num_clients=1,
                 color_by_speed=False,
                 use_ballistic=False):
        """Instantiate SumoParams."""
        super(SumoParams, self).__init__(
            sim_step, render, restart_instance, emission_path, save_render,
            sight_radius, show_radius, pxpm, force_color_update)
        self.port = port
        self.lateral_resolution = lateral_resolution
        self.no_step_log = no_step_log
        self.seed = seed
        self.overtake_right = overtake_right
        self.print_warnings = print_warnings
        self.teleport_time = teleport_time
        self.num_clients = num_clients
        self.color_by_speed = color_by_speed
        self.use_ballistic = use_ballistic


class EnvParams:
    """Environment and experiment-specific parameters.

    This includes specifying the bounds of the action space and relevant
    coefficients to the reward function, as well as specifying how the
    positions of vehicles are modified in between rollouts.
    这包括指定动作空间的边界和奖励函数的相关系数，以及指定车辆位置在推出之间的修改方式。

    Attributes
    ----------
    additional_params : dict, optional
        Specify additional environment params for a specific
        environment configuration
        为特定环境配置指定额外的环境参数
    horizon : int, optional
        number of steps per rollouts
        每次推出的步骤数
    warmup_steps : int, optional
        number of steps performed before the initialization of training
        during a rollout. These warmup steps are not added as steps
        into training, and the actions of rl agents during these steps
        are dictated by sumo. Defaults to zero
        在推出期间训练初始化之前执行的步骤数。 这些热身步骤不会作为步骤添加到训练中，并且 rl 智能体在这些步骤中的动作由 sumo 决定。 默认为零
    sims_per_step : int, optional
        number of sumo simulation steps performed in any given rollout
        step. RL agents perform the same action for the duration of
        these simulation steps.
        在任何给定的推出步骤中执行的SUMO模拟步骤数。 RL代理在这些模拟步骤的持续时间内执行相同的操作。
    evaluate : bool, optional
        flag indicating that the evaluation reward should be used
        so the evaluation reward should be used rather than the
        normal reward
        flag 表示应该使用评估奖励所以应该使用评估奖励而不是正常奖励
    clip_actions : bool, optional
        specifies whether to clip actions from the policy by their range when
        they are inputted to the reward function. Note that the actions are
        still clipped before they are provided to `apply_rl_actions`.
        指定在将动作输入到奖励函数时是否按范围从策略中剪裁动作。 请注意，在将操作提供给“apply_rl_actions”之前，这些操作仍然会被剪裁。
    """

    def __init__(self,
                 additional_params=None,
                 horizon=float('inf'),
                 warmup_steps=0,
                 sims_per_step=1,
                 evaluate=False,
                 clip_actions=True):
        """Instantiate EnvParams."""
        self.additional_params = \
            additional_params if additional_params is not None else {}
        self.horizon = horizon
        self.warmup_steps = warmup_steps
        self.sims_per_step = sims_per_step
        self.evaluate = evaluate
        self.clip_actions = clip_actions

    def get_additional_param(self, key):
        """Return a variable from additional_params."""
        return self.additional_params[key]


class NetParams:
    """Network configuration parameters.

    Unlike most other parameters, NetParams may vary drastically dependent
    on the specific network configuration. For example, for the ring road
    the network parameters will include a characteristic length, number of
    lanes, and speed limit.
    与大多数其他参数不同，NetParams可能会根据特定的网络配置而发生巨大变化。 例如，对于环路，网络参数将包括特征长度、车道数和限速。

    In order to determine which additional_params variable may be needed
    for a specific network, refer to the ADDITIONAL_NET_PARAMS variable
    located in the network file.
    为了确定特定网络可能需要哪个 additional_params 变量，请参考位于网络文件中的 ADDITIONAL_NET_PARAMS 变量。

    Attributes
    ----------
    inflows : InFlows type, optional
        specifies the inflows of specific edges and the types of vehicles
        entering the network from these edges
        指定特定边的流入以及从这些边进入网络的车辆类型
    osm_path : str, optional
        path to the .osm file that should be used to generate the network
        configuration files
        应该用于生成网络配置文件的 .osm 文件的路径
    template : str, optional
        path to the network template file that can be used to instantiate a
        netowrk in the simulator of choice
        可用于在所选模拟器中实例化网络的网络模板文件的路径
    additional_params : dict, optional
        network specific parameters; see each subclass for a description of
        what is needed
        网络特定参数； 查看每个子类以获取所需内容的描述
    """

    def __init__(self,
                 inflows=None,
                 osm_path=None,
                 template=None,
                 additional_params=None):
        """Instantiate NetParams."""
        self.inflows = inflows or InFlows()
        self.osm_path = osm_path
        self.template = template
        self.additional_params = additional_params or {}


class InitialConfig:
    """Initial configuration parameters.

    These parameters that affect the positioning of vehicle in the
    network at the start of a rollout. By default, vehicles are uniformly
    distributed in the network.
    这些参数会在首次推出时影响车辆在网络中的定位。 默认情况下，车辆在网络中均匀分布。

    Attributes
    ----------
    shuffle : bool, optional  # TODO: remove
        specifies whether the ordering of vehicles in the Vehicles class
        should be shuffled upon initialization.
        指定 Vehicles 类中车辆的顺序是否应在初始化时打乱。
    spacing : str, optional
        specifies the positioning of vehicles in the network relative to
        one another. May be one of: "uniform", "random", or "custom".
        Default is "uniform".
        指定车辆在网络中的相对位置。 可能是以下之一：“统一”、“随机”或“自定义”。 默认为“统一”。
    min_gap : float, optional  # TODO: remove
        minimum gap between two vehicles upon initialization, in meters.
        Default is 0 m.
        初始化时两辆车之间的最小间隙，以米为单位。 默认值为 0 米。
    x0 : float, optional  # TODO: remove
        position of the first vehicle to be placed in the network
        放置在网络中的第一辆车的位置
    perturbation : float, optional
        standard deviation used to perturb vehicles from their uniform
        position, in meters. Default is 0 m.
        用于扰乱车辆从其统一位置的标准偏差，以米为单位。 默认值为 0 米。
    bunching : float, optional
        reduces the portion of the network that should be filled with
        vehicles by this amount.
        减少了网络中应该由车辆填充的部分
    lanes_distribution : int, optional
        number of lanes vehicles should be dispersed into. If the value is
        greater than the total number of lanes on an edge, vehicles are
        spread across all lanes.
        车辆应分散到多个车道。如果该值大于边缘上的车道总数，则车辆将分布在所有车道上。
    edges_distribution : str or list of str or dict, optional
        edges vehicles may be placed on during initialization,
        在初始化过程中，可以放置边缘车辆
        may be one of:
        * "all": vehicles are distributed over all edges
        *“所有”：车辆分布在所有边缘
        * list of edges: list of edges vehicles can be distributed over
        *边缘列表：车辆可以分布的边缘列表
        * dict of edges: where the key is the name of the edge to be
          utilized, and the elements are the number of cars to place on
          each edge
        *边的字典：其中键是要使用的边的名称，元素是要放置在每个边上的汽车的数量
    additional_params : dict, optional
        some other network-specific params
    """

    def __init__(self,
                 shuffle=False,
                 spacing="uniform",
                 min_gap=0,
                 perturbation=0.0,
                 x0=0,
                 bunching=0,
                 lanes_distribution=float("inf"),
                 edges_distribution="all",
                 additional_params=None):
        """Instantiate InitialConfig.

        These parameters that affect the positioning of vehicle in the
        network at the start of a rollout. By default, vehicles are uniformly
        distributed in the network.
        """
        self.shuffle = shuffle
        self.spacing = spacing
        self.min_gap = min_gap
        self.perturbation = perturbation
        self.x0 = x0
        self.bunching = bunching
        self.lanes_distribution = lanes_distribution
        self.edges_distribution = edges_distribution
        self.additional_params = additional_params or dict()


class SumoCarFollowingParams:
    """Parameters for sumo-controlled acceleration behavior.

    Attributes
    ----------
    speed_mode : str or int, optional
        may be one of the following:

         * "right_of_way" (default): respect safe speed, right of way and
           brake hard at red lights if needed. DOES NOT respect
           max accel and decel which enables emergency stopping.
           Necessary to prevent custom models from crashing
*“right_of_way”（默认值）：遵守安全速度、路权，必要时在红灯时用力刹车。不遵守允许紧急停车的最大加速和减速。有必要防止自定义模型崩溃
         * "obey_safe_speed": prevents vehicles from colliding
           longitudinally, but can fail in cases where vehicles are allowed
           to lane change
*“obey_safe_speed”：防止车辆纵向碰撞，但在允许车辆变道的情况下可能会失败
         * "no_collide": Human and RL cars are preventing from reaching
           speeds that may cause crashes (also serves as a failsafe). Note:
           this may lead to collisions in complex networks
*“no_cluster”：人类和RL汽车正在防止达到可能导致碰撞的速度（也用作故障保护）。注意：这可能会导致复杂网络中的冲突
         * "aggressive": Human and RL cars are not limited by sumo with
           regard to their accelerations, and can crash longitudinally
*“攻击性”：人类和RL赛车的加速度不受SUMO的限制，可以纵向碰撞
         * "all_checks": all sumo safety checks are activated
*“all_checks”：所有SUMO安全检查均已激活
         * int values may be used to define custom speed mode for the given
           vehicles, specified at:
           http://sumo.dlr.de/wiki/TraCI/Change_Vehicle_State#speed_mode_.280xb3.29

    accel : float
        see Note
    decel : float
        see Note
    sigma : float
        see Note
    tau : float
        see Note
    min_gap : float
        see minGap Note
    max_speed : float
        see maxSpeed Note
    speed_factor : float
        see speedFactor Note
    speed_dev : float
        see speedDev in Note
    impatience : float
        see Note
    car_follow_model : str
        see carFollowModel in Note
    kwargs : dict
        used to handle deprecations

    Note
    ----
    For a description of all params, see:
    http://sumo.dlr.de/wiki/Definition_of_Vehicles,_Vehicle_Types,_and_Routes
    """

    def __init__(
            self,
            speed_mode='right_of_way',
            accel=2.6,
            decel=4.5,
            sigma=0.5,
            tau=1.0,  # past 1 at sim_step=0.1 you no longer see waves
            min_gap=2.5,
            max_speed=30,
            speed_factor=1.0,
            speed_dev=0.1,
            impatience=0.5,
            car_follow_model="IDM",
            **kwargs):
        """Instantiate SumoCarFollowingParams."""
        # check for deprecations (minGap)
        if "minGap" in kwargs:
            deprecated_attribute(self, "minGap", "min_gap")
            min_gap = kwargs["minGap"]

        # check for deprecations (maxSpeed)
        if "maxSpeed" in kwargs:
            deprecated_attribute(self, "maxSpeed", "max_speed")
            max_speed = kwargs["maxSpeed"]

        # check for deprecations (speedFactor)
        if "speedFactor" in kwargs:
            deprecated_attribute(self, "speedFactor", "speed_factor")
            speed_factor = kwargs["speedFactor"]

        # check for deprecations (speedDev)
        if "speedDev" in kwargs:
            deprecated_attribute(self, "speedDev", "speed_dev")
            speed_dev = kwargs["speedDev"]

        # check for deprecations (carFollowModel)
        if "carFollowModel" in kwargs:
            deprecated_attribute(self, "carFollowModel", "car_follow_model")
            car_follow_model = kwargs["carFollowModel"]

        # create a controller_params dict with all the specified parameters
        self.controller_params = {
            "accel": accel,
            "decel": decel,
            "sigma": sigma,
            "tau": tau,
            "minGap": min_gap,
            "maxSpeed": max_speed,
            "speedFactor": speed_factor,
            "speedDev": speed_dev,
            "impatience": impatience,
            "carFollowModel": car_follow_model,
        }

        # adjust the speed mode value
        if isinstance(speed_mode, str) and speed_mode in SPEED_MODES:
            speed_mode = SPEED_MODES[speed_mode]
        elif not (isinstance(speed_mode, int)
                  or isinstance(speed_mode, float)):
            logging.error("Setting speed mode of to default.")
            speed_mode = SPEED_MODES["obey_safe_speed"]

        self.speed_mode = speed_mode


class SumoLaneChangeParams:
    """Parameters for sumo-controlled lane change behavior.

    Attributes
    ----------
    lane_change_mode : str or int, optional
        may be one of the following:
        * "no_lc_safe" (default): Disable all SUMO lane changing but still
          handle safety checks (collision avoidance and safety-gap enforcement)
          in the simulation. Binary is [001000000000]
*“no_lc_safe”（默认值）：禁用所有SUMO变道，但仍在模拟中处理安全检查（避免碰撞和加强安全间隙）。二进制为[00001000000000]
        * "no_lc_aggressive": SUMO lane changes are not executed, collision
          avoidance and safety-gap enforcement are off.
          Binary is [000000000000]
*“no_lc_aggressive”：SUMO车道变更未执行，防撞和安全间距强制关闭。二进制为[m000000000000]
        * "sumo_default": Execute all changes requested by a custom controller
          unless in conflict with TraCI. Binary is [011001010101].
*“sumo_default”：执行自定义控制器请求的所有更改，除非与TraCI冲突。二进制为[0110001010101]。
        * "no_strategic_aggressive": Execute all changes except strategic
          (routing) lane changes unless in conflict with TraCI. Collision
          avoidance and safety-gap enforcement are off. Binary is [010001010100]
*“no_storial_aggressive”：执行除策略（路线）车道更改外的所有更改，除非与TraCI冲突。防撞和安全间隙强制关闭。二进制代码为[010001010100]
        * "no_strategic_safe": Execute all changes except strategic
          (routing) lane changes unless in conflict with TraCI. Collision
          avoidance and safety-gap enforcement are on. Binary is [011001010100]
*“no_stegic_safe”：执行除策略（路线）车道更改外的所有更改，除非与TraCI冲突。防撞和安全间隙强制已启用。二进制代码为[0110001010100]
        * "only_strategic_aggressive": Execute only strategic (routing) lane
          changes unless in conflict with TraCI. Collision avoidance and
          safety-gap enforcement are off. Binary is [000000000001]
*“only_strategic_aggressive”：仅执行策略（路线）车道更改，除非与TraCI冲突。防撞和安全间隙强制关闭。二进制值为[0000000000001]
        * "only_strategic_safe": Execute only strategic (routing) lane
          changes unless in conflict with TraCI. Collision avoidance and
          safety-gap enforcement are on. Binary is [001000000001]
*“only_strategic_safe”：仅执行策略（路线）车道更改，除非与TraCI冲突。防撞和安全间隙强制已启用。二进制代码为[00100100000001]
        * "no_cooperative_aggressive": Execute all changes except cooperative
          (change in order to allow others to change) lane changes unless in
          conflict with TraCI. Collision avoidance and safety-gap enforcement
          are off. Binary is [010001010001]
*“no-cooperative_aggressive”：执行除合作（为了允许其他人改变而改变）车道外的所有改变，除非与TraCI冲突。防撞和安全间隙强制关闭。二进制为[010001010001]
        * "no_cooperative_safe": Execute all changes except cooperative
          lane changes unless in conflict with TraCI. Collision avoidance and
          safety-gap enforcement are on. Binary is [011001010001]
*“no-cooperative_safe”：执行除合作车道变更外的所有变更，除非与TraCI冲突。防撞和安全间隙强制已启用。二进制代码为[01100010001]
        * "only_cooperative_aggressive": Execute only cooperative lane changes
          unless in conflict with TraCI. Collision avoidance and safety-gap
          enforcement are off. Binary is [000000000100]
*“only_cooperative_aggressive”：仅执行合作车道变更，除非与TraCI冲突。防撞和安全间隙强制关闭。二进制值为[00000000000100]
        * "only_cooperative_safe": Execute only cooperative lane changes
          unless in conflict with TraCI. Collision avoidance and safety-gap
          enforcement are on. Binary is [001000000100]
*“only_cooperative_safe”：仅执行合作车道变更，除非与TraCI冲突。防撞和安全间隙强制已启用。二进制值为[00100100000100]
        * "no_speed_gain_aggressive": Execute all changes except speed gain (the
           other lane allows for faster driving) lane changes unless in conflict
           with TraCI. Collision avoidance and safety-gap enforcement are off.
           Binary is [010001000101]
*“no_speed_gain_aggressive”：执行除速度增益（另一条车道允许更快的行驶）以外的所有车道更改，除非与TraCI冲突。防撞和安全间隙强制关闭。二进制为[0010001000101]
        * "no_speed_gain_safe": Execute all changes except speed gain
          lane changes unless in conflict with TraCI. Collision avoidance and
          safety-gap enforcement are on. Binary is [011001000101]
*“no_speed_gain_safe”：执行除速度增益车道更改外的所有更改，除非与TraCI冲突。防撞和安全间隙强制已启用。二进制代码为[01100001001]
        * "only_speed_gain_aggressive": Execute only speed gain lane changes
          unless in conflict with TraCI. Collision avoidance and safety-gap
          enforcement are off. Binary is [000000010000]
*“only_speed_gain_aggressive”：仅执行速度增益车道更改，除非与TraCI冲突。防撞和安全间隙强制关闭。二进制值为【0000000 10000】
        * "only_speed_gain_safe": Execute only speed gain lane changes
          unless in conflict with TraCI. Collision avoidance and safety-gap
          enforcement are on. Binary is [001000010000]
*“only_speed_gain_safe”：仅执行速度增益车道更改，除非与TraCI冲突。防撞和安全间隙强制已启用。二进制为[00100100010000]
        * "no_right_drive_aggressive": Execute all changes except right drive
          (obligation to drive on the right) lane changes unless in conflict
          with TraCI. Collision avoidance and safety-gap enforcement are off.
          Binary is [010000010101]
*“no_right_drive_aggressive”：执行除右舵驾驶（右舵驾驶义务）车道变更外的所有变更，除非与TraCI冲突。防撞和安全间隙强制关闭。二进制为[0100000010101]
        * "no_right_drive_safe": Execute all changes except right drive
          lane changes unless in conflict with TraCI. Collision avoidance and
          safety-gap enforcement are on. Binary is [011000010101]
*“no_right_drive_safe”：执行除右侧车道更改外的所有更改，除非与TraCI冲突。防撞和安全间隙强制已启用。二进制代码为[0110000010101]
        * "only_right_drive_aggressive": Execute only right drive lane changes
          unless in conflict with TraCI. Collision avoidance and safety-gap
          enforcement are off. Binary is [000001000000]
*“only_right_drive_aggressive”：仅执行右侧车道更改，除非与TraCI冲突。防撞和安全间隙强制关闭。二进制值为[0000001000000]
        * "only_right_drive_safe": Execute only right drive lane changes
          unless in conflict with TraCI. Collision avoidance and safety-gap
          enforcement are on. Binary is [001001000000]
*“only_right_drive_safe”：仅执行右侧车道更改，除非与TraCI冲突。防撞和安全间隙强制启用。二进制为[00100101000000]

        * int values may be used to define custom lane change modes for the
          given vehicles, specified at:
          http://sumo.dlr.de/wiki/TraCI/Change_Vehicle_State#lane_change_mode_.280xb6.29

    model : str, optional
        see laneChangeModel in Note
    lc_strategic : float, optional
        see lcStrategic in Note
    lc_cooperative : float, optional
        see lcCooperative in Note
    lc_speed_gain : float, optional
        see lcSpeedGain in Note
    lc_keep_right : float, optional
        see lcKeepRight in Note
    lc_look_ahead_left : float, optional
        see lcLookaheadLeft in Note
    lc_speed_gain_right : float, optional
        see lcSpeedGainRight in Note
    lc_sublane : float, optional
        see lcSublane in Note
    lc_pushy : float, optional
        see lcPushy in Note
    lc_pushy_gap : float, optional
        see lcPushyGap in Note
    lc_assertive : float, optional
        see lcAssertive in Note
    lc_accel_lat : float, optional
        see lcAccelLate in Note
    kwargs : dict
        used to handle deprecations

    Note
    ----
    For a description of all params, see:
    http://sumo.dlr.de/wiki/Definition_of_Vehicles,_Vehicle_Types,_and_Routes
    """

    def __init__(self,
                 lane_change_mode="no_lc_safe",
                 model="LC2013",
                 lc_strategic=1.0,
                 lc_cooperative=1.0,
                 lc_speed_gain=1.0,
                 lc_keep_right=1.0,
                 lc_look_ahead_left=2.0,
                 lc_speed_gain_right=1.0,
                 lc_sublane=1.0,
                 lc_pushy=0,
                 lc_pushy_gap=0.6,
                 lc_assertive=1,
                 lc_accel_lat=1.0,
                 **kwargs):
        """Instantiate SumoLaneChangeParams."""
        # check for deprecations (lcStrategic)
        if "lcStrategic" in kwargs:
            deprecated_attribute(self, "lcStrategic", "lc_strategic")
            lc_strategic = kwargs["lcStrategic"]

        # check for deprecations (lcCooperative)
        if "lcCooperative" in kwargs:
            deprecated_attribute(self, "lcCooperative", "lc_cooperative")
            lc_cooperative = kwargs["lcCooperative"]

        # check for deprecations (lcSpeedGain)
        if "lcSpeedGain" in kwargs:
            deprecated_attribute(self, "lcSpeedGain", "lc_speed_gain")
            lc_speed_gain = kwargs["lcSpeedGain"]

        # check for deprecations (lcKeepRight)
        if "lcKeepRight" in kwargs:
            deprecated_attribute(self, "lcKeepRight", "lc_keep_right")
            lc_keep_right = kwargs["lcKeepRight"]

        # check for deprecations (lcLookaheadLeft)
        if "lcLookaheadLeft" in kwargs:
            deprecated_attribute(self, "lcLookaheadLeft", "lc_look_ahead_left")
            lc_look_ahead_left = kwargs["lcLookaheadLeft"]

        # check for deprecations (lcSpeedGainRight)
        if "lcSpeedGainRight" in kwargs:
            deprecated_attribute(self, "lcSpeedGainRight",
                                 "lc_speed_gain_right")
            lc_speed_gain_right = kwargs["lcSpeedGainRight"]

        # check for deprecations (lcSublane)
        if "lcSublane" in kwargs:
            deprecated_attribute(self, "lcSublane", "lc_sublane")
            lc_sublane = kwargs["lcSublane"]

        # check for deprecations (lcPushy)
        if "lcPushy" in kwargs:
            deprecated_attribute(self, "lcPushy", "lc_pushy")
            lc_pushy = kwargs["lcPushy"]

        # check for deprecations (lcPushyGap)
        if "lcPushyGap" in kwargs:
            deprecated_attribute(self, "lcPushyGap", "lc_pushy_gap")
            lc_pushy_gap = kwargs["lcPushyGap"]

        # check for deprecations (lcAssertive)
        if "lcAssertive" in kwargs:
            deprecated_attribute(self, "lcAssertive", "lc_assertive")
            lc_assertive = kwargs["lcAssertive"]

        # check for deprecations (lcAccelLat)
        if "lcAccelLat" in kwargs:
            deprecated_attribute(self, "lcAccelLat", "lc_accel_lat")
            lc_accel_lat = kwargs["lcAccelLat"]

        # check for valid model
        if model not in ["LC2013", "SL2015"]:
            logging.error("Invalid lane change model! Defaulting to LC2013")
            model = "LC2013"

        if model == "LC2013":
            self.controller_params = {
                "laneChangeModel": model,
                "lcStrategic": str(lc_strategic),
                "lcCooperative": str(lc_cooperative),
                "lcSpeedGain": str(lc_speed_gain),
                "lcKeepRight": str(lc_keep_right),
                # "lcLookaheadLeft": str(lc_look_ahead_left),
                # "lcSpeedGainRight": str(lcSpeedGainRight)
            }
        elif model == "SL2015":
            self.controller_params = {
                "laneChangeModel": model,
                "lcStrategic": str(lc_strategic),
                "lcCooperative": str(lc_cooperative),
                "lcSpeedGain": str(lc_speed_gain),
                "lcKeepRight": str(lc_keep_right),
                "lcLookaheadLeft": str(lc_look_ahead_left),
                "lcSpeedGainRight": str(lc_speed_gain_right),
                "lcSublane": str(lc_sublane),
                "lcPushy": str(lc_pushy),
                "lcPushyGap": str(lc_pushy_gap),
                "lcAssertive": str(lc_assertive),
                "lcAccelLat": str(lc_accel_lat)
            }

        # adjust the lane change mode value
        if isinstance(lane_change_mode, str) and lane_change_mode in LC_MODES:
            lane_change_mode = LC_MODES[lane_change_mode]
        elif not (isinstance(lane_change_mode, int)
                  or isinstance(lane_change_mode, float)):
            logging.error("Setting lane change mode to default.")
            lane_change_mode = LC_MODES["no_lc_safe"]

        self.lane_change_mode = lane_change_mode


class InFlows:
    """Used to add inflows to a network.

    Inflows can be specified for any edge that has a specified route or routes.
    可以为具有指定路径或路径的任何边指定流入。
    """

    def __init__(self):
        """Instantiate Inflows."""
        self.__flows = []

    def add(self,
            edge,
            veh_type,
            vehs_per_hour=None,
            probability=None,
            period=None,
            depart_lane="first",
            depart_speed=0,
            name="flow",
            begin=1,
            end=86400,
            number=None,
            **kwargs):
        r"""Specify a new inflow for a given type of vehicles and edge.

        Parameters
        ----------
        edge : str
            starting edge for the vehicles in this inflow
        veh_type : str
            type of the vehicles entering the edge. Must match one of the types
            set in the Vehicles class
        vehs_per_hour : float, optional
            number of vehicles per hour, equally spaced (in vehicles/hour).
            Cannot be specified together with probability or period
        probability : float, optional
            probability for emitting a vehicle each second (between 0 and 1).
            Cannot be specified together with vehs_per_hour or period
        period : float, optional
            insert equally spaced vehicles at that period (in seconds). Cannot
            be specified together with vehs_per_hour or probability
        depart_lane : int or str
            the lane on which the vehicle shall be inserted. Can be either one
            of:

            * int >= 0: index of the lane (starting with rightmost = 0)
            * "random": a random lane is chosen, but the vehicle insertion is
              not retried if it could not be inserted
            * "free": the most free (least occupied) lane is chosen
            * "best": the "free" lane (see above) among those who allow the
              vehicle the longest ride without the need to change lane
            * "first": the rightmost lane the vehicle may use

            Defaults to "first".
        depart_speed : float or str
            the speed with which the vehicle shall enter the network (in m/s)
            can be either one of:

            - float >= 0: the vehicle is tried to be inserted using the given
              speed; if that speed is unsafe, departure is delayed
            - "random": vehicles enter the edge with a random speed between 0
              and the speed limit on the edge; the entering speed may be
              adapted to ensure a safe distance to the leading vehicle is kept
            - "speedLimit": vehicles enter the edge with the maximum speed that
              is allowed on this edge; if that speed is unsafe, departure is
              delayed

            Defaults to 0.
        name : str, optional
            prefix for the id of the vehicles entering via this inflow.
            Defaults to "flow"
        begin : float, optional
            first vehicle departure time (in seconds, minimum 1 second).
            Defaults to 1 second
        end : float, optional
            end of departure interval (in seconds). This parameter is not taken
            into account if 'number' is specified. Defaults to 24 hours
        number : int, optional
            total number of vehicles the inflow should create (due to rounding
            up, this parameter may not be exactly enforced and shouldn't be set
            too small). Default: infinite (c.f. 'end' parameter)
        kwargs : dict, optional
            see Note

        Note
        ----
        For information on the parameters start, end, vehs_per_hour,
        probability, period, number, as well as other vehicle type and routing
        parameters that may be added via \*\*kwargs, refer to:
        http://sumo.dlr.de/wiki/Definition_of_Vehicles,_Vehicle_Types,_and_Routes
        """
        # check for deprecations
        def deprecate(old, new):
            deprecated_attribute(self, old, new)
            new_val = kwargs[old]
            del kwargs[old]
            return new_val

        if "vehsPerHour" in kwargs:
            vehs_per_hour = deprecate("vehsPerHour", "vehs_per_hour")
        if "departLane" in kwargs:
            depart_lane = deprecate("departLane", "depart_lane")
        if "departSpeed" in kwargs:
            depart_speed = deprecate("departSpeed", "depart_speed")

        new_inflow = {
            "name": "%s_%d" % (name, len(self.__flows)),
            "vtype": veh_type,
            "edge": edge,
            "departLane": depart_lane,
            "departSpeed": depart_speed,
            "begin": begin,
            "end": end
        }
        new_inflow.update(kwargs)

        inflow_params = [vehs_per_hour, probability, period]
        n_inflow_params = len(inflow_params) - inflow_params.count(None)
        if n_inflow_params != 1:
            raise ValueError(
                "Exactly one among the three parameters 'vehs_per_hour', "
                "'probability' and 'period' must be specified in InFlows.add. "
                "{} were specified.".format(n_inflow_params))
        if probability is not None and (probability < 0 or probability > 1):
            raise ValueError(
                "Inflow.add called with parameter 'probability' set to {}, but"
                " probability should be between 0 and 1.".format(probability))
        if begin is not None and begin < 1:
            raise ValueError(
                "Inflow.add called with parameter 'begin' set to {}, but begin"
                " should be greater or equal than 1 second.".format(begin))

        if number is not None:
            del new_inflow["end"]
            new_inflow["number"] = number

        if vehs_per_hour is not None:
            new_inflow["vehsPerHour"] = vehs_per_hour
        if probability is not None:
            new_inflow["probability"] = probability
        if period is not None:
            new_inflow["period"] = period

        self.__flows.append(new_inflow)

    def get(self):
        """Return the inflows of each edge."""
        return self.__flows
