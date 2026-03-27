# 🏥 RIESGO TRIAJE INTELIGENTE UCEMED

Sistema inteligente para calcular el riesgo cardiovascular basado en criterios OMS simplificados. Diseñado para optimizar el triaje en centros de salud.

## 🎯 Características

- ✅ Cálculo automático de riesgo cardiovascular
- ✅ Validación completa de datos
- ✅ Almacenamiento en base de datos SQLite
- ✅ API REST con Flask
- ✅ Generación de códigos QR para afiliación
- ✅ Historial de pacientes

## 📋 Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Rafaelparrabalza-dev/RIESGO-TRIAJE-INTELIGENTE-UCEMED.git
cd RIESGO-TRIAJE-INTELIGENTE-UCEMED
```

### 2. Crear entorno virtual

```bash
# En Linux/Mac
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 📚 API Endpoints

### 1. Verificar que está activa
**GET** `/`

```bash
curl http://localhost:5000/
```

**Respuesta:**
```json
{
  "mensaje": "SRP ACTIVO"
}
```

---

### 2. Calcular riesgo cardiovascular
**POST** `/calcular`

**Ejemplo de solicitud:**
```bash
curl -X POST http://localhost:5000/calcular \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "telefono": "1234567890",
    "edad": 55,
    "sexo": "M",
    "fuma": "Si",
    "diabetes": "No",
    "pa": "145",
    "colesterol": 220
  }'
```

**Parámetros:**
- `nombre` (string): Nombre del paciente **(requerido)**
- `telefono` (string): Teléfono del paciente
- `edad` (integer): Edad del paciente **(requerido)** (0-120)
- `sexo` (string): M o F **(requerido)**
- `fuma` (string): "Si" o "No" **(requerido)**
- `diabetes` (string): "Si" o "No" **(requerido)**
- `pa` (integer): Presión arterial sistólica **(requerido)** (60-250)
- `colesterol` (integer): Colesterol total **(requerido)** (0-400)

**Respuesta exitosa (201):**
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "riesgo": "ALTO",
  "score": 9
}
```

**Respuesta con errores (400):**
```json
{
  "errores": [
    "Edad debe estar entre 0 y 120",
    "Colesterol debe estar entre 0 y 400"
  ]
}
```

---

### 3. Obtener todos los pacientes
**GET** `/pacientes`

```bash
curl http://localhost:5000/pacientes
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Juan Pérez",
    "telefono": "1234567890",
    "edad": 55,
    "sexo": "M",
    "fuma": "Si",
    "diabetes": "No",
    "pa": 145,
    "colesterol": 220,
    "riesgo": "ALTO",
    "score": 9,
    "fecha": "2026-03-27T10:30:45.123456"
  }
]
```

## 📊 Niveles de Riesgo

| Nivel | Score | Interpretación |
|-------|-------|----------------|
| **BAJO** | ≤ 3 | Riesgo bajo de enfermedad cardiovascular |
| **MODERADO** | 4-6 | Riesgo moderado, requiere seguimiento |
| **ALTO** | ≥ 7 | Riesgo alto, referencia médica recomendada |

## 🔐 Validaciones

La aplicación valida automáticamente:
- ✅ Nombre no vacío (mínimo 2 caracteres)
- ✅ Edad entre 0 y 120 años
- ✅ Sexo solo "M" o "F"
- ✅ Presión arterial entre 60 y 250
- ✅ Colesterol entre 0 y 400
- ✅ Campos Si/No correctamente formateados

## 📱 Próximas Mejoras

- [ ] Generador de códigos QR para afiliación
- [ ] Interfaz web
- [ ] Autenticación de usuarios
- [ ] Exportar reportes en PDF
- [ ] Análisis estadístico de poblaciones
- [ ] Integración con sistemas EHR

## 👨‍💻 Autor

**Rafael Parra Balza**
- GitHub: [@Rafaelparrabalza-dev](https://github.com/Rafaelparrabalza-dev)

## 📄 Licencia

Este proyecto está bajo la licencia MIT - ver el archivo LICENSE para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

---

**Hecho con ❤️ para UCEMED**