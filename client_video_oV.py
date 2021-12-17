import argparse
import base64
import json

import cv2
import numpy as np
import requests
import time
#import pdb; 


def process_response(response):
    results = json.loads(response.text)
    results = results.get('data', response.text)
    return response.status_code, results


def encode_img(frame, encoding):
    _, buf = cv2.imencode(encoding, frame)
    return buf


def post_img(url, port, frame: np.array, 
            encoding: str = 'png'):

    buf = encode_img(frame, '.' + encoding)
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

    cap = cv2.VideoCapture(0)
    print ("CAP: ",cap) 
    while True:
        #capture video frame by frame
        ret, frame = cap.read()
        if ret == False:
            print('NO FACE DETECTED')
            break

        #status_code, bounding_boxes = post_img(url=config.url, port=config.port, img=frame)
        status_code, bounding_boxes = post_img(url='http://127.0.0.1', port=6000, frame=frame)

        height, width, _ = frame.shape

        if status_code == 200:
            print('Request successful.')
        
            for (x1,y1,x2,y2,) in bounding_boxes:
                print(f'pre: {[x1,y2,x2,y2]}')
                x1 = int(x1*width)
                y1 = int(y1*width)
                x2 = int(x2*width)
                y2 = int(y2*width)
                print(f'post: {[x1,y2,x2,y2]}')
            
                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0) ,2)
        
            #breakpoint()

            cv2.imshow('Results', frame)
            #time.sleep(0.1)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
                #after the loop release the cap object
                cap.release()
       
        else:
            print(f'Request returned error {status_code}')


if __name__ == "__main__":
    main()
