# Proyecto de Robótica - Robot Manipulador Serial (ROS 2)

Este repositorio contiene el espacio de trabajo (workspace) de ROS 2 para la simulación y control de un brazo robótico serial de 4 Grados de Libertad (GDL). 

Cumple con los requisitos de la Primera Entrega:
- Modelo URDF y visualización 3D en **RViz**.
- Cálculo de **Cinemática Directa (DH)** integrada.
- Comunicación bidireccional por **Serial (USB)** para recibir datos de potenciómetros/encoders y enviar comandos al robot físico.

---

## 🛠️ Requisitos e Instalación

Para ejecutar la parte de la computadora necesitas **Ubuntu** con **ROS 2** (probado en Jazzy).

### 1. ¿No tienes ROS 2 Jazzy instalado? (Aplica para Ubuntu y WSL2)
Si tu compañero no tiene ROS 2, primero debe asegurarse de tener **Ubuntu 24.04** (ya sea nativo o descargado desde la Microsoft Store para WSL2). Luego, debe abrir su terminal y ejecutar estos comandos bloque por bloque para instalar ROS 2 Jazzy y Colcon:

<details>
<summary><b>Haz clic aquí para ver los comandos de instalación</b></summary>

```bash
# 1. Configurar idioma
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 2. Agregar repositorios de ROS 2
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 3. Instalar ROS 2 Desktop y herramientas de compilación
sudo apt update
sudo apt install ros-jazzy-desktop -y
sudo apt install python3-colcon-common-extensions -y
```
</details>

### 2. Configurar permisos USB (Fundamental)
- **Si usas Ubuntu nativo:** El único paso extra es dar permisos a tu usuario para leer el puerto USB. Abre una terminal y ejecuta:
  `sudo usermod -a -G dialout $USER` (Luego debes reiniciar tu computadora o cerrar sesión).
- **Si usas Windows (WSL2):** 
  1. Instala ROS 2 dentro de tu WSL2.
  2. Debes instalar [usbipd-win](https://github.com/dorssel/usbipd-win) en tu Windows. Esto te permitirá "enviar" la conexión del cable USB de Windows hacia el Linux de WSL2.
  3. Al igual que en Ubuntu, dentro de WSL2 debes ejecutar `sudo usermod -a -G dialout $USER` para tener permisos sobre el USB.

### 2. Compilar el proyecto en ROS 2
Abre una terminal en esta carpeta y ejecuta:
```bash
# Cargar ROS 2
source /opt/ros/jazzy/setup.bash

# Compilar
colcon build

# Cargar el entorno
source install/setup.bash
```

---

## 🚀 Cómo ejecutar el proyecto (Se necesitan 2 terminales)

**Terminal 1 (Visualización RViz):**
```bash
cd ~/Desktop/Robotica/robot_manipulador_ros2
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch proy_pkg robot.launch.py
```
*Se abrirá RViz mostrando el modelo 3D del robot.*

**Terminal 2 (Control Interactivo):**
Abre una nueva terminal en esta misma carpeta:
Abre una nueva terminal:
```bash
cd ~/Desktop/Robotica/robot_manipulador_ros2
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run proy_pkg interactive_publisher
```
*Aparecerá un menú pidiendo 4 ángulos. Escribe por ejemplo `30 50 20 10`. El código calculará la Cinemática Directa (DH), actualizará RViz y enviará la orden por USB al Arduino.*

---

## 💻 Código para el Arduino / ESP32

A la computadora y a ROS 2 **no les importa qué placa usen** (Arduino o ESP32), ya que la comunicación es universal por cable USB a 115200 baudios. El código de Python de nuestra carpeta de ROS 2 no necesita ningún cambio.

**⚠️ IMPORTANTE: Este código de abajo NO se ejecuta en ROS 2 ni en Linux.**
Tu compañero debe hacer lo siguiente en su computadora (en Windows normal o Ubuntu, donde prefiera):
1. Abrir el **Arduino IDE**.
2. Ir a *Herramientas -> Administrar Bibliotecas...* y buscar/instalar la librería **`ESP32Servo`**.
3. Pegar este código, adaptarlo a sus motores y subirlo a la placa ESP32.

```cpp
#include <ESP32Servo.h>

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;

void setup() {
  // Es crítico usar 115200 baudios para que ROS 2 lo entienda
  Serial.begin(115200);
  
  // ---> INICIA TUS SERVOS AQUÍ <---
  // Asignar los pines correctos de tu ESP32 para cada motor
  servo1.attach(13); 
  servo2.attach(12);
  servo3.attach(14);
  servo4.attach(27);
}

void loop() {
  // 1. LEER LOS ÁNGULOS DESEADOS QUE ENVÍA ROS 2 (Computadora)
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    
    // Si el texto empieza con "CMD," son los comandos de ROS 2
    if (data.startsWith("CMD,")) {
      float q1, q2, q3, q4;
      // Extraemos los 4 números
      sscanf(data.c_str(), "CMD,%f,%f,%f,%f", &q1, &q2, &q3, &q4);
      
      // ---> MUEVE TUS MOTORES A LOS ÁNGULOS q1, q2, q3, q4 AQUÍ <---
      // Ejemplo: servo1.write(q1); 
      // (Ojo: mapear los ángulos si tu servo solo va de 0 a 180)
    }
  }

  // 2. ENVIAR REALIMENTACIÓN A ROS 2 (Para mover el modelo 3D en RViz)
  // ---> LEE TUS SENSORES O POSICIONES ACTUALES AQUÍ <---
  float real_q1 = 0.0; // Reemplazar con analogRead() o valor real
  float real_q1 = 0.0; // Reemplazar con analogRead() si tienen potenciómetros reales
  float real_q2 = 0.0; 
  float real_q3 = 0.0; 
  float real_q4 = 0.0; 

  // Enviar los valores de vuelta a la computadora
  Serial.print("FBK,");
  Serial.print(real_q1); Serial.print(",");
  Serial.print(real_q2); Serial.print(",");
  Serial.print(real_q3); Serial.print(",");
  Serial.println(real_q4);
  
  // Una pausa pequeña para no saturar la conexión (~20 Hz)
  delay(50); 
}
```
