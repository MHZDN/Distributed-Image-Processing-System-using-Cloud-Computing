import pickle
import queue
import select
import socket
import threading
import time
import logging
import cv2

# Set up logging
logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# data sent by masterVM
# ["op","channel","image","value","height","width"]
# data received from vms
# ["op","channel","processedimage"]
VMS_IP_Port = {
    "vm1": ["10.0.0.5", 5051],
    "vm2": ["10.0.0.6", 5052],
    "vm3": ["10.0.0.7", 5053]
}

def MasterTask(name, r, g, b, value, height=0, width=0):
    result_queue = queue.Queue(3)
    if name == "intensity-grey":
        processed = vm2.process(name, "ig", r, value, height, width)
        return processed
    if name == "threshold":
        processed = vm1.process(name, "th", r, value, height, width)
        return processed
    else:
        vm1.start_process(name, "r", r, value, height, width)
        vm2.start_process(name, "b", b, value, height, width)
        vm3.start_process(name, "g", g, value, height, width)
        time.sleep(0.01)
        vm1_receive_thread = threading.Thread(target=vm1.receive_process, args=(result_queue,))
        vm1_receive_thread.start()
        vm2_receive_thread = threading.Thread(target=vm2.receive_process, args=(result_queue,))
        vm2_receive_thread.start()
        vm3_receive_thread = threading.Thread(target=vm3.receive_process, args=(result_queue,))
        vm3_receive_thread.start()
        while not result_queue.full():
            continue
        adjusted_R = adjusted_G = adjusted_B = None
        for i in range(3):
            item = result_queue.get()
            if item[1] == "r":
                adjusted_R = item[2]
            elif item[1] == "b":
                adjusted_B = item[2]
            elif item[1] == "g":
                adjusted_G = item[2]
        processed = cv2.merge((adjusted_R, adjusted_G, adjusted_B))
    return processed


class VM:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.vmSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.vmSocket.connect((self.ip, self.port))

    def process(self, op, channel, image, value, height, width):
        try:
            logging.info("[ServerMaster]: Start sending")
            self.send_data([op, channel, image, value, height, width])
            logging.info("[ServerMaster]: Start receive process")
            received_data = self.receive_data()
            operation = received_data[0]
            ch = received_data[1]
            processed_image_channel = received_data[2]
            return processed_image_channel

        except OSError as oErr:
            logging.error(f"[ServerMaster]: OSError: {oErr}")
        except Exception as e:
            logging.error(f"[ServerMaster]: Exception: {e}")

    def start_process(self, op, channel, image, value, height, width):
        try:
            logging.info("[ServerMaster]: Start sending")
            self.send_data([op, channel, image, value, height, width])

        except OSError as oErr:
            logging.error(f"[ServerMaster]: OSError: {oErr}")
        except Exception as e:
            logging.error(f"[ServerMaster]: Exception: {e}")

    def receive_process(self, result_queue):
        try:
            logging.info("[ServerMaster]: Start receive process")
            received_data = self.receive_data()
            operation = received_data[0]
            ch = received_data[1]
            processed_image_channel = received_data[2]

            result_queue.put([operation, ch, processed_image_channel])

        except OSError as oErr:
            logging.error(f"[ServerMaster]: OSError: {oErr}")
        except Exception as e:
            logging.error(f"[ServerMaster]: Exception: {e}")

    def close_vm(self):
        self.send_data(["EXIT"])
        received_data = self.receive_data()
        self.vmSocket.close()

    def receive_data(self):
        timeout = 5
        data = b""
        ready_to_read, _, _ = select.select([self.vmSocket], [], [])
        if ready_to_read:
            logging.info("[ServerMaster]: Start receiving data")
            self.vmSocket.settimeout(timeout)
            while True:
                try:
                    chunk = self.vmSocket.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                except socket.timeout:
                    break
        array = pickle.loads(data)
        logging.info("[ServerMaster]: Returning received array")
        return array

    def send_data(self, data):
        serialized_data = pickle.dumps(data)
        self.vmSocket.sendall(serialized_data)


vm1 = VM(VMS_IP_Port["vm1"][0], VMS_IP_Port["vm1"][1])
vm2 = VM(VMS_IP_Port["vm2"][0], VMS_IP_Port["vm2"][1])
vm3 = VM(VMS_IP_Port["vm3"][0], VMS_IP_Port["vm3"][1])
