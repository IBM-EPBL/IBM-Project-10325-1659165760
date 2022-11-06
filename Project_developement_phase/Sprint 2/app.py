from flask import Flask, render_template, request
import requests
from tensorflow.keras.models import load_model
from keras.preprocessing import image
import keras
import tensorflow as tf
import numpy as np
import json
from json import JSONEncoder
from ibm_watson_machine_learning import APIClient
import os

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

app = Flask(__name__)

@app.route('/')
def index_view():
    return render_template('index.html')

def image_proces(filename) :
    img = load_img(filename, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x

UPLOAD_FOLDER = '/home/wintermute/IBM Final/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/classify', methods=['POST'])
def classify():
    
    file = request.files['fileupload']
    file.save(app.config['UPLOAD_FOLDER'] + file.filename)
    if request.method == 'POST':
        file_path = os.path.join('uploads', file.filename)

        img = keras.utils.load_img(file_path, target_size=(64,64))
        x = tf.keras.utils.img_to_array(img)
        x = np.expand_dims(x, axis=0)

        numpyData = {"input_data": x}
        encodedNumpyData = json.dumps(numpyData, cls=NumpyArrayEncoder)

        API_KEY = "Jt6zCW766j8adRl2c-fKzm1laLnAylF1FQZTByox1nbX"
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        mltoken = token_response.json()["access_token"]

        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

        payload_scoring = {
	        "input_data": [{
		    "fields": [],
		    "values": x.tolist()
	    }]
        }

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/361bab85-a294-4866-a61d-94106be4aec0/predictions?version=2022-11-05', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
    res = response_scoring.json()['predictions'][0]['values'][0][0]
    count = 0
    types = ['Left Bundle Branch Block', 'Normal', 'Premature Atrial Contraction', 'Premature Ventricular Contractions', 'Right Bundle Branch Block', 'Ventricular Fibrillation']
    pos = res.index(1.0)
    return render_template('index.html', result = types[pos])

    
if __name__ == '__main__':
    app.run(debug=True, port=9300)