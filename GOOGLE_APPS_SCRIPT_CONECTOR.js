/**
 * ============================================================================
 * GOOGLE APPS SCRIPT - API BIDIRECCIONAL & ESPEJO EN TIEMPO REAL
 * Mercado Pago Point Smart CRM - Tono Dashboard
 * ============================================================================
 */

const SHEET_BASE = "Base_Maestra";
const SHEET_LOGS = "Bitacora_Actividad";

/**
 * ⚡ FUNCIÓN MÁGICA DE 1 CLIC:
 * Ejecuta esta función una sola vez para que Google Sheets cree las dos pestañas
 * y descargue automáticamente los 644 comercios con diseño y colores sin subir archivos.
 */
function INICIALIZAR_HOJA_AUTOMATICA() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Crear o limpiar Base_Maestra
  let baseSheet = ss.getSheetByName(SHEET_BASE);
  if (!baseSheet) {
    baseSheet = ss.insertSheet(SHEET_BASE, 0);
  } else {
    baseSheet.clear();
  }

  // 2. Crear o verificar Bitacora_Actividad
  let logSheet = ss.getSheetByName(SHEET_LOGS);
  if (!logSheet) {
    logSheet = ss.insertSheet(SHEET_LOGS, 1);
  }

  // 3. Encabezados Base_Maestra
  const headers1 = [
    "ID", "Nombre Comercio", "Giro / Industria", "Ciudad", "Estado", 
    "Dirección", "Contacto", "Teléfono", "Email", "Sitio Web", 
    "Rating Google", "Reseñas", "TPV Mensual Estimado", "Gancho Comercial", 
    "Dolor Principal", "Estatus", "Etapa Comercial", "Toques", "Última Nota", "Fecha Actualización"
  ];
  baseSheet.appendRow(headers1);
  baseSheet.getRange(1, 1, 1, headers1.length)
    .setBackground("#0A2540")
    .setFontColor("#FFFFFF")
    .setFontWeight("bold")
    .setFontFamily("Arial");

  // 4. Encabezados Bitacora_Actividad
  const headers2 = [
    "Timestamp", "ID Comercio", "Nombre Comercio", "Ciudad", "Canal (Llamada/WA/Visita)",
    "Resultado (SÍ / NO / No Contestó)", "Etapa Resultante", "Gancho Comercial Utilizado",
    "Notas de la Interacción", "TPV Estimado", "Usuario"
  ];
  if (logSheet.getLastRow() === 0) {
    logSheet.appendRow(headers2);
    logSheet.getRange(1, 1, 1, headers2.length)
      .setBackground("#00A650")
      .setFontColor("#FFFFFF")
      .setFontWeight("bold")
      .setFontFamily("Arial");
  }

  // 5. Descargar los 644 comercios en crudo desde GitHub en 0.5 segundos
  const url = "https://raw.githubusercontent.com/agutierrez11/tono-dashboard-leads-ratio/main/leads_644.json";
  const res = UrlFetchApp.fetch(url);
  const leads = JSON.parse(res.getContentText());

  const rows = leads.map((m, idx) => [
    m.id || ("MP-QR-" + String(idx + 1).padStart(4, "0")),
    m.name || "",
    m.industry || "",
    m.city || "Cancún",
    "Quintana Roo",
    m.address || "",
    m.contact || "Encargado / Dueño",
    String(m.phone || ""),
    m.email || "",
    m.website || "",
    m.rating || 5.0,
    m.reviews || 0,
    m.tpv || 500000,
    m.hook || "",
    m.pain || "",
    "DISPONIBLE",
    "1. Calificación",
    0,
    "",
    ""
  ]);

  // Escribir los 644 registros de un solo golpe (toma 1 segundo)
  baseSheet.getRange(2, 1, rows.length, headers1.length).setValues(rows);
  baseSheet.setFrozenRows(1);
  logSheet.setFrozenRows(1);

  // Borrar 'Hoja 1' si quedó sobrando
  const extraSheet = ss.getSheetByName("Hoja 1");
  if (extraSheet && ss.getSheets().length > 1) {
    ss.deleteSheet(extraSheet);
  }
}

/**
 * LECTURA EN VIVO: El Tablero de GitHub consulta esta función al abrir
 */
function doGet(e) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(SHEET_BASE) || ss.getSheets()[0];
    const data = sheet.getDataRange().getValues();
    
    if (data.length <= 1) {
      return jsonResponse({ success: true, count: 0, leads: [] });
    }

    const leads = [];

    for (let i = 1; i < data.length; i++) {
      const row = data[i];
      if (!row[0] && !row[1]) continue;
      
      leads.push({
        id: String(row[0] || ""),
        name: String(row[1] || ""),
        industry: String(row[2] || ""),
        city: String(row[3] || ""),
        state: String(row[4] || "Quintana Roo"),
        address: String(row[5] || ""),
        contact: String(row[6] || "Encargado / Dueño"),
        phone: String(row[7] || ""),
        email: String(row[8] || ""),
        website: String(row[9] || ""),
        rating: Number(row[10]) || 5.0,
        reviews: Number(row[11]) || 0,
        tpv: Number(row[12]) || 500000,
        hook: String(row[13] || ""),
        pain: String(row[14] || ""),
        status: String(row[15] || "DISPONIBLE"),
        stage: String(row[16] || "calificacion"),
        touches: Number(row[17]) || 0,
        lastNote: String(row[18] || ""),
        updatedAt: String(row[19] || "")
      });
    }

    let activeDealsSnapshot = [];
    try {
      const snapSheet = ss.getSheetByName("Snapshot_Cartera");
      if (snapSheet) {
        const rawJson = snapSheet.getRange("A2").getValue();
        if (rawJson) {
          activeDealsSnapshot = JSON.parse(rawJson);
        }
      }
    } catch (e) {}

    // Detección automática de métricas de Campañas Masivas YAMM
    let yammSent = 0, yammOpened = 0, yammClicked = 0, yammResponded = 0;
    try {
      const headerRow = data[0].map(h => String(h || "").toLowerCase());
      const mergeColIdx = headerRow.findIndex(h => h.includes("merge status") || h.includes("yamm"));
      if (mergeColIdx !== -1) {
        for (let i = 1; i < data.length; i++) {
          const val = String(data[i][mergeColIdx] || "").toUpperCase();
          if (val.includes("EMAIL_SENT") || val.includes("ENVIADO")) yammSent++;
          if (val.includes("EMAIL_OPENED") || val.includes("ABIERTO")) { yammSent++; yammOpened++; }
          if (val.includes("EMAIL_CLICKED") || val.includes("CLIC")) { yammSent++; yammOpened++; yammClicked++; }
          if (val.includes("RESPONDED") || val.includes("RESPONDI")) yammResponded++;
        }
      }
    } catch (e) {}

    return jsonResponse({
      success: true,
      count: leads.length,
      leads: leads,
      activeDealsSnapshot: activeDealsSnapshot,
      yammStats: {
        sent: yammSent,
        opened: yammOpened,
        clicked: yammClicked,
        responded: yammResponded,
        openRate: yammSent > 0 ? Math.round((yammOpened / yammSent) * 100) + "%" : "—",
        clickRate: yammSent > 0 ? Math.round((yammClicked / yammSent) * 100) + "%" : "—"
      }
    });
  } catch (err) {
    return jsonResponse({ success: false, error: err.toString() });
  }
}

/**
 * ESCRITURA EN VIVO: El Tablero manda las llamadas, toques y cambios de etapa
 */
function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    const action = body.action;
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    
    // 1. REGISTRAR ACTIVIDAD EN BITÁCORA
    if (action === "log_touch") {
      const logSheet = ss.getSheetByName(SHEET_LOGS);
      if (logSheet) {
        logSheet.appendRow([
          new Date().toISOString(),
          body.dealId || "",
          body.dealName || "",
          body.city || "",
          body.channel || "Llamada",
          body.result || "N/A",
          body.stage || "",
          body.hook || "",
          body.notes || "",
          body.tpv || 500000,
          "Antonio Gutiérrez"
        ]);
      }
      
      updateBaseMaestraRow(ss, body.dealId, {
        touches: body.touches,
        stage: body.stage,
        status: body.status || "EN_PROCESO",
        lastNote: body.notes
      });

      return jsonResponse({ success: true, message: "Touch logged & deal mirrored" });
    }

    // 2. ACTUALIZAR ESTADO DE COMERCIO
    if (action === "update_deal") {
      updateBaseMaestraRow(ss, body.dealId, body.updates);
      return jsonResponse({ success: true, message: "Deal updated" });
    }

    // 3. JALAR LOTE (Marca en el Sheet como EN_CARTERA y pinta la fila en verde)
    if (action === "pull_batch") {
      const ids = body.dealIds || [];
      const baseSheet = ss.getSheetByName(SHEET_BASE);
      if (baseSheet && ids.length > 0) {
        const idSet = new Set(ids);
        const data = baseSheet.getDataRange().getValues();
        for (let i = 1; i < data.length; i++) {
          if (idSet.has(String(data[i][0]))) {
            baseSheet.getRange(i + 1, 16).setValue("EN_CARTERA");
            baseSheet.getRange(i + 1, 20).setValue(new Date().toLocaleDateString("es-MX"));
            baseSheet.getRange(i + 1, 1, 1, 16).setBackground("#E8F5E9");
          }
        }
      }
      return jsonResponse({ success: true, message: "Batch marked in Sheet" });
    }

    // 4. GUARDAR SNAPSHOT DE RECUPERACIÓN ANTE BORRADO DE COOKIES
    if (action === "save_snapshot") {
      let snapSheet = ss.getSheetByName("Snapshot_Cartera");
      if (!snapSheet) {
        snapSheet = ss.insertSheet("Snapshot_Cartera");
        try { snapSheet.hideSheet(); } catch (e) {}
      }
      snapSheet.getRange("A1").setValue(new Date().toISOString());
      snapSheet.getRange("A2").setValue(JSON.stringify(body.activeDeals || []));
      return jsonResponse({ success: true, message: "Cloud snapshot saved" });
    }

    return jsonResponse({ success: false, error: "Acción no reconocida" });
  } catch (err) {
    return jsonResponse({ success: false, error: err.toString() });
  }
}

function updateBaseMaestraRow(ss, dealId, updates) {
  if (!dealId || !updates) return;
  const sheet = ss.getSheetByName(SHEET_BASE);
  if (!sheet) return;
  
  const data = sheet.getDataRange().getValues();
  for (let i = 1; i < data.length; i++) {
    if (String(data[i][0]) === String(dealId)) {
      const rowNum = i + 1;
      if (updates.status) sheet.getRange(rowNum, 16).setValue(updates.status);
      if (updates.stage) sheet.getRange(rowNum, 17).setValue(updates.stage);
      if (updates.touches !== undefined) sheet.getRange(rowNum, 18).setValue(updates.touches);
      if (updates.lastNote !== undefined) sheet.getRange(rowNum, 19).setValue(updates.lastNote);
      sheet.getRange(rowNum, 20).setValue(new Date().toLocaleDateString("es-MX"));
      
      if (updates.status === "GANADO") {
        sheet.getRange(rowNum, 1, 1, 19).setBackground("#C8E6C9");
      } else if (updates.status === "DESCARTADO" || updates.status === "PERDIDO") {
        sheet.getRange(rowNum, 1, 1, 19).setBackground("#FFEBEE");
      } else if (updates.status === "DISPONIBLE") {
        sheet.getRange(rowNum, 1, 1, 19).setBackground("#FFFFFF");
      }
      break;
    }
  }
}

function jsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * 🤖 AUTOMATIZACIÓN DE RESPUESTAS DE CORREO:
 * Revisa en tu cuenta de Gmail si alguno de los comercios a los que se envió correo ha respondido.
 * Si detecta una respuesta, actualiza la columna Resultado en Bitacora_Actividad a "SÍ (Respondió Correo)"
 * y en Base_Maestra avanza el estatus a "EN_CONVERSACION" con etapa "2. Negociación".
 * 
 * Puedes ejecutarla manualmente o programarla como un 'Activador' (Trigger) que corra cada 1 hora.
 */
function REVISAR_RESPUESTAS_GMAIL() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const logSheet = ss.getSheetByName(SHEET_LOGS);
  const baseSheet = ss.getSheetByName(SHEET_BASE);
  if (!logSheet || !baseSheet) return;

  const logs = logSheet.getDataRange().getValues();
  const base = baseSheet.getDataRange().getValues();

  // Mapa de ID -> Email y Fila en Base_Maestra
  const leadMap = {};
  for (let i = 1; i < base.length; i++) {
    const id = String(base[i][0] || "").trim();
    const email = String(base[i][8] || "").trim().toLowerCase();
    if (id && email) {
      leadMap[id] = { email: email, row: i + 1, name: String(base[i][1] || "") };
    }
  }

  let updated = 0;
  for (let r = 1; r < logs.length; r++) {
    const channel = String(logs[r][4] || "").toLowerCase();
    const result = String(logs[r][5] || "");
    const dealId = String(logs[r][1] || "").trim();

    // Si es un correo enviado en espera
    if (channel.includes("correo") && (result.includes("Enviado") || result.includes("espera") || result.includes("No Contestó"))) {
      const leadInfo = leadMap[dealId];
      if (leadInfo && leadInfo.email) {
        // Buscar en Gmail si hay correos entrantes de esa dirección
        const query = "from:" + leadInfo.email + " to:me";
        const threads = GmailApp.search(query, 0, 5);
        if (threads && threads.length > 0) {
          const lastMsgDate = threads[0].getLastMessageDate();
          
          // Actualizar Bitácora
          logSheet.getRange(r + 1, 6).setValue("SÍ (Respondió Correo)");
          logSheet.getRange(r + 1, 6).setBackground("#C8E6C9");
          logSheet.getRange(r + 1, 9).setValue("Respondió en Gmail el " + lastMsgDate.toLocaleDateString("es-MX"));

          // Actualizar Base_Maestra
          baseSheet.getRange(leadInfo.row, 16).setValue("EN_CONVERSACION");
          baseSheet.getRange(leadInfo.row, 17).setValue("2. Negociación");
          baseSheet.getRange(leadInfo.row, 20).setValue(new Date().toLocaleDateString("es-MX"));
          baseSheet.getRange(leadInfo.row, 1, 1, 16).setBackground("#FFF9C4");
          updated++;
        }
      }
    }
  }
  Logger.log("Revisión completada. Respuestas detectadas: " + updated);
}

/**
 * ⚡ FUNCIÓN DE 1 CLIC: ACTUALIZAR LOS 181 CORREOS ENRIQUECIDOS
 * Ejecuta esta función en Apps Script para llenar la columna Email (columna 9)
 * en Base_Maestra con los 181 correos de GitHub sin borrar tus notas ni avances.
 */
function ACTUALIZAR_CORREOS_ENRIQUECIDOS() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(SHEET_BASE);
  if (!sheet) return;
  
  const url = "https://raw.githubusercontent.com/agutierrez11/tono-dashboard-leads-ratio/main/leads_644.json";
  const res = UrlFetchApp.fetch(url);
  const leads = JSON.parse(res.getContentText());
  const leadMap = {};
  leads.forEach(l => { 
    if (l.email && l.email.trim() && !l.email.includes("Sin correo")) {
      leadMap[l.id] = l.email.trim(); 
    }
  });

  const data = sheet.getDataRange().getValues();
  let updatedCount = 0;
  for (let i = 1; i < data.length; i++) {
    const id = String(data[i][0]).trim();
    if (leadMap[id]) {
      sheet.getRange(i + 1, 9).setValue(leadMap[id]);
      updatedCount++;
    }
  }
  Logger.log("Correos enriquecidos actualizados en Base_Maestra: " + updatedCount);
}
