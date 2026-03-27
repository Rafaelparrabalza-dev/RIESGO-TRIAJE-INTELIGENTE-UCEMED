from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3
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
            fecha TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def validar_datos(data):
    """Valida que los datos sean correctos"""
    errores = []
    
    # Validar nombre
    nombre = data.get('nombre', '').strip()
    if not nombre or len(nombre) < 2:
        errores.append("Nombre inválido")
    
    # Validar edad
    try:
        edad = int(data.get('edad', 0))
        if edad < 0 or edad > 120:
            errores.append("Edad debe estar entre 0 y 120")
    except ValueError:
        errores.append("Edad debe ser un número")
    
    # Validar sexo
    sexo = data.get('sexo', '').upper()
    if sexo not in ['M', 'F']:
        errores.append("Sexo debe ser M o F")
    
    # Validar opciones Si/No
    for campo in ['fuma', 'diabetes']:
        valor = data.get(campo, '').capitalize()
        if valor not in ['Si', 'No']:
            errores.append(f"{campo} debe ser Si o No")
    
    # Validar presión arterial
    try:
        pa_str = data.get('pa', '120')
        pa = int(pa_str.split('/')[0]) if '/' in pa_str else int(pa_str)
        if pa < 60 or pa > 250:
            errores.append("Presión arterial inválida")
    except (ValueError, IndexError):
        errores.append("Formato de presión arterial inválido")
    
    # Validar colesterol
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

    # Edad
    if edad >= 60:
        score += 3
    elif edad >= 45:
        score += 2

    # Sexo
    if sexo == "M":
        score += 1

    # Hábito de fumar
    if fuma == "Si":
        score += 2

    # Diabetes
    if diabetes == "Si":
        score += 3

    # Presión arterial
    if pa >= 140:
        score += 2
    elif pa >= 130:
        score += 1

    # Colesterol
    if colesterol >= 240:
        score += 2
    elif colesterol >= 200:
        score += 1

    # Determinar nivel de riesgo
    if score <= 3:
        nivel = "BAJO"
    elif score <= 6:
        nivel = "MODERADO"
    else:
        nivel = "ALTO"

    return nivel, score

@app.route('/')
def inicio():
    """Endpoint de prueba"""
    return jsonify({"mensaje": "SRP ACTIVO"}), 200

@app.route('/calcular', methods=['POST'])
def calcular():
    """Calcula el riesgo cardiovascular de un paciente"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        # Validar datos
        errores = validar_datos(data)
        if errores:
            return jsonify({"errores": errores}), 400
        
        # Extraer datos validados
        nombre = data.get('nombre', '').strip()
        telefono = data.get('telefono', '').strip()
        edad = int(data.get('edad'))
        sexo = data.get('sexo', '').upper()
        fuma = data.get('fuma', '').capitalize()
        diabetes = data.get('diabetes', '').capitalize()
        pa = int(data.get('pa', '120').split('/')[0])
        colesterol = int(data.get('colesterol', 180))
        
        # Calcular riesgo
        nivel, score = calcular_riesgo(edad, sexo, fuma, diabetes, pa, colesterol)
        
        # Guardar en base de datos
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

@app.route('/pacientes', methods=['GET'])
def obtener_pacientes():
    """Obtiene todos los pacientes registrados"""
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)