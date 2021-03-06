# iSight
iSight is a smart assist for the visually impaired. It takes the visual input through a camera mounted on a cap and gives an auditory output to the user regarding the contents in the camera's vicinity.

### Demo
https://drive.google.com/file/d/1cpjqhke6yeJiW5cuS2AoX2o3VNE7mBYt/view?usp=sharing

### Usage Scenario
Currently, the scenario is such that the user gives verbal instructions to the system like "Find bottle" and the system in turn scans the view and informs the user if the object that is being searched for is in the camera's view. This scanning is done in realtime and the information can be used to identify the objects. The system can be further updated to accomplish other tasks such as playing music, YouTube or web browsing (search results should be provided using text to speech).

### Software Aspect
The system would be running on a Raspberry Pi. The model has not been decided yet. First speech recognition is used to get the user commands. The video feed from the camera is analyzed frame by frame and the requested object to be searched is looked for. Each frame is passed through a pre-trained model (currently using the tensorflow models trained on the COCO dataset; different models are being tested to identify the best model for the purpose). This model would preferably be in the cloud and the inference would run on it as well in order to save fps. The information about the detections will be used to identify if the requested object is in the camera's view. If it is, text to speech python libraries would be used to inform the user about it's location (whether it is at the center, left or right of the user; the output can be configured to be more precise about the location).

### Progress Update (21/06/2020)
Implemented IBM's MAX object detector on the Raspberry Pi. The requests for predictions were issued from the Raspberry Pi. These requests were recieved by a laptop which was running the server. The inference was run on this laptop and the predictions were sent back to the Raspberry Pi as a .json file. This interaction was done using ngrok which displays the locally hosted web server (on the laptop) as a subdomain of the ngrok servers. This enables the Raspberry Pi to recieve the predictions by requesting from this ngrok website. The prediction took approximately 6 seconds. This speed is insufficient. Hosting on a cloud server with better specs than the laptop should be attempted.

### Progress Update (22/06/2020)
Hosted the MAX object detector on Google Cloud's Compute Engine. The object detector was put into a Docker container and Kubernetes cluster was formed using the docker images. First, the speed was tested with 5 instances of the image. This took about 5-6 seconds per prediction. Afterwards, a different docker image (taken from [here](https://github.com/tprlab/docker-detect)) was tested. This gave faster responses than the MAX object detector even when run on the localhost. This too was hosted on Google Cloud as the previous docker image. However, this time, 10 instances (pods) of the image were run on Kubernetes. This system gave a response at about 2.45 fps over the span of 30 seconds (less than half a second per frame). This seems to be a sufficient performance for the required task. The fps is expected to decrease as the rest of the components are implemented but it is not expected to be an issue.

### Progress Update (12/08/2020)
A custom Dockerfile and the respective Docker image was created such that it includes just the components we require. Another thing that should be attempted is running the inference (Docker image) on a machine with GPU.

### Progress Update (23/09/2020)
Implemented the text to speech, speech recognition and the logic for switching between modes on command. For speech recognition, the python library called SpeechRecognition was used. Steven Hickson's PiAUISuite was also tried for speech recognition. However, the version of Raspbian installed was incompatible with that which PiAUISuite was created for. Used Pytesseract to add a feature to be able to read text that was placed in front of the camera. It wasn't too accurate under low lit conditions. The text has to be clear as well.
Furthermore, implemented capabilities for voice controlled YouTube searching and Wikipedia searching using the python libraries, pywhatkit and wikipedia, respectively.
