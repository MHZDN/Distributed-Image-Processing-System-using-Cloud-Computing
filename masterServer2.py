import pickle
import select
import socket
import threading
from CL_For_Image import CL_Image_Preprocessing



masterip=socket.gethostbyname(socket.gethostname())
# masterip="0.0.0.0"
masterport=5090
# healthport=8090
#
#data sent from client to server
#   [operation,image]
#data sent from server to client
#   [operation,processedImage]
#
class MainServer(threading.Thread):
    def __init__(self,ip,port,masterSocket) -> None:
        super(MainServer, self).__init__()
        self.ip=ip
        self.port=port
        self.masterSocket=masterSocket
        self.CL = CL_Image_Preprocessing()

    def run(self):
        while True:
            try:
                receivedData=self.receive_data()
                if len(receivedData)==0:
                    continue
                operation = receivedData[0]
                image=receivedData[1]
                print(f"Received image with operation:{operation} ")
                processed=None
                if operation=="Gray":
                    processed = self.CL.To_gray_pyopencl(image)
                    # return self.gray(inputImage)
                elif operation=="Brighten":
                    processed=self.CL.Intensity_pyopencl(image, 1)
                    # return self.bright(inputImage)
                elif operation=="Darken":
                    processed = self.CL.Intensity_pyopencl(image, 0)
                    # return self.dark(inputImage)
                elif operation=="Threshold":
                    processed = self.CL.Threshhold(image)
                    # return self.threshold(inputImage)
                if not (processed is None):
                    self.send_data([operation,processed])
                else :
                    raise Exception("master processed image is None")
            except OSError as oErr:
                print("OSError: {0}".format(oErr))
            except Exception as e:
                print("Exception: {0}".format(e))
                break

    def receive_data(self):
        timeout=5
        # Receive the data from the client
        data = b""
        ready_to_read, _, _ = select.select([self.masterSocket], [], [])
        if ready_to_read:
            print(f"start receiving data")
            self.masterSocket.settimeout(timeout)
            while True:
                try:
                    chunk = self.masterSocket.recv(4096)
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
        print("sending serialized")
        # Send the serialized array to the server
        self.masterSocket.sendall(serialized_data)


# def listenHealth():
    
#     healthSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     healthSocket.bind((masterip, healthport))
#     print(f"Start health probe listening on ip:{masterip} , port:{healthport}")
#     healthSocket.listen(1)
#     while healthSocket:
#         if not healthSocket:
#             continue
#         readable,_,_ = select.select([healthSocket],[],[])
#         sock,addr = healthSocket.accept()
#         print(f"Health Probe")
#         sock.send(("done").encode())
#         sock.close()
    
def listenServer():
    
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSocket.bind((masterip, masterport))
    print(f"Start listening on ip:{masterip} , port:{masterport}")
    tcpSocket.listen(5)
    while tcpSocket:
        if not tcpSocket:
            continue
        readable,_,_ = select.select([tcpSocket],[],[])
        serverSocket,serverAddress = tcpSocket.accept()
        if(serverAddress[0]=="168.63.129.16"):
            serverSocket.send(("done").encode())
            print(f"Health Probe")
            serverSocket.close()
            continue
        newThread = MainServer(serverAddress[0],serverAddress[1],serverSocket)
        print(f"Starting Thread with:{serverAddress[0]} : {serverAddress[1]} ")
        newThread.start()


if __name__ == "__main__":
    # threading.Thread(target=listenHealth).start()
    threading.Thread(target=listenServer).start()
    


