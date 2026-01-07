from flask import Flask, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv
from models import db, Usuario, Noticia, Partido, Producto

load_dotenv(override=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'intel2711')
db_url = os.getenv('DATABASE_URL', 'sqlite:///online_sports.db')
print(f"DEBUG: Connecting to {db_url.split('@')[-1] if '@' in db_url else db_url}") # Debug print
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app) # Habilitar CORS para que el frontend pueda comunicarse

db.init_app(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/api/status')
def status():
    return jsonify({"status": "ok", "message": "Backend is running"})

@app.route('/api/noticias')
def get_noticias():
    deporte = request.args.get('deporte')
    query = Noticia.query
    if deporte:
        query = query.filter_by(deporte=deporte)
    noticias = query.order_by(Noticia.fecha_publicacion.desc()).all()
    return jsonify([n.to_dict() for n in noticias])

@app.route('/api/noticia/<int:noticia_id>')
def get_noticia(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)
    return jsonify(noticia.to_dict())

@app.route('/api/partidos')
def get_partidos():
    deporte = request.args.get('deporte')
    query = Partido.query
    if deporte:
        query = query.filter_by(deporte=deporte)
    partidos = query.order_by(Partido.fecha_hora).all()
    return jsonify([p.to_dict() for p in partidos])

@app.route('/api/partido/<int:partido_id>')
def get_partido(partido_id):
    partido = Partido.query.get_or_404(partido_id)
    return jsonify(partido.to_dict())

@app.route('/api/productos')
def get_productos():
    categoria = request.args.get('categoria')
    query = Producto.query
    if categoria:
        query = query.filter_by(categoria=categoria)
    productos = query.all()
    return jsonify([p.to_dict() for p in productos])

@app.route('/api/buscar')
def buscar():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"noticias": [], "partidos": [], "productos": []})
    
    noticias = Noticia.query.filter(db.or_(Noticia.titulo.ilike(f'%{q}%'), Noticia.contenido.ilike(f'%{q}%'))).all()
    partidos = Partido.query.filter(db.or_(Partido.equipo_local.ilike(f'%{q}%'), Partido.equipo_visitante.ilike(f'%{q}%'))).all()
    productos = Producto.query.filter(db.or_(Producto.nombre.ilike(f'%{q}%'), Producto.descripcion.ilike(f'%{q}%'))).all()
    
    return jsonify({
        "noticias": [n.to_dict() for n in noticias],
        "partidos": [p.to_dict() for p in partidos],
        "productos": [p.to_dict() for p in productos]
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username:
        username = username.strip()

    print(f"DEBUG LOGIN ATTEMPT: username='{username}', password='{password}'") # Debug print

    user = Usuario.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return jsonify({"success": True, "user": user.to_dict()})
    
    print(f"DEBUG LOGIN FAILED: User found: {user is not None}")
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"success": True})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if username:
        username = username.strip()
    if email:
        email = email.strip()

    if Usuario.query.filter_by(username=username).first():
        return jsonify({"success": False, "message": "Username already exists"}), 400
    
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already exists"}), 400

    new_user = Usuario(username=username, email=email)
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True, "message": "User registered successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/noticias', methods=['POST'])
def add_noticia():
    data = request.json
    try:
        nueva_noticia = Noticia(
            titulo=data['titulo'],
            contenido=data['contenido'],
            deporte=data['deporte'],
            autor=data['autor'],
            destacada=data.get('destacada', False)
        )
        db.session.add(nueva_noticia)
        db.session.commit()
        return jsonify({"success": True, "message": "Noticia agregada"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/partidos', methods=['POST'])
def add_partido():
    data = request.json
    try:
        if 'fecha_hora' in data:
            data['fecha_hora'] = datetime.strptime(data['fecha_hora'], '%Y-%m-%d %H:%M')
            
        nuevo_partido = Partido(
            equipo_local=data['equipo_local'],
            equipo_visitante=data['equipo_visitante'],
            deporte=data['deporte'],
            liga=data['liga'],
            fecha_hora=data['fecha_hora'],
            estado=data['estado'],
            resultado_local=data.get('resultado_local'),
            resultado_visitante=data.get('resultado_visitante')
        )
        db.session.add(nuevo_partido)
        db.session.commit()
        return jsonify({"success": True, "message": "Partido agregado"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/noticia/<int:noticia_id>', methods=['PUT'])
def update_noticia(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)
    data = request.json
    try:
        noticia.titulo = data.get('titulo', noticia.titulo)
        noticia.contenido = data.get('contenido', noticia.contenido)
        noticia.deporte = data.get('deporte', noticia.deporte)
        noticia.autor = data.get('autor', noticia.autor)
        if 'destacada' in data:
            noticia.destacada = data['destacada']
        
        db.session.commit()
        return jsonify({"success": True, "message": "Noticia actualizada"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/noticia/<int:noticia_id>', methods=['DELETE'])
def delete_noticia(noticia_id):
    noticia = Noticia.query.get_or_404(noticia_id)
    try:
        db.session.delete(noticia)
        db.session.commit()
        return jsonify({"success": True, "message": "Noticia eliminada"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/partido/<int:partido_id>', methods=['PUT'])
def update_partido(partido_id):
    partido = Partido.query.get_or_404(partido_id)
    data = request.json
    try:
        partido.equipo_local = data.get('equipo_local', partido.equipo_local)
        partido.equipo_visitante = data.get('equipo_visitante', partido.equipo_visitante)
        partido.deporte = data.get('deporte', partido.deporte)
        partido.liga = data.get('liga', partido.liga)
        partido.estado = data.get('estado', partido.estado)
        partido.resultado_local = data.get('resultado_local', partido.resultado_local)
        partido.resultado_visitante = data.get('resultado_visitante', partido.resultado_visitante)
        
        if 'fecha_hora' in data:
             partido.fecha_hora = datetime.strptime(data['fecha_hora'], '%Y-%m-%d %H:%M')

        db.session.commit()
        return jsonify({"success": True, "message": "Partido actualizado"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/partido/<int:partido_id>', methods=['DELETE'])
def delete_partido(partido_id):
    partido = Partido.query.get_or_404(partido_id)
    try:
        db.session.delete(partido)
        db.session.commit()
        return jsonify({"success": True, "message": "Partido eliminado"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/seed-db', methods=['POST'])
def seed_db():
    try:
        # Datos de FÚTBOL
        noticias_futbol = [
            Noticia(titulo="Messi gana su octavo Balón de Oro", contenido="Lionel Messi hace historia...", deporte="futbol", autor="Carlos Ruiz", destacada=True),
            Noticia(titulo="El Real Madrid ficha a joven promesa", contenido="El Real Madrid ha anunciado...", deporte="futbol", autor="María González"),
            Noticia(titulo="La Premier League bate récord", contenido="La Premier League inglesa...", deporte="futbol", autor="David Smith")
        ]
        
        db.session.add_all(noticias_futbol)
        db.session.commit()
        return jsonify({"success": True, "message": "Datos de prueba agregados"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
