import math
import sys
import threading
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import serial # Importamos la libreria para comunicacion USB

rad = math.radians

def dh_matrix(theta, d, a, alpha):
    """Calcula la matriz de transformación homogénea de Denavit-Hartenberg"""
    ct = math.cos(theta)
    st = math.sin(theta)
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    return [
        [ct, -st*ca,  st*sa, a*ct],
        [st,  ct*ca, -ct*sa, a*st],
        [ 0,     sa,     ca,    d],
        [ 0,      0,      0,    1]
    ]

def multiply_matrices(A, B):
    """Multiplica dos matrices 4x4"""
    result = [[0.0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            for k in range(4):
                result[i][j] += A[i][k] * B[k][j]
    return result

class InteractiveAnglePublisher(Node):
    def __init__(self):
        super().__init__('interactive_angle_publisher')
        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)
        
        # Intentar conectar con el Arduino/ESP32 por USB
        self.serial_conn = None
        try:
            # En Linux/WSL2 suele ser /dev/ttyUSB0 o /dev/ttyACM0. En Windows seria 'COM3', etc.
            self.serial_conn = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.05)
            self.get_logger().info('✅ Conectado al Arduino por USB (/dev/ttyUSB0)')
        except Exception as e:
            self.get_logger().warn('⚠️ Arduino no detectado. Iniciando en modo SIMULACIÓN pura.')

        # Valores iniciales en radianes (0 grados)
        self.current_angles = [0.0, 0.0, 0.0, 0.0]
        
        # Publicamos de manera constante a 10 Hz para que RViz mantenga la posición
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        # Lanzamos un hilo separado para leer la terminal sin bloquear el bucle de ROS 2
        self.thread = threading.Thread(target=self.input_loop)
        self.thread.daemon = True
        self.thread.start()
        
        self.get_logger().info('Nodo interactivo listo.')

    def timer_callback(self):
        # --- LEER REALIMENTACIÓN DEL ARDUINO ---
        if self.serial_conn and self.serial_conn.is_open:
            try:
                if self.serial_conn.in_waiting > 0:
                    linea = self.serial_conn.readline().decode('utf-8').strip()
                    if linea.startswith('FBK,'):
                        partes = linea.split(',')
                        if len(partes) == 5:
                            # Actualizamos los angulos con la informacion real del sensor
                            self.current_angles = [
                                rad(float(partes[1])),
                                rad(float(partes[2])),
                                rad(float(partes[3])),
                                rad(float(partes[4]))
                            ]
            except Exception as e:
                pass

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4']
        msg.position = self.current_angles
        self.publisher_.publish(msg)

    def input_loop(self):
        print('\n==================================================')
        print(' Control interactivo de ángulos para el brazo robótico')
        print(' Inscribe los valores en grados separados por espacios.')
        print(' Ejemplo: 30 50 20 10')
        print('==================================================\n')
        
        while rclpy.ok():
            try:
                entrada = input('Ingresa joint_1 joint_2 joint_3 joint_4 (grados): ')
                
                if not entrada.strip():
                    continue
                    
                valores = [float(x) for x in entrada.split()]
                
                if len(valores) != 4:
                    print('Error: Debes ingresar exactamente 4 valores.')
                    continue
                
                # --- VALIDAR LIMITES DEL URDF ---
                # joint_1: 0 a 180 (0 a 3.142 rad)
                # joint_2: -90 a 90 (-1.57 a 1.57 rad)
                # joint_3: 0 a 180 (0 a 3.142 rad)
                # joint_4: -180 a 0 (-3.142 a 0 rad)
                if not (0 <= valores[0] <= 180):
                    print(f'❌ Error: joint_1 ({valores[0]}) está fuera de límite. Rango permitido: [0 a 180]')
                    continue
                if not (-90 <= valores[1] <= 90):
                    print(f'❌ Error: joint_2 ({valores[1]}) está fuera de límite. Rango permitido: [-90 a 90]')
                    continue
                if not (0 <= valores[2] <= 180):
                    print(f'❌ Error: joint_3 ({valores[2]}) está fuera de límite. Rango permitido: [0 a 180]')
                    continue
                if not (-180 <= valores[3] <= 0):
                    print(f'❌ Error: joint_4 ({valores[3]}) está fuera de límite. Rango permitido: [-180 a 0]')
                    continue
                    
                # Convertimos los grados ingresados a radianes (Modo Simulación)
                self.current_angles = [
                    rad(valores[0]),
                    rad(valores[1]),
                    rad(valores[2]),
                    rad(valores[3]),
                ]
                
                # --- ENVIAR COMANDO AL ARDUINO ---
                if self.serial_conn and self.serial_conn.is_open:
                    comando = f"CMD,{valores[0]},{valores[1]},{valores[2]},{valores[3]}\n"
                    self.serial_conn.write(comando.encode('utf-8'))
                    print(f'--> 📡 Enviado al Arduino: {comando.strip()}')
                else:
                    print(f'--> 💻 (Simulación) Actualizado a: {valores} grados')
                
                # --- CALCULO DE CINEMATICA DIRECTA (DENAVIT-HARTENBERG) ---
                q1, q2, q3, q4 = self.current_angles
                
                # Parametros extraidos del URDF (metros)
                L1 = 0.056
                L2 = 0.120
                L3 = 0.090
                L4 = 0.050 # Distancia final aproximada de la punta del efector
                
                # 1. Creamos las 4 matrices de transformacion
                T1 = dh_matrix(q1, L1, 0, math.pi/2)
                T2 = dh_matrix(q2, 0, L2, 0)
                T3 = dh_matrix(q3, 0, L3, 0)
                T4 = dh_matrix(q4, 0, L4, 0)
                
                # 2. Multiplicamos T1 * T2 * T3 * T4
                T02 = multiply_matrices(T1, T2)
                T03 = multiply_matrices(T02, T3)
                T04 = multiply_matrices(T03, T4)
                
                # 3. Extraemos la posicion final (X, Y, Z)
                x = T04[0][3]
                y = T04[1][3]
                z = T04[2][3]
                
                print(f'\n=== Cinemática Directa (DH) ===')
                print(f' Posición del efector final:')
                print(f' X: {x:.4f} m')
                print(f' Y: {y:.4f} m')
                print(f' Z: {z:.4f} m')
                print('===============================\n')
                
            except ValueError:
                print('Error: Por favor ingresa solo números válidos.')
            except EOFError:
                break

def main(args=None):
    rclpy.init(args=args)
    node = InteractiveAnglePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
