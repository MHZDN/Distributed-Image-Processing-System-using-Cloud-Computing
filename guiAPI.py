import pickle
import select
import socket
import logging
# from CL_For_Image import CL_Image_Preprocessing

# Configure logging
logging.basicConfig(filename='ui.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Clear the log file
open('ui.log', 'w').close()


#UK load balancer
# LOAD_BALANCER_IP="4.234.184.113"
#FR load balancer
# LOAD_BALANCER_IP="40.66.43.172"
#Global load balancer
LOAD_BALANCER_IP="20.8.176.72"
class guiAPI:
    def __init__(self):
        # self.CL = CL_Image_Preprocessing()
        # self.dnsName=DNSName
        self.port=5090
        self.sock=None
    def gray(self,img):
        # ip=self.getVmIP()
        logger.info(f"LBIP: {LOAD_BALANCER_IP}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((LOAD_BALANCER_IP, self.port))
        logger.info("Socket connected")
        self.start_process("Gray",img)
        op,result = self.receive_data()
        self.sock.close()
        self.sock=None
        return result
    def threshold(self,img):
        # ip=self.getVmIP()
        logger.info(f"LBIP: {LOAD_BALANCER_IP}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((LOAD_BALANCER_IP, self.port))
        logger.info("Socket connected")
        self.start_process("Threshold",img)
        op,result = self.receive_data()
        self.sock.close()
        self.sock=None
        return result
    def bright(self,img):
        # ip=self.getVmIP()
        logger.info(f"LBIP: {LOAD_BALANCER_IP}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((LOAD_BALANCER_IP, self.port))
        logger.info("Socket connected")
        self.start_process("Brighten",img)
        op,result = self.receive_data()
        self.sock.close()
        self.sock=None
        return result
    def dark(self,img):
        # ip=self.getVmIP()
        logger.info(f"LBIP: {LOAD_BALANCER_IP}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((LOAD_BALANCER_IP, self.port))
        logger.info("Socket connected")
        self.start_process("Darken",img)
        op,result = self.receive_data()
        self.sock.close()
        self.sock=None
        return result
    
    def processImage(self,inputImage,op):
        if op=="Gray":
            return self.gray(inputImage)
        elif op=="Brighten":
            return self.bright(inputImage)
        elif op=="Darken":
            return self.dark(inputImage)
        elif op=="Threshold":
            return self.threshold(inputImage)
            
    def start_process(self,op,image):
        try:
            logger.info("Start sending")
            self.send_data([op,image])
            
            
        except OSError as oErr:
            logger.info(f"OSError occured")
        except Exception as e:
            logger.info(f"Exception occured")
    
    def receive_data(self):
        timeout=5
        # Receive the data from the client
        data = b""
        ready_to_read, _, _ = select.select([self.sock], [], [])
        if ready_to_read:
            logger.info("Start receiving data")
            self.sock.settimeout(timeout)
            while True:
                try:
                    chunk = self.sock.recv(4096)
                    if not chunk:
                        break  # No more data being received
                    data += chunk
                except socket.timeout:
                # Timeout occurred, no more data being received
                    break
        # Deserialize the received data
        array = pickle.loads(data)
        logger.info("Returning received array")
        return array

    def send_data(self, data):
        # Serialize the array
        serialized_data = pickle.dumps(data)

        # Send the serialized array to the server
        self.sock.sendall(serialized_data)