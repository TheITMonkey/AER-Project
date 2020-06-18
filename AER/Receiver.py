import socket, requests, json, hashlib, threading, struct, time

from termcolor import colored

import netifaces
import os
from threading import Condition, Lock
import queue



class Receiver():

    
    def __init__(self, peerID, address,caches):
            
        self.multicast_ip = "239.8.8.8"
        self.multicast_port = ('',7001)
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peerID = peerID
        self.address = address
        self.lock = Lock()
        self.condition = Condition()
        self.caches = caches
        self.Messages = {}

    def multicast(self):
        self.socketUDP.bind(self.multicast_port)
        group = socket.inet_aton(self.multicast_ip)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.socketUDP.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while 1:
            #print( colored('ºº waiting for multicast messages ºº','green'))
            data, addr = self.socketUDP.recvfrom(1024)
            data = json.loads(data.decode())
            
           # if data['RequesterID'] != self.peerID:
            #    print(colored("++ Received multicast ++",'green'))
            #    print(colored(data,'green'))
            
            with self.condition:
                self.lock.acquire()
                if data['RequesterID'] != self.peerID :
                    if data['type'] in self.Messages:
                        self.Messages[data['type']].append({'addr':addr,'data':data})
                    else:
                        self.Messages.update({data['type']:[{'addr':addr,'data':data}]})
             #       print(colored("Received message, waking up my friends",'green'))
                    self.condition.notify()
                self.lock.release()



    def unicast(self):

        self.socketTCP.bind(self.address)
        self.socketTCP.listen(1)

        BUFFER_SIZE = 1024
        while 1:
            data = b''
            aux = b''
            #print(colored('** Waiting for unicast messages **','blue'))
            conn, addr = self.socketTCP.accept()

            while 1:     
                aux = conn.recv(BUFFER_SIZE)
                if not aux: break
                data = data + aux

            if data is not b'':
                data = json.loads(data.decode())
             #   print(colored("-- Received Unicast from " + str(addr) + "--",'blue'))
              #  print(colored(data,'blue'))
                conn.close()
            
                with self.condition:
                    self.lock.acquire()
                    if data['type'] in self.Messages:
                        self.Messages[data['type']].append({'addr':addr,'data':data})
                    else:
                        self.Messages.update({data['type']:[{'addr':addr,'data':data}]})
                    
                    self.lock.release()
               #     print(colored("Received message, waking up my friends",'blue'))
                    self.condition.notify()

    def getMessage(self, msgType=None,timeout=None, requesterID=None):
        msg_temp = None
        with self.condition:
            while(len(self.Messages) == 0):
                res = self.condition.wait(timeout)
                if not res: return {'Msg':'Timeout exceded'}
            
            #Mensagens especificas
            try:
                self.lock.acquire()
                if msgType is not None:
                    if not msgType in self.Messages:
                        return None
                    msgs = self.Messages[msgType]

                    for msg in msgs:
                        if requesterID is None:
                            msg_temp = msg
                            self.Messages[msgType].remove(msg)
                            return msg_temp
                        elif msg['data']['RequesterID'] == requesterID:
                            msg_temp = msg
                            self.Messages[msgType].remove(msg)
                            return msg_temp

                #Qualquer tipo de mensagens
                else:
                    for (Type,Messages) in self.Messages.items():
                        if len(Messages) != 0:
                            msg_temp = Messages[0]
                            self.Messages[Type].remove(msg_temp)
                            return msg_temp

            finally:
                self.lock.release()            
        return msg_temp

    def receive_files(self):
        receive_socket = socket.socket()
        receive_socket.bind(('0.0.0.0',5001))
        
        receive_socket.listen(10)
        while True:
           # print("Waiting for connections to download")
            conn, addr = receive_socket.accept()
            print("Peer with IP: <" + str(addr) + "> wants to send files")
            t = threading.Thread(target=self.fileClient, args=("thread",conn))
            t.start()

        receive_socket.close()



    def fileClient(self,name,socket):

        data = socket.recv(1024)    
        msg = json.loads(data.decode())
        
        filename = msg['filename']
        filesize = msg['filesize']
        print("Will download file with name",filename,"and size",filesize)
        
        split = filename.split(".") 
        filename = split[0] + "_new." + split[1]

        f = open(filename, 'wb')
        data = socket.recv(1024)
        totalRecv = len(data)
        f.write(data)
        while totalRecv < filesize:
            data = socket.recv(4096)
            totalRecv += len(data)
            f.write(data)
            if (totalRecv/float(filesize)*100) % 5 :
                print("{0:.2f}".format((totalRecv/float(filesize))*100)+"% Done")
        print("Download Complete!!!")
        
        socket.close()
