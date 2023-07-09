from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import onnxruntime as rt

app = Flask(__name__)

# Carregar o modelo ONNX de reconhecimento de emoções
emotion_model = rt.InferenceSession('model/FER-Emotion-Recognition.onnx')

# Carregar o modelo Haar Cascade para detecção de rostos
face_cascade = cv2.CascadeClassifier('model/haarcascade_frontalface_default.xml')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file found.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    try:
        # Salvar a imagem enviada pelo usuário
        image_path = 'app/uploads/' + file.filename
        file.save(image_path)

        # Carregar a imagem e convertê-la para escala de cinza
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detectar rostos na imagem
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Realizar o reconhecimento de emoções para cada rosto detectado
        emotions = []
        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (48, 48))  # Redimensionar a face para o tamanho esperado pelo modelo
            face = np.expand_dims(face, axis=0)  # Adicionar uma dimensão extra para representar o lote (batch)
            face = np.expand_dims(face, axis=3)  # Adicionar uma dimensão extra para representar os canais (escala de cinza)

            # Realizar a inferência no modelo ONNX para obter as probabilidades das emoções
            input_name = emotion_model.get_inputs()[0].name
            output_name = emotion_model.get_outputs()[0].name
            emotion_probs = emotion_model.run([output_name], {input_name: face.astype(np.float32)})[0]

            # Obter a emoção com a maior probabilidade
            emotion_label = np.argmax(emotion_probs)

            # Mapear o índice da emoção para a respectiva classe
            emotion_classes = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
            emotion = emotion_classes[emotion_label]

            emotions.append(emotion)

        return jsonify({'emotions': emotions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
