FROM python:3.7-slim as build

ARG COVA_COMMIT='b2471121eb2c7737c12a6c8181b824ee36b24f45'

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y -q --no-install-recommends protobuf-compiler libgl1-mesa-dev libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    grpcio-tools protobuf numpy \
    opencv-python-headless pandas \
    pillow imutils flask flask_restful response

RUN apt-get update && apt-get install --yes git && \
    git clone https://github.com/HiEST/cova-tuner.git && \
    cd cova-tuner && git checkout $COVA_COMMIT && \
    rm -rf /var/lib/apt/lists/*

FROM python:3.7-slim
COPY --from=build /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
COPY --from=build /cova-tuner /cova-tuner

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y -q --no-install-recommends libgl1-mesa-glx libsm6 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN cd /cova-tuner && pip install -e . && pip install openvino 

COPY server.py /

# WORKDIR ['/']
ENTRYPOINT ["python", "server.py"]
