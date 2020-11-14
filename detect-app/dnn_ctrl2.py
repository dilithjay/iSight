import dnn_conf
import cv2 as cv
import numpy as np

classFile = '/detect-app/coco.names'
classNames = []
with open(classFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configPath = '/detect-app/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = '/detect-app/frozen_inference_graph.pb'

net = None

def init():
    global net
    net = cv.dnn_DetectionModel(weightsPath, configPath)
    return net


def inference(img, thr=0.3):
    if img is None:
        return False, "No image"
    if net is None:
        return False, "No net"
    net.setInputSize(300, 300)
    net.setInputScale(1.0/127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)
    
    # classIds, confs, bbox = net.detect(img, confThreshold=thr)
    
    return True, net.detect(img, confThreshold=thr)

def build_detection(out):
    classIds, confs, bbox = out
    boxes = list(bbox)
    conf = list(np.array(confs).reshape(1,-1)[0])
    conf = list(map(float,conf))
    indices = cv.dnn.NMSBoxes(boxes,conf,0.3,0.2)
    ret = []
    for j in indices:
        i = j[0]
        a = {}
        a["class"] = int(classIds[i][0])
        a["name"] = classNames[classIds[i][0] - 1]
        a["score"] = float(confs[i][0])
        a["x"], a["y"], a["w"], a["h"] = bbox[i].tolist()
        ret.append(a)
    return ret

def detect(img):
    rc, out = inference(img)
    if not rc:
        return rc, out
    return True, build_detection(out)


if __name__ == '__main__':
    init()
    img = cv.imread(sys.argv[1])
    d = detect(img)
    print (d)
    
