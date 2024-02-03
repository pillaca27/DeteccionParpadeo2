CREATE TABLE USUARIO_PARPADEO (
    ID INT IDENTITY(1,1),
    NOMBRE VARCHAR(50),
	CLAVE VARCHAR(100),
    PRIMARY KEY (ID)
);
--
-- Crear tabla DETECCI�N_PARPADEO
CREATE TABLE DETECCION_PARPADEO (
    IDDETECCION INT IDENTITY(1,1) PRIMARY KEY,
    ID_USUARIO INT,
    CONTADOR INT,
    FOREIGN KEY (ID_USUARIO) REFERENCES USUARIO_PARPADEO(ID)
);
--
INSERT INTO USUARIO_PARPADEO (NOMBRE)
VALUES ('Crystal');
--
INSERT INTO USUARIO_PARPADEO (NOMBRE)
VALUES ('Docente');
--
select*from DETECCION_PARPADEO
--
SELECT*FROM USUARIO_PARPADEO
--
INSERT INTO DETECCION_PARPADEO (ID_USUARIO, CONTADOR)
VALUES (1, 0);
---
SELECT*FROM DETECCION_PARPADEO 
--
UPDATE USUARIO_PARPADEO SET CLAVE = '123'
--
UPDATE DETECCION_PARPADEO SET CONTADOR ='0'
--
1	Crystal	123
2	Docente	123
--
1	1	34
--
/*
Usuario
 - Docente -- Clave
 - Alumno -- Clave -- Cambio de Contrase�a

Persona
 - datos similares

Docente
 - Curso relacionado dentro ello se tendr� el c�digo de usuario
 
Alumno
 - informaci�n del DNI
 - Adem�s de datos adicionales necesarios tendr� el c�digo de usuario

Clase
 - Docente encargado
 - Nombre de la clase

Clase_Alumno
 - Clase
 - Alumno
 - as� se que alumno pertenece a cada clase para tener acceso

Deteccion_Parpadeo
 - Se ver� los microsue�os por usuario que viene hacer del alumno
 - hora en la cu�l se registr� y clase -- donde se obtiene del logeo.
*/
--
CREATE TABLE PyEye_Usuario (
    UsuarioID INT PRIMARY KEY IDENTITY(1,1),
    Usuario VARCHAR(6),
    Clave VARCHAR(100)
);
-- Tabla para almacenar informaci�n general de las personas (Docentes y Alumnos)
CREATE TABLE PyEye_Persona (
    PersonaID INT PRIMARY KEY,
    Nombre VARCHAR(50),
    Apellido VARCHAR(50),
    DNI VARCHAR(10) UNIQUE
);

-- Tabla para almacenar informaci�n espec�fica de los Docentes
CREATE TABLE PyEye_Docente (
    DocenteID INT PRIMARY KEY,
    CursoRelacionado VARCHAR(100),
    Usuario VARCHAR(6) UNIQUE,
    FOREIGN KEY (DocenteID) REFERENCES PyEye_Persona(PersonaID)
);

-- Tabla para almacenar informaci�n espec�fica de los Alumnos
CREATE TABLE PyEye_Alumno (
    AlumnoID INT PRIMARY KEY,
    Usuario VARCHAR(6) UNIQUE,
    FOREIGN KEY (AlumnoID) REFERENCES PyEye_Persona(PersonaID)
);

-- Tabla para almacenar informaci�n de las Clases
CREATE TABLE PyEye_Clase (
    ClaseID INT PRIMARY KEY,
    DocenteID INT,
    NombreClase VARCHAR(100),
    FOREIGN KEY (DocenteID) REFERENCES PyEye_Docente(DocenteID)
);

-- Tabla para relacionar Clases y Alumnos
CREATE TABLE PyEye_Clase_Alumno (
    ClaseAlumnoID INT PRIMARY KEY,
    ClaseID INT,
    AlumnoID INT,
    FOREIGN KEY (ClaseID) REFERENCES PyEye_Clase(ClaseID),
    FOREIGN KEY (AlumnoID) REFERENCES PyEye_Alumno(AlumnoID)
);

-- Tabla para registrar la detecci�n de parpadeo
CREATE TABLE PyEye_Deteccion_Parpadeo (
    DeteccionID INT PRIMARY KEY,
    ClaseAlumnoID INT,
    HoraRegistro DATETIME
    FOREIGN KEY (ClaseAlumnoID) REFERENCES PyEye_Clase_Alumno(ClaseAlumnoID)
);
--
DROP TABLE PyEye_Usuario
DROP TABLE PyEye_Persona
DROP TABLE PyEye_Docente
DROP TABLE PyEye_Alumno
DROP TABLE PyEye_Clase
DROP TABLE PyEye_Clase_Alumno
DROP TABLE PyEye_Deteccion_Parpadeo

--
SELECT*FROM PyEye_Alumno
--
INSERT into PyEye_Usuario (Usuario, Clave) VALUES ('CPPC', '123')
INSERT into PyEye_Usuario (Usuario, Clave) VALUES ('DPPD', '123')
--
INSERT INTO PyEye_Persona (PersonaID, Nombre, Apellido, DNI) VALUES(1, 'DOCENTE', 'DOCENTE', '76545678');
INSERT INTO PyEye_Persona (PersonaID, Nombre, Apellido, DNI) VALUES(2, 'CRYSTAL', 'PILLACA', '76545679');
--
INSERT INTO PyEye_Docente (DocenteID, CursoRelacionado, Usuario) VALUES(1, 'INGLÉS', 'CPPC');
--
INSERT INTO PyEye_Alumno (AlumnoID, Usuario) VALUES(2, 'DPPD');
--
INSERT INTO PyEye_Clase (ClaseID, DocenteID, NombreClase) VALUES(1, 1, 'INGLÉS');
--
INSERT INTO PyEye_Clase_Alumno (ClaseAlumnoID, ClaseID, AlumnoID) VALUES(1, 1, 2);
--
INSERT INTO PyEye_Deteccion_Parpadeo (DeteccionID, ClaseAlumnoID, HoraRegistro) VALUES(1, 1, null);
--
INSERT INTO PyEye_Deteccion_Parpadeo (DeteccionID, ClaseAlumnoID, HoraRegistro) VALUES(0, 0, '');
--
DELETE FROM PyEye_Deteccion_Parpadeo
--

INSERT INTO PyEye_Deteccion_Parpadeo (DeteccionID, ClaseAlumnoID, HoraRegistro) VALUES(1, 1, GETDATE());
--
DECLARE @ClaseAlumnoID INT;
DECLARE @DeteccionID INT;

SET @ClaseAlumnoID = 1; -- Cambia este valor según tu necesidad

-- Verificar si ya existe un registro con el mismo ClaseAlumnoID
IF EXISTS (SELECT @DeteccionID = MAX(DeteccionID) FROM PyEye_Deteccion_Parpadeo WHERE ClaseAlumnoID = @ClaseAlumnoID) 
    SET @DeteccionID = @DeteccionID + 1;
ELSE
    SET @DeteccionID = 1;

-- Insertar el nuevo registro con los valores calculados
INSERT INTO PyEye_Deteccion_Parpadeo (DeteccionID, ClaseAlumnoID, HoraRegistro) VALUES (@DeteccionID, @ClaseAlumnoID, GETDATE());
--
DELETE FROM PyEye_Clase
--
DELETE FROM PyEye_Clase_Alumno 
--
DELETE FROM PyEye_Deteccion_Parpadeo
--
SELECT*FROM PyEye_Deteccion_Parpadeo
--


































