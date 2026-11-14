-- Script de creación de la base de datos HeladeriaDB
IF DB_ID('HeladeriaDB') IS NULL
    CREATE DATABASE HeladeriaDB;
GO

USE HeladeriaDB;
GO

CREATE TABLE Mesas (
    id_mesa INT PRIMARY KEY IDENTITY(1,1),
    numero INT NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'libre'
);

CREATE TABLE Productos (
    id_producto INT PRIMARY KEY IDENTITY(1,1),
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL DEFAULT 'General',
    precio DECIMAL(10,2) NOT NULL,
    disponible BIT NOT NULL DEFAULT 1
);

CREATE TABLE Pedidos (
    id_pedido INT PRIMARY KEY IDENTITY(1,1),
    id_mesa INT NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT GETDATE(),
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    FOREIGN KEY (id_mesa) REFERENCES Mesas(id_mesa)
);

CREATE TABLE DetallePedido (
    id_detalle INT PRIMARY KEY IDENTITY(1,1),
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
);
GO

-- Datos iniciales
INSERT INTO Mesas (numero, estado) VALUES (1, 'libre'), (2, 'libre'), (3, 'libre');

INSERT INTO Productos (nombre, categoria, precio, disponible) VALUES
    ('Brownie con Helado', 'Postres', 12000, 1),
    ('Helado Chocolate', 'Helados', 5000, 1),
    ('Helado de Vainilla', 'Helados', 4500, 1),
    ('Malteada Fresa', 'Bebidas', 8000, 1);
GO