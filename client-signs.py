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

    req_url = f'{url}:{port}/detect'
    try:
        r = requests.post(req_url, data={
            'img': img64,
        })
    except ConnectionResetError:
        return False, None

    return process_response(r)


def detect_faces(frame, server_ip, port, min_score):
    status_code, detections = post_img(url=server_ip, port=port, frame=frame)

    height, width, _ = frame.shape
    face_detected = False
    if status_code == 200:
        for i, box in enumerate(detections['boxes']):
            score = detections['scores'][i]
            class_id = detections['class_ids'][i]
            label = LABEL_MAP[class_id]

        
            if score < min_score:
                continue

            # Hem detectat una cara
            # Activem reconeixement de signes
            face_detected = True 

            x1,y1,x2,y2 = box
            print(x1,x2,y1,y2)
            x1 = int(x1*width)
            y1 = int(y1*height)
            x2 = int(x2*width)
            y2 = int(y2*height)
        
            cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0) ,2)
            
            cv2.putText(frame, f'{label}: {score*100:.2f}%', (int(x1), int(y1)-10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)

    else:
            print(f'Request returned error {status_code}')
            
    return frame, face_detected


def detect_signs(frame, server_ip, port):
    status_code, sign_detections = post_img(url=server_ip, port=port, frame=frame)

    # Processar deteccio de signes

    return frame


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
    face_detected = False
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

        frame = cv2.resize(frame, (1280, 720))
        
        if not ret:
            break

        frame_original = frame.copy()

        frame, face_detected_in_frame = detect_faces(frame, args.server_ip_faces, args.port)
        if face_detected_in_frame:
            face_detected = True
        
        if face_detected:
            sign_detected = detect_signs(frame_original, args.server_ip_signs, args.port)

        cv2.imshow('Results', frame)
            
        if args.delay:
            time.sleep(args.delay)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    #after the loop release the cap object
    cap.release()


if __name__ == "__main__":
    main()
