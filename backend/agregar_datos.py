import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, db, Noticia, Partido
from datetime import datetime

def agregar_datos_ejemplo():
    with app.app_context():
        try:
            # Verificar si ya existen datos
            if Noticia.query.filter_by(deporte='futbol').first():
                print("⚠️  Ya existen datos de deportes. ¿Quieres continuar? (s/n)")
                respuesta = input().lower()
                if respuesta != 's':
                    return

            # Datos de ejemplo para fútbol
            noticia_futbol = Noticia(
                titulo="Haaland marca quintupleta en la Champions",
                contenido="Erling Haaland hizo historia al marcar 5 goles en un solo partido de Champions League contra el RB Leipzig.",
                deporte="futbol",
                autor="Periodista Deportivo"
            )
            db.session.add(noticia_futbol)

            partido_futbol = Partido(
                equipo_local="PSG",
                equipo_visitante="Marseille",
                deporte="futbol", 
                liga="Ligue 1",
                fecha_hora=datetime(2024, 2, 15, 20, 0),
                estado="programado"
            )
            db.session.add(partido_futbol)

            # Datos de ejemplo para baloncesto
            noticia_baloncesto = Noticia(
                titulo="Curry anota 62 puntos en un partido",
                contenido="Stephen Curry establece su récord personal de anotación con 62 puntos contra Portland Trail Blazers.",
                deporte="baloncesto",
                autor="Analista NBA"
            )
            db.session.add(noticia_baloncesto)

            partido_baloncesto = Partido(
                equipo_local="Nets",
                equipo_visitante="Suns",
                deporte="baloncesto",
                liga="NBA",
                fecha_hora=datetime(2024, 2, 14, 21, 30),
                estado="programado"
            )
            db.session.add(partido_baloncesto)

            # Datos de ejemplo para tenis
            noticia_tenis = Noticia(
                titulo="Nueva generación domina el tenis femenino",
                contenido="Jugadoras como Coco Gauff y Emma Raducanu están revolucionando el tenis femenino mundial.",
                deporte="tenis", 
                autor="Especialista Tenis"
            )
            db.session.add(noticia_tenis)

            partido_tenis = Partido(
                equipo_local="Federer",
                equipo_visitante="Murray",
                deporte="tenis",
                liga="Exhibición",
                fecha_hora=datetime(2024, 2, 16, 18, 0),
                estado="programado"
            )
            db.session.add(partido_tenis)

            db.session.commit()
            print("✅ Datos agregados exitosamente!")

        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    agregar_datos_ejemplo()