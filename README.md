# Huella Azul — Clínica Veterinaria

## Análisis y diseño
Nombre: Huella Azul — Sistema de gestión veterinaria.

Problema: Las clínicas veterinarias requieren administrar información de propietarios, pacientes, consultas y tratamientos. Llevar esta información en papel dificulta su búsqueda y actualización.

Objetivo general: Construir un sistema web funcional de administración veterinaria con frontend HTML/CSS/JavaScript, backend Python/FastAPI y base de datos relacional SQLite.

Usuarios: Recepción, profesionales veterinarios y personal administrativo.

Funciones principales: CRUD completo de propietarios, mascotas, veterinarios, servicios, citas e historial clínico. Validación de relaciones, prevención de citas simultáneas para un mismo veterinario, consulta de estadísticas y búsqueda desde la interfaz.

## Tecnologías
- Python 3.10 o superior + FastAPI + Pydantic
- SQLite con claves foráneas
- HTML, CSS y JavaScript sin frameworks
- GitHub para repositorio y Vercel para despliegue (pendiente de realizar por el estudiante)

## Instrucciones de instalación y ejecución
1. Descomprimir el proyecto.
2. Abrir la carpeta `Veterinaria_Huella_Azul` en Visual Studio Code.
3. Abrir la terminal de VS Code en esa carpeta.
4. Ejecutar `python -m pip install -r requirements.txt`.
5. Ejecutar `python -m uvicorn main:app --reload`.
6. Abrir http://127.0.0.1:8000 para ver la web y http://127.0.0.1:8000/docs para ver la API.

La base SQLite `veterinaria.db` incluida almacena datos de demostración; si se elimina, la aplicación crea otra automáticamente al iniciarse.

## Estructura
```
Veterinaria_Huella_Azul/
├── main.py                         # API FastAPI y CRUD
├── database.py                     # Modelo relacional SQLite y datos iniciales
├── veterinaria.db                  # Base SQLite de ejemplo
├── static/
│   ├── index.html                  # Página principal y formularios
│   ├── styles.css                  # Diseño azul/blanco responsivo
│   └── app.js                      # Consumo real de API
├── docs/
│   └── diagrama_entidad_relacion.mmd
├── requirements.txt
├── vercel.json
├── .gitignore
└── README.md
```

## Base de datos y relaciones
- `propietarios`: PK `id`, nombre, teléfono, correo.
- `mascotas`: PK `id`, FK `propietario_id`, nombre, especie, raza, edad.
- `veterinarios`: PK `id`, nombre, especialidad, teléfono.
- `servicios`: PK `id`, nombre, descripción, precio.
- `citas`: PK `id`, FK `mascota_id`, `veterinario_id`, `servicio_id`, fecha, hora, estado, notas.
- `historial`: PK `id`, FK `mascota_id`, `veterinario_id`, fecha, diagnóstico, tratamiento.

Diagrama entidad-relación en `docs/diagrama_entidad_relacion.mmd`, visualizable en https://mermaid.live/ .

## CRUD/API
Endpoints generales: `GET /api/{tabla}`, `GET /api/{tabla}/{id}`, `POST /api/{tabla}`, `PUT /api/{tabla}/{id}`, `DELETE /api/{tabla}/{id}`; además `GET /api/resumen`. Los nombres de tabla válidos son `propietarios`, `mascotas`, `veterinarios`, `servicios`, `citas`, `historial`.

Las filas en la interfaz se cargan desde SQLite mediante llamadas `fetch` a FastAPI. Se verifica la existencia de claves foráneas y se impide borrar un registro referenciado por otros.

## GitHub y Vercel
No se ha publicado automáticamente. El estudiante debe subir el proyecto a un repositorio GitHub y publicar en Vercel. IMPORTANTE: la persistencia de SQLite local no está garantizada en Vercel porque su sistema de archivos de funciones es temporal o de solo lectura. Para demostrar CRUD persistente en producción, se requiere un almacenamiento persistente compatible o un despliegue alternativo con disco persistente. La versión local funciona con SQLite, como exige la guía. No presentar un enlace Vercel como funcional hasta resolver esto y probarlo.

Este proyecto es una demostración académica. El historial clínico contiene datos de prueba; no usar para expedientes reales sin autenticación, permisos, seguridad y copias de respaldo.
