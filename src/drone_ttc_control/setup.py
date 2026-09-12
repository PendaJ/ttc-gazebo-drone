from glob import glob
from setuptools import find_packages, setup

package_name = 'drone_ttc_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Msuega Iorpenda',
    maintainer_email='iorpendaj2@gmail.com',
    description=(
        'ROS 2 control and synchronized image/odometry capture for '
        'X3 UAV monocular TTC experiments.'
    ),
    license='BSD-3-Clause',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'ttc_experiment = drone_ttc_control.ttc_experiment:main',
        ],
    },
)
