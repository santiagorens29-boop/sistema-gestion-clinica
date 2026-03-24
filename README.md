# 🏥 Sistema de Gestión Clínica (Full Stack)

Este es un sistema integral para la administración de centros médicos, desarrollado con una arquitectura desacoplada utilizando una API REST.

## 🛠️ Stack Tecnológico
* **Backend:** Python & Django con **Django REST Framework (DRF)**.
* **Frontend:** **Vue.js** (Framework progresivo de JavaScript).
* **Base de Datos:** SQLite (Desarrollo).
* **Estilos:** Bootstrap 5 para un diseño responsive.

## 🚀 Funcionalidades y Arquitectura
* **API RESTful:** Comunicación fluida entre el backend y el frontend mediante endpoints JSON.
* **Gestión de Pacientes e Historias Clínicas:** CRUD completo con validaciones.
* **Sistema de Turnos:** Lógica de negocio para la asignación de citas médicas.
* **Seguridad:** Autenticación y manejo de permisos por roles (Médicos / Secretaría).

## 📦 Instalación y Uso
1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Ejecutar migraciones: `python manage.py migrate`.
5. Iniciar servidor de desarrollo: `python manage.py runserver`.