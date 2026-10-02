"""Launch the real-vehicle serial bridge and the steering encoder reader.

Launch arguments:
  serial_port        device path for the drive-by-wire serial link (default /dev/ttyUSB0)
  dry_run            compute relay decisions and log them but never write to serial
                     (default false) -- useful for testing the bridge against a
                     live /cmd_ackermann + /steering/angle stream with no hardware
                     attached, or with hardware attached but power intentionally off.
  encoder            also start encoder_node to publish /steering/angle (default true);
                     set false if something else publishes it.
  encoder_port       device path for the steering encoder MCU (default /dev/ttyACM0)
  encoder_baud       encoder MCU baud rate (default 115200)
  encoder_config     YAML with the encoder calibration (degrees_per_count, invert,
                     offset_deg); default is this package's config/encoder.yaml
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('dry_run', default_value='false'),
        DeclareLaunchArgument('encoder', default_value='true'),
        DeclareLaunchArgument('encoder_port', default_value='/dev/ttyACM0'),
        DeclareLaunchArgument('encoder_baud', default_value='115200'),
        DeclareLaunchArgument('encoder_config', default_value=PathJoinSubstitution(
            [FindPackageShare('vehicle_bridge'), 'config', 'encoder.yaml'])),
        Node(
            package='vehicle_bridge',
            executable='serial_bridge_node',
            name='serial_bridge_node',
            output='screen',
            parameters=[{
                'serial_port': LaunchConfiguration('serial_port'),
                'dry_run': LaunchConfiguration('dry_run'),
            }],
        ),
        Node(
            package='vehicle_bridge',
            executable='encoder_node',
            name='encoder_node',
            output='screen',
            condition=IfCondition(LaunchConfiguration('encoder')),
            parameters=[LaunchConfiguration('encoder_config'), {
                'serial_port': LaunchConfiguration('encoder_port'),
                'baud': ParameterValue(LaunchConfiguration('encoder_baud'), value_type=int),
            }],
        ),
    ])
