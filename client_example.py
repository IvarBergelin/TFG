import argparse
import base64
import json

import cv2
import numpy as np
import requests


def process_response(response):
    results = json.loads(response.text)
    results = results.get('data', response.text)
    return response.status_code, results


def encode_img(img, encoding):
    _, buf = cv2.imencode(encoding, img)
    return buf


def post_img(url, port, img: np.array, 
            encoding: str = 'png'):

    buf = encode_img(img, '.' + encoding)
    img64 = base64.b64encode(buf)

    req_url = f'{url}:{port}/show'
    try:
        r = requests.post(req_url, data={
            'img': img64,
        })
    except ConnectionResetError:
        return False, None

    return process_response(r)


def main():
    args = argparse.ArgumentParser()
    args.add_argument("image", type=str, help="Path to the image to send to the server.")
    args.add_argument("--url", type=str, default='http://172.17.0.2', help="Server's url.")
    args.add_argument("--port", type=int, default=6000, help="Port to listen to incoming requests.")
    

    config = args.parse_args()

    img = cv2.imread(config.image)
    status_code, bounding_boxes = post_img(url=config.url, port=config.port, img=img)

    if status_code == 200:
        print('Request successful.')
        
        for (x,y,w,h) in bounding_boxes:
            print (x,y,w,h)
            
            #cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

        #cv2.imshow("Results", img)
        #cv2.waitKey(0)
    else:
        print(f'Request returned error {status_code}')


if __name__ == "__main__":
    main()
