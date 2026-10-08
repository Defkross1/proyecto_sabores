# 🍲 El Comilón - Sistema Web de Gestión de Menús y Pedidos

<div align="center">

![Django Version](https://img.shields.io/badge/Django-6.1.1-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python)
![Security](https://img.shields.io/badge/Security-RBAC%20%7C%20IDOR%20Protection-orange?style=for-the-badge&logo=security)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

*Plataforma web integral para la planificación de menús semanales, gestión de convenios corporativos, control de pedidos en tiempo real y trazabilidad logística.*

</div>

---

## 📋 Tabla de Contenidos
- [Acerca del Proyecto](#-acerca-del-proyecto)
- [Características Principales](#-características-principales)
- [Arquitectura y Módulos](#-arquitectura-y-módulos)
- [Seguridad Implementada](#-seguridad-implementada)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Autor](#-autor)

---

## 🚀 Acerca del Proyecto
**"El Comilón"** es una solución de software desarrollada en **Django** diseñada para optimizar la experiencia de alimentación institucional y corporativa. Permite a los usuarios (trabajadores en convenio o clientes independientes) visualizar platos caseros destacados, planificar su menú semanal de lunes a viernes, personalizar acompañamientos (ensalada o consomé) y gestionar su historial de pedidos con total autonomía y seguridad.

---
## 📄 Informe Técnico y Arquitectura del Sistema

### 1. Pila Tecnológica y Componentes del Sistema
* **Python (Versión 3.14):** Lenguaje de programación base utilizado para la lógica de negocio, manejo de vistas, modelos y validaciones del servidor.
* **Django (Versión 6.1.1):** Framework web principal encargado del enrutamiento URL (`urls.py`), el mapeo objeto-relacional (`models.py`), el motor de plantillas y el manejo de sesiones y autenticación segura.
* **SQLite:** Sistema de gestión de bases de datos relacional integrado, utilizado para almacenar de forma persistente la información de usuarios, roles, menús, ítems y transacciones de pedidos.
* **Pillow:** Biblioteca de procesamiento de imágenes en Python, integrada para la correcta manipulación y renderizado de recursos gráficos (fotografías de platos y perfiles).
* **Bootstrap (v5.3):** Framework CSS utilizado para proporcionar una interfaz de usuario limpia, responsiva, moderna y estandarizada en todos los dispositivos.

### 2. Módulos y Reglas de Negocio Implementadas
* **Módulo de Autenticación y Roles (`usuarios`):** Jerarquías de usuario gestionadas mediante un modelo personalizado y decoradores de seguridad estrictos (`@rol_requerido`) para los roles `CLIENTE`, `ATENCION`, `REPARTIDOR` y `GERENTE`. Incluye doble flujo de registro para clientes comunes y corporativos (con validación de RUT institucional y clave fija `empresa123`).
* **Módulo de Pedidos y Trazabilidad Temporizada (`pedidos`):** 
  * Unificación automática de ítems en una única orden activa de tipo `SOLICITADO`.
  * Restricciones temporales basadas estrictamente en la zona horaria real de Chile (`America/Santiago`), bloqueando días pasados (tarjetas rojas), habilitando actuales/futuros (tarjetas verdes) y permitiendo programar los lunes de la semana siguiente los viernes o fines de semana.
  * Pasarela de selección de métodos de pago (Efectivo, Tarjeta o Transferencia en local o delivery) con bloqueo dinámico de la boleta digital hasta que el pago sea confirmado.
* **Panel de Administración Gerencial (`gerente_dashboard`):** 
  * Cálculo automatizado de las ganancias del día en tiempo real (filtrando únicamente pedidos pagados en la fecha chilena actual).
  * CRUD completo de menús con sincronización directa en la portada principal y soporte de subida de imágenes mediante `ImageField`.
  * Seguimiento operativo de estados de delivery, consumos detallados de los clientes y listados organizados de cuentas comunes y corporativas.

---
## ✨ Características Principales

### 🛒 Sincronización Interactiva (Portada $\rightarrow$ Historial)
* **Acceso Directo:** Al hacer clic en *"Ir a Pedir"* desde cualquier plato de la portada principal, el sistema procesa el ítem de inmediato, lo registra en la base de datos y redirige al usuario directo a **"Mis Pedidos"**.
* **Menú Semanal Inteligente:** Selección de platos por día con validación horaria estricta de corte en servidor (tope hasta las 15:00 hrs de cada jornada).
* **Personalización de Acompañamientos:** Posibilidad de elegir entre **Ensalada** (🥗), **Consomé** (🍲) o sin acompañamiento por cada plato seleccionado.

### 🏢 Gestión de Convenios Corporativos
* Autenticación segura para trabajadores mediante validación de **RUT y clave institucional** vinculados a su empresa en convenio.
* Asignación automática de la dirección corporativa de entrega correspondiente a la empresa aliada.

### 📊 Historial y Control del Cliente ("Mis Pedidos")
* Visualización detallada del estado de los pedidos (*Solicitado, En Preparación, En Ruta, Entregado*).
* **Gestión Activa:** Opciones de **Edición** (cambio de platos y acompañamientos) y **Eliminación** habilitadas exclusivamente para pedidos en estado `SOLICITADO`.
* Cálculo y visualización en tiempo real del **Total a Pagar** con formato monetario localizado estandarizado.

---

## 🔒 Seguridad Implementada
El sistema cuenta con un blindaje robusto orientado a entornos de producción empresariales:
* **Mitigación de IDOR (Insecure Direct Object Reference):** Validación estricta de propiedad de recursos (`cliente=request.user`) en el historial y en las acciones de edición/eliminación de pedidos para evitar que usuarios no autorizados manipulen datos ajenos vía URL.
* **Control de Acceso Basado en Roles (RBAC):** Uso de decoradores personalizados (`@rol_requerido`) para restringir los paneles operativos y de gerencia (`ATENCION`, `REPARTIDOR`, `GERENTE`).
* **Protección contra Fijación de Sesión:** Ejecución de `request.session.cycle_key()` al autenticar al usuario para rotar el identificador de sesión.
* **Transacciones Atómicas:** Uso de bloques `transaction.atomic()` para garantizar la consistencia relacional y evitar estados corruptos en la base de datos.
* **Cabeceras de Seguridad:** Configuración de cookies HTTPOnly y políticas estrictas contra Clickjacking (`X_FRAME_OPTIONS = 'DENY'`).

---

## 🏗️ Arquitectura y Módulos
* **`usuarios`**: Gestión centralizada de perfiles de usuario, roles organizacionales, empresas en convenio y direcciones de entrega.
* **`pedidos`**: Núcleo comercial encargado de la administración de catálogos de platos (`PlatoMenu`), proveedores, pedidos principales (`Pedidos`), ítems y dashboards operativos para atenciones y despachos.

---

## ⚙️ Instalación y Configuración Local

Sigue estos pasos para clonar y poner en marcha el proyecto en tu entorno local:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/Defkross1/proyecto_sabores.git](https://github.com/Defkross1/proyecto_sabores.git)
   cd proyecto_sabores-main


Crear y activar el entorno virtual:

Bash
python -m venv venv
# En Windows (PowerShell):
.\venv\Scripts\Activate

# En Mac/Linux:
source venv/bin/activate


Instalar las dependencias:

Bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# O alternativamente:
python -m pip install django Pillow

Aplicar las migraciones de base de datos:

Bash
python manage.py makemigrations
python manage.py migrate


Crear un superusuario (Opcional para administración):

Bash
python manage.py createsuperuser


Ejecutar el servidor de desarrollo:

Bash
python manage.py runserver
Abre tu navegador y accede a http://127.0.0.1:8000/.

👨‍💻 Autor
Desarrollado con dedicación por Antolín Andrés Molina Sanhueza (Estudiante en INACAP) como parte del desarrollo e ingeniería del sistema web institucional El Comilón.