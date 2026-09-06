# Proyecto de Robótica - Robot Manipulador Serial (ROS 2)

Este repositorio contiene el espacio de trabajo (workspace) de ROS 2 para la simulación y control de un brazo robótico serial de 4 Grados de Libertad (GDL). 

Cumple con los requisitos de la Primera Entrega:
- Modelo URDF y visualización 3D en **RViz**.
- Cálculo de **Cinemática Directa (DH)** integrada.
- Comunicación bidireccional por **Serial (USB)** para recibir datos de potenciómetros/encoders y enviar comandos al robot físico.

---

## 🛠️ Requisitos e Instalación

Para ejecutar este proyecto necesitas tener **Ubuntu** con **ROS 2** instalado (probado en Jazzy).

### Si usas Windows (WSL2):
1. Debes instalar ROS 2 dentro de tu distribución de WSL2.
2. **Para que WSL2 detecte el Arduino por USB:** Necesitas instalar [usbipd-win](https://github.com/dorssel/usbipd-win) en Windows. Esto te permitirá "pasar" el puerto COM de Windows a `/dev/ttyUSB0` en Ubuntu.

### Compilar el proyecto
Abre una terminal en esta carpeta y ejecuta:
```bash
# Limpiar instalaciones previas por si acaso
rm -rf build/ install/ log/

# Compilar
colcon build

# Cargar el entorno
source install/setup.bash
```

---

## 🚀 Cómo ejecutar el proyecto (Se necesitan 2 terminales)

**Terminal 1 (Visualización RViz):**
```bash
source install/setup.bash
ros2 launch proy_pkg robot.launch.py
```
*Se abrirá RViz mostrando el modelo 3D del robot.*

**Terminal 2 (Control Interactivo):**
Abre una nueva terminal en esta misma carpeta:
```bash
source install/setup.bash
ros2 run proy_pkg interactive_publisher
```
*Aparecerá un menú pidiendo 4 ángulos. Escribe por ejemplo `30 50 20 10`. El código calculará la Cinemática Directa (DH), actualizará RViz y enviará la orden por USB al Arduino.*

---

## 💻 Código para el Arduino / ESP32 (Para el compañero)

Este paquete de ROS 2 espera comunicarse con el robot físico a través de un "idioma" (protocolo) muy simple por USB. 

El compañero encargado del hardware debe tomar el siguiente código, integrarlo con su lógica de control de motores, y subirlo a la placa (Arduino/ESP32):

```cpp
void setup() {
  // Es crítico usar 115200 baudios para que ROS 2 lo entienda
  Serial.begin(115200);
  
  // ---> INICIA TUS SERVOS AQUÍ <---
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
    }
  }

  // 2. ENVIAR REALIMENTACIÓN A ROS 2 (Para mover el modelo 3D en RViz)
  // ---> LEE TUS SENSORES O POSICIONES ACTUALES AQUÍ <---
  float real_q1 = 0.0; // Reemplazar con analogRead() o valor real
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
