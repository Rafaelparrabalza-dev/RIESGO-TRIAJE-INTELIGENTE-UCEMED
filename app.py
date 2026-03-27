# Updated app.py with web interface and QR features

from flask import Flask, request, jsonify
import qrcode

app = Flask(__name__)

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json.get('data')
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    qr_image = qrcode.make(data)
    qr_image_path = './static/qr_code.png'
    qr_image.save(qr_image_path)
    return jsonify({'message': 'QR Code generated', 'path': qr_image_path}), 200

@app.route('/')
def home():
    return 'Welcome to the RIESGO TRIAJE INTELIGENTE API!'

if __name__ == '__main__':
    app.run(debug=True)