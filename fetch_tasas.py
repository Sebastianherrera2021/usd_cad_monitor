import requests
import sqlite3
from datetime import datetime

ACCESS_KEY = 'd75106e3fef1d76416c4a92afd6a9a48'
DB_NAME = 'tasas.db'

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
                'usd_cad': usd_cad,
                'usd_cop': usd_cop,
                'cad_cop': cad_cop
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

if __name__ == "__main__":
    inicializar_db()
    tasas = obtener_tasas()
    if tasas:
        guardar_tasas(tasas)
