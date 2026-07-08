# Control y Asignación de Usuarios (Wayki Trek)

Este documento detalla la asignación de usuarios y configuraciones administrativas en el sistema Odoo para Wayki Trek.

> [!IMPORTANT]
> **Administrador Temporal Activo:**
> Actualmente, el usuario **Amaru Cusi** (`network@waykitrek.net`, ID de usuario `2`) está configurado como el administrador del sistema en la instancia de Odoo y es el que se usa en las variables de entorno del archivo `.env` (`ODOO_USER=network@waykitrek.net`).

## Usuarios Configurados y Firmas de Correo

Se han actualizado los siguientes usuarios con sus datos formales y sus respectivas firmas de correo (que incluyen el logo de Wayki Trek embebido):

| Nombre | Puesto | Teléfono | Correo (Login) | ID de Usuario | ID de Partner |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Leo Cusi** | Administrador | +51 984 463 021 | `leocusi@waykitrek.net` | 13 | 44 |
| **Américo Aguilar** | Ventas | +51 969 775 002 | `sales@waykitrek.net` | 5 | 36 |
| **Carlos Fernandez** | Post-Ventas | +51 987 378 388 | `coordinator@waykitrek.net` | 9 | 40 |
| **Amaru Cusi** | Marketing | +51 913 551 308 | `network@waykitrek.net` | 2 | 3 |

---

## Instrucciones para el Cambio de Administrador

Si en el futuro se requiere transferir el rol de administrador principal a **Leo Cusi** (`leocusi@waykitrek.net`):

1. **En Odoo:**
   - Acceder a *Ajustes > Administrar usuarios*.
   - Otorgar permisos de *Administración (Ajustes)* al usuario Leo Cusi.
2. **En este repositorio (`py-odoo-cli`):**
   - Actualizar las variables de entorno en el archivo `.env`:
     ```env
     ODOO_USER=leocusi@waykitrek.net
     ODOO_PASSWORD=la_nueva_api_key_de_leo
     ```
