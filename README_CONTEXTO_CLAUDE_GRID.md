# 📖 README: Contexto Maestro, Arquitectura y Estrategia B2B
### Proyecto: Mercado Pago Point Smart 4G & Funnel Comercial Quintana Roo
> **Destinatario:** Claude (Grid / Agents Hub / Mercado Libre)  
> **Usuario:** Antonio Gutiérrez ("Tono") — *Account Executive B2B, Mercado Pago*  
> **Territorio:** Quintana Roo (Cancún, Playa del Carmen, Tulum, Chetumal, Cozumel) + Expansión Nacional (Top 15 Plazas Desatendidas)

---

## 🎯 1. ¿Quién es el Usuario y Cuál es su Objetivo?

Antonio es **Account Executive B2B en Mercado Pago**. Su misión comercial es la prospección, calificación, negociación y cierre de comercios medianos y grandes (MQLs/SQLs con facturación mensual de **\$50,000 MXN hasta más de \$2.5M+ MXN**) para adoptar el ecosistema de cobro de Mercado Pago:
* **Terminales Físicas:** Point Smart 4G (chip multi-operador gratis, impresión térmica, batería de larga duración).
* **Soluciones Digitales:** Cobro con QR, Link de Pago, Pasarela Web.
* **Valores Agregados Clave:** **Liquidación inmediata en fin de semana** (a diferencia de la banca tradicional que retiene el dinero hasta el martes), comisiones altamente competitivas y **Meses Sin Intereses (3 a 24 MSI)**.

**Filosofía Operativa:**
Antonio **NO hace cambaceo tradicional a pie bajo el sol de 38°C** de manera desordenada. Su modelo es **Prospección Quirúrgica Híbrida/Digital**:
1. Extrae y enriquece comercios de alto poder adquisitivo con decisores en WhatsApp o teléfono directo.
2. Abre conversación con un **Gancho Comercial Personalizado (Hook)** atacando el dolor del banco actual (caídas de terminales, retención de dinero o comisiones abusivas).
3. Cierra o agenda videollamada/visita de alto impacto. La terminal se entrega de inmediato o por paquetería Full de Mercado Libre en 24 a 48 horas.

---

## 🏛️ 2. Arquitectura Técnica del Ecosistema

El sistema comercial de Antonio se compone de 3 capas interconectadas:

```
┌────────────────────────────────────────────────────────┐
│  1. FRONTEND: Dashboard Táctico HTML5 / JS             │
│     (tono-dashboard-mercadopago.html)                  │
│     - Mesa de trabajo táctica (Cartera Activa)         │
│     - Tacómetro comercial SVG y Métricas en vivo        │
│     - Kanban de 5 etapas                               │
│     - Integración con Grid.sheets SDK en intranet MeLi │
└──────────────────────────┬─────────────────────────────┘
                           │ Lectura / Escritura
                           ▼
┌────────────────────────────────────────────────────────┐
│  2. BASE DE DATOS: Google Sheets (Drive Corporativo)   │
│     ID de la Hoja: [VINCULADA EN DRIVE MELI]           │
│     - "Base_Maestra": 644 comercios en Quintana Roo    │
│     - "Bitacora_Actividad": Historial de llamadas/WA   │
│     - "Snapshot_Cartera": Estado de recuperación cloud │
│     - "Candidatos_Staging": Buzón de nuevos ingresos   │
└──────────────────────────▲─────────────────────────────┘
                           │ Ingesta Automática
                           ▼
┌────────────────────────────────────────────────────────┐
│  3. LEAD ENGINE: Motores de Ingesta Diaria             │
│     - DENUE (INEGI): Negocios de reciente apertura     │
│     - Meta Ad Library: Negocios pagando pauta en IG/FB │
│     - Apify / Places: Scrapers de las 8 verticales oro │
└────────────────────────────────────────────────────────┘
```

---

## 📊 3. Esquema Exacto de la Base de Datos (Google Sheets)

Para cualquier script o llamada de Grid, este es el contrato de datos obligatorio:

### Pestaña 1: `Base_Maestra` (Acordeón de 644 comercios)
| Columna | Índice | Campo | Descripción | Ejemplo / Valores |
| :---: | :---: | :--- | :--- | :--- |
| **A** | 1 | `id` | ID único permanente | `MP-QR-0001` |
| **B** | 2 | `name` | Nombre comercial del negocio | `Spa & Wellness Cancún` |
| **C** | 3 | `industry` | Giro comercial | `Salud y Belleza / Spa` |
| **D** | 4 | `city` | Ciudad | `Cancún`, `Playa del Carmen`, `Tulum` |
| **E** | 5 | `state` | Estado | `Quintana Roo` |
| **F** | 6 | `address` | Dirección física | `Av. Bonampak SM 4A` |
| **G** | 7 | `contact` | Decisor / Dueño / Encargado | `Dra. Elena Ramos (Dueña)` |
| **H** | 8 | `phone` | Teléfono normalizado (10 dígitos) | `9981234567` |
| **I** | 9 | `email` | Correo electrónico | `contacto@spawellness.com` |
| **J** | 10 | `website` | Sitio Web o Instagram | `https://instagram.com/spa...` |
| **K** | 11 | `rating` | Calificación Google Maps (1.0 - 5.0) | `4.9` |
| **L** | 12 | `reviews` | Número de reseñas públicas | `142` |
| **M** | 13 | `tpv` | Facturación mensual estimada | `650000` |
| **N** | 14 | `hook` | Gancho de apertura comercial | *"Veo que atienden extranjeros con tarjeta..."* |
| **O** | 15 | `pain` | Dolor principal detectado | *"Su banco les retiene dinero el fin de semana"* |
| **P** | 16 | `status` | Estatus operativo | `DISPONIBLE`, `EN_CARTERA`, `CRM MP OK`, `SUCURSAL_VINCULADA`, `DESCARTADO` |
| **Q** | 17 | `stage` | Etapa en el pipeline | `calificacion`, `negociacion`, `closing_deal`, `ganado`, `perdido` |
| **R** | 18 | `touches` | Contador de toques/llamadas | `3` |
| **S** | 19 | `lastNote` | Texto de la última interacción | *"Llamada conectada, le mando cotización por WA"* |
| **T** | 20 | `updatedAt` | Fecha última modificación | `2026-11-10T14:30:00.000Z` |

### Pestaña 2: `Bitacora_Actividad` (Audit Log Append-Only)
Registra cada llamada, WhatsApp, correo o visita en tiempo real:
* `Col A`: Timestamp ISO.
* `Col B`: ID Comercio (`MP-QR-XXXX`).
* `Col C`: Nombre Comercio.
* `Col D`: Ciudad.
* `Col E`: Canal (`Llamada`, `WhatsApp`, `Correo`, `Visita`).
* `Col F`: Resultado (`SÍ / Aceptó`, `NO / Rechazó`, `No Contestó / Buzón`, `Visita Agendada`).
* `Col G`: Etapa Resultante (`calificacion`, `negociacion`, etc.).
* `Col H`: Gancho comercial usado.
* `Col I`: Notas del contacto.
* `Col J`: TPV Estimado.
* `Col K`: Usuario (`Antonio Gutiérrez`).

### Pestaña 3: `Candidatos_Staging` (Buzón de Nuevos Prospectos - REGLA DE ORO)
> [!IMPORTANT]
> **Ningún script automatizado debe escribir directamente en `Base_Maestra`.**  
> Todo negocio extraído por scrapers, DENUE o Meta Ads debe caer primero en `Candidatos_Staging`.  
> Antes de promoverlo a `Base_Maestra`, se ejecuta el filtro anti-duplicados (comparando los 10 dígitos de `phone` o similitud de nombre).

---

## 📈 4. Reglas de Negocio y Metas del Dashboard (KPIs)

El dashboard tiene un selector temporal continuo de **Lunes a Domingo** (las metas no se rompen si el mes termina a mitad de semana):
1. **Vista "Hoy":**
   * **Nuevos Prospectos Jalados:** Meta = **8 al día**. Si no ha jalado ninguno hoy, muestra `0 / 8 min`.
   * **Toques Comerciales:** Meta = **15 toques al día** (llamadas, mensajes, visitas).
2. **Vista "Esta Semana":**
   * **Nuevos Prospectos:** Meta = **40 a la semana** (5 días hábiles $\times$ 8).
   * **Toques Comerciales:** Meta = **75 toques a la semana**.
3. **Vista "Este Mes":**
   * Meta proporcional a los días hábiles del mes en curso.
   * **Cierres Ganados MP:** Meta = **2 cierres de alto volumen al mes**.

### Etapas del Funnel (Kanban Stages):
1. `calificacion`: **1. Calificación** (Primer contacto, validación de facturación >\$50k y decisor).
2. `negociacion`: **2. Negociación** (Envío de propuesta económica, comparador financiero, comisiones).
3. `closing_deal`: **3. Closing Deal** (Aceptación verbal, recolección de documentos fiscales, alta de terminales).
4. `ganado`: **4. Cierres Ganados MP ★** (Terminales entregadas y procesando transacciones).
5. `perdido`: **Descarte / Perdido** (Comercio no califica o rechazó propuesta).

---

## 💎 5. Las 8 Verticales de Oro en Quintana Roo

Estas son las industrias con mayor tasa de conversión y ticket promedio en Cancún, Playa del Carmen y Tulum:
1. **Renta de Yates, Catamaranes y Tours Náuticos:** Tickets de \$8,000 a \$60,000 MXN. Clientes extranjeros, urgencia de terminal 4G en muelle.
2. **Escuelas y Centros de Buceo PADI:** Tickets de \$4,000 a \$25,000 MXN. Dólares, liquidación en fin de semana.
3. **Beach Clubs, Rooftops y Restaurantes Fine Dining:** Tickets de \$2,500 a \$15,000 MXN. Caídas de bancos tradicionales en fin de semana.
4. **Talleres Mecánicos y Agencias de Renta (Autos/Motos/RZR):** Tickets de \$5,000 a \$35,000 MXN. Clave: 3 a 12 MSI.
5. **Mobiliario, Albercas y Cancelería:** Boom inmobiliario y remodelación de Airbnbs. Tickets de \$15,000 a \$120,000 MXN.
6. **Eventos, Bodas Destino y Fotografía Profesional:** Tickets de \$15,000 a \$80,000 MXN.
7. **Joyerías, Galerías de Arte y Concept Stores:** Gran volumen de Visa/Mastercard/Amex extranjeras.
8. **Spas Médicos, Clínicas Dentales y Cirugía Plástica:** Turismo médico de alto valor.

---

## 🗺️ 6. El Top 15 de Plazas Desatendidas (Venta Remota Digital)

Antonio no solo vende en Quintana Roo; cuenta con un archivo nacional de más de **3,500 comercios calificados** en las 15 plazas más desatendidas por la banca tradicional en México:
1. **Baja California Sur:** Los Cabos (Cabo San Lucas / San José), La Paz.
2. **Sonora:** Hermosillo, Puerto Peñasco, Nogales, Cd. Obregón.
3. **Sinaloa:** Culiacán, Mazatlán, Los Mochis.
4. **Chihuahua:** Cd. Juárez, Chihuahua Capital, Delicias.
5. **Coahuila:** Torreón, Saltillo, Monclova, Piedras Negras.
6. **Nayarit:** Bahía de Banderas (Punta Mita, Nuevo Nayarit), Tepic.
7. **Durango:** Durango Capital, Gómez Palacio.
8. **Tamaulipas:** Tampico, Reynosa, Matamoros, Nuevo Laredo.
9. **San Luis Potosí:** San Luis Potosí Capital, Ciudad Valles.
10. **Michoacán:** Morelia, Uruapan, Zamora.
11. **Colima:** Manzanillo, Colima Capital.
12. **Aguascalientes:** Aguascalientes Capital.
13. **Zacatecas:** Zacatecas Capital, Fresnillo.
14. **Hidalgo:** Pachuca, Tizayuca.
15. **Campeche:** Ciudad del Carmen, Campeche Capital.

*Estrategia:* Venta 100% digital vía WhatsApp/llamada y envío inmediato de la Point Smart por paquetería de Mercado Libre en 24 a 48 horas.

---

## 🛠️ 7. Instrucciones para Claude en Grid

1. **Integración con Grid.sheets:**
   * Utilizar `<script src="/d/_assets/grid-sdk.js"></script>` y `Grid.configure({ docId })`.
   * Reemplazar las llamadas directas `fetch(GOOGLE_SHEET_API_URL)` por los métodos asíncronos nativos `Grid.sheets.get(...)` y `Grid.sheets.set(...)`.
2. **Preservación Total de Datos:**
   * No modificar los nombres de las columnas ni las fórmulas de `Base_Maestra`.
   * Respetar los IDs existentes (`MP-QR-0001` al `MP-QR-0644`).
3. **Ingesta DENUE / Meta Ads:**
   * Crear la pestaña `Candidatos_Staging` para recibir los nuevos registros diarios.
   * Implementar la función de deduplicación que compare el teléfono normalizado a 10 dígitos antes de insertar un nuevo comercio en `Base_Maestra`.
