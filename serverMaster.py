import pickle
import queue
import select
import socket
import threading
import time

import cv2

#data sent by masterVM
#   ["op","channel","image","value","height","width"]
#data received from vms
#   ["op","channel","processedimage"]
VMS_IP_Port={"vm1":["10.0.0.5",5051],
             "vm2":["10.0.0.6",5052],
             "vm3":["10.0.0.7",5053]}
def MasterTask( name, r, g, b, value, height = 0, width = 0):
    result_queue = queue.Queue(3)
    if name=="intensity-grey":
        processed = vm2.process(name,"ig",r,value,height,width)
        return processed
    if name=="threshold":
        processed =vm1.process(name,"th",r,value,height,width)
        return processed
    else:
        vm1.start_process(name,"r",r,value,height,width)
        vm2.start_process(name,"b",b,value,height,width)
        vm3.start_process(name,"g",g,value,height,width)
        time.sleep(0.01)
        vm1_receive_thread=threading.Thread(target=vm1.receive_process,args=(result_queue,))
        vm1_receive_thread.start()
        vm2_receive_thread=threading.Thread(target=vm2.receive_process,args=(result_queue,))
        vm2_receive_thread.start()
        vm3_receive_thread=threading.Thread(target=vm3.receive_process,args=(result_queue,))
        vm3_receive_thread.start()
        while not result_queue.full():
            continue
        adjusted_R= adjusted_G= adjusted_B=None
        for i in range(3):
            item = result_queue.get()
            if item[1]=="r":
                adjusted_R=item[2]
            elif item[1]=="b":
                adjusted_B=item[2]
            elif item[1]=="g":
                adjusted_G=item[2]
        # adjusted_R = vm1.process(name,"r",r,value,height,width,result_queue)
        # time.sleep(0.01)
        # adjusted_B = vm2.process(name,"b",b,value,height,width,result_queue)
        # time.sleep(0.01)
        # adjusted_G = vm3.process(name,"g",g,value,height,width,result_queue)
        # time.sleep(0.01)
        processed = cv2.merge((adjusted_R, adjusted_G, adjusted_B))
    return processed
    
class VM:
    def __init__(self,ip,port)->None:
        # super(VM, self).__init__()
        self.ip=ip
        self.port=port
        self.vmSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.vmSocket.connect((self.ip, self.port))
        

    def process(self,op,channel,image,value,height,width):
        try:
            print("start sending")
            self.send_data([op,channel,image,value,height,width])
            print("start receive process")
            receivedData= self.receive_data()
            operation = receivedData[0]
            ch=receivedData[1]
            processedImageChannel=receivedData[2]
            return processedImageChannel
            
            
        except OSError as oErr:
            print("OSError: {0}".format(oErr))
        except Exception as e:
            print("Exception: {0}".format(e))
    def start_process(self,op,channel,image,value,height,width):
        try:
            print("start sending")
            self.send_data([op,channel,image,value,height,width])
            
            
        except OSError as oErr:
            print("OSError: {0}".format(oErr))
        except Exception as e:
            print("Exception: {0}".format(e))
    
    def receive_process(self,result_queue):
        try:
            print("start receive process")
            receivedData= self.receive_data()
            operation = receivedData[0]
            ch=receivedData[1]
            processedImageChannel=receivedData[2]
            
            result_queue.put([operation,ch,processedImageChannel])
            # return [operation,ch,processedImageChannel]
            
            
        except OSError as oErr:
            print("OSError: {0}".format(oErr))
        except Exception as e:
            print("Exception: {0}".format(e))
    def closeVM(self):
        self.send_data(["EXIT"])
        receivedData=self.receive_data()
        self.vmSocket.close()
    def receive_data(self):
        timeout=5
        # Receive the data from the client
        data = b""
        ready_to_read, _, _ = select.select([self.vmSocket], [], [])
        if ready_to_read:
            print(f"start receiving data")
            self.vmSocket.settimeout(timeout)
            while True:
                try:
                    chunk = self.vmSocket.recv(4096)
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
        self.vmSocket.sendall(serialized_data)
        
    
            
vm1=VM(VMS_IP_Port["vm1"][0],VMS_IP_Port["vm1"][1])
vm2=VM(VMS_IP_Port["vm2"][0],VMS_IP_Port["vm2"][1])
vm3=VM(VMS_IP_Port["vm3"][0],VMS_IP_Port["vm3"][1])