import cv2
import mediapipe as mp
import math
import time

# Realizamos la VideoCaptura
cap = cv2.VideoCapture(0)
cap.set(3, 1280) #Definimos el ancho de la ventana
cap.set(4, 720) #Definimos el alto de la ventana

# Variable de conteo
parpadeo = False
conteo = 0
tiempo = 0
inicio = 0
final = 0
conteo_sue = 0
muestra = 0

# Creamos nuestra funcion de dibujo
mpDibujo = mp.solutions.drawing_utils
confDibu = mpDibujo.DrawingSpec(thickness=1, circle_radius=1) #Ajustamos la configuracion de dibujo

# Creamos un objeto donde almacenaremos la malla facial
mpMallaFacial = mp.solutions.face_mesh #Primero llamamos la funcion
mpMallaFacial = mpMallaFacial.FaceMesh(max_num_faces=1) #Creamos el objeto (ctrl + click)


# Creamos el while principal
while True:

    ret, frame = cap.read()
    # Correcion del color
    frameRGB = cv2.cvtColor(frame, cv2, COLOR_BGR2RGB)

    # Observamos los resultados
    resultados = MallaFacial.process(frameRGB)

    # Creamos unas listas donde almacenaremos los resultados
    px = []
    py = []
    lista = []
    r = 5
    t = 3

    if resultados.multi_face_landmarks: #Si detectamos algun rostro
        for rostros in resultados.multi_face_landmarks: #Mostramos el rostro detectado
            mpDibujo.draw_landmarks(frame, rostros, mpMallaFacial.FACE_CONNECTIONS, confDibu, confDibu)

            # Ahora vamos a extraer los puntos del rostro detectado
            for id, puntos in enumerate(rostros, landmark):
                #print(puntos) #Nos entrega una proporcion
                al, an, c = frame.shape
                x, y = int (puntos.x*an), int(puntos.y*al)
                px.append(x)
                py.append(y)
                lista.append([id, x, y])
                if len(lista) == 468:
                    #Ojo derecho
                    x1, y1 = lista[145][1:]
                    x2, y2 = lista[159][1:]
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    # sale una una cosita negra en el ojo
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 0), t)
                    cv2.circle(frame, (x1, y1), r, (0, 0, 0), cv2.FILED)
                    cv2.circle(frame, (x2, y2), r, (0, 0, 0), cv2.FILED)
                    cv2.circle(frame, (cx, cy), r, (0, 0, 0), cv2.FILED)
                    longitud1 = math.hypo(x2 - x1, y2- y1)
                    #print(longitud)

                    # Ojo Izquierdo
                    x3, y3 = lista[374][1:]
                    x4, y4 = lista[386][1:]
                    cx2, cy2 = (x3 + x4) // 2, (y3 + y4) // 2
                    longitud2 = math.hypo(x4 - x3, y4- y3)
                    #print(longitud2)

                    # Conteo de parpadeos
                    cv2.putText(frame, f'parpadeos; {int(conteo)}', (300, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    cv2.putText(frame, f'Micro Suenos: {int(conteo_sue)}', (780, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.putText(frame, f'Duracion: {str(muestra)}', (550, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                    
                    if longitud1 <= 10 and longitud2 <= 10 and parpadeo == False: #Parpadeo
                        conteo = conteo + 1
                        parpadeo = True
                        inicio = time.time()

                    elif longitud2 > 10 and longitud2 > 10 and parpadeo == True: #Seguridad parpadeo
                        parpadeo = False
                        final = time.time()

                    # Temporizador
                    tiempo = round(final - inicio, 0)

                    # Contador de Micro suenos
                    if tiempo >= 3:
                        conteo_sue = conteo_sue + 1
                        muestra = tiempo
                        inicio = 0
                        final = 0