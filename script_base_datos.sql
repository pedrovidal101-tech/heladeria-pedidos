-- Script de creación de la base de datos y tablas
CREATE DATABASE HeladeriaDB;
GO

USE HeladeriaDB;
GO

-- Tabla de Mesas
CREATE TABLE Mesas (
    id_mesa INT PRIMARY KEY IDENTITY(1,1),
    numero INT NOT NULL,
    estado VARCHAR(20) DEFAULT 'libre'
);

-- Tabla de Pedidos
CREATE TABLE Pedidos (
    id_pedido INT PRIMARY KEY IDENTITY(1,1),
    id_mesa INT NOT NULL,
    fecha_hora DATETIME DEFAULT GETDATE(),
    estado VARCHAR(20) DEFAULT 'pendiente',
    FOREIGN KEY (id_mesa) REFERENCES Mesas(id_mesa)
);

-- Registros de prueba iniciales
INSERT INTO Mesas (numero, estado) VALUES (1, 'ocupada'), (2, 'ocupada'), (3, 'libre');
INSERT INTO Pedidos (id_mesa, estado) VALUES (1, 'pendiente'), (2, 'pendiente');
GO