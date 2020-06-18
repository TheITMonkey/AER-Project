from termcolor import colored
from datetime import datetime


class Handler:
    def __init__(self,peerID,caches):
        self.caches = caches
        self.peerID = peerID
    
    def handle_receive_msg(self,data):
        response = {}
        msg = data['data']

        if not 'type' in msg:
            response = None
        else:
            msg_type = msg['type']
            if msg_type == 'Join':
                response = self.join_receive(msg)
                if not 'ancestor' in response  or not 'sucessor' in response:
                    response = None
            elif msg_type == 'Join-Response':
                response = self.finish_connection(msg)          
            elif msg_type == 'Ping':
                response = self.ping(msg)
            elif msg_type == 'Pong':
                response = self.pong(msg)
            elif msg_type == 'Update-Ancestors':
                response = self.update_ancestors(msg)    
            elif msg_type == 'Update-Sucessors':
                response = self.update_sucessors(msg)
            elif msg_type == 'Send-Content':
                response = self.request_content(msg)
            elif msg_type == 'Save-Content':
                response = self.save_content(msg) 
            elif msg_type == 'Update-Ancestors-Response':
                response = self.update_ancestors_response(msg)
            elif msg_type == 'Update-Sucessors-Response':
                response = self.update_sucessors_response(msg)
            elif msg_type == 'Send-Response':
                response = self.send_content_response(msg)
            elif msg_type == 'Save-Ancestors':
                response = self.save_ancestor(msg)
            elif msg_type == 'Save-Sucessors':
                response = self.save_sucessors(msg)
            elif msg_type == 'Find-Content':
                response = self.find_content(msg)
            elif msg_type == 'Find-Content-Response':
                response = self.find_content_response(msg)
            else:
                print(colored("Wrong Message Type " + msg_type,'red'))
                response = None


        addr = (data['addr'][0], 5000)

        result = {'addr':addr,'data':response}
        return result


    def join_receive(self,msg):
        #ir buscar o gajo que enviou a mensagem
        msgID = msg['RequesterID']       
        response = {'type':'Join-Response', 'PeerID':msgID, 'RequesterID':self.peerID} 
        if msgID == self.peerID:
          #  print(colored("My message, ingoring on join",'red'))
            return None

        sucessorID = self.caches.get_sucessor(0)

        # Não tem ninguem nas caches ainda
        if sucessorID == None:
            response = update_join_message(response,self.peerID,self.peerID)
            
            self.caches.add_sucessor(msgID, datetime.fromisoformat(msg['timestamp']),0)
            self.caches.add_ancestor(msgID, datetime.fromisoformat(msg['timestamp']),0)
            self.caches.caches()
        else:
        #verificar se eu preciso de responder a mensagem do gajo
            if msgID > self.peerID:
            #verificar se não é um sucessor meu a tratar da mensagem ou se sou eu
                if msgID < sucessorID:
                #o MSGID passa a ser meu sucessor
                    response = update_join_message(response,self.peerID,sucessorID)
                
                elif msgID > sucessorID:
                    if self.peerID > sucessorID:
                        response = update_join_message(response, self.peerID, sucessorID)
                
            elif msgID < self.peerID:

                if msgID < sucessorID:
                # O MSGID PASSA A SER MEU SUCESSOR
                    if self.peerID > sucessorID:
                        response = update_join_message(response,self.peerID,sucessorID)
                
            else:
                print(colored("MsgID is equals to our ID"),'red')
        return response


   
    def finish_connection(self,msg):
        # na msg temos o sucessor e o antecessor:
        timestamp = datetime.fromisoformat(msg['timestamp'])
        self.caches.add_sucessor(msg['sucessor'],timestamp,0)
        self.caches.add_ancestor(msg['ancestor'],timestamp,0)
    
        self.caches.caches()
        
        response_array = []
        update_sucessors_msg = {
            'type':'Update-Sucessors',
            'RequesterID': self.peerID,
            'PeerID': self.caches.get_sucessor(0), #Id do peer a quem queremos enviar o pedido
            'SucessorIndex': 0 #Indice do sucessor que pretendemos obter como resposta
                               }

        update_ancestors_msg = {
            'type':'Update-Ancestors',
            'RequesterID':self.peerID,
            'PeerID': self.caches.get_ancestor(0),
            'AncestorIndex': 0
                               }

        request_contents = {
            'type':'Send-Content',
            'RequesterID': self.peerID,
            'PeerID' : self.caches.get_ancestor(0),
            'ContentID': self.peerID # Pedir os nossos conteudos
        }
        
        #Vamos atualizar os sucessores e antecessores presentes nas tabelas
            #Vamos ter de pedir os restantes antecessores
            #Vamos ter de pedir os restantes sucessores
        #Vamos pedir os conteudos a guardar
        #Vamos criar a tabela dos shortcuts
            

        #No final:
        response_array.append(update_sucessors_msg)
        response_array.append(update_ancestors_msg)
        response_array.append(request_contents)

        response = {'response_array':response_array}
        return response


    def ping(self,msg):
        response = None
        if msg['PeerID'] == self.peerID:
            response = {'type':'Pong', 'RequesterID':self.peerID, 'PeerID':msg['RequesterID']}

        return response

    def pong(self,msg):
        
        if msg['PeerID'] == self.peerID:
            self.caches.add_ping(msg['RequesterID'])
           # print(colored("Recebi um pong",'red','on_grey'))

        return None

    def update_sucessors(self,msg):
        #ir buscar o gajo que enviou a mensagem
        msgID = msg['PeerID']       
        requesterID = msg['RequesterID']
        response = {'type':'Update-Sucessors-Response','PeerID':requesterID,'RequesterID':self.peerID, 'SucessorIndex':msg['SucessorIndex']} 

        if requesterID == self.peerID:
            print(colored("My message, ingoring on update_sucessors",'red'))
            return None 
        
        elif self.caches.sucessors_size()>0 and msgID == self.peerID:
            index = msg['SucessorIndex']
            sucessorID = self.caches.get_sucessor(index)
            response.update({"sucessorID":sucessorID})
        elif msgID != self.peerID:
            print(colored("Update sucessors not for us",'red'))
            return None
        else:
            print(colored("Sucessors Caches is Empty",'red'))
            return None
            
        return response
    
    def update_ancestors(self,msg):
         #ir buscar o gajo que enviou a mensagem
        msgID = msg['PeerID']
        requesterID = msg['RequesterID']       
        response = {'type':'Update-Ancestors-Response','PeerID':requesterID,'RequesterID':self.peerID, 'AncestorIndex':msg['AncestorIndex']} 

        if requesterID == self.peerID:
            print(colored("My message, ingoring on update ancestors",'red'))
            return None

        elif self.caches.ancestors_size()>0 and msgID == self.peerID:
            index = msg['AncestorIndex']
            ancestorID = self.caches.get_ancestor(index)
            response.update({"ancestorID":ancestorID})
        elif msgID != self.peerID:
            print(colored("Update ancestors not for us!",'red'))
            return None
        else:
            print(colored("Ancestors Caches is Empty",'red'))
            return None
            
        return response

    def save_content(self,msg):
            #ir buscar o gajo que enviou a mensagem
            msgID = msg['PeerID']       
            requesterID = msg['RequesterID']
            response = {'type':'Save-Response', 'PeerID':requesterID,'RequesterID':self.peerID} 
            
            if requesterID == self.peerID:
                print(colored("My message, ingoring on save content",'red'))
                return None
            

            if self.caches.ancestor_Exist(requesterID):
                content = msg['Content']
                contentID = msg['ContentID']
                self.caches.add_content(content, contentID)
                print(colored("Saved in Cache the content with ID equal to "+contentID,'red'))
            else: 
                print(colored("Cannot perform your request because i'm empty",'red')) 

            return response

    def request_content(self,msg):
            #ir buscar o gajo que enviou a mensagem
            msgID = msg['PeerID']    
            requesterID = msg['RequesterID']   
            response = {'type':'Send-Response','PeerID':requesterID,'RequesterID':self.peerID,'ContentID':msg['ContentID']}

            if requesterID == self.peerID:
                print(colored("My message, ingoring on request content",'red'))
                return None
            elif self.caches.sucessor_Exist(requesterID) and msgID == self.peerID:
                contentID = msg['ContentID']              
                response.update({'content':self.caches.get_content(contentID)})
                print(colored("Retrieving the content with ID "+ str(contentID),'red'))
            elif msgID != self.peerID:
                print(colored("Request Content not for us",'red'))
                return None
            else:
                print(colored("Cannot perform your request because i'm empty!",'red'))  
                response.update({'content':None})

            return response

    def update_ancestors_response(self, msg):
        
        if msg['ancestorID'] is None:
            return None
        
        if msg['PeerID'] == self.peerID:
            self.caches.add_ancestor(msg['ancestorID'],datetime.fromisoformat(msg['timestamp']),msg['AncestorIndex']+1)
        
        return None
        
    
    def update_sucessors_response(self,msg):
        
        if msg['sucessorID'] is None:
            return None
        if msg['PeerID'] == self.peerID:
            self.caches.add_sucessor(msg['sucessorID'],datetime.fromisoformat(msg['timestamp']), msg['SucessorIndex']+1)
        
        return None

    def send_content_response(self,msg):
        if not 'content' in msg:
            return None
        if msg['content'] is None:
            return None
            
        self.caches.add_content(msg['content'],msg['ContentID'],datetime.fromisoformat(msg['timestamp']))
     
        return None
    

    def save_ancestor(self,msg):
        requesterID = msg['RequesterID']
        msgID = msg['PeerID']
        index = msg['Index']

        if msgID != self.peerID or requesterID == self.peerID:
            return None
        
        self.caches.add_ancestor(requesterID,datetime.fromisoformat(msg['timestamp']),index)
        
        return None


    def save_sucessors(self,msg):
        requesterID = msg['RequesterID']
        msgID = msg['PeerID']
        index = msg['Index']

        if msgID != self.peerID or requesterID == self.peerID:
            return None
        
        self.caches.add_sucessor(requesterID,datetime.fromisoformat(msg['timestamp']),index)
        

        return None

    def find_content(self, msg):
        response = None
        # verificar se somos nos a responder:
        contentID = msg['ContentID']
        if contentID < self.peerID and contentID > self.caches.get_ancestor(0):
            response = {'type':'Find-Content-Response','PeerID':msg['RequesterID'], 'Filepath':msg['Filepath'], 'RequesterID':self.peerID}

        elif contentID > self.peerID and contentID > self.caches.get_ancestor(0) and self.peerID < self.caches.get_ancestor(0):
            response = {'type':'Find-Content-Response','PeerID':msg['RequesterID'], 'Filepath':msg['Filepath'], 'RequesterID':self.peerID}

        elif contentID == self.peerID:
            response = {'type':'Find-Content-Response','PeerID':msg['RequesterID'], 'Filepath':msg['Filepath'], 'RequesterID':self.peerID}

        return response

    
    def find_content_response(self, msg):
        senderID = msg['RequesterID']

        response = None

        if msg['PeerID'] == self.peerID:
            response = {'type':'Save-Content', 'PeerID':senderID, 'RequesterID':self.peerID, 'Filepath':msg['Filepath']}

        return response


def update_join_message(response,antecessor,sucessor):
    response.update({'ancestor':antecessor,'sucessor':sucessor})
    #dar update nas caches
    return response