# Backend - Librería Nazareth

## 📌 Descripción general

El backend de **Librería Nazareth** es una API REST desarrollada en **Django** que da soporte tanto a la aplicación web (Angular) como a la aplicación móvil (Android). Es el núcleo del sistema: gestiona la lógica de negocio, la autenticación, y el acceso a la base de datos.

Este repositorio contiene todo lo necesario para levantar el backend y la base de datos en un entorno de desarrollo local.

---

## 🎯 Decisión de arquitectura

### ¿Por qué un repositorio separado?

Decidimos separar el backend en su propio repositorio por las siguientes razones:

1. **Separación de responsabilidades**: El backend es la fuente del sistema. Tanto la web como la app móvil consumen sus APIs, pero no dependen de su código fuente.
2. **Equipos independientes**: Cada frente (backend, web, mobile) puede trabajar a su ritmo sin pisar cambios de otros.
3. **CI/CD independiente**: Cada repositorio puede tener su propio pipeline de integración y despliegue.
4. **Escalabilidad**: Si en el futuro se agrega otro cliente (por ejemplo, una app iOS), solo se conecta a la API existente.
5. **Mantenibilidad**: El código Python (Django) no se mezcla con TypeScript (Angular) ni Java (Android), evitando conflictos en el `.gitignore` y en las herramientas de build.

### Estructura de repositorios del proyecto

| Repositorio | Descripción | Tecnología |
|---|---|---|
| [`LibreriaNazareth-Backend`](https://github.com/Webstars-ispc/LibreriaNazareth-Backend) | API REST + Base de datos | Django + MySQL/PostgreSQL |
| [`LibreriaNazareth-Web`](https://github.com/Webstars-ispc/LibreriaNazareth) | Aplicación web | Angular |
| [`LibreriaNazarethAppMovil`](https://github.com/Webstars-ispc/LibreriaNazarethAppMovil) | Aplicación móvil | Android (Java) |

---

## 🛠️ Tecnologías utilizadas

- **Lenguaje**: Python 3.10+
- **Framework**: Django + Django REST Framework
- **Base de datos**: MySQL 
- **Autenticación**: JWT (JSON Web Tokens)
- **Gestión de dependencias**: `pip` + `requirements.txt`
- **Entorno virtual**: `venv`

---

## 📂 Estructura del repositorio
LibreriaNazareth-Backend/  
│  
├── api/ # App Django principal  
│ ├── migrations/ # Migraciones de la BD  
│ ├── admin.py  
│ ├── apps.py  
│ ├── models.py # Modelos de datos  
│ ├── serializers.py # Serializers de DRF  
│ ├── tests.py  
│ ├── urls.py  
│ └── views.py # Vistas / endpoints  
│  
├── config/ # Configuración del proyecto Django  
│ ├── settings.py  
│ ├── urls.py  
│ ├── asgi.py  
│ └── wsgi.py  
│  
├── usuarios/ # App de gestión de usuarios  
│ ├── migrations/  
│ ├── admin.py  
│ ├── apps.py  
│ ├── email_backend.py  
│ ├── models.py  
│ ├── permissions.py  
│ ├── serializers.py  
│ ├── tests.py  
│ ├── urls.py  
│ └── views.py  
│  
├── database/ # Scripts y datos de la base de datos  
│ ├── basededatos.sql # Script de creación de tablas  
│ ├── cargar_datos.py # Script de carga de datos desde Excel  
│ ├── INVENTARIOPRUEBA.xlsx # Datos de prueba  
│ └── README.md # Instrucciones de uso  
│  
├── .env_modelo # Ejemplo de variables de entorno  
├── .gitignore  
├── manage.py  
├── requirements.txt  
└── README.md  

## 🚀 Cómo levantar el proyecto
PRIMERO QUE NADA: ABRIMOS NUESTRO IDE (por ejemplo Visual Studio Code)  

### Clonar el repositorio 
```bash
git clone https://github.com/Webstars-ispc/LibreriaNazareth-Backend.git
cd LibreriaNazareth-Backend
```

### Crear y activar el entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Backend — Django
* Iniciar MySQL/MariaDB: 
Abrí el Panel de Control de XAMPP y hacé clic en Start en la fila de MySQL. Debe aparecer en verde.

* Crear la base de datos: 
Abrí phpMyAdmin (http://localhost/phpmyadmin) y creá una base de datos con el nombre LibreriaNazareth (o el que prefieras) con cotejamiento utf8mb4_general_ci.

* Averiguar tu IP local (ej. `192.168.0.15`), esta se reemplazará en el archivo .env_modelo donde dice "TU-IPv4":
   ```bash
   ipconfig        # en cmd Windows
   ```
* Configurar variables de entorno: abri tu editor de codigo, dirigite a la carpeta BackEnd y modifica el archivo ".env_modelo" con tus credenciales:
```bash
SECRET_KEY=tu-clave-secreta #la genera django al crear el proyecto
DEBUG=True
DB_NAME=LibreriaNazareth
DB_USER=root
DB_PASSWORD=         # En XAMPP suele estar vacío
DB_HOST=localhost
DB_PORT=3306
LLOWED_HOSTS=TU-IPv4,localhost,127.0.0.1 # Listar dominios. En desarrollo dejar vacio (localhost). En produccion agregar dominio real
CSRF_TRUSTED_ORIGINS=http://TU-IPv4:8000,http://localhost:8000
CORS_ALLOWED_ORIGINS=http://localhost:4200,http://TU-IPv4:8000
```
(En caso de que no tengas una clave secreta, generala aleatoriamente: 
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Luego renombra el archivo a .env

* Abri una terminal en la carpeta Backend
* Crear entorno virtual, activarlo e instalar dependencias: 
```bash
python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```
* Ejecutar migraciones: crea todas las tablas automaticamente
```bash
python manage.py migrate
```
* Las tablas van a estar vacias asi que hay que cargar datos, para no hacerlo manualmente uno por uno ejecutamos el archivo cargar_datos.py que se encuentra en la carpeta database
```bash
python cargar_datos.py
```
* Inicializar el servidor:
```bash
python manage.py runserver
```
El backend estará disponible en http://127.0.0.1:8000/
