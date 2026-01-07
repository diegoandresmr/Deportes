import os
import sys

print("=" * 60)
print("🔥 RESET COMPLETO DE BASE DE DATOS ONLINE SPORTS 🔥")
print("=" * 60)

# Agregar directorio actual al path
sys.path.append('.')

try:
    from app import app, db, Usuario, Noticia, Partido, Producto
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de que app.py esté en el mismo directorio")
    sys.exit(1)

with app.app_context():
    print("\n1. Eliminando base de datos existente...")
    
    # Archivos de base de datos a eliminar
    db_files = ['online_sports.db', 'instance/online_sports.db']
    
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"   🗑️  Eliminado: {db_file}")
        else:
            print(f"   ℹ️  No encontrado: {db_file}")
    
    print("\n2. Creando nueva base de datos...")
    db.drop_all() # Ensure we drop tables in Postgres too
    db.create_all()
    print("   ✅ Base de datos creada")
    
    print("\n3. Verificando estructura...")
    
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    print("\n   📋 Tablas creadas:")
    for table in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns(table)]
        print(f"   ├─ {table}: {', '.join(columns)}")
    
    print("\n4. Creando usuario admin de prueba...")
    try:
        admin = Usuario(
            username="admin",
            email="admin@online-sports.com"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("   ✅ Usuario admin creado (usuario: admin, contraseña: admin123)")
    except Exception as e:
        print(f"   ⚠️  Error creando usuario: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 RESET COMPLETADO EXITOSAMENTE!")
    print("=" * 60)
    print("\n📋 PASOS SIGUIENTES:")
    print("1. Ejecuta: python app.py")
    print("2. Visita: http://localhost:5000/")
    print("3. Para agregar datos deportivos visita: /agregar-datos-deportes")
    print("4. Inicia sesión con: usuario: admin, contraseña: admin123")
    print("\n⚠️  NOTA: Si aún ves errores, verifica que tu app.py tenga los modelos correctos")