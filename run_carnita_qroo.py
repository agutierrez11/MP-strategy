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

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN", "")
ACTOR_ID = "compass~crawler-google-places"

# Target specifically Quintana Roo (Cancun, Playa del Carmen, Tulum)
# Capped strictly at 150 places (~$0.60 USD) to fit perfectly within the remaining free balance
QUERIES_QROO = [
    "clinica estetica cancun",
    "med spa cancun",
    "pilates reformer cancun",
    "hospital veterinario cancun 24 horas",
    "clinica dental cancun dental tourism",
    "clinica estetica playa del carmen",
    "spa playa del carmen",
    "pilates reformer playa del carmen",
    "boutique concept store tulum",
    "wellness spa tulum",
    "hospital veterinario playa del carmen",
    "beach club restaurante tulum"
]

print(f"Total Quintana Roo queries: {len(QUERIES_QROO)}")
print("Launching Apify run for Quintana Roo (Cap: 150 places)...")

run_input = {
    "searchStringsArray": QUERIES_QROO,
    "maxCrawledPlacesPerSearch": 12,
    "maxCrawledPlaces": 140,
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
    stats = s_res['data'].get('stats', {})
    usage = s_res['data'].get('usageTotalUsd', 0)
    item_count = s_res['data'].get('datasetItemsCount', 0)
    print(f"[{time.strftime('%H:%M:%S')}] Status: {status} | Scraped: {item_count}/150 | Usage: ${usage:.4f} USD")
    
    if status in ['SUCCEEDED', 'FAILED', 'TIMED-OUT', 'ABORTED']:
        break

print("Downloading Quintana Roo dataset items...")
dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&format=json"
items = json.loads(urllib.request.urlopen(dataset_url).read().decode('utf-8'))
print(f"Total downloaded: {len(items)} places!")

# Process Quintana Roo Leads
processed_qroo = []
seen_titles = set()

for idx, p in enumerate(items, 1):
    title = p.get('title', '').strip()
    if not title or title.lower() in seen_titles:
        continue
    seen_titles.add(title.lower())
    
    phone = p.get('phoneUnformatted') or p.get('phone') or ''
    phone_clean = ''.join(c for c in str(phone) if c.isdigit())
    
    address = p.get('address', '')
    city = 'Cancún'
    addr_lower = (address + ' ' + title).lower()
    if 'playa del carmen' in addr_lower or 'solidaridad' in addr_lower:
        city = 'Playa del Carmen'
    elif 'tulum' in addr_lower:
        city = 'Tulum'
    elif 'cozumel' in addr_lower:
        city = 'Cozumel'
    elif 'chetumal' in addr_lower:
        city = 'Chetumal'
    
    category = p.get('categoryName', '') or ''
    total_reviews = p.get('reviewsCount', 0) or 0
    rating = p.get('totalScore', 0.0) or 0.0
    website = p.get('website', '') or ''
    
    # Classify niche
    cat_full = (category + ' ' + title).lower()
    if any(k in cat_full for k in ['estetica', 'spa', 'dermatol', 'cirugia', 'facial', 'cosmet']):
        niche = "Clínica Estética & MedSpa"
        ticket = "$3,500 - $14,000 MXN"
        tpv = "$550,000 - $1,400,000 MXN"
        pts = 2.5
        hook = f"Hola {title}, vi sus tratamientos y valoraciones en {city}. En Mercado Pago tenemos tasa preferencial del 1.75% con meses sin intereses para paquetes estéticos y entrega inmediata en mano de la terminal Smart hoy mismo."
    elif any(k in cat_full for k in ['pilates', 'reformer', 'yoga', 'fitness', 'gimnasio']):
        niche = "Pilates Reformer & Wellness"
        ticket = "$1,800 - $3,500 MXN"
        tpv = "$280,000 - $650,000 MXN"
        pts = 2.0
        hook = f"Hola equipo de {title}, un gusto saludarles. Noté la alta demanda de sus clases en {city}. Apoyamos a estudios boutique con terminal Smart sin rentas fijas y cobro recurrente para membresías. ¿Podría pasar a mostrársela hoy?"
    elif any(k in cat_full for k in ['dental', 'odontol', 'dentist']):
        niche = "Clínica Dental & Turismo Médico"
        ticket = "$4,000 - $25,000 MXN"
        tpv = "$600,000 - $1,800,000 MXN"
        pts = 2.5
        hook = f"Buen día Dr./Dra. de {title}, un saludo en {city}. Para cobro de tratamientos dentales y pacientes extranjeros, Mercado Pago acepta tarjetas internacionales y Amex sin sobrecosto, con liquidación al instante. ¿Le dejo una terminal de prueba hoy?"
    elif any(k in cat_full for k in ['veterinar', 'pet', 'mascotas']):
        niche = "Hospital Veterinario"
        ticket = "$1,200 - $7,000 MXN"
        tpv = "$350,000 - $800,000 MXN"
        pts = 2.0
        hook = f"Hola {title}, excelente servicio veterinario en {city}. Con Mercado Pago Smart pueden cobrar cirugías y hospitalizaciones a meses sin intereses y el dinero cae en segundos. Te la entrego personalmente en tu clínica."
    elif any(k in cat_full for k in ['beach club', 'restaurante', 'bar']):
        niche = "Beach Club & Restaurante High-End"
        ticket = "$1,500 - $5,000 MXN"
        tpv = "$800,000 - $2,500,000 MXN"
        pts = 2.5
        hook = f"Hola {title}, vi el ambientazo y flujo en {city}. La terminal Smart de Mercado Pago tiene batería todo el día para cobrar a pie de playa o mesa, acepta propinas en pantalla y no se desconecta. Te la llevo hoy para demo."
    else:
        niche = "Boutique & Concept Store"
        ticket = "$1,500 - $4,800 MXN"
        tpv = "$250,000 - $550,000 MXN"
        pts = 1.5
        hook = f"Hola {title}, hermosa propuesta en {city}. Con Mercado Pago Smart tienes terminal sin contratos forzosos, ideal para venta en tienda y eventos. ¿En qué horario te queda bien que pase a mostrártela?"

    whatsapp_link = f"https://wa.me/52{phone_clean}" if len(phone_clean) >= 10 else "Sin teléfono directo"
    
    processed_qroo.append({
        "ID_Lead": f"QR-CARNITA-{idx:03d}",
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

df_qroo = pd.DataFrame(processed_qroo)
print(f"Quintana Roo processed leads count: {len(df_qroo)}")

# Load existing Foraneo leads
csv_foraneos_path = r"C:\Users\Antonio\OneDrive\Escritorio\Mercado Pago Strategy\CARNITA_PROSPECCION_DIGITAL_LEADS.csv"
if os.path.exists(csv_foraneos_path):
    df_foraneos = pd.read_csv(csv_foraneos_path)
    df_foraneos['Tipo_Cierre'] = "DIGITAL REMOTO (Envío paquetería)"
else:
    df_foraneos = pd.DataFrame()

# Build Playbook and Scripts
playbook_rows = [
    {
        "Canal / Tipo": "Quintana Roo - Cierre Presencial en Mano",
        "Velocidad Ciclo": "24 a 48 Horas",
        "Estrategia de Contacto": "1. Mandar WhatsApp / DM en Instagram por la mañana con el Hook personalizado.\n2. Si confirman interés, acordar visita ese mismo día.\n3. Llevar la terminal Smart POS en mano, configurarla en 10 minutos con su cuenta y dejarla transaccionando.",
        "Manejo de Objeción: 'Ya tengo banco'": "Totalmente, y hacen bien en respaldarse. La gran ventaja de Mercado Pago es que no cobramos renta mensual ni te exigimos facturación mínima. La dejas como terminal de respaldo para cuando se caiga el sistema bancario o para meses sin intereses.",
        "Manejo de Objeción: 'La comisión es alta'": "Si facturas más de $200k al mes, Mercado Pago te baja la tasa al 1.75% o menos, y lo más valioso: el dinero no te cae en 48 horas como el banco tradicional, te cae al segundo, con rendimientos diarios."
    },
    {
        "Canal / Tipo": "Estados Foráneos - Prospección Digital Remota",
        "Velocidad Ciclo": "5 a 8 Días (por paquetería)",
        "Estrategia de Contacto": "1. Mensaje de WhatsApp directo al dueño/gerente con el gancho del archivo.\n2. Enviar demo en video de 30 segundos mostrando la pantalla táctil de la Smart POS.\n3. Registro en línea mediante tu link de asesor comercial y envío express de la terminal por Mercado Libre.",
        "Manejo de Objeción: '¿Cómo me llega la terminal?'": "Te llega en 24-48 horas por Mercado Envíos a la puerta de tu negocio con envío gratis, lista para encender y cobrar.",
        "Manejo de Objeción: 'No conozco el soporte'": "Yo soy tu ejecutivo asignado directo de Mercado Pago. Te doy soporte personalizado por WhatsApp para cualquier duda o activación."
    }
]
df_playbook = pd.DataFrame(playbook_rows)

# Master Excel File Generation
desktop_master = r"C:\Users\Antonio\OneDrive\Escritorio\Mercado Pago Strategy\CARNITA_MASTER_PROSPECCION_MERCADOPAGO.xlsx"

with pd.ExcelWriter(desktop_master, engine='openpyxl') as writer:
    df_qroo.to_excel(writer, sheet_name='QUINTANA_ROO_PRESENCIAL', index=False)
    if not df_foraneos.empty:
        df_foraneos.to_excel(writer, sheet_name='FORANEOS_DIGITAL_REMOTA', index=False)
    df_playbook.to_excel(writer, sheet_name='PLAYBOOK_CIERRES_Y_GUIA', index=False)

# Styling with openpyxl
wb = openpyxl.load_workbook(desktop_master)

# Style Quintana Roo Sheet
ws_qroo = wb['QUINTANA_ROO_PRESENCIAL']
header_fill_qroo = PatternFill(start_color="008080", end_color="008080", fill_type="solid") # Teal / Caribbean Blue
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
border_thin = Border(left=Side(style='thin', color='E0E0E0'),
                     right=Side(style='thin', color='E0E0E0'),
                     top=Side(style='thin', color='E0E0E0'),
                     bottom=Side(style='thin', color='E0E0E0'))

for cell in ws_qroo[1]:
    cell.fill = header_fill_qroo
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws_qroo.row_dimensions[1].height = 28

for row in ws_qroo.iter_rows(min_row=2, max_row=ws_qroo.max_row):
    for cell in row:
        cell.border = border_thin
        cell.font = Font(name="Calibri", size=10)
        col_letter = get_column_letter(cell.column)
        if col_letter in ['E', 'F']:
            if cell.value and str(cell.value).startswith('http'):
                cell.font = Font(name="Calibri", size=10, color="0000FF", underline="single")
        elif col_letter in ['J', 'K', 'L']:
            cell.alignment = Alignment(horizontal="center")

for col in ws_qroo.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_qroo.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 48)

# Style Foraneos Sheet
if 'FORANEOS_DIGITAL_REMOTA' in wb.sheetnames:
    ws_for = wb['FORANEOS_DIGITAL_REMOTA']
    header_fill_for = PatternFill(start_color="004B87", end_color="004B87", fill_type="solid") # Mercado Pago Navy
    for cell in ws_for[1]:
        cell.fill = header_fill_for
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws_for.row_dimensions[1].height = 28
    
    for row in ws_for.iter_rows(min_row=2, max_row=ws_for.max_row):
        for cell in row:
            cell.border = border_thin
            cell.font = Font(name="Calibri", size=10)
            col_letter = get_column_letter(cell.column)
            if col_letter in ['E', 'F']:
                if cell.value and str(cell.value).startswith('http'):
                    cell.font = Font(name="Calibri", size=10, color="0000FF", underline="single")
    for col in ws_for.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_for.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 48)

# Style Playbook Sheet
ws_pb = wb['PLAYBOOK_CIERRES_Y_GUIA']
header_fill_pb = PatternFill(start_color="1B5E20", end_color="1B5E20", fill_type="solid") # Dark Green
for cell in ws_pb[1]:
    cell.fill = header_fill_pb
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws_pb.row_dimensions[1].height = 28

for row in ws_pb.iter_rows(min_row=2, max_row=ws_pb.max_row):
    for cell in row:
        cell.border = border_thin
        cell.font = Font(name="Calibri", size=10)
        cell.alignment = Alignment(vertical="top", wrap_text=True)

for col in ws_pb.columns:
    col_letter = get_column_letter(col[0].column)
    ws_pb.column_dimensions[col_letter].width = 38

wb.save(desktop_master)
print(f"MASTER EXCEL SAVED SUCCESSFULLY: {desktop_master}")
