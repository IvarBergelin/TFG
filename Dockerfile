#Dockerfile, Image, Container
FROM python:3.9.5

ADD client_example.py .
ADD rebe.jpeg .

RUN pip install --upgrade pip
RUN pip install numpy
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python
RUN pip install requests

CMD ["python", "./client_example.py", "rebe.jpeg"]