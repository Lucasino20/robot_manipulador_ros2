import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Nombre de tu paquete
    pkg_name = 'proy_pkg'
    pkg_share = get_package_share_directory(pkg_name)
    
    # Ruta donde está tu archivo URDF (ajusta el nombre si el archivo se llama diferente)
    urdf_file_name = 'robot_arm_urdf.urdf' # Cambia esto por el nombre real de tu URDF
    urdf_path = os.path.join(pkg_share, 'urdf', urdf_file_name)
    
    # Leemos el contenido del archivo URDF como texto plano
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()
        
    # 1. Nodo robot_state_publisher (Lee el URDF y publica las transformaciones /tf)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}],
    )

    # Ruta del archivo de configuración de RViz
    rviz_config_path = os.path.join(pkg_share, 'config', 'view_robot.rviz')

    # 2. Nodo RViz2 (Visualizador gráfico)
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
    )
    
    # 3. Nodo joint_state_publisher_gui (Agrega la ventana con los sliders)
    # Descomenta las siguientes líneas si prefieres usar los sliders gráficos en lugar de la terminal:
    # joint_state_publisher_gui_node = Node(
    #     package='joint_state_publisher_gui',
    #     executable='joint_state_publisher_gui',
    #     name='joint_state_publisher_gui',
    #     parameters=[{'robot_description': robot_desc}],
    # )
    
    # Retornamos la descripción del lanzamiento
    return LaunchDescription([
        robot_state_publisher_node, 
        # joint_state_publisher_gui_node,  # <-- Descomenta esta línea también si usas los sliders
        rviz_node
    ])