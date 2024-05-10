import pickle
import select
import socket
# from CL_For_Image import CL_Image_Preprocessing



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
        print(f"LBIP:{LOAD_BALANCER_IP}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((LOAD_BALANCER_IP, self.port))
        print(f"sock connected")
        self.start_process("Gray",img)
        op,result = self.receive_data()
        self.sock.close()
        self.sock=None
        return result
    def threshold(self,img):
        # ip=self.getVmIP()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((LOAD_BALANCER_IP, self.port))
        self.start_process("Threshold",img)
        op,result = self.receive_data()
        self.sock.close()
        self.sock=None
        return result
    def bright(self,img):
        # ip=self.getVmIP()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((LOAD_BALANCER_IP, self.port))
        self.start_process("Brighten",img)
        op,result = self.receive_data()
        self.sock.close()
        self.sock=None
        return result
    def dark(self,img):
        # ip=self.getVmIP()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((LOAD_BALANCER_IP, self.port))
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
            print("start sending")
            self.send_data([op,image])
            
            
        except OSError as oErr:
            print("OSError: {0}".format(oErr))
        except Exception as e:
            print("Exception: {0}".format(e))
    
    def receive_data(self):
        timeout=5
        # Receive the data from the client
        data = b""
        ready_to_read, _, _ = select.select([self.sock], [], [])
        if ready_to_read:
            print(f"start receiving data")
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
        print("returning received array")
        return array

    def send_data(self, data):
        # Serialize the array
        serialized_data = pickle.dumps(data)

        # Send the serialized array to the server
        self.sock.sendall(serialized_data)