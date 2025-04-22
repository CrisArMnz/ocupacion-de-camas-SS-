import requests
from io import BytesIO
from datetime import datetime

# --- 1. Descargar archivo desde Google Sheets ---
sheet_id = "1U-djDnSaFwv3vUJhIC3BhicMzQgppeWn"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
excel_bytes = BytesIO(requests.get(url).content)

# --- 2. Leer libro y filtrar hojas que son fechas ---
xls = pd.ExcelFile(excel_bytes)
hojas_2025 = [h for h in xls.sheet_names if '2025' in h]

# Ordenar como fechas, pero manteniendo strings originales
hojas_ordenadas = sorted(hojas_2025, key=lambda x: datetime.strptime(x.strip(), "%d-%m-%Y"))

# --- 3. Procesar últimas 2 hojas (ajustable) ---
dfs = []
for hoja in hojas_ordenadas[-2:]:
    temp_df = xls.parse(hoja, header=None)
    try:
        header_row = temp_df[temp_df[1] == "Establecimiento"].index[0]
    except IndexError:
        continue  # saltar hoja si no se encuentra encabezado
    
    df = xls.parse(hoja, header=header_row)
    df["fecha"] = hoja
    if "Establecimiento" in df.columns:
        df["Establecimiento"].fillna(method="ffill", inplace=True)
    dfs.append(df)

# --- 4. Concatenar resultado final ---
df_total = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
