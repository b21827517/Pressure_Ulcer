# I implemented flask operations and called backend functions in this python file
from flask import Flask, request, send_file, jsonify
import os
import base64
from PIL import Image
import sys
import argparse
import torch
import torch.nn as nn
import torchvision.models as models

from backend.run import image_writer
from backend.cropper import predictWithVGG16WithRoi
app = Flask(__name__)

#Getting image from gallery
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        print(file)
        file.save('uploads/' + file.filename)
        image_writer('uploads/' + file.filename)
        return 'File uploaded successfully'
    
#App is getting segmented image from backend
@app.route('/get_file', methods=['GET'])
def get_file():
    # Getting Segmented image 
    file_path = '/Users/efekalayci/Sondeneme/predicted_mask_2.png'
    file_name = os.path.basename(file_path)
    #Using pretrained vgg model
    vgg16_model = models.vgg16(pretrained=True)
    vgg16_model.classifier[6] = nn.Linear(4096, 4) # 4 types of outputs
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    vgg16_model.load_state_dict(torch.load(f"{app.config['PATH']}/vgg16_best_model.pt", map_location=DEVICE))
    #Getting predicted values
    l0, l1, l2, l3, n0, n1, n2, n3= predictWithVGG16WithRoi(f"{app.config['PATH']}/original_image.png",vgg16_model, DEVICE,file_path)
    values = f"{l0} {l1} {l2} {l3} {n0} {n1} {n2} {n3}"

    # Read file content and encode it to base64
    with open(file_path, "rb") as file:
        file_content = base64.b64encode(file.read()).decode('utf-8')

    # Create a response dictionary
    response = {
        'file_name': file_name,
        'file_content': file_content,
        'values': values,
    }

    return jsonify(response)
#Running flask on this host
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Flask app with custom host, port, and path.")
    parser.add_argument('--host', type=str, default='172.20.10.2', help='The host IP address to bind to.')
    parser.add_argument('--port', type=int, default=5000, help='The port to bind to.')
    parser.add_argument('--path', type=str, required=True, help='The path to a specific file or directory.')

    args = parser.parse_args()
        
    app.run(host=args.host, port=args.port)
