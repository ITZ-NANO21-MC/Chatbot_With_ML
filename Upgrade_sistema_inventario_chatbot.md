## 🗂️ Plan: Chatbot de WhatsApp (Standalone)

**Objetivo:** Tener un chatbot funcional para automatización empresarial (facturación, consultas, etc.) **sin integración con inventario**.  
**Entregable final:** Bot que responde preguntas frecuentes y ejecuta acciones simples (ej. enviar factura, agendar cita).

| Fase | Tareas (días) | Entregable funcional | Cómo demostrarlo |
|------|---------------|----------------------|------------------|
| **Fase 0** (1 día) | • Tomar tu proyecto actual (Chatbot_With_ML) y crear repositorio nuevo.<br>• Actualizar dependencias y configurar entorno. | Código base listo para extender. | El bot responde el mensaje “/start” con un saludo. |
| **Fase 1: Estructura Modular** (2 días) | • Separar en carpetas: `handlers/`, `services/`, `utils/`.<br>• Crear archivo `config.py` con variables de entorno.<br>• Implementar logging centralizado. | Arquitectura limpia que permite agregar nuevos comandos fácilmente. | Ejecutar `pylint` (o similar) y ver que no hay errores de importación. |
| **Fase 2: Comandos Básicos** (2 días) | • Añadir comandos: `/stock` (responde “Próximamente”), `/precio`, `/contacto`, `/horario`.<br>• Responder con mensajes predefinidos. | El bot responde a 4 comandos con información estática. | Enviar `/contacto` y recibir “Teléfono: +58...”. |
| **Fase 3: Conversación con Menús** (3 días) | • Implementar estado de conversación (diccionario en memoria).<br>• Crear menú con opciones numéricas (1. Consultar stock, 2. Precios, 3. Hablar con humano).<br>• Guardar contexto del usuario (última interacción). | Flujo interactivo donde el usuario elige opciones y el bot responde coherentemente. | Enviar “Hola”, el bot ofrece menú; seleccionar “1” y obtener respuesta. |
| **Fase 4: Integración con Google Sheets (Base de Conocimiento)** (3 días) | • Usar Google Sheets API (gratuita) como base de datos de productos/precios.<br>• El bot lee la hoja pública y responde consultas de stock/precio reales. | El bot puede responder “¿Cuánto cuesta la pantalla de iPhone 12?” leyendo desde un spreadsheet. | Crear hoja con dos productos; preguntar por uno y obtener el precio correcto. |
| **Fase 5: Envío de Facturas / Mensajes Programados** (3 días) | • Añadir comando `/factura` que genere un PDF simple (usando `reportlab`) y lo envíe.<br>• Job diario que envíe recordatorios a usuarios activos. | El bot puede crear y enviar un archivo PDF por WhatsApp. | Solicitar `/factura` y recibir un documento adjunto. |
| **Fase 6: Manejo de Errores y Logs** (2 días) | • Capturar excepciones de API de WhatsApp y reintentar.<br>• Guardar logs de conversaciones en archivo rotativo.<br>• Añadir comando `/reporte` para dueño (envía logs por email). | Sistema robusto que no se cae ante errores de red. | Simular error de conexión; el bot lo registra y sigue funcionando. |
| **Fase 7: Despliegue como Servicio** (2 días) | • Escribir script `install.sh` que configure `systemd` (para Linux) o tarea programada (Windows).<br>• Documentar cómo mantenerlo corriendo 24/7. | El bot se inicia automáticamente al encender la PC del cliente. | Reiniciar la PC y verificar que el proceso está activo (`systemctl status chatbot`). |

**Tiempo total estimado:** 18 días laborables (~3-4 semanas).  
*Nota:* Este plan no incluye la integración con inventario; es el producto autónomo que puedes vender a cualquier PYME.

---

## 🧭 Cómo priorizar según tu cliente actual

| Situación | Orden recomendado | Tiempo hasta primer ingreso adicional |
|-----------|-------------------|--------------------------------------|
| Cliente quiere el inventario mejorado (sin chatbot) | Plan 1 → luego Plan 3 (si pide upgrade) | 2-3 semanas (Fase 1 y 2 del Plan 1) |
| Cliente quiere automatizar atención por WhatsApp primero | Plan 2 → luego Plan 3 | 1-2 semanas (Fase 2 del Plan 2) |
| Cliente quiere el sistema completo (inventario + chatbot) | Plan 1 (rápido) + Plan 3 (integral) | 1 mes (Plan 1 completo) |

---

## ✅ Próximas acciones concretas (para esta semana)

1. **Elige un plan** según la necesidad de tu cliente actual. Si ya le vendiste el inventario, empieza con **Plan 1, Fase 0 y Fase 1**.
2. **Crea el Gist de prueba** para el sistema de licencias (gratuito y te servirá para ambos planes).
3. **Configura el entorno de desarrollo** con variables de entorno separadas para inventario y chatbot.
