# -*- coding: utf-8 -*-
# Code adapted from Tensorflow Object Detection Framework
# https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb
# Tensorflow Object Detection Detector

import tensorflow as tf
import numpy as np
import imutils
import time
import cv2
import paho.mqtt.client as mqtt
import time
import logging
import os.path
from datetime import datetime

class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef() 
            with tf.compat.v2.io.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.compat.v1.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        start_time = time.time()
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})
        end_time = time.time()

        #print("Elapsed Time:", end_time-start_time)

        im_height, im_width,_ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0,i,0] * im_height),
                        int(boxes[0,i,1]*im_width),
                        int(boxes[0,i,2] * im_height),
                        int(boxes[0,i,3]*im_width))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()

#create functions for callback
def on_log(client, userdata, level, buf):
    logging.info(buf)
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag=True
    else:
        logging.info("bad connection returned code="+str(rc))
        client.loop_stop()
def on_disconnect(client, userdata, rc):
    logging.info("client disconnected")
def on_publish(client,userdata,mid):            
    logging.info("data published \n")  

if __name__ == "__main__":
    broker="pblredes.ddns.net"
    port=1883
    logging.basicConfig(level=logging.INFO)
    mqtt.Client.connected_flag=False
    cliente = mqtt.Client("Cam4")                          
    cliente.username_pw_set("pblredes", "pblredes1234")
    cliente.on_log = on_log
    cliente.on_connect = on_connect
    cliente.on_disconnect = on_disconnect
    cliente.on_publish = on_publish  
    cliente.connect(broker,port)            
    cliente.loop_start()
    while not cliente.connected_flag:
        time.sleep(1)

    model_path = 'faster_rcnn_inception_v2_coco_2018_01_28/frozen_inference_graph.pb'
    odapi = DetectorAPI(path_to_ckpt=model_path)
    threshold = 0.9  
    cap = cv2.VideoCapture('Video6.mp4')
    success, img = cap.read()
    success = True
    count = 1
    ciclo = 0
    ini = time.time()
    manda = True
    while success:
        cap.set(cv2.CAP_PROP_POS_MSEC, (count*1000))
        success, img = cap.read()
        if success:
            #img = cv2.resize(img, (1280, 720))
        
            # Resize the image to the correct size
            img = imutils.resize(img, width=800)

            
            cv2.imwrite("foto.jpg", img)
            f = open("foto.jpg", "rb") #3.7kiB in same folder
            fileContent = f.read()
            byteArr = bytearray(fileContent)
            ret = cliente.publish("camera1", byteArr, 0)
            print("published return="+str(ret))

            boxes, scores, classes, num = odapi.processFrame(img)

            # Visualization of the results of a detection.

			fim = time.time()
			if ((fim-ini)<=ciclo):
				manda = False
			else:
				manda = True
				ciclo = ciclo+5

			if(manda):
	            for i in range(len(boxes)):
	                # Class 1 represents human
	                if classes[i] == 1 and scores[i] > threshold:
	                    box = boxes[i]
	                    cv2.rectangle(img,(box[1],box[0]),(box[3],box[2]),(0,0,255),2)
	                    cv2.imwrite("lockdown/frame%d.jpg" %count, img)
	                    print("Detectou")  
	                    print("Enviando...")                
	                    if(os.path.exists("lockdown/frame%d.jpg" %count)):
	                        print("O arquivo existe")
	                        try:    
	                            f = open("lockdown/frame%d.jpg" %count, "rb") #3.7kiB in same folder
	                            fileContent = f.read()
	                            byteArr = bytearray(fileContent)
	                            ret = cliente.publish("logImagem", byteArr, 0)
	                            print("published return="+str(ret))
	                            f.close()
	                        except:
	                            print("não enviou ou abriu o arquivo") 
	                        tempo = datetime.now()
	                        envia = tempo.strftime("%d/%m/%Y %H:%M:%S")
	                        enviar = "Cam1 " + envia
	                        print(enviar)
	                        ret2 = cliente.publish("logTexto", enviar, 0)  #qos-0
	                        print("published return="+str(ret2))
	                    else:
	                        print("O arquivo não existe")                             

	            cv2.imshow("preview", img)
	            key = cv2.waitKey(1)
	            if key & 0xFF == ord('q'):
	                break
	            count +=1 
            
        