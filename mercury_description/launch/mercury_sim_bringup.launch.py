import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node, SetParameter
from ament_index_python.packages import get_package_share_directory
import xacro
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    ld = LaunchDescription()

    # Specify the name of the package and path to xacro file within the package
    pkg_name = 'mercury_description'
    file_subpath = 'urdf/mercury.urdf.xacro'

    # Use xacro to process the file - this gets published on the /robot_description topic
    xacro_file = os.path.join(get_package_share_directory(pkg_name), file_subpath)
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # robot state publisher node
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_description_raw}],
        output='screen'
    )

    # Include the launch file from coursework2 package
    coursework2_launch_file = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [get_package_share_directory('coursework2'), '/launch', '/sim_bringup.launch.py']),
        launch_arguments={}.items(),
    )

    # Spawn the robot model in Gazebo using ros_gz_sim create
    node_spawn_entity = Node(
        package='ros_gz_sim', executable='create',
        arguments=['-topic', '/robot_description', '-z', '0.5'],
        output='screen'
    )

    # Bridge
    # https://github.com/gazebosim/ros_gz/tree/humble/ros_gz_bridge
    node_ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=  [
                    # Ros2 Topic + Ros2 Message Type + Ignition Msg Type
                    '/model/mercury/cmd_vel'  + '@geometry_msgs/msg/Twist'   + '@' + 'ignition.msgs.Twist',
                    '/model/mercury/odometry' + '@nav_msgs/msg/Odometry'     + '[' + 'ignition.msgs.Odometry',
                    '/model/mercury/scan'     + '@sensor_msgs/msg/LaserScan' + '@' + 'ignition.msgs.LaserScan',
                    '/model/mercury/tf'       + '@tf2_msgs/msg/TFMessage'    + '[' + 'ignition.msgs.Pose_V',
                    '/model/mercury/imu'      + '@sensor_msgs/msg/Imu'       + '[' + 'ignition.msgs.IMU',
                    '/model/mercury/depth'    + '@sensor_msgs/msg/Image'     + '@' + 'ignition.msgs.Image',
                    '/world/empty/model/mercury/joint_state' + '@sensor_msgs/msg/JointState' + '[' + 'ignition.msgs.Model',
                    ],
        parameters= [{'qos_overrides./mercury.subscriber.reliability': 'reliable'}],
        remappings= [
                    # command velocity remmaped to /mercury/cmd_vel
                    ('/model/mercury/cmd_vel',  '/mercury/cmd_vel'),
                    # odometry diff. drive wheel dead-reckoning remapped to /odom_raw
                    ('/model/mercury/odometry', '/odom_raw'),
                    # laser scan remapped to /scan
                    ('/model/mercury/scan',     '/scan'),
                    ('/model/mercury/tf',       '/tf'),
                    # imu remapped to /imu_raw
                    ('/model/mercury/imu',      '/imu_raw'),
                    # depth camer remapped to /depth
                    ('/model/mercury/depth', '/depth'),
                    ('/world/empty/model/mercury/joint_state', 'joint_states')
                    ],
        output='screen'
    )

    # Define the twist_mux node
    twist_mux = os.path.join(get_package_share_directory(pkg_name), 'config', 'twist_mux.yaml')

    twist_mux_node = Node(
         package='twist_mux',
         executable='twist_mux',
         name='twist_mux',
         parameters=[twist_mux],
         output='screen'
     )

    # Define the teleop_twist_keyboard node
    teleop_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        prefix='xterm -e',  # Opens in a new terminal
        remappings=[
            ('/cmd_vel', '/teleop_cmd_vel'),
        ],
        output='screen'
    )


    # Add actions to LaunchDescription
    ld.add_action(SetParameter(name='use_sim_time', value=True))
    ld.add_action(node_robot_state_publisher)
    ld.add_action(node_ros_gz_bridge)
    ld.add_action(coursework2_launch_file)
    ld.add_action(node_spawn_entity)
    ld.add_action(twist_mux_node)
    ld.add_action(teleop_node)


    return ld
