"""API y página web de Huella Azul Veterinaria."""
from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from database import get_connection,initialize_database
from typing import Literal

class Propietario(BaseModel):
 nombre:str=Field(min_length=1,max_length=100)
 telefono:str=Field(min_length=1,max_length=30)
 correo:str=Field(default='',max_length=120)
class Mascota(BaseModel):
 nombre:str=Field(min_length=1,max_length=80)
 especie:Literal['Perro','Gato','Ave','Conejo','Otro']
 raza:str=Field(default='',max_length=80)
 edad:int=Field(ge=0,le=100)
 propietario_id:int=Field(gt=0)
class Veterinario(BaseModel):
 nombre:str=Field(min_length=1,max_length=100)
 especialidad:str=Field(min_length=1,max_length=100)
 telefono:str=Field(default='',max_length=30)
class Servicio(BaseModel):
 nombre:str=Field(min_length=1,max_length=100)
 descripcion:str=''
 precio:float=Field(ge=0)
class Cita(BaseModel):
 mascota_id:int=Field(gt=0)
 veterinario_id:int=Field(gt=0)
 servicio_id:int=Field(gt=0)
 fecha:str=Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
 hora:str=Field(pattern=r'^\d{2}:\d{2}$')
 estado:Literal['Programada','Confirmada','Completada','Cancelada']='Programada'
 notas:str=''
class Historial(BaseModel):
 mascota_id:int=Field(gt=0)
 fecha:str=Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
 diagnostico:str=Field(min_length=1)
 tratamiento:str=''
 veterinario_id:int=Field(gt=0)

MODELOS={'propietarios':Propietario,'mascotas':Mascota,'veterinarios':Veterinario,'servicios':Servicio,'citas':Cita,'historial':Historial}
ROOT=Path(__file__).resolve().parent
@asynccontextmanager
async def lifespan(app):
 initialize_database()
 yield
app=FastAPI(title='Huella Azul | Veterinaria',version='1.0',lifespan=lifespan)
app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
@app.get('/',include_in_schema=False)
def home():return FileResponse(ROOT/'static'/'index.html')
@app.get('/api/resumen')
def resumen():
 with get_connection() as c:
  d={t:c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in MODELOS}
  d['citas_pendientes']=c.execute("SELECT COUNT(*) FROM citas WHERE estado IN ('Programada','Confirmada')").fetchone()[0]
  return d

def validar_tabla(tabla):
 if tabla not in MODELOS:raise HTTPException(404,'Módulo no encontrado')

def integrity_error(e):
 raise HTTPException(409,'No se pudo guardar: un registro relacionado no existe, está en uso o el dato está duplicado.') from e

def validar_cita(tabla,data,c,exclude=-1):
 if tabla!='citas' or data['estado']=='Cancelada':return
 duplicado=c.execute('''SELECT id FROM citas WHERE veterinario_id=? AND fecha=? AND hora=? AND estado IN ('Programada','Confirmada') AND id!=?''',(data['veterinario_id'],data['fecha'],data['hora'],exclude)).fetchone()
 if duplicado:raise HTTPException(409,'El veterinario ya tiene una cita a esa fecha y hora.')

@app.get('/api/{tabla}')
def listar(tabla:str):
 validar_tabla(tabla)
 with get_connection() as c:return [dict(r) for r in c.execute(f'SELECT * FROM {tabla} ORDER BY id DESC')]
@app.get('/api/{tabla}/{id}')
def obtener(tabla:str,id:int):
 validar_tabla(tabla)
 with get_connection() as c:r=c.execute(f'SELECT * FROM {tabla} WHERE id=?',(id,)).fetchone()
 if not r:raise HTTPException(404,'Registro no encontrado')
 return dict(r)
@app.post('/api/{tabla}',status_code=201)
def crear(tabla:str,datos:dict):
 validar_tabla(tabla)
 data=MODELOS[tabla].model_validate(datos).model_dump()
 keys=list(data)
 try:
  with get_connection() as c:
   validar_cita(tabla,data,c)
   cur=c.execute(f"INSERT INTO {tabla} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})",tuple(data.values()))
   return dict(c.execute(f'SELECT * FROM {tabla} WHERE id=?',(cur.lastrowid,)).fetchone())
 except sqlite3.IntegrityError as e:integrity_error(e)
@app.put('/api/{tabla}/{id}')
def editar(tabla:str,id:int,datos:dict):
 validar_tabla(tabla)
 data=MODELOS[tabla].model_validate(datos).model_dump()
 try:
  with get_connection() as c:
   validar_cita(tabla,data,c,id)
   cur=c.execute(f"UPDATE {tabla} SET {','.join(k+'=?' for k in data)} WHERE id=?",(*data.values(),id))
   if not cur.rowcount:raise HTTPException(404,'Registro no encontrado')
   return dict(c.execute(f'SELECT * FROM {tabla} WHERE id=?',(id,)).fetchone())
 except sqlite3.IntegrityError as e:integrity_error(e)
@app.delete('/api/{tabla}/{id}',status_code=204)
def eliminar(tabla:str,id:int):
 validar_tabla(tabla)
 try:
  with get_connection() as c:
   cur=c.execute(f'DELETE FROM {tabla} WHERE id=?',(id,))
   if not cur.rowcount:raise HTTPException(404,'Registro no encontrado')
 except sqlite3.IntegrityError as e:integrity_error(e)
