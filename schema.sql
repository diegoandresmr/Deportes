-- Create Usuario table
CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    equipo_favorito VARCHAR(100)
);

-- Create Noticia table
CREATE TABLE IF NOT EXISTS noticia (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    contenido TEXT NOT NULL,
    deporte VARCHAR(50) NOT NULL,
    imagen_url VARCHAR(300),
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    autor VARCHAR(100),
    destacada BOOLEAN DEFAULT FALSE
);

-- Create Partido table
CREATE TABLE IF NOT EXISTS partido (
    id SERIAL PRIMARY KEY,
    equipo_local VARCHAR(100) NOT NULL,
    equipo_visitante VARCHAR(100) NOT NULL,
    deporte VARCHAR(50) NOT NULL,
    liga VARCHAR(100),
    fecha_hora TIMESTAMP NOT NULL,
    resultado_local INTEGER,
    resultado_visitante INTEGER,
    estado VARCHAR(20),
    estadio VARCHAR(200)
);

-- Create Producto table
CREATE TABLE IF NOT EXISTS producto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    precio FLOAT NOT NULL,
    categoria VARCHAR(100),
    imagen_url VARCHAR(300),
    stock INTEGER DEFAULT 0
);
