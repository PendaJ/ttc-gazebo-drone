from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    default_params = PathJoinSubstitution([
        FindPackageShare('drone_ttc_control'),
        'config',
        'experiment.yaml',
    ])

    params_arg = DeclareLaunchArgument(
        'params_file',
        default_value=default_params,
        description='ROS 2 parameter YAML for the TTC experiment.',
    )

    experiment = Node(
        package='drone_ttc_control',
        executable='ttc_experiment',
        name='ttc_experiment',
        output='screen',
        parameters=[LaunchConfiguration('params_file')],
    )

    return LaunchDescription([
        params_arg,
        experiment,
    ])
