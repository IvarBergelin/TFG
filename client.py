import argparse
import base64
import json

import cv2
import numpy as np
import requests
import time
#import pdb; 

LABEL_MAP = {
    0: 'background',
    1: 'person',
    2: 'vehicle',
    3: 'bike',
}

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
    args.add_argument("--skip", type=int, default=0, help="Frameskipping.")
    args.add_argument("--min-score", type=float, default=0.1, help="Minimum score to consider detection as valid.")
    
    args = args.parse_args()
    
    server_ip = f'http://{args.ip}'

    if args.stream is None:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(args.stream)

    next_frame = args.skip
    while True: 
        #capture video frame by frame
        ret, frame = cap.read()

        if args.stream is not None:
            cap.set(1, next_frame)
            next_frame += args.skip
        else:
            next_frame -= 1
            if next_frame > 0:
                continue
            else:
                next_frame = args.skip

        #frame = cv2.resize(frame, (1280, 720))
        # frame_bgr = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2RGB)

        if not ret:
            break

        status_code, detections = post_img(url=server_ip, port=args.port, frame=frame)

        height, width, _ = frame.shape
        if status_code == 200:
        
            for i, box in enumerate(detections['boxes']):
                score = detections['scores'][i]
                class_id = detections['class_ids'][i]
                label = LABEL_MAP[class_id]

            
                if score < args.min_score:
                    continue

                x1,y1,x2,y2 = box
                print(x1,x2,y1,y2)
                x1 = int(x1*width)
                y1 = int(y1*height)
                x2 = int(x2*width)
                y2 = int(y2*height)
            
                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0) ,2)
                
                cv2.putText(frame, f'{label}: {score*100:.2f}%', (int(x1), int(y1)-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)
            

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
