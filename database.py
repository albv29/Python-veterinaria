"""Esquema SQLite para Huella Azul Veterinaria."""
import sqlite3
import os
from pathlib import Path
DB_PATH=Path(os.getenv('DATABASE_PATH',str(Path(__file__).resolve().parent/'veterinaria.db')))
SCHEMA='''
CREATE TABLE IF NOT EXISTS propietarios(id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL,telefono TEXT NOT NULL,correo TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS mascotas(id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL,especie TEXT NOT NULL,raza TEXT NOT NULL DEFAULT '',edad INTEGER NOT NULL DEFAULT 0 CHECK(edad>=0),propietario_id INTEGER NOT NULL,FOREIGN KEY(propietario_id) REFERENCES propietarios(id) ON DELETE RESTRICT);
CREATE TABLE IF NOT EXISTS veterinarios(id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL,especialidad TEXT NOT NULL,telefono TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS servicios(id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL UNIQUE,descripcion TEXT NOT NULL DEFAULT '',precio REAL NOT NULL CHECK(precio>=0));
CREATE TABLE IF NOT EXISTS citas(id INTEGER PRIMARY KEY AUTOINCREMENT,mascota_id INTEGER NOT NULL,veterinario_id INTEGER NOT NULL,servicio_id INTEGER NOT NULL,fecha TEXT NOT NULL,hora TEXT NOT NULL,estado TEXT NOT NULL DEFAULT 'Programada' CHECK(estado IN ('Programada','Confirmada','Completada','Cancelada')),notas TEXT NOT NULL DEFAULT '',FOREIGN KEY(mascota_id) REFERENCES mascotas(id) ON DELETE RESTRICT,FOREIGN KEY(veterinario_id) REFERENCES veterinarios(id) ON DELETE RESTRICT,FOREIGN KEY(servicio_id) REFERENCES servicios(id) ON DELETE RESTRICT);
CREATE TABLE IF NOT EXISTS historial(id INTEGER PRIMARY KEY AUTOINCREMENT,mascota_id INTEGER NOT NULL,fecha TEXT NOT NULL,diagnostico TEXT NOT NULL,tratamiento TEXT NOT NULL DEFAULT '',veterinario_id INTEGER NOT NULL,FOREIGN KEY(mascota_id) REFERENCES mascotas(id) ON DELETE RESTRICT,FOREIGN KEY(veterinario_id) REFERENCES veterinarios(id) ON DELETE RESTRICT);
CREATE INDEX IF NOT EXISTS idx_citas_fecha ON citas(fecha,hora);
'''
def get_connection():
 DB_PATH.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(DB_PATH,timeout=15)
 c.row_factory=sqlite3.Row
 c.execute('PRAGMA foreign_keys=ON')
 return c

def initialize_database():
 with get_connection() as c:
  c.executescript(SCHEMA)
  if not c.execute('SELECT COUNT(*) FROM servicios').fetchone()[0]:
   c.executemany('INSERT INTO servicios(nombre,descripcion,precio) VALUES (?,?,?)',[
    ('Consulta general','Valoración integral para perros y gatos',18000),('Vacunación','Aplicación de vacunas y control preventivo',12000),('Desparasitación','Tratamiento contra parásitos',8500),('Odontología','Limpieza y revisión dental',28000),('Control de salud','Seguimiento preventivo',15000)])
  if not c.execute('SELECT COUNT(*) FROM veterinarios').fetchone()[0]:
   c.executemany('INSERT INTO veterinarios(nombre,especialidad,telefono) VALUES (?,?,?)',[('Dra. Sofía Vargas','Medicina general','8888-1001'),('Dr. Daniel Rojas','Medicina preventiva','8888-1002')])
  if not c.execute('SELECT COUNT(*) FROM propietarios').fetchone()[0]:
   c.executemany('INSERT INTO propietarios(nombre,telefono,correo) VALUES (?,?,?)',[('María Fernández','8888-2030','maria@ejemplo.com'),('Carlos Jiménez','8888-2031','carlos@ejemplo.com')])
  if not c.execute('SELECT COUNT(*) FROM mascotas').fetchone()[0]:
   c.executemany('INSERT INTO mascotas(nombre,especie,raza,edad,propietario_id) VALUES (?,?,?,?,?)',[('Luna','Perro','Golden retriever',3,1),('Milo','Gato','Mestizo',2,2),('Nala','Perro','Beagle',4,1)])
