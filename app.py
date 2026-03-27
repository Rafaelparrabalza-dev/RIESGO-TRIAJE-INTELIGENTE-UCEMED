from flask import Flask, request, jsonify, render_template
from datetime import datetime
import sqlite3
import qrcode
from io import BytesIO
import base64
import os

app = Flask(__name__)

# Configuración
DB_PATH = 'srp.db'

def init_db():
    """Inicializa la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            edad INTEGER NOT NULL,
            sexo TEXT NOT NULL,
            fuma TEXT NOT NULL,
            diabetes TEXT NOT NULL,
            pa INTEGER NOT NULL,
            colesterol INTEGER NOT NULL,
            riesgo TEXT NOT NULL,
            score INTEGER NOT NULL,
            afiliado INTEGER DEFAULT 0,
            fecha TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def validar_datos(data):
    """Valida que los datos sean correctos"""
    errores = []
    
    nombre = data.get('nombre', '').strip()
    if not nombre or len(nombre) < 2:
        errores.append("Nombre inválido (mínimo 2 caracteres)")
    
    try:
        edad = int(data.get('edad', 0))
        if edad < 0 or edad > 120:
            errores.append("Edad debe estar entre 0 y 120")
    except ValueError:
        errores.append("Edad debe ser un número")
    
    sexo = data.get('sexo', '').upper()
    if sexo not in ['M', 'F']:
        errores.append("Sexo debe ser M o F")
    
    for campo in ['fuma', 'diabetes']:
        valor = data.get(campo, '').capitalize()
        if valor not in ['Si', 'No']:
            errores.append(f"{campo} debe ser Si o No")
    
    try:
        pa_str = data.get('pa', '120')
        pa = int(pa_str.split('/')[0]) if '/' in pa_str else int(pa_str)
        if pa < 60 or pa > 250:
            errores.append("Presión arterial inválida (60-250)")
    except (ValueError, IndexError):
        errores.append("Formato de presión arterial inválido")
    
    try:
        colesterol = int(data.get('colesterol', 180))
        if colesterol < 0 or colesterol > 400:
            errores.append("Colesterol debe estar entre 0 y 400")
    except ValueError:
        errores.append("Colesterol debe ser un número")
    
    return errores

def calcular_riesgo(edad, sexo, fuma, diabetes, pa, colesterol):
    """Calcula el riesgo cardiovascular (OMS simplificado)"""
    score = 0

    if edad >= 60:
        score += 3
    elif edad >= 45:
        score += 2

    if sexo == "M":
        score += 1

    if fuma == "Si":
        score += 2

    if diabetes == "Si":
        score += 3

    if pa >= 140:
        score += 2
    elif pa >= 130:
        score += 1

    if colesterol >= 240:
        score += 2
    elif colesterol >= 200:
        score += 1

    if score <= 3:
        nivel = "BAJO"
    elif score <= 6:
        nivel = "MODERADO"
    else:
        nivel = "ALTO"

    return nivel, score

def generar_qr_base64(texto):
    """Genera un código QR en base64"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(texto)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f"Error generando QR: {e}")
        return None

# ============ RUTAS WEB ============

@app.route('/')
def inicio():
    """Página principal"""
    return render_template('index.html')

@app.route('/triaje')
def triaje():
    """Página de triaje"""
    return render_template('triaje.html')

@app.route('/afiliacion/<int:paciente_id>')
def afiliacion(paciente_id):
    """Página de afiliación con QR"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM pacientes WHERE id = ?', (paciente_id,))
        paciente = c.fetchone()
        conn.close()
        
        if not paciente:
            return "Paciente no encontrado", 404
        
        url_afiliacion = f"http://localhost:5000/afiliar/{paciente_id}"
        qr_img = generar_qr_base64(url_afiliacion)
        
        return render_template('afiliacion.html', paciente=dict(paciente), qr=qr_img)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/afiliar/<int:paciente_id>', methods=['GET', 'POST'])
def afiliar(paciente_id):
    """Endpoint para afiliar paciente"""
    try:
        if request.method == 'POST':
            data = request.json
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('UPDATE pacientes SET afiliado = 1 WHERE id = ?', (paciente_id,))
            conn.commit()
            conn.close()
            
            return jsonify({"mensaje": "Paciente afiliado exitosamente", "paciente_id": paciente_id}), 200
        else:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM pacientes WHERE id = ?', (paciente_id,))
            paciente = c.fetchone()
            conn.close()
            
            if not paciente:
                return "Paciente no encontrado", 404
            
            return render_template('afiliar.html', paciente=dict(paciente))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pacientes-list')
def pacientes_list():
    """Página con lista de pacientes"""
    return render_template('pacientes.html')

# ============ API ENDPOINTS ============

@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    """API: Calcula el riesgo cardiovascular de un paciente"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        errores = validar_datos(data)
        if errores:
            return jsonify({"errores": errores}), 400
        
        nombre = data.get('nombre', '').strip()
        telefono = data.get('telefono', '').strip()
        edad = int(data.get('edad'))
        sexo = data.get('sexo', '').upper()
        fuma = data.get('fuma', '').capitalize()
        diabetes = data.get('diabetes', '').capitalize()
        pa = int(data.get('pa', '120').split('/')[0])
        colesterol = int(data.get('colesterol', 180))
        
        nivel, score = calcular_riesgo(edad, sexo, fuma, diabetes, pa, colesterol)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO pacientes 
            (nombre, telefono, edad, sexo, fuma, diabetes, pa, colesterol, riesgo, score, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, telefono, edad, sexo, fuma, diabetes, pa, colesterol, nivel, score, datetime.now().isoformat()))
        conn.commit()
        paciente_id = c.lastrowid
        conn.close()
        
        return jsonify({
            "id": paciente_id,
            "nombre": nombre,
            "riesgo": nivel,
            "score": score
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pacientes', methods=['GET'])
def api_pacientes():
    """API: Obtiene todos los pacientes registrados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM pacientes ORDER BY fecha DESC')
        pacientes = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify(pacientes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/paciente/<int:paciente_id>', methods=['GET'])
def api_paciente(paciente_id):
    """API: Obtiene un paciente específico"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM pacientes WHERE id = ?', (paciente_id,))
        paciente = c.fetchone()
        conn.close()
        
        if not paciente:
            return jsonify({"error": "Paciente no encontrado"}), 404
        
        return jsonify(dict(paciente)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/qr/<int:paciente_id>')
def api_qr(paciente_id):
    """API: Obtiene el QR de afiliación de un paciente"""
    try:
        url_afiliacion = f"http://localhost:5000/afiliar/{paciente_id}"
        qr_img = generar_qr_base64(url_afiliacion)
        
        if not qr_img:
            return jsonify({"error": "No se pudo generar el QR"}), 500
        
        return jsonify({"qr": qr_img, "paciente_id": paciente_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)