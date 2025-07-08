# Imagen base con python
FROM python:3.13.5

# Establece el directorio de trabajo 
WORKDIR /calendario

# Copiar los archivos del proyecto
COPY backend/requirements.txt ./

# Instala las dependencias (requirements.txt)
RUN pip install -r requirements.txt


COPY . .

# Comando para correr la aplicación
# CMD ["python", "run.py"]