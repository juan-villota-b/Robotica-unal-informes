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
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='juan-villota-b',
    maintainer_email='juvillotab@unal.edu.co',
    description='Modelado y control de robots moviles - Guia de laboratorio CAP4 (Corke)',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'act1_modelo_bicicleta = lab_robotica.act1_modelo_bicicleta:main',
            'act2_ir_a_punto = lab_robotica.act2_ir_a_punto:main',
            'act3_seguimiento_linea = lab_robotica.act3_seguimiento_linea:main',
            'act4_pure_pursuit = lab_robotica.act4_pure_pursuit:main',
        ],
    },
)
