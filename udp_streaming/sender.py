# For debugging :
# - run the server and remember the IP of the server
# And interact with it through the command line:
# echo -n "get" > /dev/udp/192.168.0.39/1080
# echo -n "quit" > /dev/udp/192.168.0.39/1080

# C:\Users\pablo\Documents\Pablo\Universidad\Trabajos\6. Sexto Semestre\Redes\Labs\Lab 4\Streaming UDP\Server\udp_streaming\github_udp_streaming

import socket
import cv2
import time
from threading import Thread, Lock

debug = True
jpg_quality = 10
# Cambiar la ip a convenir
host = "192.168.1.146"
port = 1080


class VideoGrabber(Thread):
        def __init__(self, jpeg_quality):
                Thread.__init__(self)
                self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
                # ------------------------------------------------------
                # Calcula los cuadros por segundo (fps) del video
                self.cap = cv2.VideoCapture('video.mp4')
                num_frames = 120
                start = time.time()
                for i in range(0, num_frames):
                    self.cap.read()
                end = time.time()
                seconds = end - start
                self.fps = num_frames/seconds
                self.cap.release()
                print("FPS del video: " + str(self.fps))
                # ------------------------------------------------------
                # Recupera el video a streamear
                self.cap = cv2.VideoCapture('video.mp4')
                # Configura los fps del video
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)
                self.running = True
                self.buffer = None
                self.lock = Lock()

        def stop(self):
                self.running = False

        def get_buffer(self):
                if self.buffer is not None:
                        self.lock.acquire()
                        cpy = self.buffer.copy()
                        self.lock.release()
                        return cpy

        def run(self):
                while self.running:
                        success, img = self.cap.read()
                        time.sleep(1/self.fps)
                        if not success:
                                continue
                        # Compresión JPG
                        self.lock.acquire()
                        result, self.buffer = cv2.imencode('.jpg', img, self.encode_param)
                        self.lock.release()


grabber = VideoGrabber(jpg_quality)
grabber.start()


def get_message():
    return grabber.get_buffer()


running = True

# DGRAM indica que el socket utiliza protocolo UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (host, port)

print('Iniciando en %s puerto %s\n' % server_address)

sock.bind(server_address)

while running:
        data, address = sock.recvfrom(4)
        data = data.decode('utf-8')
        if data == "get":
                buffer = get_message()
                if buffer is None:
                        continue
                if len(buffer) > 65507:
                        print("El mensaje es muy grande para un datagrama UDP")
                        sock.sendto("FAIL".encode('utf-8'), address)
                        continue
                sock.sendto(buffer.tobytes(), address)
        elif data == "quit":
                grabber.stop()
                running = False

print("Quitting..")
grabber.join()
sock.close()
