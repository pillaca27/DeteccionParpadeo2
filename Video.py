# Importamos librerias
from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import math
import time
# import pymysql
import pyodbc


# Establecer los valores de la conexión
server = '20.51.212.0'  # Dirección IP o nombre del servidor SQL Server
port = '62913'  # Número de puerto del servidor SQL Server
database = 'Spring_CanevaroSaneamiento'  # Nombre de la base de datos
username = 'caja'  # Nombre de usuario para autenticación
password = 'cajaCusco2021'  # Contraseña del usuario

# Construir la cadena de conexión
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"

# Establecer la conexión a la base de datos
conn = pyodbc.connect(connection_string)

# Crear un cursor
cursor = conn.cursor()

# Obtener los valores de la URL de conexión
# url = 'jdbc:mysql://localhost:3306/Deteccion_Parpadeos?serverTimezone=UTC'

# # Extraer los valores del host, usuario, contraseña y nombre de la base de datos
# host = url.split('//')[1].split(':')[0]
# user = 'root'  # Inserta el nombre de usuario correspondiente
# password = 'mysql'  # Inserta la contraseña correspondiente
# database = url.split('/')[-1].split('?')[0]

# # Establecer la conexión a la base de datos
# conn = pymysql.connect(
#     host=host,
#     user=user,
#     password=password,
#     database=database
# )

# Crear un cursor
# cursor = conn.cursor()

# Creamos nuestra funcion de dibujo
mpDibujo = mp.solutions.drawing_utils
confDibu = mpDibujo.DrawingSpec(thickness=1, circle_radius=1)

# Creamos un objeto donde almacenaremos la malla facial
mpMallaFacial = mp.solutions.face_mesh
MallaFacial = mpMallaFacial.FaceMesh(max_num_faces=1)

# Realizamos la Videocaptura
cap = cv2.VideoCapture(0)

# Creamos la app
app = Flask(__name__)

# Mostramos el video en RT
def gen_frame():

    # Variable
    parpadeo = False
    conteo = 0
    tiempo = 0
    inicio = 0
    final = 0
    conteo_sue = 0
    muestra = 0

    # Empezamos
    while True:
        # Leemos la VideoCaptura
        ret, frame = cap.read()

        # Listas
        px = []
        py = []
        lista = []

        # Si tenemos un error
        if not ret:
            break

        else:

            # Correcion del color
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Observamos los resultados
            resultados = MallaFacial.process(frameRGB)

            # Si tenemos rostros
            if resultados.multi_face_landmarks:
                # Iteramos
                for rostros in resultados.multi_face_landmarks:
                    # Dibujamos
                    mpDibujo.draw_landmarks(frame, rostros, mpMallaFacial.FACEMESH_TESSELATION, confDibu, confDibu)

                    for id, puntos in enumerate(rostros.landmark):
                        al, an, c = frame.shape
                        x, y = int(puntos.x * an), int(puntos.y * al)
                        px.append(x)
                        py.append(y)

                        lista.append([id, x, y])

                        if len(lista) == 468:
                            # Ojo derecho
                            x1, y1 = lista[145][1:]
                            x2, y2 = lista[159][1:]

                            longitud1 = math.hypot(x2 - x1, y2 - y1)

                            # Ojo izquierdo
                            x3, y3 = lista[374][1:]
                            x4, y4 = lista[386][1:]

                            longitud2 = math.hypot(x4 - x3, y4 - y3)
                            
                            cv2.putText(frame, f'Parpadeos: {int(conteo)}', (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                        (0, 255, 0), 2)
                            cv2.putText(frame, f'Micro Suenos: {int(conteo_sue)}', (380, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                        (0, 0, 240), 2)
                            cv2.putText(frame, f'Duracion: {int(muestra)}', (210, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                                        (0, 0, 255), 2)

                            
                            # If's
                            if longitud1 <= 10 and longitud2 <= 10 and parpadeo == False:
                                conteo = conteo + 1
                                parpadeo = True
                                inicio = time.time()

                                # Insertar el conteo en la base de datos
                                sql = "UPDATE DETECCION_PARPADEO SET CONTADOR = ? WHERE IDDETECCION = 1"
                                val = (conteo,)
                                cursor.execute(sql, val)

                                conn.commit()
                                # Insertar el conteo en la base de datos
                                #sql = "UPDATE PARPADEO SET conteo = %s WHERE idparpadeo = 1"
                                #val = (conteo,)
                                #cursor.execute(sql, val)

                                # Confirmar los cambios en la base de datos
                                #conn.commit()

                            elif longitud2 > 10 and longitud1 > 10 and parpadeo == True:
                                parpadeo = False
                                final = time.time()

                            tiempo = round(final - inicio, 0)

                            if tiempo >= 3:
                                conteo_sue = conteo_sue + 1
                                muestra = tiempo
                                inicio = 0
                                final = 0


            # Codificamos nuestro video en Bytes
            suc, encode = cv2.imencode('.jpg', frame)
            frame = encode.tobytes()

        yield(b'--frame\r\n'
              b'content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    # Cerrar el cursor y la conexión
    cursor.close()
    conn.close()
    #cursor.close()
    #conn.close()

# Ruta de aplicacion 'principal'
@app.route('/')
def index():
    return render_template('Index.html')

# Ruta del video
@app.route('/video')
def video():
    return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ejecutamos la app
if __name__ == "__main__":
    app.run(debug=True)
