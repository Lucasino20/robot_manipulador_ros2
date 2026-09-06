import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'proy_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Registra el paquete en el índice de ROS 2
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Instala los archivos de launch
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # Instala el archivo URDF
        (os.path.join('share', package_name, 'urdf'), glob('proy_pkg/urdf/*.urdf')),
        # Instala las mallas 3D (.STL y .stl por si acaso)
        (os.path.join('share', package_name, 'meshes'), glob('proy_pkg/meshes/*.[sS][tT][lL]')),
        # Instala la configuracion de RViz
        (os.path.join('share', package_name, 'config'), glob('config/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='usuario',
    maintainer_email='usuario@todo.todo',
    description='Paquete de simulacion y control de brazo robotico',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Registra el ejecutable del publicador interactivo
            'interactive_publisher = proy_pkg.rob_publisher:main',
        ],
    },
)