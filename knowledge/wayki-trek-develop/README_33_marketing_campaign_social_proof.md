# WTK - Campaña de Marketing: Prueba Social y Acompañamiento

## Descripción General

Esta campaña de marketing automatizada está diseñada para el CRM de **Wayki Trek** dentro del módulo nativo de **"Automatización de Marketing"** de Odoo Enterprise.

Su objetivo es **retener y convertir leads que ya tienen una propuesta económica en sus manos** (etapa *"Negociación / Cotización"*) pero que aún no han tomado la decisión de reservar. En lugar de presionar con descuentos, la campaña genera confianza a través de testimonios reales y contenido de valor.

---

## El Problema que Resuelve

Un lead que llega a la etapa de *"Negociación / Cotización"* ya mostró interés. El mayor riesgo en esta etapa es el **silencio y la inercia**: el cliente pide la cotización, la ve, y simplemente no responde porque le generan dudas sobre la experiencia real (dificultad, calidad del servicio, seguridad, etc.).

Sin esta automatización, ese lead se queda en la columna indefinidamente hasta que un vendedor lo recuerda (o no).

---

## ¿Cómo Funciona? (Flujo Paso a Paso)

```
Lead entra a "Negociación / Cotización" (ID 6)
              ↓
    Odoo lo registra como Participante
    en la Campaña de Prueba Social
              ↓
      Espera 1 hora (modo prueba)
        o 2 días (modo producción)
              ↓
   Se ejecuta la Acción de Servidor:
    "WTK - Mkt Campaign: Enviar Social Proof WhatsApp"
              ↓
     ¿El cliente tiene un canal de WhatsApp?
        ↙ SÍ               NO ↘
Se envía el mensaje          Solo se registra
de Prueba Social por         la nota interna
WhatsApp al cliente          en el Chatter
        ↓                       ↓
Se registra una nota interna en el Chatter del Lead CRM:
"Campaña de Marketing Activa: Se envió el mensaje de Prueba Social por WhatsApp."
```

---

## El Mensaje de WhatsApp Enviado

El siguiente mensaje se envía directamente al canal de conversación de WhatsApp del cliente dentro de Odoo:

> **"¡Hola [Nombre del Cliente]! Sé que estás planeando tu aventura a [Nombre del Lead/Destino]. Quería compartirte este breve video de 1 minuto sobre cómo es un día de campamento con nuestro equipo de Wayki Trek: https://youtu.be/video_waykitrek. Además, más del 98% de nuestros caminantes nos califican con 5 estrellas en TripAdvisor. ¿Tienes alguna duda sobre la preparación física o el equipo necesario? Estoy aquí para ayudarte."**

> [!IMPORTANT]
> El enlace `https://youtu.be/video_waykitrek` es un **placeholder**. Antes de activar la campaña en producción, debes reemplazarlo con el enlace real del video de Wayki Trek en el código Python de la acción de servidor.

---

## Componentes Técnicos en Odoo

| Componente | Tipo Odoo | ID | Nombre en Odoo |
|---|---|---|---|
| **Script de instalación** | Archivo Python local | — | `33_setup_negotiation_marketing_campaign.py` |
| **Campaña madre** | `marketing.campaign` | **2** | WTK - Campaña: Prueba Social y Acompañamiento |
| **Actividad del flujo** | `marketing.activity` | **4** | WTK - Enviar Social Proof WhatsApp |
| **Acción de servidor** | `ir.actions.server` | **625** | WTK - Mkt Campaign: Enviar Social Proof WhatsApp |

### Parámetros de la Actividad

| Parámetro | Modo Prueba | Modo Producción |
|---|---|---|
| **Retraso** | 1 hora | 2 días |
| **Intervalo** | `hours` | `days` |
| **Tipo de disparador** | Al inicio del flujo (`begin`) | Al inicio del flujo (`begin`) |

> [!NOTE]
> El módulo de "Automatización de Marketing" de Odoo no admite la unidad de tiempo en "minutos". La unidad mínima disponible es **"horas"**. Por eso el modo prueba está configurado en 1 hora en lugar de 1 minuto.

---

## Filtro de Entrada a la Campaña

La campaña solo acepta como participantes a los leads que cumplan el siguiente criterio:

```python
[("stage_id", "=", 6)]  # Negociación / Cotización
```

Esto garantiza que ningún lead de otras etapas del CRM sea incluido en el flujo de mensajes.

---

## ¿Cómo Activar la Campaña?

La campaña fue creada en estado **Borrador (Draft)** para permitir una revisión visual antes de activarla.

1. Ingresa a Odoo y abre la aplicación **Automatización de Marketing**.
2. Localiza la campaña **"WTK - Campaña: Prueba Social y Acompañamiento"**.
3. Verás el flujograma visual mostrando la actividad programada.
4. Haz clic en el botón **"Iniciar" (Start)** en la parte superior.
5. A partir de ese momento, cada lead que entre (o ya esté) en la etapa de *"Negociación / Cotización"* se convertirá automáticamente en un participante del flujo.

---

## ¿Cómo Pasar a Modo Producción (2 Días)?

1. Abre el script de instalación:
   ```
   knowledge/wayki-trek-develop/33_setup_negotiation_marketing_campaign.py
   ```
2. Modifica la variable de configuración en la línea 19:
   ```python
   # Antes (Prueba)
   TEST_MODE = True

   # Después (Producción)
   TEST_MODE = False
   ```
3. Actualiza el enlace del video de Wayki Trek en el bloque `python_code` del script.
4. Ejecuta el script desde la terminal del proyecto:
   ```bash
   .venv/bin/python knowledge/wayki-trek-develop/33_setup_negotiation_marketing_campaign.py
   ```
   *El script detectará automáticamente los registros existentes (ID 2, 4, 625) y solo actualizará el retraso a 2 días sin crear duplicados.*

---

## Comportamiento Inteligente

La acción de servidor tiene un comportamiento adaptativo según el estado de WhatsApp del lead:

| Situación | Comportamiento |
|---|---|
| El cliente **tiene canal de WhatsApp** en Odoo | Envía el mensaje de Prueba Social por WhatsApp **+** registra nota interna en el Chatter |
| El cliente **no tiene canal de WhatsApp** aún | Solo registra la nota interna en el Chatter para que el vendedor lo contacte de forma manual |

---

## Cómo Monitorear los Resultados en Odoo

Una vez activa la campaña, Odoo muestra de forma automática las siguientes métricas en la interfaz gráfica:

- **Total de participantes:** Cuántos leads han entrado al flujo.
- **Participantes en curso:** Leads que aún están esperando que se cumpla el plazo de tiempo.
- **Participantes completados:** Leads que ya recibieron la acción.
- **Ratio de éxito:** Porcentaje de ejecuciones correctas vs fallidas.

---

## Archivos Relacionados

| Archivo | Descripción |
|---|---|
| [`33_setup_negotiation_marketing_campaign.py`](./33_setup_negotiation_marketing_campaign.py) | Script de instalación y configuración de la campaña |
| [`32_setup_lead_whatsapp_automation.py`](./32_setup_lead_whatsapp_automation.py) | Automatización paralela para leads en la etapa "Primer mensaje" |
