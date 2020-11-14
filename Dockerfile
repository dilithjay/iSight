FROM python:3.7-stretch

RUN pip3 install flask
RUN pip3 install protobuf
RUN pip3 install requests
RUN pip3 install opencv_python

# required to fix an error that occurs due to missing packages
RUN dpkg --add-architecture i386
RUN apt update
RUN apt install -y libgl1-mesa-glx

COPY /detect-app /detect-app

EXPOSE 80

CMD ["python3", "/detect-app/app.py"]
