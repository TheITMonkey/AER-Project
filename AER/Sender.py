import socket
import threading
import json
from datetime import datetime
from termcolor import colored
import pytz
import os

class Sender():
    def __init__(self):

        self.multicast_ip = "239.8.8.8"
        self.multicast_port = 7001
        self.timeout = 5
    
    def send_multicast(self,content):
        print(colored("Creating thread to send multicast message with type = " + str(content['type']),'yellow','on_magenta'))

        content.update({'timestamp':str(datetime.now(pytz.utc))})

        l = threading.Thread(target=self.multicast ,kwargs={'content':content})
        l.start()


    def send_unicast(self,address,content):
        print(colored("Creating thread to send unicast message with type = " + str(content['type']),'cyan','on_magenta'))

        content.update({'timestamp':str(datetime.now(pytz.utc))})

        l = threading.Thread(target=self.unicast,kwargs={'address':address,'content':content})
        l.start()


    """
        Enviar pedido multicast para a rede com o conteudo passado
        O content é um objeto JSON
    """
    def multicast(self, content):
        socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketUDP.settimeout(self.timeout)
        address = (self.multicast_ip, self.multicast_port)  
        socketUDP.sendto(bytes(json.dumps(content),"utf-8"), address)
        socketUDP.close()
                

    """ 
        Enviar pedido TCP para o endereço passada com o o conteudo passado
        O address deve ser um tuplo contendo o ip e a port do genero (ip,port)
        O content deve ser um objeto JSON
    """
    def unicast(self, address, content):
        socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketTCP.settimeout(self.timeout)
        socketTCP.connect(address)
        socketTCP.send(bytes(json.dumps(content),"utf-8"))
        socketTCP.close()

    def send_file(self,address,msg):
        print(colored("Creating thread to send unicast message with type = " + str(msg['type']),'white','on_magenta'))
        l = threading.Thread(target=self.filesender,kwargs={'address':address,'msg':msg}).start()


    def filesender(self, address, msg):  
        filepath = msg['Filepath']

        socketFiles = socket.socket()
        print("Trying to connect to ", address)
        socketFiles.connect(address)

        if os.path.isfile(filepath):
            msg = {'filesize':os.path.getsize(filepath), 'filename':filepath}
            socketFiles.send(bytes(json.dumps(msg),'utf-8'))

            print("Sent filename and filesize to ", address)

            with open(filepath,'rb') as f:
                bytesToSend = f.read(1024)
                socketFiles.send(bytesToSend)
                while bytesToSend != "":
                    bytesToSend = f.read(1024)
                    socketFiles.send(bytesToSend)
        
        else:
            print(colored("File does not exist!",'red'))

        socketFiles.close()




    
