from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'intel2711') # Needed for sessions

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000/api')

@app.template_filter('format_datetime')
def format_datetime(value, format='%d/%m/%Y %H:%M'):
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            # Handle ISO format from backend
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format)

# Login Manager for Frontend Session
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Class for Frontend Session
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    # Retrieve user from session if possible, or just create dummy if we trust session
    if 'user' in session:
        u_data = session['user']
        if str(u_data['id']) == str(user_id):
            return User(u_data['id'], u_data['username'], u_data['email'])
    return None

# Helpers
def get_backend_data(endpoint, params=None):
    try:
        response = requests.get(f"{BACKEND_URL}/{endpoint}", params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
    return []

# Routes
@app.route('/')
def index():
    noticias = get_backend_data('noticias')[:6]
    partidos = get_backend_data('partidos')[:5] # Filter/Sort needed? Backend does it?
    productos = get_backend_data('productos')[:4]
    return render_template('index.html', noticias=noticias, partidos=partidos, productos=productos)

@app.route('/noticias')
def noticias():
    noticias_lista = get_backend_data('noticias')
    return render_template('noticias.html', noticias=noticias_lista)

@app.route('/deportes')
def deportes():
    deporte = request.args.get('deporte', '')
    params = {'deporte': deporte} if deporte else {}
    noticias = get_backend_data('noticias', params)
    partidos = get_backend_data('partidos', params)
    return render_template('deportes.html', noticias=noticias, partidos=partidos, deporte_seleccionado=deporte)

@app.route('/buscar')
def buscar():
    q = request.args.get('q', '')
    if q:
        data = get_backend_data('buscar', {'q': q})
        return render_template('buscar.html', 
                             query=q,
                             resultados_noticias=data.get('noticias', []),
                             resultados_partidos=data.get('partidos', []),
                             resultados_productos=data.get('productos', []),
                             total_resultados=len(data.get('noticias', [])) + len(data.get('partidos', [])) + len(data.get('productos', [])))
    return render_template('buscar.html', query='', total_resultados=0)

@app.route('/noticia/<int:noticia_id>')
def noticia_detalle(noticia_id):
    noticia = get_backend_data(f'noticia/{noticia_id}')
    if not noticia:
        return "Noticia no encontrada", 404
    return render_template('noticia_detalle.html', noticia=noticia)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        
        try:
            resp = requests.post(f"{BACKEND_URL}/register", json={
                'username': username, 
                'email': email, 
                'password': password
            })
            data = resp.json()
            
            if resp.status_code == 200:
                flash('Registro exitoso! Por favor inicia sesión.', 'success')
                return redirect(url_for('login'))
            else:
                flash(data.get('message', 'Error en el registro'), 'error')
        except Exception as e:
            flash(f'Error de conexión: {e}', 'error')
            
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        try:
            resp = requests.post(f"{BACKEND_URL}/login", json={'username': username, 'password': password})
            data = resp.json()
            
            if data.get('success'):
                user_data = data['user']
                user = User(user_data['id'], user_data['username'], user_data['email'])
                session['user'] = user_data # Store minimal data
                login_user(user)
                flash('Inicio de sesión exitoso!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
        except Exception as e:
            flash(f'Error de conexión: {e}', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('index'))

@app.route('/agregar-noticia', methods=['GET', 'POST'])
@login_required
def agregar_noticia():
    if request.method == 'POST':
        data = {
            'titulo': request.form['titulo'],
            'contenido': request.form['contenido'],
            'deporte': request.form['deporte'],
            'autor': request.form['autor'],
            'destacada': 'destacada' in request.form
        }
        try:
            resp = requests.post(f"{BACKEND_URL}/noticias", json=data)
            if resp.status_code == 200:
                flash('Noticia agregada!', 'success')
                return redirect(url_for('noticias'))
            else:
                flash(f"Error: {resp.json().get('error')}", 'error')
        except Exception as e:
            flash(f"Error: {e}", 'error')
            
    return render_template('agregar_noticia.html')

@app.route('/agregar-partido', methods=['GET', 'POST'])
@login_required
def agregar_partido():
    if request.method == 'POST':
        data = {
            'equipo_local': request.form['equipo_local'],
            'equipo_visitante': request.form['equipo_visitante'],
            'deporte': request.form['deporte'],
            'liga': request.form['liga'],
            'fecha': request.form['fecha'],
            'hora': request.form['hora'],
            'estado': request.form['estado'],
            'fecha_hora': f"{request.form['fecha']} {request.form['hora']}"
        }
        try:
            resp = requests.post(f"{BACKEND_URL}/partidos", json=data)
            if resp.status_code == 200:
                flash('Partido agregado!', 'success')
                return redirect(url_for('deportes'))
            else:
                flash(f"Error: {resp.json().get('error')}", 'error')
        except Exception as e:
            flash(f"Error: {e}", 'error')
            
    return render_template('agregar_partido.html')

@app.route('/editar-noticia/<int:noticia_id>', methods=['GET', 'POST'])
@login_required
def editar_noticia(noticia_id):
    if request.method == 'POST':
        data = {
            'titulo': request.form['titulo'],
            'contenido': request.form['contenido'],
            'deporte': request.form['deporte'],
            'autor': request.form['autor'],
            'destacada': 'destacada' in request.form
        }
        try:
            resp = requests.put(f"{BACKEND_URL}/noticia/{noticia_id}", json=data)
            if resp.status_code == 200:
                flash('Noticia actualizada!', 'success')
                return redirect(url_for('noticia_detalle', noticia_id=noticia_id))
            else:
                flash(f"Error: {resp.json().get('error')}", 'error')
        except Exception as e:
            flash(f"Error: {e}", 'error')
    
    # GET: Fetch existing data
    noticia = get_backend_data(f"noticia/{noticia_id}")
    return render_template('editar_noticia.html', noticia=noticia)

@app.route('/eliminar-noticia/<int:noticia_id>', methods=['POST'])
@login_required
def eliminar_noticia(noticia_id):
    try:
        resp = requests.delete(f"{BACKEND_URL}/noticia/{noticia_id}")
        if resp.status_code == 200:
            flash('Noticia eliminada correctamente', 'success')
            return redirect(url_for('noticias'))
        else:
            flash('Error al eliminar noticia', 'error')
    except Exception as e:
        flash(f'Error de conexión: {e}', 'error')
    return redirect(url_for('noticias'))

@app.route('/editar-partido/<int:partido_id>', methods=['GET', 'POST'])
@login_required
def editar_partido(partido_id):
    if request.method == 'POST':
        data = {
            'equipo_local': request.form['equipo_local'],
            'equipo_visitante': request.form['equipo_visitante'],
            'deporte': request.form['deporte'],
            'liga': request.form['liga'],
            'fecha': request.form['fecha'],
            'hora': request.form['hora'],
            'estado': request.form['estado'],
            'fecha_hora': f"{request.form['fecha']} {request.form['hora']}"
        }
        try:
            resp = requests.put(f"{BACKEND_URL}/partido/{partido_id}", json=data)
            if resp.status_code == 200:
                flash('Partido actualizado!', 'success')
                return redirect(url_for('index'))
            else:
                flash(f"Error: {resp.json().get('error')}", 'error')
        except Exception as e:
            flash(f"Error: {e}", 'error')

    # GET: Fetch existing data
    partido = get_backend_data(f"partido/{partido_id}")
    # Separar fecha y hora para el formulario
    if partido and partido.get('fecha_hora'):
        try:
            # fecha_hora viene como ISO string
            dt = datetime.fromisoformat(partido['fecha_hora'])
            partido['fecha'] = dt.strftime('%Y-%m-%d')
            partido['hora'] = dt.strftime('%H:%M')
        except:
            pass
            
    return render_template('editar_partido.html', partido=partido)

@app.route('/eliminar-partido/<int:partido_id>', methods=['POST'])
@login_required
def eliminar_partido(partido_id):
    try:
        resp = requests.delete(f"{BACKEND_URL}/partido/{partido_id}")
        if resp.status_code == 200:
            flash('Partido eliminado correctamente', 'success')
            return redirect(url_for('index'))
        else:
            flash('Error al eliminar partido', 'error')
    except Exception as e:
        flash(f'Error de conexión: {e}', 'error')
    return redirect(url_for('index'))

@app.route('/agregar-datos-deportes')
def agregar_datos_deportes():
    try:
        requests.post(f"{BACKEND_URL}/seed-db")
        return """
        <h1>✅ Datos agregados</h1>
        <a href="/">Volver</a>
        """
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

