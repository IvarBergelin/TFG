#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import base64
import json
from json import JSONEncoder

from edge_autotune.dnn.infer import ModelIE

from numpy.lib.type_check import imag
from flask import Flask, Response
from flask_restful import Resource, Api, reqparse
import cv2
import numpy as np
import pandas as pd
import pdb

FACE_DETECT_MODEL = 'models/intel/face-detection-adas-0001/FP16/face-detection-adas-0001.xml'

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


class Show(Resource):

    def __init__(self, model_path) -> None:
        self.model = ModelIE(model_path)

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
        
        results = self.model.run([img])[0]
        # faces = []

        # for i, box in enumerate(results['boxes']):
        #     score = results['scores'][i]
        #     class_id = results['class_ids'][i]
        #     label = results['labels'][i]
            
        #     if score < 0.3:
        #         continue
            
        #     faces.append(box)

        #results = results[0]
        #pdb.set_trace()

        return Response(
            response=json.dumps({ 
                "data": results,
            }),
            status=200,
            mimetype='application/json'
        )


def start_server(
    port: int = 6000,
    model: str = None,
):
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Show, '/show', resource_class_kwargs={'model_path': model})
    app.run(port=port, host='0.0.0.0')
    

def main():
    args = argparse.ArgumentParser()
    args.add_argument("--port", type=int, default=6000, help="Port to listen to incoming requests.")
    args.add_argument("--model", type=str, default=FACE_DETECT_MODEL, help="Detection model.")
    
    config = args.parse_args()
    start_server(config.port, config.model)
    

if __name__ == '__main__':
    main()
