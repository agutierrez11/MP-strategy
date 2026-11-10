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

# New Fresh Apify Token ($5.00 USD intact)
NEW_APIFY_TOKEN = os.getenv("APIFY_API_TOKEN", "")
ACTOR_ID = "compass~crawler-google-places"

QUERIES_CHETUMAL = [
    # Clínicas, Salud & Estética en Chetumal
    "clinica estetica spa Chetumal Quintana Roo",
    "clinica dental ortodoncia Chetumal Quintana Roo",
    "hospital veterinario clinica veterinaria Chetumal Quintana Roo",
    "laboratorio clinico analisis Chetumal Quintana Roo",
    
    # Restaurantes & Vida Nocturna (Boulevard Bahía y Centro)
    "restaurante marisqueria Boulevard Bahia Chetumal Quintana Roo",
    "restaurante bar cafeteria Chetumal Centro Quintana Roo",
    
    # Comercio de Alto Ticket (Refaccionarias, Ferreterías, Mayoreo)
    "refaccionaria automotriz llantera Chetumal Quintana Roo",
    "ferreteria materiales para construccion Chetumal Quintana Roo",
    "boutique zapateria joyeria Avenida Heroes Chetumal Quintana Roo",
    "gimnasio crossfit fitness Chetumal Quintana Roo",
    
    # Hotelería & Servicios en Chetumal
    "hotel suites hospedaje Chetumal Quintana Roo",
    "notaria publica despacho contable Chetumal Quintana Roo",
    
    # Bacalar (Eco-turismo, Hotelería Boutique, Restaurantes Laguna)
    "hotel boutique cabanas Bacalar Quintana Roo",
    "restaurante bar laguna Bacalar Quintana Roo",
    "spa masajes wellness Bacalar Quintana Roo",
    "tours nauticos velero kayak Bacalar Quintana Roo",
    
    # Felipe Carrillo Puerto (Zona Centro-Sur)
    "restaurante hotel Felipe Carrillo Puerto Quintana Roo",
    "clinica farmacia veterinaria Felipe Carrillo Puerto Quintana Roo"
]

print("Using existing completed Apify dataset for Chetumal & Sur Q.Roo...")
dataset_id = "4ccJRfTmfUHgMTOMY"
print(f"Downloading Chetumal & Sur dataset items from {dataset_id}...")
dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={NEW_APIFY_TOKEN}&format=json"
items = json.loads(urllib.request.urlopen(dataset_url).read().decode('utf-8'))
print(f"Total downloaded: {len(items)} places!")

# Process leads
processed_chetumal = []
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
    
    if 'bacalar' in addr_lower:
        city = 'Bacalar'
    elif 'carrillo puerto' in addr_lower:
        city = 'Felipe Carrillo Puerto'
    else:
        city = 'Chetumal'
    
    category = p.get('categoryName', '') or ''
    total_reviews = p.get('reviewsCount', 0) or 0
    rating = p.get('totalScore', 0.0) or 0.0
    website = p.get('website', '') or ''
    
    # Classify niche & customize pitch
    cat_full = (category + ' ' + title).lower()
    
    if any(k in cat_full for k in ['estetica', 'spa', 'dermatol', 'cirugia', 'facial', 'cosmet']):
        niche = "Clínica Estética & Spa"
        ticket = "$2,500 - $8,000 MXN"
        tpv = "$350,000 - $850,000 MXN"
        pts = 2.0
        hook = f"Hola {title}, vi sus excelentes valoraciones en {city}. En Mercado Pago tenemos tasa preferencial desde 1.75% con meses sin intereses para paquetes estéticos y entrega en mano de la terminal Smart sin rentas mensuales."
    elif any(k in cat_full for k in ['dental', 'dentist', 'ortodon']):
        niche = "Clínica Dental & Ortodoncia"
        ticket = "$2,000 - $15,000 MXN"
        tpv = "$400,000 - $1,100,000 MXN"
        pts = 2.0
        hook = f"Buen día Dr./Dra. de {title}, un gusto saludarle en {city}. Apoyamos a consultorios dentales para cobrar tratamientos y prótesis a meses sin intereses, con el dinero disponible al segundo en su cuenta Mercado Pago."
    elif any(k in cat_full for k in ['hotel', 'resort', 'cabana', 'hostal', 'hospedaje']):
        niche = "Hotelería & Hospedaje Boutique"
        ticket = "$1,800 - $6,500 MXN"
        tpv = "$500,000 - $1,600,000 MXN"
        pts = 2.5
        hook = f"Hola {title}, un saludo a su equipo en {city}. Con la terminal Smart de Mercado Pago aceptan tarjetas internacionales, Amex y pagos contactless sin comisiones sorpresa ni fallas de red, con entrega inmediata en mano."
    elif any(k in cat_full for k in ['restaurante', 'marisqueria', 'bar', 'cafe']):
        niche = "Restaurante & Alimentos de Alto Flujo"
        ticket = "$450 - $1,800 MXN"
        tpv = "$300,000 - $900,000 MXN"
        pts = 2.0
        hook = f"Hola {title}, gran propuesta gastronómica en {city}. Nuestra terminal Smart tiene batería para todo el turno, acepta propina directa en pantalla y no te cobra renta cuando baje la temporada."
    elif any(k in cat_full for k in ['refaccion', 'auto', 'llant', 'taller', 'mecanic']):
        niche = "Refaccionaria & Automotriz"
        ticket = "$1,500 - $12,000 MXN"
        tpv = "$450,000 - $1,200,000 MXN"
        pts = 2.0
        hook = f"Hola {title}, vi su fuerte presencia en {city}. Con Mercado Pago Smart pueden ofrecer 3, 6 y 12 meses sin intereses en refacciones o llantas y ustedes cobran de contado al instante."
    elif any(k in cat_full for k in ['ferreter', 'material', 'construc', 'plomer']):
        niche = "Ferretería & Materiales"
        ticket = "$1,200 - $18,000 MXN"
        tpv = "$500,000 - $1,500,000 MXN"
        pts = 2.5
        hook = f"Estimado equipo de {title}, un saludo en {city}. Para mostrador de ferretería y contratistas, la Smart POS imprime ticket al momento, acepta tarjeta empresarial y les da liquidez inmediata para pagar a proveedores."
    elif any(k in cat_full for k in ['tour', 'velero', 'kayak', 'lancha', 'aventura']):
        niche = "Tours Náuticos & Ecoturismo"
        ticket = "$1,000 - $5,000 MXN"
        tpv = "$350,000 - $950,000 MXN"
        pts = 2.0
        hook = f"Hola {title}, excelente servicio en {city}. Con la terminal portátil Smart pueden cobrar directo a pie de muelle o lancha con señal 4G gratuita ilimitada, ideal para turistas extranjeros."
    elif any(k in cat_full for k in ['veterinar', 'pet', 'mascota']):
        niche = "Hospital Veterinario"
        ticket = "$800 - $4,500 MXN"
        tpv = "$250,000 - $600,000 MXN"
        pts = 1.5
        hook = f"Hola {title}, un gusto saludar a su clínica en {city}. Mercado Pago les permite cobrar consultas, cirugías y alimentos premium con terminal Smart sin contratos forzosos ni penalizaciones."
    else:
        niche = "Comercio & Servicios Generales"
        ticket = "$800 - $3,500 MXN"
        tpv = "$200,000 - $500,000 MXN"
        pts = 1.5
        hook = f"Hola {title}, un saludo en {city}. En Mercado Pago tenemos terminal Smart sin rentas mensuales fija, ideal para mejorar tus opciones de cobro. Te la entrego personalmente en tu negocio."

    whatsapp_link = f"https://wa.me/52{phone_clean}" if len(phone_clean) >= 10 else "Sin teléfono directo"
    
    processed_chetumal.append({
        "ID_Lead": f"QR-SUR-{idx:03d}",
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

df_sur = pd.DataFrame(processed_chetumal)
print(f"Total Chetumal & Sur processed leads: {len(df_sur)}")

# Now integrate into Master Excel
desktop_master = r"C:\Users\Antonio\OneDrive\Escritorio\Mercado Pago Strategy\CARNITA_MASTER_PROSPECCION_MERCADOPAGO.xlsx"

# Read existing sheets
if os.path.exists(desktop_master):
    try:
        df_qroo_prev = pd.read_excel(desktop_master, sheet_name='QUINTANA_ROO_PRESENCIAL')
    except Exception:
        df_qroo_prev = pd.DataFrame()
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
    df_foraneos = pd.DataFrame()
    df_playbook = pd.DataFrame()

# Concatenate Chetumal to Quintana Roo
df_qroo_combined = pd.concat([df_qroo_prev, df_sur], ignore_index=True)
df_qroo_combined = df_qroo_combined.drop_duplicates(subset=['Comercio'], keep='first')
print(f"Total Combined Quintana Roo Leads (Norte + Sur): {len(df_qroo_combined)}")

# Also create a dedicated CHETUMAL_Y_SUR tab for easy filtering
with pd.ExcelWriter(desktop_master, engine='openpyxl') as writer:
    df_qroo_combined.to_excel(writer, sheet_name='TODO_QUINTANA_ROO', index=False)
    df_sur.to_excel(writer, sheet_name='CHETUMAL_Y_BACALAR', index=False)
    if not df_foraneos.empty:
        df_foraneos.to_excel(writer, sheet_name='FORANEOS_DIGITAL_REMOTA', index=False)
    if not df_playbook.empty:
        df_playbook.to_excel(writer, sheet_name='PLAYBOOK_CIERRES_Y_GUIA', index=False)

# Styling with openpyxl
wb = openpyxl.load_workbook(desktop_master)

header_fill_teal = PatternFill(start_color="008080", end_color="008080", fill_type="solid")
header_fill_navy = PatternFill(start_color="004B87", end_color="004B87", fill_type="solid")
header_fill_green = PatternFill(start_color="1B5E20", end_color="1B5E20", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
border_thin = Border(left=Side(style='thin', color='E0E0E0'),
                     right=Side(style='thin', color='E0E0E0'),
                     top=Side(style='thin', color='E0E0E0'),
                     bottom=Side(style='thin', color='E0E0E0'))

for sheet_name in ['TODO_QUINTANA_ROO', 'CHETUMAL_Y_BACALAR', 'FORANEOS_DIGITAL_REMOTA', 'PLAYBOOK_CIERRES_Y_GUIA']:
    if sheet_name not in wb.sheetnames:
        continue
    ws = wb[sheet_name]
    fill = header_fill_teal if 'QUINTANA' in sheet_name or 'CHETUMAL' in sheet_name else (header_fill_navy if 'FORANEOS' in sheet_name else header_fill_green)
    
    for cell in ws[1]:
        cell.fill = fill
        cell.font = header_font
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
print(f"MASTER EXCEL UPDATED WITH CHETUMAL & BACALAR: {desktop_master}")
