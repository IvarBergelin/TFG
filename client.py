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
    args = argparse.ArgumentParser()
    args.add_argument("--stream", type=str, default=None, help="Stream to decode.")
    args.add_argument("--port", type=int, default=6000, help="Port to listen to incoming requests.")
    args.add_argument("--ip", type=str, default='127.0.0.1', help="Server's IP.")
    args.add_argument("--delay", type=float, default=0, help="Delay between frames (in seconds).")
    
    server_ip = f'http://{args.ip}'

    if args.stream is None:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(args.stream)
        
    while True:
        #capture video frame by frame
        ret, frame = cap.read()
        if not ret:
            break

        status_code, bounding_boxes = post_img(url=server_ip, port=args.port, frame=frame)

        height, width, _ = frame.shape
        if status_code == 200:
        
            for (x1,y1,x2,y2,) in bounding_boxes:
                x1 = int(x1*width)
                y1 = int(y1*width)
                x2 = int(x2*width)
                y2 = int(y2*width)
            
                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0) ,2)

            cv2.imshow('Results', frame)
            
            if args.delay:
                time.sleep(args.delay)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print(f'Request returned error {status_code}')

    #after the loop release the cap object
    cap.release()


if __name__ == "__main__":
    main()
