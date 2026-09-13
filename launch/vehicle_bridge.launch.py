"""Launch the real-vehicle serial bridge.

Launch arguments:
  serial_port  device path for the drive-by-wire serial link (default /dev/ttyUSB0)
  dry_run      compute relay decisions and log them but never write to serial
               (default false) -- useful for testing the bridge against a
               live /cmd_ackermann + /steering/angle stream with no hardware
               attached, or with hardware attached but power intentionally off.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('dry_run', default_value='false'),
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
    ])
