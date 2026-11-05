from glob import glob
import os

from setuptools import setup

package_name = 'localization_lab'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.lua') + glob('config/*.yaml')
        ),
        (
            os.path.join('share', package_name, 'rviz'),
            glob('rviz/*.rviz')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='docente',
    maintainer_email='docente@lab.com',
    description='Localization and SLAM laboratory',
    license='Apache-2.0',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'simple_controller = localization_lab.simple_controller:main',
        ],
    },
)
