import socket
import cv2
import numpy as np

cv2.namedWindow("Image")

# Socket usa UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Cambiar la ip a convenir
host = "192.168.1.146"
port = 1080
server_address = (host, port)

while True:
    # Envía mensaje para iniciar transmición de video
    sent = sock.sendto("get".encode('utf-8'), server_address)

    data, server = sock.recvfrom(65507)
    print("Fragment size : {}".format(len(data)))
    if len(data) == 4:
        # Mensaje de error para el servidor
        if data == "FAIL":
            continue
    array = np.frombuffer(data, dtype=np.dtype('uint8'))
    img = cv2.imdecode(array, 1)
    # Se muestra el video
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Asking the server to quit")
        sock.sendto("quit".encode('utf-8'), server_address)
        print("Quitting")
        break
