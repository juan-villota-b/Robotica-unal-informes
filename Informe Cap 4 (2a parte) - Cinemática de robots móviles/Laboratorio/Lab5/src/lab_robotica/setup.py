from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'lab_robotica'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.rviz')),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='juan-villota-b',
    maintainer_email='juvillotab@unal.edu.co',
    description='Control de robots moviles - Guia CAP4 (Corke): '
                'actividades 3, 4 y 5 en el TurtleBot3',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'act3_linea_turtlebot3 = lab_robotica.act3_linea_turtlebot3:main',
            'act4_pure_pursuit_turtlebot3 = lab_robotica.act4_pure_pursuit_turtlebot3:main',
            'act5_go_to_goal = lab_robotica.act5_go_to_goal:main',
        ],
    },
)
