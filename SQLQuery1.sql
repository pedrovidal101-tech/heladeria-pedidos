CREATE DATABASE HeladeriaDB;
GO

USE HeladeriaDB;
GO

-- Tabla Mesas
CREATE TABLE Mesas (
    id_mesa INT PRIMARY KEY IDENTITY(1,1),
    numero INT NOT NULL UNIQUE,
    estado VARCHAR(20) DEFAULT 'libre'
);

-- Tabla Productos
CREATE TABLE Productos (
    id_producto INT PRIMARY KEY IDENTITY(1,1),
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL
);

-- Tabla Pedidos
CREATE TABLE Pedidos (
    id_pedido INT PRIMARY KEY IDENTITY(1,1),
    id_mesa INT FOREIGN KEY REFERENCES Mesas(id_mesa),
    estado VARCHAR(20) DEFAULT 'pendiente',
    fecha_hora DATETIME DEFAULT GETDATE()
);

-- Insertar datos iniciales de prueba
INSERT INTO Mesas (numero) VALUES (1), (2), (3);
INSERT INTO Productos (nombre, precio) VALUES ('Helado Chocolate', 5000), ('Malteada Fresa', 8000);