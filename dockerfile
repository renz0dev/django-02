# 1. Usa una imagen base de Python
FROM python:3.10-slim

# 2. Establece un directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copia los archivos del proyecto al contenedor
COPY . /app

# 4. Instala las dependencias del sistema necesarias para mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# 5. Instala las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Exponer el puerto de Django (por defecto 8000)
EXPOSE 8000

# 7. Comando por defecto para iniciar el servidor de Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "dashboard.wsgi:application"]