import os
import requests, json, time, os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

token = os.getenv("APIFY_API_TOKEN", "")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 24 Ultra-targeted "Carnita" queries: High Ticket, Social-First, Owner on WhatsApp
# Targeting: Clínicas Estéticas, Spas Médicos, Pilates Reformer, Boutiques Trendy, Hospitales Veterinarios
carnita_queries = [
    # Baja California Sur (Los Cabos & La Paz) - Turismo, Bienestar, Dólares
    "clinica estetica spa Cabo San Lucas BCS",
    "pilates reformer fitness studio Cabo San Lucas BCS",
    "boutique joyeria concept store San Jose del Cabo BCS",
    "clinica estetica spa La Paz BCS",
    "hospital veterinario 24 horas La Paz BCS",
    
    # Sinaloa (Culiacán & Mazatlán) - Alto poder adquisitivo en belleza, moda y gastronomía
    "clinica estetica dermatologia Culiacan Sinaloa",
    "pilates reformer fitness boutique Culiacan Sinaloa",
    "boutique ropa diseñador Culiacan Sinaloa",
    "spa clinica estetica Mazatlan Sinaloa",
    "restaurante bar gastro Mazatlan Sinaloa",
    "hospital veterinario Culiacan Sinaloa",
    
    # Sonora (Hermosillo & Puerto Peñasco) - Gran volumen en salud, fitness y moda
    "clinica estetica spa Hermosillo Sonora",
    "pilates reformer gimnasio boutique Hermosillo Sonora",
    "boutique ropa joyeria Hermosillo Sonora",
    "spa wellness salon Puerto Peñasco Sonora",
    "clinica dental implantes Puerto Peñasco Sonora",
    
    # Coahuila (Saltillo & Torreón) - Riqueza industrial y consumo premium
    "clinica estetica spa Torreon Coahuila",
    "pilates reformer fitness Torreon Coahuila",
    "boutique concept store Saltillo Coahuila",
    "clinica estetica dermatologia Saltillo Coahuila",
    
    # Chihuahua (Chihuahua Capital & Cd. Juárez) - Turismo médico y clínicas de alto ticket
    "clinica estetica cirugia plastica Chihuahua Chihuahua",
    "pilates reformer fitness Chihuahua Chihuahua",
    "clinica estetica dental Ciudad Juarez Chihuahua",
    "hospital veterinario Ciudad Juarez Chihuahua"
]

print(f"Total Carnita queries prepared: {len(carnita_queries)}")

# We cap maxCrawledPlaces at 600 places = exactly ~$2.40 USD (safe within $2.48 balance)
payload = {
    "searchStringsArray": carnita_queries,
    "maxCrawledPlaces": 600,
    "maxCrawledPlacesPerSearch": 25,
    "language": "es",
    "scrapeResponseFromOwnerText": False,
    "scrapeReviewsPersonalData": False,
    "reviewsSort": "newest",
    "maxReviews": 0,
    "maxImages": 0
}

actor_id = "compass~crawler-google-places"
url = f"https://api.apify.com/v2/acts/{actor_id}/runs"

print("Starting Apify Carnita Run...")
res = requests.post(url, headers=headers, json=payload)

if res.status_code in [200, 201]:
    run_data = res.json().get("data", {})
    run_id = run_data.get("id")
    dataset_id = run_data.get("defaultDatasetId")
    print(f"RUN LAUNCHED! Run ID: {run_id} | Dataset ID: {dataset_id}")
    
    # Monitor execution
    while True:
        time.sleep(15)
        check = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}", headers=headers).json().get("data", {})
        status = check.get("status")
        usage = check.get("usageTotalUsd", 0)
        
        # count items
        d_res = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}", headers=headers)
        count = d_res.json().get("data", {}).get("itemCount", 0) if d_res.status_code == 200 else 0
        
        print(f"[{time.strftime('%H:%M:%S')}] Status: {status} | Scraped: {count}/600 | Usage: ${usage:.4f} USD")
        if status in ["SUCCEEDED", "ABORTED", "TIMED-OUT", "FAILED"]:
            break
            
    # Download dataset items
    print("Downloading Carnita dataset items...")
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true&format=json"
    items = requests.get(dataset_url, headers=headers).json()
    print(f"Total downloaded: {len(items)} places!")
    
    # Process into high-converting sales format
    leads = []
    for idx, it in enumerate(items, 1):
        title = it.get("title") or "Sin Nombre"
        phone = it.get("phone") or "Consultar Instagram/Web"
        address = it.get("address") or ""
        city = it.get("city") or ""
        state = it.get("state") or ""
        rating = it.get("totalScore") or 0.0
        reviews = it.get("reviewsCount") or 0
        category = it.get("categoryName") or "Estilo de Vida / Salud"
        website = it.get("website") or it.get("url") or ""
        
        # Detect channel / niche
        cat_lower = category.lower() + " " + title.lower()
        if any(w in cat_lower for w in ["estetica", "spa", "dermatolog", "cirug", "skin", "dental"]):
            nicho = "Clínica Estética / Salud Premium"
            ticket = "Alto Ticket ($2,500 - $12,000 MXN)"
            tpv = "$400,000 - $1,100,000 MXN"
            pts = "2.0 a 2.5 pts (Calidad Máxima)"
            gancho_wa = f"Hola, vi su clínica en redes. Una pregunta para administración: ¿en sus paquetes y tratamientos ya tienen habilitados 3 y 6 MSI con terminal SmartPOS en mostrador, o todavía les retienen el dinero 48 hrs con el banco?"
        elif any(w in cat_lower for w in ["pilates", "gym", "fitness", "crossfit", "estudio"]):
            nicho = "Fitness Boutique / Wellness"
            ticket = "Membresías Recurrentes ($1,800 - $3,500 MXN)"
            tpv = "$250,000 - $650,000 MXN"
            pts = "1.5 a 2.0 pts (Calidad Alta)"
            gancho_wa = f"Hola buen día, vi su estudio de {title} en Instagram. Pregunta rápida de mostrador: ¿qué tasa de comisión les cobra su terminal actual para las membresías? Tenemos SmartPOS 4G al 1.65% sin renta de equipo. ¿A quién le comparto la comparativa?"
        elif any(w in cat_lower for w in ["veterinar", "pet", "animal"]):
            nicho = "Hospital Veterinario / Pet Care"
            ticket = "Medio-Alto ($1,000 - $6,000 MXN)"
            tpv = "$300,000 - $750,000 MXN"
            pts = "1.5 a 2.0 pts (Calidad Alta)"
            gancho_wa = f"Hola, una pregunta para gerencia de {title}: en cirugías y consultas nocturnas, ¿ya cuentan con terminal 4G de respaldo que no dependa de su internet local y liquide fondos al segundo?"
        else:
            nicho = "Boutique / Comercio Trendy"
            ticket = "Medio ($1,200 - $4,500 MXN)"
            tpv = "$200,000 - $500,000 MXN"
            pts = "1.5 pts (Calidad Sólida)"
            gancho_wa = f"Hola, felicidades por sus colecciones en Instagram. Pregunta rápida: para ventas en mostrador y pedidos por WhatsApp, ¿aceptan cobro con link y terminal con 3-6 MSI al 1.65% fijo?"
            
        leads.append({
            "ID_Lead": f"CARNITA-{idx:04d}",
            "Comercio": title,
            "Nicho_Vertical": nicho,
            "Plaza_Ciudad": f"{city}, {state}".strip(", "),
            "Telefono_WhatsApp": phone,
            "Instagram_SitioWeb": website,
            "Direccion": address,
            "Google_Rating": f"{rating} ★" if rating > 0 else "N/A",
            "Resenas": reviews,
            "Ticket_Promedio_Estimado": ticket,
            "TPV_Mensual_Estimado": tpv,
            "Puntos_Calidad_MP": pts,
            "Gancho_WhatsApp_Listo": gancho_wa
        })
        
    df_carnita = pd.DataFrame(leads)
    
    # Save CSV & Excel
    out_csv = r"C:\Users\Antonio\OneDrive\Escritorio\Mercado Pago Strategy\CARNITA_PROSPECCION_DIGITAL_LEADS.csv"
    out_xlsx = r"C:\Users\Antonio\OneDrive\Escritorio\Mercado Pago Strategy\CARNITA_PROSPECCION_DIGITAL_LEADS.xlsx"
    out_xlsx_local = r"c:\Users\Antonio\.gemini\antigravity-ide\scratch\paymind-growth-engine\CARNITA_PROSPECCION_DIGITAL_LEADS.xlsx"
    
    df_carnita.to_csv(out_csv, index=False, encoding='utf-8-sig')
    
    # Build styled Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Carnita Digital 2026"
    ws.views.sheetView[0].showGridLines = True
    
    # Header styling
    ws.merge_cells("A1:M1")
    t = ws["A1"]
    t.value = "CARNITA DIGITAL: PROSPECCIÓN SOCIAL-FIRST (CLÍNICAS, FITNESS BOUTIQUE & MODA)"
    t.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    t.fill = PatternFill(start_color="0B2545", end_color="0B2545", fill_type="solid")
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 34
    
    ws.merge_cells("A2:M2")
    s = ws["A2"]
    s.value = "Los Cabos • Culiacán • Mazatlán • Hermosillo • Torreón • Saltillo • Cd. Juárez | Con WhatsApp & Gancho de Apertura Listo"
    s.font = Font(name="Calibri", size=10, italic=True, color="64748B")
    s.fill = PatternFill(start_color="EBF2FA", end_color="EBF2FA", fill_type="solid")
    s.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20
    
    for c_idx, col_name in enumerate(df_carnita.columns, 1):
        cell = ws.cell(row=3, column=c_idx)
        cell.value = col_name.replace("_", " ")
        cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="134074", end_color="134074", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[3].height = 26
    
    thin = Border(
        left=Side(style='thin', color="D1D5DB"),
        right=Side(style='thin', color="D1D5DB"),
        top=Side(style='thin', color="D1D5DB"),
        bottom=Side(style='thin', color="D1D5DB")
    )
    
    for r_idx, r_data in df_carnita.iterrows():
        r_num = r_idx + 4
        ws.row_dimensions[r_num].height = 26
        f_color = "F8FAFC" if r_num % 2 == 0 else "FFFFFF"
        fill = PatternFill(start_color=f_color, end_color=f_color, fill_type="solid")
        for c_idx, val in enumerate(r_data, 1):
            c = ws.cell(row=r_num, column=c_idx)
            c.value = val
            c.font = Font(name="Calibri", size=9, color="1E293B")
            c.fill = fill
            c.border = thin
            c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=(c_idx in [13]))
            
    for col in ws.columns:
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        max_len = max(len(str(c.value or '')) for c in col)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 48)
        
    ws.freeze_panes = "C4"
    wb.save(out_xlsx)
    wb.save(out_xlsx_local)
    print("Carnita Excel and CSV saved successfully to desktop!")
else:
    print("Failed to start run:", res.status_code, res.text)
