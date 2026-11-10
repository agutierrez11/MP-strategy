import os
import requests, json, time, os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

token = os.getenv("APIFY_API_TOKEN", "")
headers = {"Authorization": f"Bearer {token}"}

run_id = "9LhScTE3A8k0cPVbH"
dataset_id = "YxE2h0Ngz8n5AK94Q"

print(f"Monitoring Apify Run {run_id}...")

while True:
    try:
        res = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}", headers=headers)
        if res.status_code == 200:
            data = res.json().get("data", {})
            status = data.get("status")
            usage_usd = data.get("usageTotalUsd", 0)
            
            # Check dataset item count
            d_res = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}", headers=headers)
            item_count = d_res.json().get("data", {}).get("itemCount", 0) if d_res.status_code == 200 else 0
            
            print(f"[{time.strftime('%H:%M:%S')}] Status: {status} | Items scraped so far: {item_count} | Cost: ${usage_usd:.4f} USD")
            
            if status in ["SUCCEEDED", "ABORTED", "TIMED-OUT", "FAILED"]:
                print(f"Run finished with status: {status}")
                break
        time.sleep(20)
    except Exception as e:
        print("Error during check:", e)
        time.sleep(15)

# Download dataset
print("Downloading items from Apify dataset...")
dataset_items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true&format=json"
d_items_res = requests.get(dataset_items_url, headers=headers)
items = d_items_res.json()

print(f"Successfully downloaded {len(items)} places from Apify!")

# Transform into structured lead records
clean_leads = []
for idx, it in enumerate(items, 1):
    title = it.get("title") or "Sin Nombre"
    phone = it.get("phone") or "Consultar mostrador"
    address = it.get("address") or ""
    city = it.get("city") or ""
    state = it.get("state") or ""
    rating = it.get("totalScore") or 0.0
    reviews = it.get("reviewsCount") or 0
    category = it.get("categoryName") or "Comercio Local"
    website = it.get("website") or it.get("url") or ""
    
    # Classify Quality Tier based on reviews and category
    if reviews >= 100 or any(k in category.lower() for k in ["ferreter", "refaccion", "maquinaria", "camion", "industrial", "mayoreo"]):
        tpv = "$350,000 - $1,200,000 MXN"
        pts = "2.0 a 2.5 pts (Calidad Máxima)"
        tier = "Tier 1 Plus / Ballena Regional"
    else:
        tpv = "$120,000 - $350,000 MXN"
        pts = "1.5 pts (Calidad Sólida)"
        tier = "Tier 1 (Quick Win 15-30 días)"
        
    pitch = f"Modernización de terminal mostrador con SmartPOS Mercado Pago. Reducción de comisiones al 1.65% con disponibilidad inmediata de fondos y 3-6 MSI sin penalizaciones por renta."
    
    clean_leads.append({
        "ID": f"VIRGEN-{idx:04d}",
        "Nombre_Comercial": title,
        "Giro_Categoria": category,
        "Estado_Plaza": f"{city}, {state}".strip(", "),
        "Telefono_WhatsApp": phone,
        "Direccion_Completa": address,
        "Google_Rating": f"{rating} ★" if rating > 0 else "N/A",
        "Numero_Resenas": reviews,
        "Sitio_Web_Redes": website,
        "Estrato_Tier": tier,
        "TPV_Estimado_Mensual": tpv,
        "Puntos_Calidad_Proyectados": pts,
        "Pitch_Mercado_Pago": pitch
    })

df_final = pd.DataFrame(clean_leads)

# Save to Excel and CSV
dest_excel_desktop = r"C:\Users\Antonio\OneDrive\Escritorio\Mercado Pago Strategy\TOP_1200_LEADS_ESTADOS_VIRGENES_APIFY.xlsx"
dest_excel_local = r"c:\Users\Antonio\.gemini\antigravity-ide\scratch\paymind-growth-engine\TOP_1200_LEADS_ESTADOS_VIRGENES_APIFY.xlsx"
dest_csv_desktop = r"C:\Users\Antonio\OneDrive\Escritorio\Mercado Pago Strategy\TOP_1200_LEADS_ESTADOS_VIRGENES_APIFY.csv"

# Save CSV
df_final.to_csv(dest_csv_desktop, index=False, encoding='utf-8-sig')

# Save Excel with formatting
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Leads 1200 Estados Vírgenes"
ws.views.sheetView[0].showGridLines = True

# Palettes
NAVY = "0B2545"
WHITE = "FFFFFF"
LIGHT_BLUE = "EBF2FA"
GRAY_BORDER = "D1D5DB"
ZEBRA = "F8FAFC"
DARK_TEXT = "1E293B"

ws.merge_cells("A1:M1")
t_cell = ws["A1"]
t_cell.value = "PIPELINE MAESTRO DE 1,200 LEADS DE ALTO TPV - ESTADOS VÍRGENES (MERCADO PAGO)"
t_cell.font = Font(name="Calibri", size=14, bold=True, color=WHITE)
t_cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
t_cell.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 34

ws.merge_cells("A2:M2")
s_cell = ws["A2"]
s_cell.value = "Sonora, Sinaloa, BCS, Coahuila, Chihuahua, Tamaulipas, Michoacán, Colima, SLP, Aguascalientes | Enriquecidos con Apify & Google Maps"
s_cell.font = Font(name="Calibri", size=10, italic=True, color="64748B")
s_cell.fill = PatternFill(start_color=LIGHT_BLUE, end_color=LIGHT_BLUE, fill_type="solid")
s_cell.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[2].height = 20

headers = list(df_final.columns)
ws.row_dimensions[3].height = 26
for c_idx, h in enumerate(headers, 1):
    c = ws.cell(row=3, column=c_idx)
    c.value = h.replace("_", " ")
    c.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
    c.fill = PatternFill(start_color="134074", end_color="134074", fill_type="solid")
    c.alignment = Alignment(horizontal="center", vertical="center")

thin_border = Border(
    left=Side(style='thin', color=GRAY_BORDER),
    right=Side(style='thin', color=GRAY_BORDER),
    top=Side(style='thin', color=GRAY_BORDER),
    bottom=Side(style='thin', color=GRAY_BORDER)
)

for r_idx, row in df_final.iterrows():
    row_num = r_idx + 4
    ws.row_dimensions[row_num].height = 24
    fill = PatternFill(start_color=ZEBRA if row_num % 2 == 0 else WHITE,
                       end_color=ZEBRA if row_num % 2 == 0 else WHITE,
                       fill_type="solid")
    for c_idx, val in enumerate(row, 1):
        cell = ws.cell(row=row_num, column=c_idx)
        cell.value = val
        cell.font = Font(name="Calibri", size=9, color=DARK_TEXT)
        cell.fill = fill
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="left", vertical="center")

# Adjust widths
for col in ws.columns:
    col_letter = openpyxl.utils.get_column_letter(col[0].column)
    max_len = max(len(str(cell.value or '')) for cell in col)
    ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

ws.freeze_panes = "C4"
wb.save(dest_excel_desktop)
wb.save(dest_excel_local)
print("Saved Excel successfully to desktop and workspace!")
