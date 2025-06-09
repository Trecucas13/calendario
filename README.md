# Proyecto de Gestión de Citas Médicas

## Descripción General

Este proyecto es una aplicación web diseñada para facilitar la gestión de citas médicas. Permite a los usuarios autenticarse, programar, visualizar y administrar citas. La aplicación cuenta con un backend robusto para manejar la lógica de negocio y la interacción con la base de datos, y un frontend intuitivo para la interacción del usuario.

## Características Principales

*   **Autenticación de Usuarios:** Sistema seguro para el registro e inicio de sesión de usuarios.
*   **Gestión de Citas:** Funcionalidades para crear, ver, actualizar y eliminar citas médicas.
*   **Calendario Interactivo:** Interfaz de calendario para seleccionar fechas y visualizar la disponibilidad.
*   **Administración de Pacientes:** Herramientas para registrar y gestionar la información de los pacientes.
*   **Gestión de Usuarios:** Panel para administrar los usuarios del sistema.
*   **Interfaz Intuitiva:** Diseño amigable y fácil de usar para una buena experiencia de usuario.

## Estructura del Proyecto

El proyecto está organizado en las siguientes carpetas principales:

*   **`auth/`**: Contiene los módulos relacionados con la autenticación de usuarios.
*   **`backend/`**: Incluye la lógica del servidor, APIs y la interacción con la base de datos (usando FastAPI).
    *   **`app/core/`**: Configuración central y utilidades.
    *   **`app/crud/`**: Operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para los modelos de datos.
    *   **`app/models/`**: Definiciones de los modelos de la base de datos (SQLAlchemy).
    *   **`app/routers/`**: Endpoints de la API para gestionar las diferentes funcionalidades.
    *   **`app/schemas/`**: Esquemas Pydantic para la validación y serialización de datos.
*   **`database/`**: Scripts y configuraciones relacionadas con la base de datos.
*   **`models/`**: Contiene módulos para operaciones específicas de la base de datos y lógica de negocio del frontend (Flask).
    *   **`actualizar/`**: Lógica para actualizar registros.
    *   **`eliminar/`**: Lógica para eliminar registros.
    *   **`inserciones/`**: Lógica para insertar nuevos registros.
    *   **`vistas/`**: Lógica para presentar datos en el frontend.
*   **`static/`**: Archivos estáticos como CSS, JavaScript e imágenes.
*   **`templates/`**: Plantillas HTML para las vistas del frontend.

## Archivos Principales

*   **`app.py`**: Archivo principal de la aplicación Flask (frontend).
*   **`backend/app/main.py`**: Archivo principal de la aplicación FastAPI (backend).
*   **`requirements.txt`**: Lista de dependencias de Python para el proyecto.
*   **`calendario.db`**: Base de datos SQLite utilizada por la aplicación.
*   **`savia_salud.sql`**: Posiblemente un script SQL para la inicialización de la base de datos.

## Puesta en Marcha (General)

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-directorio>
    ```

2.  **Instalar dependencias:**
    Asegúrate de tener Python instalado. Luego, instala las dependencias listadas en `requirements.txt` y `backend/requirements.txt`.
    ```bash
    pip install -r requirements.txt
    pip install -r backend/requirements.txt
    ```

3.  **Configurar la base de datos:**
    *   Asegúrate de que el archivo `calendario.db` esté presente o que la configuración en `database/config.py` y `backend/app/core/database.py` apunte a la base de datos correcta.
    *   Si existe un script como `savia_salud.sql`, puede ser necesario ejecutarlo para inicializar el esquema de la base de datos.

4.  **Ejecutar la aplicación:**
    *   **Backend (FastAPI):** Navega al directorio `backend` y ejecuta la aplicación usando Uvicorn.
        ```bash
        cd backend
        uvicorn app.main:app --reload
        ```
        Generalmente, el backend estará disponible en `http://127.0.0.1:8000`.

    *   **Frontend (Flask):** Ejecuta la aplicación Flask.
        ```bash
        python app.py
        ```
        Generalmente, el frontend estará disponible en `http://127.0.0.1:5000`.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar este proyecto, por favor sigue estos pasos:

1.  Haz un fork del repositorio.
2.  Crea una nueva rama para tus cambios (`git checkout -b feature/nueva-funcionalidad`).
3.  Realiza tus cambios y haz commit (`git commit -am 'Añade nueva funcionalidad'`).
4.  Empuja tus cambios a la rama (`git push origin feature/nueva-funcionalidad`).
5.  Abre un Pull Request.
