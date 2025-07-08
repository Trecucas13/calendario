📅 Backend - Agendamiento de Citas Savia Salud EPS
==================================================

Este es el backend del aplicativo de agendamiento de citas desarrollado para Savia Salud EPS. Está construido con FastAPI, SQLAlchemy y se conecta a una base de datos MySQL (gestionada desde PhpMyAdmin).

🚀 Funcionalidades implementadas
--------------------------------

👤 Registro Base (/registros)
- Carga individual de pacientes.
- Carga masiva desde archivos `.xlsx` o `.csv`.
- Validación por llave compuesta: tipo_id + num_id + proceso.
- Consulta de registros enriquecida con la mejor gestión (/registros/completo).

🧾 Gestión (/gestiones)
- Registro de gestiones desde el frontend/modal (tipificación, comentario, ID de llamada, usuario).
- Cálculo automático de la mejor gestión por paciente (según ranking).
- Histórico completo de gestiones con campos del paciente y categorización.

⚙️ Tipificaciones (/tipificaciones)
- Carga individual o masiva de tipificaciones base.
- Cada tipificación incluye su ranking y tipo_contacto (EFECTIVO, NO EFECTIVO, NO CONTACTADO).

📂 Estructura del proyecto
--------------------------

backend/
├── app/
│   ├── core/             # Conexión DB
│   ├── crud/             # Lógica de negocio
│   ├── models/           # Modelos SQLAlchemy
│   ├── routers/          # Endpoints FastAPI
│   ├── schemas/          # Esquemas Pydantic
│   └── main.py           # Punto de entrada

⚙️ Requisitos
-------------

- Python 3.10 o superior
- MySQL (o PhpMyAdmin)
- pip

Instala las dependencias:

    pip install -r requirements.txt

🔌 Configuración de conexión
----------------------------

Edita el archivo app/core/database.py y reemplaza por tus datos reales:

    DATABASE_URL = "mysql+pymysql://usuario:contraseña@localhost/nombre_de_tu_bd"

▶️ Ejecutar el servidor
-----------------------

Desde la raíz del proyecto:

    uvicorn app.main:app --reload

Abre en el navegador:

- Documentación Swagger: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

✅ Endpoints clave
------------------

| Método | Ruta                             | Descripción                             |
|--------|----------------------------------|-----------------------------------------|
| GET    | /registros/                      | Lista registros individuales            |
| POST   | /registros/                      | Crea un nuevo registro                  |
| POST   | /registros/cargar_archivo/       | Carga masiva desde archivo Excel o CSV  |
| GET    | /registros/completo/             | Lista registros + mejor gestión         |
| POST   | /gestiones/                      | Crea nueva gestión (desde modal)        |
| GET    | /gestiones/historico/            | Lista histórico completo                |
| POST   | /tipificaciones/                 | Crea una tipificación                   |
| POST   | /tipificaciones/cargar_multiples/| Carga masiva de tipificaciones          |
| GET    | /tipificaciones/                 | Lista todas las tipificaciones          |

📌 Estado actual
----------------

- [x] Backend funcional probado con Swagger
- [x] Endpoints estructurados y separados por router
- [x] Listo para conexión a MySQL
- [x] Preparado para pruebas con datos reales

🧠 Autoría y soporte
--------------------

Desarrollado por el equipo de practicantes de Andes BPO con apoyo técnico de @Emperor072100
