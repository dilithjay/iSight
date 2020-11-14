FROM python:3.7-stretch

RUN pip3 install flask
RUN pip3 install protobuf
RUN pip3 install requests
RUN pip3 install opencv_python

#ADD http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_11_06_2017.tar.gz /
#RUN tar -xvf /ssd_mobilenet_v1_coco_11_06_2017.tar.gz

#ADD https://github.com/tprlab/docker-detect/archive/master.zip /
#RUN unzip /master.zip
RUN dpkg --add-architecture i386
RUN apt update
RUN apt install -y libgl1-mesa-glx

COPY /detect-app /detect-app

EXPOSE 80

#CMD ["python3", "/docker-detect-master/detect-app/dnn_ctrl.py", "/docker-detect-master/detect-app/data/pic.jpg"]
CMD ["python3", "/detect-app/app.py"]

# docker build -t gcr.io/isight123/isight docker-detect
# docker run isight
# curl -X POST -F "file=@pic.jpg" localhost:80/detect
