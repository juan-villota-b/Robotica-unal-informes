from setuptools import find_packages, setup

package_name = 'cuaterniones_ros2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='juan-villota-b',
    maintainer_email='juvillotab@unal.edu.co',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'act1_conversion = cuaterniones_ros2.act1_conversion:main',
            'act2_no_conmutativa = cuaterniones_ros2.act2_no_conmutativa:main',
            'act3_pose_publisher = cuaterniones_ros2.act3_pose_publisher:main',
            'act4_tf_broadcaster = cuaterniones_ros2.act4_tf_broadcaster:main',
            'act5_error_orientacion = cuaterniones_ros2.act5_error_orientacion:main',
            'act6_slerp = cuaterniones_ros2.act6_slerp:main',
        ],
    },
)
