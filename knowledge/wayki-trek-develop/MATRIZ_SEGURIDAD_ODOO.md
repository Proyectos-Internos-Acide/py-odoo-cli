# Matriz de Seguridad: Roles, Permisos y Visibilidad en Odoo
**Wayki Trek**
*Administración del Sistema*  
*4 de julio de 2026*

---

## 1. Introducción

Este documento especifica la estructura y distribución de roles, permisos de base de datos, visibilidad de módulos y limitaciones de acciones aplicadas para los usuarios activos en la plataforma Odoo de **Wayki Trek**. El objetivo es resguardar la integridad de los datos, evitar la fuga de información (exportación) y proteger la tarifa base de los productos y servicios turísticos.

---

## 2. Resumen de Usuarios y Roles

A continuación se detalla la asignación de usuarios y su nivel de acceso técnico en la plataforma:

| Usuario | Rol Asignado | Acceso Técnico (Ajustes) |
| :--- | :--- | :---: |
| `leocusi@waykitrek.net` | Admin Principal | Sí (Acceso Total) |
| `network@waykitrek.net` | Marketing / Redes | No |
| `sales@waykitrek.net` | Asesor de Ventas | No |
| `coordinator@waykitrek.net` | Postventas / Coordinación | No |

*Cuadro 1: Usuarios activos y roles generales.*

---

## 3. Matriz de Visibilidad de Módulos (Aplicaciones)

Define qué menús principales de Odoo son visibles en la interfaz gráfica del usuario al iniciar sesión.

| Módulo / Aplicación | Admin | Marketing | Ventas | Postventas |
| :--- | :---: | :---: | :---: | :---: |
| **CRM** | ✓ | ✓ | ✓ | ✓ |
| **Ventas (Cotizaciones)** | ✓ | ✓ | ✓ | ✓ |
| **Contactos** | ✓ | ✓ | ✓ | ✓ |
| **WhatsApp / Chat** | ✓ | ✓ | ✓ | ✓ |
| **Tableros** | ✓ | ✓ | ✓ | ✓ |
| **Redes Sociales / Automatización** | ✓ | ✓ | ✗ | ✗ |
| **Ajustes Técnicos** | ✓ | ✗ | ✗ | ✗ |
| **Facturación / Contabilidad** | ✓ | ✗ | ✗ | ✗ |

*Cuadro 2: Matriz de visibilidad de módulos principales.*

---

## 4. Matriz de Limitaciones a Nivel de Acciones (Seguridad de Datos)

Define las restricciones relacionales sobre qué acciones específicas (Crear, Leer, Editar, Borrar, Exportar) puede ejecutar cada rol sobre los datos de la empresa.

| Acción / Operación | Admin | Marketing | Ventas | Postventas |
| :--- | :---: | :---: | :---: | :---: |
| **Crear / Editar Leads (CRM)** | ✓ | ✓ | ✓ | ✓ |
| **Eliminar Leads / Oportunidades** | ✓ | ✗ | ✗ | ✗ |
| **Crear / Editar Cotizaciones (Ventas)** | ✓ | ✓ | ✓ | ✓ |
| **Eliminar Cotizaciones (SO)** | ✓ | ✗ | ✗ | ✗ |
| **Modificar Tarifas / Productos base** | ✓ | ✗ | ✗ | ✗ |
| **Exportar Contactos / Datos a Excel** | ✓ | ✗ | ✗ | ✗ |

*Cuadro 3: Matriz de acciones permitidas y restricciones.*

---

## 5. Detalle Técnico de Implementación (Grupos Odoo)

Para lograr estas restricciones en la base de datos de Odoo SaaS 19.2, se aplicó la siguiente configuración a través del ORM y sentencias seguras de Python:

1. **Seguridad de Ventas y CRM**: 
   - Se asignó a los usuarios no-administradores el grupo `sales_team.group_sale_salesman_all_leads` (*Comercial: Mostrar todas las fuentes*).
   - Se retiró el grupo `sales_team.group_sale_manager` para impedir la supresión de cotizaciones y el historial de leads.
2. **Seguridad de Datos (Exportar)**: 
   - Se desasoció el rol `base.group_allow_export` de todos los perfiles de Marketing, Ventas y Coordinación para bloquear la descarga de datos a Excel.
3. **Catálogo de Productos**: 
   - Se removió el rol `product.group_product_manager` para asegurar que no puedan modificarse las tarifas por error o descuido en los productos base.
