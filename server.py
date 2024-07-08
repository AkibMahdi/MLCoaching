from flask import Flask, request, jsonify, send_file
import requests
import os
import io
from imageUploads.images import generator

app = Flask(__name__)

# Your OpenAI API key
api_key = 'sk-proj-uFrV5wTV7VLyBzss80nhT3BlbkFJsE1Mm7ID7mKlu6JwgxyL'

# Base URL for OpenAI API
base_url = 'https://api.openai.com/v1/files'


@app.route('/')
def index():
    return "Welcome to the Image Generation API. Use the /generate_images endpoint to generate images."

# file upload functions
def upload_file(file_path, purpose="fine-tune"):
    with open(file_path, 'rb') as file:
        response = requests.post(
            base_url,
            headers={'Authorization': f'Bearer {api_key}'},
            files={'file': file},
            data={'purpose': purpose}
        )
    return response.json()


def list_files():
    response = requests.get(
        base_url,
        headers={'Authorization': f'Bearer {api_key}'}
    )
    return response.json()


def retrieve_file(file_id):
    response = requests.get(
        f'{base_url}/{file_id}',
        headers={'Authorization': f'Bearer {api_key}'}
    )
    return response.json()


def delete_file(file_id):
    response = requests.delete(
        f'{base_url}/{file_id}',
        headers={'Authorization': f'Bearer {api_key}'}
    )
    return response.json()


def retrieve_file_content(file_id):
    response = requests.get(
        f'{base_url}/{file_id}/content',
        headers={'Authorization': f'Bearer {api_key}'}
    )
    return response.content

# file upload routes
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join('/tmp', file.filename)
    file.save(file_path)
    
    purpose = request.form.get('purpose', 'fine-tune')
    response = upload_file(file_path, purpose)
    
    os.remove(file_path)
    return jsonify(response)


@app.route('/files', methods=['GET'])
def files():
    response = list_files()
    return jsonify(response)


@app.route('/files/<file_id>', methods=['GET'])
def get_file(file_id):
    response = retrieve_file(file_id)
    return jsonify(response)


@app.route('/files/<file_id>/content', methods=['GET'])
def get_file_content(file_id):
    content = retrieve_file_content(file_id)
    return send_file(
        io.BytesIO(content),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=f'{file_id}.txt'
    )




@app.route('/files/<file_id>', methods=['DELETE'])
def delete(file_id):
    response = delete_file(file_id)
    return jsonify(response)


# image route 

@app.route('/generate_images', methods=['POST'])
def generate_images():
    data = request.json
    prompt = data.get('prompt')
    n = data.get('n', 1)
    size = data.get('size', '1024x1024')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        file_paths = generator(prompt, n, size)
        return jsonify({'file_paths': file_paths}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
   app.run(port=5500, debug=True)