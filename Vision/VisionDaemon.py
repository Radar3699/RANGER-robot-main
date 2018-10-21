from models.yolo import Yolo2Model
from models.yolo import YoloNewModel
from utils.general import format_predictions, format_notification
from web.routes import routes
from log_config import LOGGING
import cv2
import json
import time
import threading
import logging.config
from devicehive_webconfig import Server, Handler
from threading import Thread
import pafy

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('detector')

class VideoStreamThread:
    def __init__(self,src=0):
        # init video stream and read first frame
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped=False

    def start(self):
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed,self.frame)=self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped=True

class myThread1(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server1 = Daemon1(DeviceHiveHandler, routes=routes,server_address=('0.0.0.0',8001))
    def run(self):
        self.server1.start()

class myThread2(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server2 = Daemon2(DeviceHiveHandler, routes=routes,server_address=('0.0.0.0',8002))
    def run(self):
        self.server2.start()

class DeviceHiveHandler(Handler):
    _device = None

    def handle_connect(self):
        self._device = self.api.put_device(self._device_id)
        super(DeviceHiveHandler, self).handle_connect()

    def send(self, data):
        if isinstance(data, str):
            notification = data
        else:
            try:
                notification = json.dumps(data)
            except TypeError:
                notification = str(data)

        self._device.send_notification(notification)



class Daemon1(Server):
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, cv2.COLOR_LUV2LBGR]

    _detect_frame_data = None
    _detect_frame_data_id = None
    _cam_thread = None

    def __init__(self,*args,**kwargs):
        super(Daemon1, self).__init__(*args,**kwargs)
        self._detect_frame_data_id = 0
        self._cam_thread = threading.Thread(target=self._cam_loop, name='cam')
        self._cam_thread.setDaemon(True)

    def _on_startup(self):
        self._cam_thread.start()

    def _cam_loop(self):

        # DEBUG:PiCam Stream
        # cam = cv2.VideoCapture('http://192.168.1.6:8080/?action=stream')

        # Multi Threaded PiCam stream
        cam = VideoStreamThread('http://192.168.1.7:8080/?action=stream')
        cam.start()

        # DEBUG: Youtube stream test
        # url = 'https://youtu.be/W1yKqFZ34y4'
        # vPafy = pafy.new(url)
        # play = vPafy.getbest(preftype="webm")
        # cam = cv2.VideoCapture(play.url)

        source_h = cam.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        source_w = cam.stream.get(cv2.CAP_PROP_FRAME_WIDTH)

        # Init New Model
        NewModel = YoloNewModel(input_shape=(source_h, source_w, 3))
        NewModel.init()

        # Init COCO model
        model = Yolo2Model(input_shape=(source_h, source_w, 3))
        model.init()

        start_time = time.time()
        frame_num = 0
        fps = 0
        try:
            while self.is_running:
                frame = cam.read().copy()

                # COCO Predictions
                predictions = model.evaluate(frame)

                # New Predictions
                NewPredictions = NewModel.evaluate(frame)

                for o in NewPredictions:
                    x1 = o['box']['left']
                    x2 = o['box']['right']

                    y1 = o['box']['top']
                    y2 = o['box']['bottom']

                    color = o['color']
                    class_name = o['class_name']

                    # Draw box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    # Draw label
                    (test_width, text_height), baseline = cv2.getTextSize(
                        class_name, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 1)
                    cv2.rectangle(frame, (x1, y1),
                                  (x1+test_width, y1-text_height-baseline),
                                  color, thickness=cv2.FILLED)
                    cv2.putText(frame, class_name, (x1, y1-baseline),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)

                end_time = time.time()
                fps = fps * 0.9 + 1/(end_time - start_time) * 0.1
                start_time = end_time

                # Draw additional info
                frame_info = 'Frame: {0}, FPS: {1:.2f}'.format(frame_num, fps)
                cv2.putText(frame, frame_info, (10, frame.shape[0]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                logger.info(frame_info)

                self._detect_frame_data_id = frame_num
                _, img = cv2.imencode('.jpg', frame, self.encode_params)
                self._detect_frame_data = img

                if NewPredictions:
                    formatted = format_predictions(NewPredictions)
                    logger.info('Predictions: {}'.format(formatted))
                    self._send_dh(format_notification(NewPredictions))

                frame_num += 1

        finally:
            # cam.release()
            cam.stop()
            model.close()
            NewModel.close()

    def _send_dh(self, data):
        if not self.dh_status.connected:
            logger.error('Devicehive is not connected')
            return

        self.deviceHive.handler.send(data)

    def get_frame(self):
        return self._detect_frame_data, self._detect_frame_data_id


class Daemon2(Server):
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, cv2.COLOR_LUV2LBGR]

    _detect_frame_data = None
    _detect_frame_data_id = None
    _cam_thread = None

    def __init__(self,*args,**kwargs):
        super(Daemon2, self).__init__(*args,**kwargs)
        self._detect_frame_data_id = 0
        self._cam_thread = threading.Thread(target=self._cam_loop, name='cam')
        self._cam_thread.setDaemon(True)

    def _on_startup(self):
        self._cam_thread.start()

    def _cam_loop(self):
        logger.info('Start camera loop')
        ###

        # PiCam Stream
        # cam = cv2.VideoCapture('http://192.168.1.6:8080/?action=stream')

        # Multi Threaded PiCam stream
        # cam = VideoStreamThread('http://192.168.1.7:8080/?action=stream')
        # cam.start()

        # Multi Threaded Amcrest Stream
        cam = VideoStreamThread('rtsp://admin:bebooz123@192.168.1.5:80/cam/realmonitor?channel=1&subtype=0')
        cam.start()

        source_h = cam.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        source_w = cam.stream.get(cv2.CAP_PROP_FRAME_WIDTH)

        model = Yolo2Model(input_shape=(source_h, source_w, 3))
        model.init()

        start_time = time.time()
        frame_num = 0
        fps = 0
        try:
            while self.is_running:
                frame = cam.read().copy()
                predictions = model.evaluate(frame)

                for o in predictions:
                    x1 = o['box']['left']
                    x2 = o['box']['right']

                    y1 = o['box']['top']
                    y2 = o['box']['bottom']

                    color = o['color']
                    class_name = o['class_name']

                    # Draw box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    # Draw label
                    (test_width, text_height), baseline = cv2.getTextSize(
                        class_name, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 1)
                    cv2.rectangle(frame, (x1, y1),
                                  (x1+test_width, y1-text_height-baseline),
                                  color, thickness=cv2.FILLED)
                    cv2.putText(frame, class_name, (x1, y1-baseline),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)

                end_time = time.time()
                fps = fps * 0.9 + 1/(end_time - start_time) * 0.1
                start_time = end_time

                # Draw additional info
                frame_info = 'Frame: {0}, FPS: {1:.2f}'.format(frame_num, fps)
                cv2.putText(frame, frame_info, (10, frame.shape[0]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                logger.info(frame_info)

                self._detect_frame_data_id = frame_num
                _, img = cv2.imencode('.jpg', frame, self.encode_params)
                self._detect_frame_data = img

                if predictions:
                    formatted = format_predictions(predictions)
                    logger.info('Predictions: {}'.format(formatted))
                    self._send_dh(format_notification(predictions))

                frame_num += 1

        finally:
            cam.stop()
            model.close()

    def _send_dh(self, data):
        if not self.dh_status.connected:
            logger.error('Devicehive is not connected')
            return

        self.deviceHive.handler.send(data)

    def get_frame(self):
        return self._detect_frame_data, self._detect_frame_data_id

if __name__ == '__main__':
    thread2 = myThread2()
    thread1 = myThread1()
    thread2.start()
    thread1.start()


