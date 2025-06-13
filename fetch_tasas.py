import requests
import sqlite3
import csv
from datetime import datetime

ACCESS_KEY = 'd75106e3fef1d76416c4a92afd6a9a48'
DB_NAME = 'tasas.db'
CSV_NAME = 'tasas_cambio.csv'

def obtener_tasas():
    url = f"http://api.currencylayer.com/live?access_key={ACCESS_KEY}&source=USD&currencies=CAD,COP&format=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get('success'):
            usd_cad = data['quotes']['USDCAD']
            usd_cop = data['quotes']['USDCOP']
            cad_cop = usd_cop / usd_cad
            timestamp = datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

            return {
                'timestamp': timestamp,
                'usd_cad': round(usd_cad, 4),
                'usd_cop': round(usd_cop, 4),
                'cad_cop': round(cad_cop, 4)
            }
        else:
            print(f"⚠ Error de API: {data['error']['info']}")
            return None

    except requests.RequestException as e:
        print(f"⚠ Error en la conexión: {e}")
        return None

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            usd_cad REAL,
            usd_cop REAL,
            cad_cop REAL
        )
    """)
    conn.commit()
    conn.close()

def guardar_tasas(tasas):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasas (timestamp, usd_cad, usd_cop, cad_cop)
        VALUES (?, ?, ?, ?)
    """, (tasas['timestamp'], tasas['usd_cad'], tasas['usd_cop'], tasas['cad_cop']))
    conn.commit()
    conn.close()
    print(f"✅ Datos guardados en la base de datos: {tasas}")

def guardar_csv(tasas):
    crear_encabezado = False
    try:
        with open(CSV_NAME, 'r'):
            pass
    except FileNotFoundError:
        crear_encabezado = True

    with open(CSV_NAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        if crear_encabezado:
            writer.writerow(['FechaHora', 'USD_CAD', 'USD_COP', 'CAD_COP'])
        writer.writerow([tasas['timestamp'], tasas['usd_cad'], tasas['usd_cop'], tasas['cad_cop']])
    print(f"✅ Datos guardados en {CSV_NAME}: {tasas}")

if __name__ == "__main__":
    inicializar_db()
    tasas = obtener_tasas()
    if tasas:
        guardar_tasas(tasas)
        guardar_csv(tasas)
