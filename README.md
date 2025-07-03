# Proyecto de Agendamiento de Citas Savia Salud EPS

Este proyecto es una aplicación web diseñada para gestionar el agendamiento de citas médicas. Combina un frontend desarrollado en Flask para la interacción del usuario y un backend en FastAPI para la lógica de negocio y la gestión de datos.

## Tecnologías Principales

- **Frontend:** Flask (Python)
- **Backend:** FastAPI (Python)
- **Base de Datos:** PostgreSQL (gestionada a través de Docker)
- **ORM:** SQLAlchemy
- **Contenerización:** Docker, Docker Compose

## Propósito General

La aplicación permite a los usuarios:
- Registrar y gestionar pacientes.
- Crear y administrar calendarios de citas.
- Agendar citas para los pacientes.
- Realizar seguimiento de las gestiones realizadas con los pacientes.
- Autenticación de usuarios con diferentes roles y permisos.
- Importar y exportar datos relevantes.
- Visualizar información y reportes.

## Estructura del Proyecto

El repositorio está organizado de la siguiente manera:

- **`app.py`**: Archivo principal de la aplicación Flask (frontend).
- **`run.py`**: Script para iniciar los servicios de Flask y FastAPI.
- **`auth/`**: Contiene la lógica de autenticación y decoradores para el control de acceso en Flask.
- **`backend/`**: Contiene la aplicación FastAPI que maneja la lógica de negocio y la API.
    - **`backend/README.md`**: Documentación detallada específica del backend FastAPI.
    - **`app/`**: Código fuente de la aplicación FastAPI.
        - **`core/`**: Configuración de la base de datos.
        - **`crud/`**: Operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para las entidades de la base de datos.
        - **`models/`**: Modelos SQLAlchemy que definen la estructura de las tablas de la base de datos.
        - **`routers/`**: Endpoints de la API FastAPI.
        - **`schemas/`**: Esquemas Pydantic para la validación de datos de entrada y salida de la API.
        - **`main.py`**: Punto de entrada de la aplicación FastAPI.
- **`database/`**: Configuración de la conexión a la base de datos para la aplicación Flask.
- **`models/`**: Contiene módulos Python para interactuar con la base de datos desde Flask, incluyendo:
    - **`actualizar/`**: Lógica para actualizar registros.
    - **`eliminar/`**: Lógica para eliminar registros.
    - **`inserciones/`**: Lógica para insertar nuevos registros.
    - **`vistas/`**: Lógica para obtener y presentar datos en las vistas de Flask.
- **`static/`**: Archivos estáticos para el frontend (CSS, JavaScript, imágenes).
- **`templates/`**: Plantillas HTML utilizadas por Flask para renderizar las páginas web.
- **`.dockerfile`**: Define la imagen Docker para las aplicaciones Flask y FastAPI.
- **`docker-compose.yml`**: Define los servicios, redes y volúmenes para ejecutar la aplicación completa con Docker Compose.
- **`requirements.txt`**: Dependencias de Python para la aplicación Flask (el backend tiene su propio `requirements.txt`).

## Configuración y Ejecución

Siga estos pasos para configurar y ejecutar el proyecto localmente utilizando Docker.

### Requisitos Previos

- **Docker:** Asegúrese de tener Docker instalado y en ejecución en su sistema. Puede descargarlo desde [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Docker Compose:** Docker Compose generalmente se incluye con Docker Desktop. Verifique su instalación.

### Variables de Entorno

Las variables de entorno necesarias para la conexión a la base de datos y otras configuraciones se definen directamente en el archivo `docker-compose.yml`. Si necesita modificarlas (por ejemplo, los puertos o las credenciales de la base de datos), puede hacerlo allí.

**Nota:** El archivo `.env` en la raíz del proyecto parece estar relacionado con la configuración de la base de datos para la aplicación Flask cuando se ejecuta fuera de Docker, pero para la ejecución con Docker, `docker-compose.yml` es la fuente principal de configuración.

### Pasos para la Ejecución

1.  **Clonar el repositorio (si aún no lo ha hecho):**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_DIRECTORIO_DEL_PROYECTO>
    ```

2.  **Construir y ejecutar los servicios con Docker Compose:**
    Abra una terminal en el directorio raíz del proyecto (donde se encuentra el archivo `docker-compose.yml`) y ejecute el siguiente comando:
    ```bash
    docker-compose up -d --build
    ```
    - `up`: Crea e inicia los contenedores.
    - `-d`: Ejecuta los contenedores en segundo plano (detached mode).
    - `--build`: Fuerza la reconstrucción de las imágenes si ha habido cambios en los Dockerfiles o el contexto de construcción.

3.  **Acceder a las aplicaciones:**
    Una vez que los contenedores estén en funcionamiento:
    -   **Aplicación Flask (Frontend):** Abra su navegador y vaya a `http://localhost:5000`
    -   **Aplicación FastAPI (Backend):**
        -   **API:** La API estará disponible en `http://localhost:8000`
        -   **Documentación Interactiva (Swagger UI):** `http://localhost:8000/docs`
        -   **Especificación OpenAPI JSON:** `http://localhost:8000/openapi.json`

4.  **Detener los servicios:**
    Para detener los contenedores, ejecute el siguiente comando en la misma terminal:
    ```bash
    docker-compose down
    ```
    Si también desea eliminar los volúmenes (esto borrará los datos de la base de datos PostgreSQL), puede usar:
    ```bash
    docker-compose down -v
    ```

## Servicios Docker

El archivo `docker-compose.yml` define los siguientes servicios:

-   **`flask_app`**:
    -   Construye y ejecuta la aplicación Flask (frontend).
    -   Utiliza el `.dockerfile` ubicado en la raíz del proyecto.
    -   Mapea el puerto `5000` del contenedor al `5000` del host.
    -   Monta el directorio actual (`.`) en `/backend` dentro del contenedor para reflejar los cambios en el código en tiempo real (aunque la ruta montada podría ser `/app` o `/frontend` para mayor claridad, según la configuración interna del Dockerfile).
    -   Depende del servicio `postgresql`.

-   **`fastapi_app`**:
    -   Construye y ejecuta la aplicación FastAPI (backend).
    -   Utiliza el mismo `.dockerfile` que `flask_app`. **Nota:** Idealmente, cada aplicación podría tener su propio Dockerfile optimizado si sus dependencias o configuraciones difieren significativamente, pero aquí comparten uno.
    -   Establece el directorio de trabajo en `/calendario/backend` dentro del contenedor.
    -   Ejecuta la aplicación con `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
    -   Mapea el puerto `8000` del contenedor al `8000` del host.
    -   Monta el directorio `./calendario` del host en `/backend` dentro del contenedor. **Consideración:** La ruta de montaje y el `working_dir` deben ser consistentes con la estructura esperada por la aplicación dentro del contenedor. El `working_dir` es `/calendario/backend` y el volumen es `./calendario` montado en `/backend`. Esto implica que la app FastAPI se espera que esté en `/backend/backend/app/main.py` desde la perspectiva del contenedor, o que el `PYTHONPATH` esté ajustado. (Revisando el `run.py`, el `fastapi_cwd` es `./backend`, lo que sugiere que el contexto de construcción para uvicorn es desde `backend/`).
    -   Depende del servicio `postgresql`.

-   **`postgresql`**:
    -   Utiliza la imagen oficial de `postgres:16`.
    -   Configura la base de datos con el nombre `postgres`, usuario `postgres` y la contraseña especificada en las variables de entorno.
    -   Mapea el puerto `5432` del contenedor (puerto por defecto de PostgreSQL) al `5432` del host.
    -   Utiliza un volumen llamado `postgres_data` para persistir los datos de la base de datos, de modo que no se pierdan cuando los contenedores se detengan y se inicien de nuevo.

## Ayuda al Cliente

### Reporte de Problemas y Solicitud de Funcionalidades

Si encuentra algún problema con la aplicación o tiene alguna sugerencia para nuevas funcionalidades, por favor, comuníquese con el equipo de desarrollo a través de los canales designados por Andes BPO.

### Documentación de la API (Backend)

El backend FastAPI proporciona una documentación interactiva (Swagger UI) que permite explorar y probar los diferentes endpoints de la API. Puede acceder a ella una vez que la aplicación esté en ejecución:

-   **Swagger UI:** `http://localhost:8000/docs`

Consulte esta documentación para entender cómo interactuar con la API, los parámetros esperados y las respuestas devueltas por cada endpoint. Para más detalles sobre la estructura y funcionalidades del backend, puede consultar el archivo `backend/README.md`.

### Sistema de Autenticación y Roles

La aplicación Flask (`app.py`) incluye un sistema de autenticación (`auth/auth_login.py`) y decoradores (`auth/decorators.py`) para proteger ciertas rutas y funcionalidades.
-   **`@login_required`**: Asegura que el usuario haya iniciado sesión antes de acceder a una ruta.
-   **`@role_required([1, 2])`**: Permite el acceso solo a usuarios con roles específicos (por ejemplo, rol 1 y rol 2). La definición exacta de estos roles y sus permisos deberá ser consultada en la lógica de la aplicación o con el equipo de desarrollo.

El inicio de sesión se realiza a través de la ruta `/` (que renderiza `login.html`). Una vez autenticado, el usuario es redirigido al panel principal (`/index`).

## Autoría y Soporte

Este proyecto fue desarrollado por el equipo de practicantes de **Andes BPO**.
Para soporte técnico o consultas adicionales, por favor, contactar a través de los canales establecidos por la organización.

## Endpoints Clave

A continuación, se describen los endpoints más relevantes de la aplicación, divididos entre el Frontend (Flask) y el Backend (FastAPI).

### Frontend (Aplicación Flask - `http://localhost:5000`)

La aplicación Flask maneja la interfaz de usuario y las interacciones directas. Muchos endpoints sirven vistas HTML, mientras que otros manejan la lógica de formularios o descargas.

**Autenticación y Vistas Principales:**

| Método | Ruta                               | Descripción                                                                 | Requiere Login | Roles Permitidos (ej.) |
|--------|------------------------------------|-----------------------------------------------------------------------------|----------------|------------------------|
| GET    | `/`                                | Página de inicio de sesión.                                                 | No             | N/A                    |
| POST   | `/login`                           | Procesa las credenciales de inicio de sesión.                               | No             | N/A                    |
| GET    | `/logout`                          | Cierra la sesión del usuario.                                               | Sí             | Todos                  |
| GET    | `/index`                           | Dashboard principal, muestra información general y calendarios.             | Sí             | 1, 2                   |
| GET    | `/formulario`                      | Muestra el formulario para la creación de nuevos calendarios.               | Sí             | 1, 2                   |
| GET    | `/actualizarCalendario/<int:id>`   | Muestra el formulario para actualizar un calendario específico.             | Sí             | 1, 2                   |
| GET    | `/pacientes`                       | Muestra la lista de pacientes registrados con paginación.                   | Sí             | 1, 2                   |
| GET    | `/calendario/<int:id_calendario>`  | Muestra la vista detallada de un calendario, incluyendo citas y horarios.   | Sí             | 1, 2                   |
| GET    | `/usuarios`                        | Muestra la lista de usuarios del sistema (gestión de usuarios).             | Sí             | 1                      |
| GET    | `/Historico_gestiones`             | Muestra el historial completo de gestiones realizadas.                      | Sí             | 1, 2                   |
| GET    | `/gestion_bd`                      | Vista de la base de datos de gestiones, mostrando la "mejor gestión".       | Sí             | 1, 2                   |
| GET    | `/gestionar`                       | Interfaz para realizar y registrar nuevas gestiones sobre pacientes/casos.  | Sí             | 1, 2                   |

**Operaciones y Funcionalidades (principalmente POST o descargas GET):**

| Método | Ruta                                      | Descripción                                                              | Requiere Login | Roles Permitidos (ej.) |
|--------|-------------------------------------------|--------------------------------------------------------------------------|----------------|------------------------|
| POST   | `/crear_calendario`                       | Procesa la creación de un nuevo calendario.                              | Sí             | 1, 2                   |
| POST   | `/actualizar_calendario/<int:id>`         | Procesa la actualización de un calendario existente.                     | Sí             | 1, 2                   |
| POST   | `/delete_calendario/<int:id>`             | Elimina un calendario específico.                                        | Sí             | 1, 2                   |
| POST   | `/insertar_usuario`                       | Registra un nuevo usuario en el sistema.                                 | Sí             | 1                      |
| POST   | `/actualizar_usuario/<documento>`         | Actualiza la información de un usuario existente.                        | Sí             | 1                      |
| POST   | `/delete_usuario/<documento>`             | Elimina un usuario del sistema.                                          | Sí             | 1                      |
| POST   | `/insertar_citas`                         | Registra nuevas citas en un calendario.                                  | Sí             | 1, 2                   |
| POST   | `/insertar_pacientes`                     | Registra nuevos pacientes en el sistema.                                 | Sí             | 1, 2                   |
| POST   | `/actualizar_pacientes/<int:id>`          | Actualiza la información de un paciente.                                 | Sí             | 1, 2                   |
| POST   | `/insertar_gestiones`                     | Registra nuevas gestiones realizadas.                                    | Sí             | 1, 2                   |
| POST   | `/insertar-municipio`                     | Agrega un nuevo municipio a la base de datos.                            | Sí             | 1, 2                   |
| POST   | `/insertar-procedimiento`                 | Agrega un nuevo procedimiento a la base de datos.                        | Sí             | 1, 2                   |
| GET    | `/generar_informe_csv/<int:id_calendario>`| Descarga un informe en formato CSV de un calendario específico.          | Sí             | 1                      |
| GET    | `/descargar_excel_citas`                  | Descarga un archivo Excel con el listado de citas.                       | Sí             | 1, 2                   |
| GET    | `/descargar_excel_gestiones`              | Descarga un archivo Excel con el listado de gestiones.                   | Sí             | 1, 2                   |

*Nota: Los roles permitidos son ejemplos basados en los decoradores `@role_required` encontrados. La lógica exacta puede variar.*

### Backend (API FastAPI - `http://localhost:8000`)

El backend FastAPI expone una API para la gestión de datos más complejos y procesos de carga masiva. La documentación interactiva completa está disponible en `http://localhost:8000/docs`.

| Método | Ruta                             | Descripción                                              |
|--------|----------------------------------|----------------------------------------------------------|
| GET    | `/registros/`                      | Lista todos los registros base individuales.             |
| POST   | `/registros/`                      | Crea un nuevo registro base (paciente).                  |
| POST   | `/registros/cargar_archivo/`       | Permite la carga masiva de registros desde archivo Excel o CSV. |
| GET    | `/registros/completo/`             | Lista los registros base enriquecidos con su mejor gestión. |
| POST   | `/gestiones/`                      | Crea una nueva gestión asociada a un registro.           |
| GET    | `/gestiones/historico/`            | Lista el histórico completo de todas las gestiones.      |
| POST   | `/tipificaciones/`                 | Crea una nueva tipificación base para las gestiones.     |
| POST   | `/tipificaciones/cargar_multiples/`| Permite la carga masiva de tipificaciones.               |
| GET    | `/tipificaciones/`                 | Lista todas las tipificaciones base existentes.          |

Para más detalles sobre los parámetros de solicitud y los esquemas de respuesta de la API FastAPI, consulte la [documentación de Swagger UI](http://localhost:8000/docs).
