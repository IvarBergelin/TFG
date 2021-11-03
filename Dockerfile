#Dockerfile, Image, Container
FROM python:3.9.5

# RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
#     apt-get install -y -q --no-install-recommends python3-opencv && \
#     rm -rf /var/lib/apt/lists/*

RUN pip install numpy opencv-python-headless pandas flask flask_restful response
ADD server_example.py .

ENTRYPOINT ["python", "./server_example.py"]
