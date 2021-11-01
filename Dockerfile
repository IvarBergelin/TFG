#Dockerfile, Image, Container
FROM python:3.9.5

ADD client_example.py .
ADD rebe.jpeg .

RUN pip install numpy opencv-python

CMD ["python3", "./client_example.py", "rebe.jpeg"]