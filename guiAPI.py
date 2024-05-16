import os
import pickle
import select
import socket
import logging

# Configure logging
log_file = "ui.log"



logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

LOAD_BALANCER_IP = "20.8.176.72"

class guiAPI:
    def __init__(self):
        self.port = 5090
        self.sock = None

    def gray(self, img):
        try:
            logger.info(f"[Host]: LBIP: {LOAD_BALANCER_IP}")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((LOAD_BALANCER_IP, self.port))
            logger.info("[Host]: Socket connected")
            self.start_process("Gray", img)
            op, result = self.receive_data()
            return result
        except Exception as e:
            logger.error(f"Error in gray(): {e}")
            return None
        finally:
            if self.sock:
                self.sock.close()

    def threshold(self, img):
        try:
            logger.info(f"[Host]: LBIP: {LOAD_BALANCER_IP}")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((LOAD_BALANCER_IP, self.port))
            logger.info("[Host]: Socket connected")
            self.start_process("Threshold", img)
            op, result = self.receive_data()
            return result
        except Exception as e:
            logger.error(f"Error in threshold(): {e}")
            return None
        finally:
            if self.sock:
                self.sock.close()

    def bright(self, img):
        try:
            logger.info(f"[Host]: LBIP: {LOAD_BALANCER_IP}")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((LOAD_BALANCER_IP, self.port))
            logger.info("[Host]: Socket connected")
            self.start_process("Brighten", img)
            op, result = self.receive_data()
            return result
        except Exception as e:
            logger.error(f"Error in bright(): {e}")
            return None
        finally:
            if self.sock:
                self.sock.close()

    def dark(self, img):
        try:
            logger.info(f"[Host]: LBIP: {LOAD_BALANCER_IP}")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((LOAD_BALANCER_IP, self.port))
            logger.info("[Host]: Socket connected")
            self.start_process("Darken", img)
            op, result = self.receive_data()
            return result
        except Exception as e:
            logger.error(f"Error in dark(): {e}")
            return None
        finally:
            if self.sock:
                self.sock.close()

    def processImage(self, inputImage, op):
        if op == "Gray":
            return self.gray(inputImage)
        elif op == "Brighten":
            return self.bright(inputImage)
        elif op == "Darken":
            return self.dark(inputImage)
        elif op == "Threshold":
            return self.threshold(inputImage)

    def start_process(self, op, image):
        try:
            logger.info("[Host]: Start sending")
            self.send_data([op, image])
        except Exception as e:
            logger.error(f"Error in start_process(): {e}")

    def receive_data(self):
        timeout = 5
        data = b""
        ready_to_read, _, _ = select.select([self.sock], [], [])
        if ready_to_read:
            logger.info("[Host]: Start receiving data")
            self.sock.settimeout(timeout)
            while True:
                try:
                    chunk = self.sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                except socket.timeout:
                    break
        array = pickle.loads(data)
        logger.info("[Host]: Returning received array")
        return array

    def send_data(self, data):
        serialized_data = pickle.dumps(data)
        self.sock.sendall(serialized_data)
