#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import base64
import json
from json import JSONEncoder



from flask import Flask, Response
from flask_restful import Resource, Api, reqparse
import cv2
import numpy as np
import pandas as pd

haar_file = (cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier(haar_file)

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


class Show(Resource):
    def get(self):
        data = pd.DataFrame([], columns=['test'])
        data = data.to_dict()
        return {'data': data}, 200


    def post(self):
        print('received post request')
        parser = reqparse.RequestParser()

        parser.add_argument('img', required=True)
        args = parser.parse_args()

        img = base64.b64decode(args.img)
        nparr = np.frombuffer(img, np.uint8)
        img = cv2.imdecode(nparr, flags=1)
        
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray)
        
        return Response(
            response=json.dumps({ 
                "data": faces.tolist(),
            }),
            status=200,
            mimetype='application/json'
        )


def start_server(
    port: int = 6000,
):
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Show, '/show')
    app.run(port=port)
    

def main():
    args = argparse.ArgumentParser()
    args.add_argument("--port", type=int, default=6000, help="Port to listen to incoming requests.")
    
    config = args.parse_args()
    start_server(config.port)
    

if __name__ == '__main__':
    main()
