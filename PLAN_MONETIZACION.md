# Plan de Implementación: Monetización SaaS del Chatbot

**Disponibilidad:** 30 horas / mes (~7.5 hrs/semana)
**Duración Estimada (MVP Comercial):** 5 Meses (150 horas totales)
**Objetivo:** Transformar el script local del chatbot en una plataforma SaaS (Software as a Service) multi-cliente.

---

## Mes 1: Fundamentos SaaS y Multi-tenencia (30 horas)
**Objetivo:** Cambiar de un modelo "un solo usuario" a una arquitectura que soporte múltiples clientes (negocios) simultáneamente.

*   **Semana 1-2 (15 hrs): Migración a Base de Datos.**
    *   Reemplazar el uso de `knowledge_base.json` por una base de datos relacional (recomendado: PostgreSQL, pero SQLite es válido para empezar).
    *   Diseñar esquema de base de datos: Tablas para `Clientes`, `Instancias_WhatsApp` (credenciales Green-API), y `Respuestas_FAQ`.
*   **Semana 3-4 (15 hrs): Refactorización del Código.**
    *   Modificar `run.py`, `routes.py` y `engine.py` para que el sistema identifique a qué cliente pertenece el mensaje entrante (usando el webhook de Green-API) y consulte la base de datos correspondiente.
*   **📦 Entregable:** El código base puede manejar al menos 2 números de WhatsApp distintos simultáneamente, con respuestas diferentes para cada uno, leyendo todo desde una base de datos.

---

## Mes 2: Panel de Administración Web MVP (30 horas)
**Objetivo:** Proveer a los clientes una interfaz gráfica para que gestionen su bot sin ver código.

*   **Semana 1 (10 hrs): Autenticación y Setup.**
    *   Configurar un framework web (Flask o FastAPI) para servir el frontend.
    *   Crear sistema de registro e inicio de sesión para los dueños de negocios.
*   **Semana 2-3 (15 hrs): CRUD de Base de Conocimientos.**
    *   Desarrollar vistas/pantallas para que el cliente pueda Agregar, Editar o Borrar preguntas y respuestas.
*   **Semana 4 (5 hrs): Configuración de Instancia.**
    *   Pantalla donde el cliente ingresa y guarda sus credenciales de Green-API (`ID_INSTANCE` y `API_TOKEN_INSTANCE`).
*   **📦 Entregable:** Un portal web funcional donde el dueño de un negocio puede loguearse y personalizar el comportamiento de su bot en tiempo real.

---

## Mes 3: Integración de IA Generativa - Nivel Premium (30 horas)
**Objetivo:** Reemplazar las respuestas rígidas por conversaciones fluidas y naturales.

*   **Semana 1-2 (15 hrs): Integración de LLM (OpenAI / Gemini).**
    *   Conectar el motor del bot con la API de OpenAI (GPT-4o-mini es económico) o Google Gemini.
    *   Implementar un sistema RAG (Retrieval-Augmented Generation): Cuando llega un mensaje, buscar la información en la base de datos y dársela al LLM para que redacte una respuesta natural.
*   **Semana 3-4 (15 hrs): Memoria de Conversación.**
    *   Implementar persistencia temporal de chats en la base de datos para que el bot recuerde lo dicho hace 5 minutos (manejo de contexto multi-turno).
*   **📦 Entregable:** El bot ya no responde como "robot", sino que puede mantener una charla coherente utilizando *exclusivamente* la información configurada por el cliente.

---

## Mes 4: Handoff Humano y Gestión de Inbox (30 horas)
**Objetivo:** Permitir a los clientes tomar el control manual cuando la IA no puede resolver la duda.

*   **Semana 1-2 (15 hrs): Interfaz de Chat (Inbox).**
    *   Añadir una pantalla al panel web que muestre las conversaciones en tiempo real.
*   **Semana 3-4 (15 hrs): Pausa de IA e Intervención.**
    *   Crear la lógica para que el bot pase a estado "Pausado" si el cliente web envía un mensaje manualmente a través del panel.
    *   Botón para "Transferir a humano" que el usuario de WhatsApp pueda presionar.
*   **📦 Entregable:** Un sistema híbrido. La IA atiende el 80% de las consultas repetitivas, pero los vendedores pueden intervenir desde el dashboard para cerrar ventas complejas.

---

## Mes 5: Producción, Despliegue y Monetización (30 horas)
**Objetivo:** Poner el producto en vivo en internet y preparar la pasarela de cobros.

*   **Semana 1-2 (15 hrs): Infraestructura y Docker.**
    *   Crear archivos `Dockerfile` y `docker-compose.yml` para empaquetar el backend, el frontend y la base de datos.
    *   Desplegar en un servidor VPS en la nube (ej. DigitalOcean, AWS EC2, o Render) y configurar un dominio con certificado SSL (HTTPS).
*   **Semana 3-4 (15 hrs): Pasarela de Pagos (Stripe).**
    *   Integrar Stripe Checkout.
    *   Lógica básica: Si la suscripción del cliente está inactiva/vencida, el webhook ignora los mensajes y no procesa respuestas.
*   **📦 Entregable:** La plataforma final publicada (`www.tu-chatbot.com`), lista para que un cliente real se registre, pague con tarjeta y conecte su WhatsApp.
