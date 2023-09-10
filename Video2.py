# Importamos librerias
from flask import Flask, render_template, Response, request, redirect, url_for, session, has_request_context
import cv2
import mediapipe as mp
import math
import time
import os
import pyodbc
import datetime

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

clave_secreta = '9f5b6e14e8d89c993e568d3b520c4f0122f56fd4c688956c'

app.config['SECRET_KEY'] = clave_secreta
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True


# def enviar_mensaje():
#     # Almacenar el mensaje en una variable de sesión
#     mensaje = "Se ha detectado un microsueño"
#     session['mensaje_microsueno'] = mensaje

#     # Redirigir a la página principal
#     return redirect(url_for('index'))

# def enviar_mensaje_microsueno():
#     # Verificar si el usuario no es "Docente"
#     username = session.get('username')
#     if username != "Docente":
#         # Ejecutar la función para enviar el mensaje
#         enviar_mensaje()

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

     # Insertar el conteo en la base de datos
    # sql = "UPDATE DETECCION_PARPADEO SET CONTADOR = ? WHERE IDDETECCION = 1"
    # val = (conteo_sue,)
    # cursor.execute(sql, val)

    # conn.commit()

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

                                # Insertar el conteo en la base de datos
                                # sql = "UPDATE DETECCION_PARPADEO SET CONTADOR = ? WHERE IDDETECCION = 1"
                                # val = (conteo_sue,)
                                # cursor.execute(sql, val)

                                # conn.commit()
                                with conn.cursor() as cursor:
                                    ClaseAlumnoID = 1  # Cambia este valor según tus necesidades

                                    # Verificar si ya existe un registro con el mismo ClaseAlumnoID
                                    cursor.execute(f"SELECT MAX(DeteccionID) FROM PyEye_Deteccion_Parpadeo WHERE ClaseAlumnoID = {ClaseAlumnoID}")
                                    row = cursor.fetchone()
                                    if row[0] is not None:
                                        DeteccionID = row[0] + 1
                                    else:
                                        DeteccionID = 1

                                    # Insertar el nuevo registro en la tabla
                                    hora_registro = datetime.datetime.now()
                                    cursor.execute("INSERT INTO PyEye_Deteccion_Parpadeo (DeteccionID, ClaseAlumnoID, HoraRegistro) VALUES (?, ?, ?)",
                                                DeteccionID, ClaseAlumnoID, hora_registro)
                                    conn.commit()

                                # Cerrar la conexión
                                
                                # enviar_mensaje_microsueno()


            # Codificamos nuestro video en Bytes
            suc, encode = cv2.imencode('.jpg', frame)
            frame = encode.tobytes()

        yield(b'--frame\r\n'
              b'content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    # Cerrar el cursor y la conexión
    cursor.close()
    conn.close()

# Ruta para iniciar sesión
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar las credenciales en la base de datos
        with conn.cursor() as cursor:
            sql = "SELECT * FROM PyEye_Usuario WHERE USUARIO = ? AND CLAVE = ?"
            val = (username, password)
            cursor.execute(sql, val)
            result = cursor.fetchone()
            
            if result:
                if username == "DPPD":
                    encender_camara = False
                else:
                    encender_camara = True

                # Guardar el nombre del usuario en la sesión
                session['username'] = username 

                # Credenciales válidas, redireccionar a la página principal
                return redirect(url_for('index', encender_camara=encender_camara))
            else:
                # Credenciales inválidas, mostrar un mensaje de error
                error_message = "Credenciales inválidas. Inténtalo de nuevo."
                return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html')

# Ruta de la página principal
@app.route('/index')
def index():
    encender_camara = request.args.get('encender_camara', default='True', type=str) == 'True'
    
    username = session.get('username')

    return render_template('Index.html', encender_camara=encender_camara, username=username)

# Ruta del video
@app.route('/video')
def video():
    return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ruta para registrar clase
@app.route('/registrar_clase', methods=['POST'])
def registrar_clase():
    if session.get('username') == 'DPPD':

         # Aquí puedes obtener el nombre de la clase desde el formulario
        nombre_clase = request.form.get('nombre_clase')

        with conn.cursor() as cursor:
            # Obtener el valor máximo actual de ClaseID en la tabla
            cursor.execute("SELECT MAX(ClaseID) FROM PyEye_Clase WHERE DocenteID = 1")
            row = cursor.fetchone()
            if row[0] is not None:
                clase_id = row[0] + 1
            else:
                clase_id = 1

            # Insertar el nuevo registro en la tabla con DocenteID por defecto de 1 y ClaseID calculado
            sql = "INSERT INTO PyEye_Clase (ClaseID, DocenteID, NombreClase) VALUES(?, 1, ?)"
            cursor.execute(sql, clase_id, nombre_clase)
            conn.commit()
            conn.close()

        # Continúa mostrando la página principal
        encender_camara = False
        username = session.get('username')
        return render_template('Index.html', encender_camara=encender_camara, username=username)


# Ejecutamos la app
if __name__ == "__main__":
    app.run(debug=True)
