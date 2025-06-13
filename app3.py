from flask import Flask, render_template_string, request
import requests
from datetime import datetime

app = Flask(__name__)
ACCESS_KEY = 'd75106e3fef1d76416c4a92afd6a9a48'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Monitor CAD-COP</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container my-5">
    <h1 class="mb-4">💱 Monitor de CAD ↔ COP</h1>
    <form method="get">
        <div class="row g-2 mb-3">
            <div class="col">
                <input type="number" step="any" class="form-control" name="monto" placeholder="Monto" value="{{ monto or '' }}">
            </div>
            <div class="col">
                <select class="form-select" name="moneda">
                    <option value="COP" {% if moneda == 'COP' %}selected{% endif %}>COP</option>
                    <option value="CAD" {% if moneda == 'CAD' %}selected{% endif %}>CAD</option>
                    <option value="USD" {% if moneda == 'USD' %}selected{% endif %}>USD</option>
                </select>
            </div>
            <div class="col">
                <button class="btn btn-primary w-100" type="submit">Calcular</button>
            </div>
        </div>
    </form>
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Última actualización: {{ timestamp }}</h5>
            <ul class="list-group">
                <li class="list-group-item">
                    <strong>CAD → COP:</strong> {{ cad_cop }} 
                    <span class="badge bg-{{ cad_status_color }}">{{ cad_status_msg }}</span>
                </li>
                <li class="list-group-item">
                    <strong>USD → COP:</strong> {{ usd_cop }} 
                    <span class="badge bg-{{ usd_status_color }}">{{ usd_status_msg }}</span>
                </li>
                <li class="list-group-item">
                    <strong>USD → CAD:</strong> {{ usd_cad }}
                    <span class="badge bg-{{ usd_cad_status_color }}">{{ usd_cad_status_msg }}</span>
                </li>
                {% if monto %}
                <li class="list-group-item">
                    <strong>Conversiones:</strong>
                    <br>{{ monto }} {{ moneda }} equivale a:
                    <ul>
                        <li>{{ res_cop }} COP</li>
                        <li>{{ res_cad }} CAD</li>
                        <li>{{ res_usd }} USD</li>
                    </ul>
                </li>
                {% endif %}
            </ul>
        </div>
    </div>
</div>
</body>
</html>
"""

def obtener_tasas():
    url = f"http://api.currencylayer.com/live?access_key={ACCESS_KEY}&source=USD&currencies=CAD,COP&format=1"
    response = requests.get(url)
    data = response.json()
    if data.get('success'):
        usd_cad = data['quotes']['USDCAD']
        usd_cop = data['quotes']['USDCOP']
        cad_cop = usd_cop / usd_cad
        timestamp = datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        return {
            'usd_cad': usd_cad,
            'usd_cop': usd_cop,
            'cad_cop': cad_cop,
            'timestamp': timestamp
        }
    else:
        return None

@app.route('/')
def home():
    tasas = obtener_tasas()
    if not tasas:
        return "<h1>⚠ Error al obtener las tasas</h1>"

    cad_cop = tasas['cad_cop']
    usd_cop = tasas['usd_cop']
    usd_cad = tasas['usd_cad']

    # Semáforo CAD → COP (para pagar)
    if cad_cop <= 3000:
        cad_status_color = "success"
        cad_status_msg = "¡Buen momento para comprar CAD!"
    elif cad_cop <= 3150:
        cad_status_color = "warning"
        cad_status_msg = "Cerca del objetivo"
    else:
        cad_status_color = "danger"
        cad_status_msg = "CAD caro, espera un poco"

    # Semáforo USD → COP
    if usd_cop >= 4000:
        usd_status_color = "success"
        usd_status_msg = "USD alto, buen momento para traer COP"
    elif usd_cop >= 3800:
        usd_status_color = "warning"
        usd_status_msg = "USD cerca del objetivo"
    else:
        usd_status_color = "danger"
        usd_status_msg = "USD bajo"

    # Semáforo USD → CAD (paridad)
    if 0.98 <= usd_cad <= 1.02:
        usd_cad_status_color = "success"
        usd_cad_status_msg = "¡Paridad casi perfecta!"
    elif 0.95 <= usd_cad < 0.98 or 1.02 < usd_cad <= 1.05:
        usd_cad_status_color = "warning"
        usd_cad_status_msg = "Cerca de la paridad"
    else:
        usd_cad_status_color = "danger"
        usd_cad_status_msg = "Lejos de la paridad"

    monto = request.args.get('monto', type=float)
    moneda = request.args.get('moneda', default='COP')

    res_cop = res_cad = res_usd = None

    if monto:
        if moneda == 'COP':
            res_cop = f"{monto:.2f}"
            res_cad = f"{monto / cad_cop:.2f}"
            res_usd = f"{monto / usd_cop:.2f}"
        elif moneda == 'CAD':
            res_cad = f"{monto:.2f}"
            res_cop = f"{monto * cad_cop:.2f}"
            res_usd = f"{monto / usd_cad:.2f}"
        elif moneda == 'USD':
            res_usd = f"{monto:.2f}"
            res_cad = f"{monto * usd_cad:.2f}"
            res_cop = f"{monto * usd_cop:.2f}"

    return render_template_string(HTML_TEMPLATE,
                                  cad_cop=f"{cad_cop:.2f}",
                                  usd_cop=f"{usd_cop:.2f}",
                                  usd_cad=f"{usd_cad:.2f}",
                                  timestamp=tasas['timestamp'],
                                  cad_status_color=cad_status_color,
                                  cad_status_msg=cad_status_msg,
                                  usd_status_color=usd_status_color,
                                  usd_status_msg=usd_status_msg,
                                  usd_cad_status_color=usd_cad_status_color,
                                  usd_cad_status_msg=usd_cad_status_msg,
                                  monto=monto,
                                  moneda=moneda,
                                  res_cop=res_cop,
                                  res_cad=res_cad,
                                  res_usd=res_usd)

if __name__ == '__main__':
    app.run(debug=True)
