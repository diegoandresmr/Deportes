from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) # Increased length for hash
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    equipo_favorito = db.Column(db.String(100))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'equipo_favorito': self.equipo_favorito
        }

class Noticia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    deporte = db.Column(db.String(50), nullable=False)
    imagen_url = db.Column(db.String(300))
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)
    autor = db.Column(db.String(100))
    destacada = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'contenido': self.contenido,
            'deporte': self.deporte,
            'imagen_url': self.imagen_url,
            'fecha_publicacion': self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            'autor': self.autor,
            'destacada': self.destacada
        }

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipo_local = db.Column(db.String(100), nullable=False)
    equipo_visitante = db.Column(db.String(100), nullable=False)
    deporte = db.Column(db.String(50), nullable=False)
    liga = db.Column(db.String(100))
    fecha_hora = db.Column(db.DateTime, nullable=False)
    resultado_local = db.Column(db.Integer)
    resultado_visitante = db.Column(db.Integer)
    estado = db.Column(db.String(20))
    estadio = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'equipo_local': self.equipo_local,
            'equipo_visitante': self.equipo_visitante,
            'deporte': self.deporte,
            'liga': self.liga,
            'fecha_hora': self.fecha_hora.isoformat() if self.fecha_hora else None,
            'resultado_local': self.resultado_local,
            'resultado_visitante': self.resultado_visitante,
            'estado': self.estado,
            'estadio': self.estadio
        }

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(100))
    imagen_url = db.Column(db.String(300))
    stock = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'categoria': self.categoria,
            'imagen_url': self.imagen_url,
            'stock': self.stock
        }
