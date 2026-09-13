from glob import glob

from setuptools import setup

package_name = 'vehicle_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='neel',
    maintainer_email='neelnaik2005@gmail.com',
    description='ROS 2 to serial drive-by-wire bridge for the real vehicle, plus the shared steering-relay controller tesla_sim uses in simulation.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'serial_bridge_node = vehicle_bridge.serial_bridge_node:main',
        ],
    },
)
