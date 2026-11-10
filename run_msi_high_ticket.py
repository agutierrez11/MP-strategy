import sys
import os
import json
import time
import urllib.request
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

# Active token with $3.28 USD intact
APIFY_TOKEN = os.getenv("APIFY_API_TOKEN", "")
ACTOR_ID = "compass~crawler-google-places"

QUERIES_MSI = [
    # Paneles Solares & Energía Renovable (Tickets: $35,000 - $180,000 MXN)
    "paneles solares energia solar Cancun Quintana Roo",
    "paneles solares Playa del Carmen Quintana Roo",
    "paneles solares Chetumal Quintana Roo",
    
    # Agencias de Viajes & Operadores Turísticos (Tickets: $15,000 - $80,000 MXN)
    "agencia de viajes paquetes Cancun Quintana Roo",
    "agencia de viajes tours Playa del Carmen Quintana Roo",
    "agencia de viajes Chetumal Quintana Roo",
    
    # Mueblerías de Lujo, Amueblado Airbnb & Interiorismo (Tickets: $25,000 - $150,000 MXN)
    "muebleria diseno interiores Cancun Quintana Roo",
    "muebleria decoracion Playa del Carmen Quintana Roo",
    "muebles decoracion interiores Tulum Quintana Roo",
    
    # Cirugía Plástica, Bariátrica & Maternidad (Tickets: $40,000 - $120,000 MXN)
    "cirujano plastico cirugia estetica Cancun Quintana Roo",
    "cirugia plastica bariatrica Playa del Carmen Quintana Roo",
    
    # Piscinas, Jacuzzis & Construcción Residencial (Tickets: $30,000 - $160,000 MXN)
    "albercas piscinas construccion Cancun Quintana Roo",
    "albercas equipamiento Playa del Carmen Quintana Roo",
    
    # Motos, Cuatrimotos, Venta de Lanchas & Motores Marinos (Tickets: $30,000 - $200,000 MXN)
    "motos cuatrimotos agencias Cancun Quintana Roo",
    "motos cuatrimotos refacciones Chetumal Quintana Roo",
    "marina motores fuera de borda lanchas Cancun Quintana Roo"
]

print(f"Total MSI-heavy queries: {len(QUERIES_MSI)}")
print("Launching Apify run for High-Ticket MSI Businesses in Q.Roo (Cap: 250 places, ~$1.00 USD)...")

run_input = {
    "searchStringsArray": QUERIES_MSI,
    "maxCrawledPlacesPerSearch": 20,
    "maxCrawledPlaces": 250,
    "language": "es",
    "countryCode": "mx"
}

run_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}"
req = urllib.request.Request(
    run_url,
    data=json.dumps(run_input).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)

res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
run_id = res['data']['id']
dataset_id = res['data']['defaultDatasetId']
print(f"RUN LAUNCHED! Run ID: {run_id} | Dataset ID: {dataset_id}")

while True:
    time.sleep(15)
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"
    s_res = json.loads(urllib.request.urlopen(status_url).read().decode('utf-8'))
    status = s_res['data']['status']
    usage = s_res['data'].get('usageTotalUsd', 0)
    item_count = s_res['data'].get('datasetItemsCount', 0)
    print(f"[{time.strftime('%H:%M:%S')}] Status: {status} | Scraped: {item_count}/250 | Usage: ${usage:.4f} USD")
    
    if status in ['SUCCEEDED', 'FAILED', 'TIMED-OUT', 'ABORTED']:
        break

print("Downloading MSI dataset items...")
dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&format=json"
items = json.loads(urllib.request.urlopen(dataset_url).read().decode('utf-8'))
print(f"Total downloaded: {len(items)} places!")

# Process MSI leads
processed_msi = []
seen_titles = set()

for idx, p in enumerate(items, 1):
    title = (p.get('title') or '').strip()
    if not title or title.lower() in seen_titles:
        continue
    seen_titles.add(title.lower())
    
    phone = p.get('phoneUnformatted') or p.get('phone') or ''
    phone_clean = ''.join(c for c in str(phone) if c.isdigit())
    
    address = p.get('address') or ''
    addr_lower = (address + ' ' + title).lower()
    
    if 'playa del carmen' in addr_lower or 'solidaridad' in addr_lower:
        city = 'Playa del Carmen'
    elif 'tulum' in addr_lower:
        city = 'Tulum'
    elif 'chetumal' in addr_lower or 'othon' in addr_lower:
        city = 'Chetumal'
    else:
        city = 'Cancún'
        
    category = p.get('categoryName') or ''
    total_reviews = p.get('reviewsCount') or 0
    rating = p.get('totalScore') or 0.0
    website = p.get('website') or ''
    
    cat_full = (category + ' ' + title).lower()
    
    if any(k in cat_full for k in ['solar', 'fotovolt', 'energia', 'panel']):
        niche = "Paneles Solares & Energía Renovable"
        ticket = "$45,000 - $180,000 MXN"
        tpv = "$600,000 - $2,200,000 MXN"
        pts = 2.5
        hook = f"Hola {title}, un saludo a su equipo de proyectos solares en {city}. En ventas de sistemas residenciales y comerciales, el cliente siempre pide 6, 12 o 18 Meses Sin Intereses. Con Mercado Pago Smart tienen la sobretasa de financiamiento más baja de México y cobran el 100% de contado al segundo. ¿Podemos agendar 10 minutos para mostrarles la comparativa de ahorro?"
    elif any(k in cat_full for k in ['viaje', 'tour', 'travel', 'vacacion', 'dmc']):
        niche = "Agencia de Viajes & Turismo Receptivo"
        ticket = "$18,000 - $75,000 MXN"
        tpv = "$400,000 - $1,500,000 MXN"
        pts = 2.5
        hook = f"Buen día {title}, gran catálogo de paquetes en {city}. Para agencias de viajes, cerrar paquetes vacacionales a 3, 6, 9 y 12 MSI sin trámites bancarios engorrosos ni fianzas duplica la conversión. Te llevo la terminal Smart hoy mismo con chip 4G incluido."
    elif any(k in cat_full for k in ['muebl', 'interior', 'decor', 'decorac', 'arq']):
        niche = "Mueblería de Diseño & Interiorismo Airbnb"
        ticket = "$25,000 - $140,000 MXN"
        tpv = "$500,000 - $1,800,000 MXN"
        pts = 2.5
        hook = f"Hola {title}, hermosa propuesta de interiorismo en {city}. Con el boom de condominios y amueblado de rentas vacacionales, los inversionistas compran paquetes completos si les das 6 o 12 MSI. Mercado Pago les activa MSI inmediato sin renta mensual."
    elif any(k in cat_full for k in ['cirug', 'bariatr', 'plastico', 'hospital', 'mater']):
        niche = "Cirugía Plástica & Especialidades Médicas"
        ticket = "$35,000 - $120,000 MXN"
        tpv = "$700,000 - $2,500,000 MXN"
        pts = 2.5
        hook = f"Estimado Dr./Dra. de {title}, un saludo en {city}. En procedimientos quirúrgicos de alto valor, los pacientes deciden por la facilidad de 12 MSI. Mercado Pago no les cobra fianza bancaria y el dinero de los honorarios queda disponible al instante."
    elif any(k in cat_full for k in ['alberca', 'piscin', 'jacuzzi']):
        niche = "Construcción de Albercas & Equipamiento"
        ticket = "$30,000 - $160,000 MXN"
        tpv = "$450,000 - $1,300,000 MXN"
        pts = 2.0
        hook = f"Hola {title}, un saludo en {city}. Para proyectos de albercas y equipo de filtrado, facilitar 12 MSI a clientes particulares cierra tratos en caliente. Les dejo una terminal Smart de prueba sin contratos forzosos."
    elif any(k in cat_full for k in ['moto', 'cuatrimoto', 'lancha', 'marin', 'embarcac']):
        niche = "Motos, Cuatrimotos & Náutica"
        ticket = "$25,000 - $220,000 MXN"
        tpv = "$600,000 - $2,800,000 MXN"
        pts = 2.5
        hook = f"Hola {title}, vi sus unidades y refacciones en {city}. Cerrar motos, cuatrimotos o motores marinos a 6, 12 o 18 MSI es clave para no perder ventas frente a agencias grandes. Les configuro la terminal hoy en 10 minutos."
    else:
        niche = "Comercio de Alto Ticket (Obligado a MSI)"
        ticket = "$15,000 - $60,000 MXN"
        tpv = "$350,000 - $900,000 MXN"
        pts = 2.0
        hook = f"Hola {title}, un saludo en {city}. En productos de alto valor, ofrecer 3, 6 y 12 Meses Sin Intereses aumenta el ticket promedio un 40%. Con Mercado Pago Smart lo activas sin burocracia bancaria ni cobros fijos."

    whatsapp_link = f"https://wa.me/52{phone_clean}" if len(phone_clean) >= 10 else "Sin teléfono directo"
    
    processed_msi.append({
        "ID_Lead": f"QR-MSI-{idx:03d}",
        "Comercio": title,
        "Nicho_Vertical": niche,
        "Plaza_Ciudad": city,
        "Tipo_Cierre": "PRESENCIAL INMEDIATO (0 días envío)",
        "Telefono_WhatsApp": whatsapp_link,
        "Telefono_Limpio": phone_clean,
        "Instagram_SitioWeb": website if website else "Ver perfil Maps/IG",
        "Direccion": address,
        "Google_Rating": rating,
        "Resenas": total_reviews,
        "Ticket_Promedio_Estimado": ticket,
        "TPV_Mensual_Estimado": tpv,
        "Puntos_Calidad_MP": pts,
        "Gancho_WhatsApp_Listo": hook
    })

df_msi = pd.DataFrame(processed_msi)
print(f"Total MSI leads processed: {len(df_msi)}")

# Now integrate into Master Excel
desktop_master = r"C:\Users\Antonio\OneDrive\Escritorio\Mercado Pago Strategy\CARNITA_MASTER_PROSPECCION_MERCADOPAGO.xlsx"

if os.path.exists(desktop_master):
    try:
        df_qroo_prev = pd.read_excel(desktop_master, sheet_name='TODO_QUINTANA_ROO')
    except Exception:
        df_qroo_prev = pd.DataFrame()
    try:
        df_sur_prev = pd.read_excel(desktop_master, sheet_name='CHETUMAL_Y_BACALAR')
    except Exception:
        df_sur_prev = pd.DataFrame()
    try:
        df_foraneos = pd.read_excel(desktop_master, sheet_name='FORANEOS_DIGITAL_REMOTA')
    except Exception:
        df_foraneos = pd.DataFrame()
    try:
        df_playbook = pd.read_excel(desktop_master, sheet_name='PLAYBOOK_CIERRES_Y_GUIA')
    except Exception:
        df_playbook = pd.DataFrame()
else:
    df_qroo_prev = pd.DataFrame()
    df_sur_prev = pd.DataFrame()
    df_foraneos = pd.DataFrame()
    df_playbook = pd.DataFrame()

# Combine MSI leads into TODO_QUINTANA_ROO
df_qroo_total = pd.concat([df_qroo_prev, df_msi], ignore_index=True)
df_qroo_total = df_qroo_total.drop_duplicates(subset=['Comercio'], keep='first')
print(f"New Total Quintana Roo Combined Leads: {len(df_qroo_total)}")

# Create dedicated MSI Tab
with pd.ExcelWriter(desktop_master, engine='openpyxl') as writer:
    df_msi.to_excel(writer, sheet_name='MSI_ALTO_TICKET_QROO', index=False)
    df_qroo_total.to_excel(writer, sheet_name='TODO_QUINTANA_ROO', index=False)
    if not df_sur_prev.empty:
        df_sur_prev.to_excel(writer, sheet_name='CHETUMAL_Y_BACALAR', index=False)
    if not df_foraneos.empty:
        df_foraneos.to_excel(writer, sheet_name='FORANEOS_DIGITAL_REMOTA', index=False)
    if not df_playbook.empty:
        df_playbook.to_excel(writer, sheet_name='PLAYBOOK_CIERRES_Y_GUIA', index=False)

# Styling with openpyxl
wb = openpyxl.load_workbook(desktop_master)

header_fill_gold = PatternFill(start_color="D4AF37", end_color="D4AF37", fill_type="solid") # Gold for High Ticket MSI
header_fill_teal = PatternFill(start_color="008080", end_color="008080", fill_type="solid")
header_fill_navy = PatternFill(start_color="004B87", end_color="004B87", fill_type="solid")
header_fill_green = PatternFill(start_color="1B5E20", end_color="1B5E20", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_font_dark = Font(name="Calibri", size=11, bold=True, color="000000")

border_thin = Border(left=Side(style='thin', color='E0E0E0'),
                     right=Side(style='thin', color='E0E0E0'),
                     top=Side(style='thin', color='E0E0E0'),
                     bottom=Side(style='thin', color='E0E0E0'))

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    if sheet_name == 'MSI_ALTO_TICKET_QROO':
        fill = header_fill_gold
        h_font = header_font_dark
    elif 'QUINTANA' in sheet_name or 'CHETUMAL' in sheet_name:
        fill = header_fill_teal
        h_font = header_font
    elif 'FORANEOS' in sheet_name:
        fill = header_fill_navy
        h_font = header_font
    else:
        fill = header_fill_green
        h_font = header_font
        
    for cell in ws[1]:
        cell.fill = fill
        cell.font = h_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 28
    
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for cell in row:
            cell.border = border_thin
            cell.font = Font(name="Calibri", size=10)
            col_letter = get_column_letter(cell.column)
            if col_letter in ['E', 'F'] and cell.value and str(cell.value).startswith('http'):
                cell.font = Font(name="Calibri", size=10, color="0000FF", underline="single")
                
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 48)

wb.save(desktop_master)
print(f"MASTER EXCEL UPDATED WITH HIGH-TICKET MSI SHEET: {desktop_master}")
