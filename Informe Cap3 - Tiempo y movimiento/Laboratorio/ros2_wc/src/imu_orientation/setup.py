from setuptools import find_packages, setup

package_name = 'imu_orientation'

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
            'imu_integrator = imu_orientation.imu_integrator:main',
            'imu_simulator = imu_orientation.imu_simulator:main',
        ],
    },
)
