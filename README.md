# Backend - Librería Nazareth

## 📌 Descripción general

El backend de **Librería Nazareth** es una API REST desarrollada en **Django** que da soporte tanto a la aplicación web (Angular) como a la aplicación móvil (Android). Es el núcleo del sistema: gestiona la lógica de negocio, la autenticación, y el acceso a la base de datos.

Este repositorio contiene todo lo necesario para usar el backend desde cualquier cliente (web o mobile). **El backend y la base de datos están desplegados en la nube (AlwaysData)** y disponibles 24/7. No hace falta levantar nada en tu PC para consumir la API.

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
| [LibreriaNazareth-Backend](https://github.com/Webstars-ispc/LibreriaNazareth-Backend) | API REST + Base de datos | Django + MySQL |
| [LibreriaNazareth-Web](https://github.com/Webstars-ispc/LibreriaNazareth) | Aplicación web | Angular |
| [LibreriaNazarethAppMovil](https://github.com/Webstars-ispc/LibreriaNazarethAppMovil) | Aplicación móvil | Android (Java) |

---

## 🛠️ Tecnologías utilizadas

- **Lenguaje**: Python 3.13
- **Framework**: Django + Django REST Framework
- **Base de datos**: MySQL (MariaDB 11.4)
- **Autenticación**: JWT (JSON Web Tokens)
- **Gestión de dependencias**: `pip` + `requirements.txt`
- **Entorno virtual**: `venv`
- **Hosting**: AlwaysData (plan Free)

---

## 📂 Estructura del repositorio

```
LibreriaNazareth-Backend/
│
├── api/                          # App Django principal
│   ├── migrations/               # Migraciones de la BD
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                 # Modelos de datos
│   ├── serializers.py            # Serializers de DRF
│   ├── tests.py
│   ├── urls.py
│   └── views.py                  # Vistas / endpoints
│
├── config/                       # Configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── usuarios/                     # App de gestión de usuarios
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── email_backend.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── database/                     # Scripts y datos de la base de datos
│   ├── basededatos.sql           # Script de creación de tablas
│   ├── cargar_datos.py           # Script de carga de datos de prueba
│   ├── INVENTARIOPRUEBA.xlsx     # Datos de prueba
│   └── README.md                 # Instrucciones de uso
│
├── .env_modelo                   # Ejemplo de variables de entorno
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🌐 Backend en la nube 

El backend y la base de datos **ya están desplegados en AlwaysData** y disponibles 24/7 para todos los equipos (web y mobile). **No hace falta levantar nada en tu PC.**

### URL base de la API

```
https://librerianazareth.alwaysdata.net/
```

### Endpoints principales

- API Root: `https://librerianazareth.alwaysdata.net/api/`
- Admin Django: `https://librerianazareth.alwaysdata.net/admin/`
- Productos: `https://librerianazareth.alwaysdata.net/api/productos/`

### Configuración en cada cliente

**Para la app móvil (Android):** en `local.properties` (del repo Android) poné:

```
API_BASE_URL=https://librerianazareth.alwaysdata.net/
```

**Para la app web (Angular):** cambiá la URL base en el `environment.ts` a:

```typescript
apiUrl: 'https://librerianazareth.alwaysdata.net/'
```

> ⚠️ **IMPORTANTE:** la URL debe terminar en `/` y usar `https://` (no `http://`, no `:8000`).

---


## 📋 Mapeo de endpoints de la API

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login (email, password) |
| POST | `/api/auth/refresh/` | Refrescar token |
| GET | `/api/auth/me/` | Perfil del usuario logueado |

### Usuarios

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/auth/usuarios/` | Listar usuarios | admin |
| POST | `/api/auth/usuarios/create/` | Crear usuario | admin |
| GET | `/api/auth/usuarios/{id}/` | Ver usuario | admin |
| PUT | `/api/auth/usuarios/{id}/` | Actualizar usuario | admin |
| DELETE | `/api/auth/usuarios/{id}/` | Eliminar usuario | admin |

### Productos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/productos/` | Listar productos |
| POST | `/api/productos/` | Crear producto |
| GET | `/api/productos/{id}/` | Ver producto |
| PUT | `/api/productos/{id}/` | Actualizar producto |
| DELETE | `/api/productos/{id}/` | Eliminar producto (admin) |

### Rubros

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/rubros/` | Listar rubros |
| POST | `/api/rubros/` | Crear rubro |
| GET | `/api/rubros/{id}/` | Ver rubro |
| PUT | `/api/rubros/{id}/` | Actualizar rubro |
| DELETE | `/api/rubros/{id}/` | Eliminar rubro |

### Marcas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/marcas/` | Listar marcas |
| POST | `/api/marcas/` | Crear marca |
| GET | `/api/marcas/{id}/` | Ver marca |
| PUT | `/api/marcas/{id}/` | Actualizar marca |
| DELETE | `/api/marcas/{id}/` | Eliminar marca |

### Ventas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/ventas/` | Listar ventas |
| POST | `/api/ventas/` | Crear venta |
| GET | `/api/ventas/{id}/` | Ver venta |
| DELETE | `/api/ventas/{id}/` | Eliminar venta (admin) |

### Carga masiva y aumentos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/cargar-excel/` | Cargar productos desde Excel |
| POST | `/api/aumentos/general/` | Aumento general |
| POST | `/api/aumentos/rubro/` | Aumento por rubro |
| POST | `/api/aumentos/marca/` | Aumento por marca |
| POST | `/api/aumentos/individual/` | Aumento individual |

---

## ⚠️ Consideraciones para el equipo

1. **La base de datos es compartida** entre web y mobile. No borres datos sin avisar al equipo.
2. **Para pruebas destructivas** (borrar usuarios, productos, etc.), usá tu propio entorno local con XAMPP/MySQL.
3. **Cualquier cambio en los modelos** afecta a todos los clientes. Coordiná con el equipo antes de hacer `migrate` en producción.
4. **El archivo `.env` de producción** solo lo modifican quienes tienen acceso SSH al servidor de AlwaysData.
5. **Si hay conflictos de merge** en el repo, avisá al equipo antes de forzar un push.

---

## 🆘 Problemas comunes

### "No se puede conectar al servidor" desde la app

- Verificá que la URL en `local.properties` sea `https://librerianazareth.alwaysdata.net/` (con `https` y barra final).
- Verificá que el celular tenga internet (datos móviles o Wi-Fi).
- Probá abrir `https://librerianazareth.alwaysdata.net/api/` en el navegador del celular.

### "401 Unauthorized" en la API

- El token JWT expiró (dura 1 hora) o no te logueaste.
- Solución: volvé a loguearte en la app.

### "DisallowedHost" al entrar a la URL

- Verificá que el dominio esté en `ALLOWED_HOSTS` dentro del `.env` de producción.

### El backend no se actualiza después de un `git pull`

- Verificá que hayas hecho `touch ~/LibreriaNazareth-Backend/__init__.py` para reiniciar uWSGI.
- Verificá los logs en el panel de AlwaysData: **Web > Sitios > tu sitio > LOGS**.

---
