import requests
import time
import json
import sys
import os
import numpy as np
import cv2 as cv
import io
import imutils
from imutils.video import VideoStream
from imutils.video import FPS

from PIL import Image
import pytesseract

import pyttsx3
engine = pyttsx3.init()

import speech_recognition as sr
r = sr.Recognizer()

from pygame import mixer
mixer.init()
mixer.music.load("select.mp3")

# for youtube
import pywhatkit
# for wikipedia
import wikipedia
# for getting time
from datetime import datetime

URL = "http://35.240.223.99:8080"

def request_detect(f):
    try:
        params = dict (file = f)
        resp = requests.post(URL + "/detect", files=params, verify=False)
        print(resp)
        if resp.status_code == requests.codes.ok:
            return 0, resp.json()
        return resp.status_code, resp.content
    except:
        return 503, None

def read_file(path):
    with open(path, "rb") as f:
        return f.read()

def to_memfile(content):
    memfile = io.BytesIO()
    memfile.write(content)
    memfile.seek(0)
    return memfile

def detect_file(path):
    with open(path, "rb") as f:
        return request_detect(f)

def detect_img(img):
    _, img_encoded = cv.imencode('.jpg', img)
    return request_detect(to_memfile(img_encoded))

with open('labels', 'r') as file:
    labels = file.read().split('\n')

def speak(speak_text):
    engine.say(speak_text)
    engine.runAndWait()

def findObject(obj, r):
    # thresholds = {'bottle': 0.3, 'person': 0.7, 'laptop': 0.6}
    print(r)
    for i in r[:-1]:
        print(i)
        if i['name'] == obj: # and i['name'] in thresholds:
            print(i)
            return (i['x'], i['y'])

def locationToText(cords):
    txt = ""
    c_x = cords[0]/w
    c_y = cords[1]/h
    
    if c_x > 0.7:
        txt = "right"
    elif c_x < 0.3:
        txt = "left"
    else:
        txt = "center"
    return txt

cap = VideoStream(src=0, usePiCamera=True).start()
check = True
fps = FPS().start()

w = 300
h = 225

def look_around(t):
    speak("Looking at what's in front of you.")
    t += time.time()
    detections = {}
    while time.time() < t:
        try:
            img = cap.read()
            img = imutils.resize(img, width=300)
        except:
            continue
        err, R = detect_img(img)
        for i in R[:-1]:
            if i['score'] > 0.3:
                name = i['name']
                pos = (i['x'], i['y'])
                if name in detections:
                    detections[name].append(pos)
                else:
                    detections[name] = [pos]
                print('Found {} at {} with {}% possibility'.format(name, locationToText(pos), round(i['score'] * 100, 2)))
                speak('Found {} at {}'.format(name, locationToText(pos)))

#----------------Single Frame Detection------------------
try_again = False
command = ""
while True:
    if not try_again:
        # Get user command
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print('speak')
            speak("How can I help you?")
            # Listen and convert from speech to text
            audio = r.listen(source,phrase_time_limit=5)
            try:
                text = r.recognize_google(audio, show_all=True)
                commands = [i['transcript'] for i in text['alternative']]
                print(commands)
                mixer.music.play()
            except:
                print("error")
                continue
        
        item = ''
        # Loop through all possible commands
        for i in commands:
            i = i.lower()
            # if user wants to find something in view
            if 'find' in i:
                command = i
                items = i.split()
                for i in items:
                    if i in labels:
                        item = i
                        break
            # if user wants to know what's around them
            elif 'look around' in i:
                command = 'look around'
                break
            # if user wants to read a text
            elif 'read' in i:
                command = 'read'
                break
            # if user wants to search Wikipedia
            elif 'search wikipedia for ' in i:
                command = i.replace('search wikipedia for', '')
                try:
                    results = wikipedia.search(command)
                    print(results[0])
                    wiki_result = wikipedia.summary(results[0], 1)
                    print(wiki_result)
                    speak(wiki_result)
                except:
                    speak("Couldn't find wikipedia article for " + command)
                break
            # if user wants to search YouTube
            elif 'search youtube for ' in i:
                command = i.replace('search youtube for', '')
                pywhatkit.playonyt(command)
                break
            # if user wants to check time
            elif "time" in i:
                cur_time = datetime.now().strftime('%I:%M %p')
                speak("The current time is " + cur_time)
                break
    try_again = False
    if 'find' in command:
        speak("Looking for " + item)
        totx, toty, count = 0, 0, 0
        # Read image from camera (get the average location from 2 images for accuracy)
        for i in range(3):
            try:
                img = cap.read()
                print(img.shape)
                img = imutils.resize(img, width=300)
            except:
                continue
            # Detect image by running inference on gcloud
            err, R = detect_img(img)
            # Check if detection score above threshold
            print(err)
            pos = findObject(item, R)
            # In case object not detected accurately
            if pos:
                x, y = pos
                totx += x
                toty += y
                count += 1
        if count:
            totx /= count
            toty /= count
        print(totx, toty)
        # Speak location through text to speech
        if count > 0:
            print("Found {} to your {}".format(item, locationToText((totx, toty))))
            speak("Found {} to your {}".format(item, locationToText((totx, toty))))
        else:
            print("Couldn't find", item)
            speak("Couldn't find " + item)
            # try_again = 'yes' in input("Would you like me to try again? ")
            ask = True
            while ask:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    speak("Would you like me to look again?")
                    audio = r.listen(source,phrase_time_limit=5)
                    try:
                        text = r.recognize_google(audio, show_all=True)
                        commands = [i['transcript'] for i in text['alternative']]
                        print(commands)
                        mixer.music.play()
                        ask = False
                    except:
                        print("error")
                        ask = True
                        continue
                    for i in commands:
                        if "yes" in i:
                            try_again = True
                            break
            
    elif 'look around' in command:
        look_around(5)
    elif 'read' in command:
        speak('Reading')
        try:
            img = cap.read()
            image = imutils.resize(img, width=300)
        except:
            continue
        im = Image.fromarray(img)
        text = pytesseract.image_to_string(im, lang='eng')
        if text != '':
            speak(text)
        else:
            speak("I couldn't find any text")
#--------------------------------------------------------

