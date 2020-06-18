
import netifaces, hashlib, threading, time
import Caches, Sender, Receiver, Handler
from datetime import datetime
from threading import Lock
import pytz
from termcolor import colored
import os

maxID = 1461501637330902918203684832716283019655932542975


"""
    Obtem o tipo da mensagem que se vai receber ao enviar um tipo de dados
"""
def response_type(request_type):
    if request_type == "Update-Sucessors":
        return "Update-Sucessors-Response"
    elif request_type == "Update-Ancestor":
        return "Update-Ancestors-Response"
    elif request_type == "Send-Content":
        return "Send-Response"

class Peer:
    def __init__(self):
        self.peerID = self.genID()
        self.caches = Caches.Caches(self.peerID)
        self.sender = Sender.Sender()
        self.receiver = Receiver.Receiver(self.peerID,("0.0.0.0",5000),self.caches)
        self.handler = Handler.Handler(self.peerID,self.caches)
        self.t1 = threading.Thread(target=self.receiver.multicast).start()
        self.t2 = threading.Thread(target=self.receiver.unicast).start()
        self.t3 = threading.Thread(target=self.receiver.receive_files).start()
        self.lock = Lock()
        
    """
        Initial connection
    """
    def connection(self):
        message = {'type':'Join','PeerID':None,'RequesterID':self.peerID}
        self.sender.send_multicast(message)
        r = None

        while r is None :
            r = self.receiver.getMessage("Join-Response",2)
        
       # print(colored("Resposta connection:",'yellow'))
        #print(colored(r,'yellow'))
        
        if 'Msg' in r and r['Msg'] == "Timeout exceded": 
            print(colored("Somos os unicos, não vamos fazer nada",'yellow'))
            return
        else:
            #processo de conexão
         #   print(colored("Vamos conectar com alguem!",'yellow'))
            response = self.handler.handle_receive_msg(r)
          #  print(colored("Resposta do handler quando se pede para tratar join-response",'yellow'))
           # print(colored(response,'yellow'))

            #Enviar as mensagens
            for r in response['data']['response_array']:
                self.sender.send_multicast(r)
                
            #Esperar as respostas
            for r in response['data']['response_array']:
                message = None
                while(message == None):
                    message = self.receiver.getMessage(response_type(r['type']) , 20, r['PeerID'])
            
                if message['data'] is not None:
                        output = self.handler.handle_receive_msg(message)
        

            #Enviar aos sucessores e antecessores quem é que eu sou e para me adicionarem nas suas caches
            i = 0
            for sucessor in self.caches.get_sucessors():
                #criar mensagem
                msg = {"type":'Save-Ancestors', "PeerID":sucessor, "RequesterID":self.peerID, "Index":i}
                #enviar dados
                self.sender.send_multicast(msg)
                i = i + 1
        
            i = 0
            for ancestor in self.caches.get_ancestors():     
                #criar mensagem
                msg = {"type":'Save-Sucessors',"PeerID":ancestor, "RequesterID":self.peerID, "Index":i}
                #enviar dados
                self.sender.send_multicast(msg)
                i = i + 1


    """
        Tratar do processo de receber mensagens e enviar a resposta
    """
    def handleMessages(self):

        print(colored("Vamos lá tratar das mensagens!",'yellow','on_red'))

        while 1:
            data = None
            while data is None:
                data = self.receiver.getMessage()
            response = self.handler.handle_receive_msg(data)
            #enviar resposta
            if response['data'] is not None:

                if response['data']['type'] == 'Save-Content':
                    print("Vamos enviar o ficheiro")
                    self.sender.send_file((response['addr'][0],5001),response['data'])
                    continue
                if response['data'] is not 'UPDATED CACHES':
            #        print(colored("Response handle Message:",'cyan'))
             #       print(colored(response,'cyan'))
                    self.sender.send_unicast(response['addr'],response['data'])

    """
       Envia mensagem a todos os sucessores e antecessores para verificar se estão vivos
    """
    def verify_connections(self):


        while 1:    
            print(colored("-_- Verifying my sucessor -_-",'red','on_cyan'))

            #Enviar pings aos sucessores
            if(self.caches.sucessors_size() > 0):
                message = {'type':'Ping', 'RequesterID': self.peerID, 'PeerID': self.caches.get_sucessor(0)}
                self.sender.send_multicast(message)

                #enviamos tudo
                #dormir durante 10s
                time.sleep(10)

                if len(self.caches.get_pings()) == 0:
                    dropperID = self.caches.get_sucessor(0)
                    # -> o sucessor[1] passa a sucessor[0]
                    self.caches.remove_sucessor(dropperID)
                    
              #      self.caches.caches()
                    # -> pergunta ao novo sucessor[0] quem é o seu sucessor[0] passando este a seu sucessor[1]
                    msg1 = {'type':'Update-Sucessors','PeerID':self.caches.get_sucessor(0), 'RequesterID':self.peerID,'SucessorIndex':0}
                    self.sender.send_multicast(msg1)

                    time.sleep(2)
                    # -> dizer ao novo sucessor[0] que eu sou o antecessor[0]
                    msg2 = {'type':'Update-Ancestors-Response','PeerID':self.caches.get_sucessor(0),    'RequesterID':self.peerID,'AncestorIndex':-1,'ancestorID':self.peerID}
                    self.sender.send_multicast(msg2)

                    time.sleep(2)
                    # -> dizer ao novo sucessor[0] que o seu antecessor[1] é o meu antecessor[0]
                    msg3 = {'type':'Update-Ancestors-Response','PeerID':self.caches.get_sucessor(0),    'RequesterID':self.peerID,'AncestorIndex':0, 'ancestorID':self.caches.get_ancestor(0)}
                    self.sender.send_multicast(msg3)
                    
                    time.sleep(2)
                    # -> dizer ao meu antecessor[0] que o seu sucessor[1] é o meu novo sucessor[0]
                    msg4 = {'type':'Update-Sucessors-Response','PeerID':self.caches.get_ancestor(0),    'RequesterID':self.peerID,'SucessorIndex':0,'sucessorID':self.caches.get_sucessor(0)}
                    self.sender.send_multicast(msg4)
                    
                    time.sleep(2) #-> Para ter a certeza que o meu novo sucessor[1] é atualizado
                    # -> dizer ao meu novo sucessor[1] que eu sou o seu antecessor[1]
                    msg5 = {'type':'Update-Ancestors-Response','PeerID':self.caches.get_sucessor(1),    'RequesterID':self.peerID,'AncestorIndex':0,'ancestorID':self.peerID}
                    self.sender.send_multicast(msg5)

                else:
                    print(colored("-_- Sucessor not dead, sleeping -_-",'red','on_cyan'))
                    

                #No final vamos limpar a cache para a proxima vez
                self.caches.clear_ping()

            print(colored("Finished verify connection process",'red','on_cyan'))
            time.sleep(20)


    """
        Gerar o ID para ser utilizado na rede
    """
    def genID(self):
        listInterfaces = netifaces.interfaces()
        listMac = []
        for x in listInterfaces:
            listMac.append(netifaces.ifaddresses(x)[netifaces.AF_LINK][0]['addr'])
            mac = listMac[len(listMac)-1] + str(datetime.now())

        hashed_key = hashlib.sha1(mac.encode()).hexdigest()
        return int(str(int(hashed_key,16))[0:6])

    
    def getPeerID(self):
        return self.peerID
    

    def show_content(self):
        print(self.caches.get_contents())


    def add_content(self):

        filename = input("Introduza o caminho para o ficheiro a guardar: ")
        print("Searching file with name",filename)
        #Transformar o nome do ficheiro num ID -> talvez adicionar-lhe a data e dar hash
        fileID = self.hash_file(filename)

        if os.path.isfile(filename):

            #Verificar se é nosso:
            if fileID < self.peerID and fileID > self.caches.get_ancestor(0):
                self.caches.add_content(filename,fileID, datetime.now(pytz.utc))
                print("Guardamos as coisas no nosso lado")
                return
                #é nosso

            elif fileID > self.peerID and fileID > self.caches.get_ancestor(0) and self.peerID <    self.caches.get_ancestor(0):
                self.caches.add_content(filename,fileID, datetime.now(pytz.utc))
                print("Guardamos as coisas no nosso lado")
                return
                #é nossso

            elif fileID == self.peerID:
                self.caches.add_content(filename,fileID, datetime.now(pytz.utc))
                print("Guardamos as coisas no nosso lado")
                return
                #é nosso

            #Perguntar a rede quem vai guardar o nosso conteudo
            msg = {'type': 'Find-Content', 'RequesterID':self.peerID, 'ContentID':fileID, 'PeerID':None,    'Filepath':filename}
            self.sender.send_multicast(msg)
        else:
            print(colored("File does not exist!",'red'))

    

    def hash_file(self, filename):
        pre_hash = filename
        hashed_file = hashlib.sha1(pre_hash.encode()).hexdigest()
        return int(str(int(hashed_file,16))[0:6])
