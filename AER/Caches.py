import pytz
from datetime import datetime
from termcolor import colored

class Caches:

    def __init__(self, peerID):
        self.sucessors = []
        self.sucessors_time = datetime.now(pytz.utc)
        self.sucessors_max = 2
        self.ancestors = []
        self.ancestors_time = datetime.now(pytz.utc)
        self.ancestors_max = 2
        self.content = {}
        self.content_time = datetime.now(pytz.utc)
        self.repetitions = {}
        self.shortcuts = {}
        self.peerID = peerID
    

        self.pings = []

    def add_content(self, content, contentID, updatetime):
        if self.content_time < updatetime:
            self.content.update({contentID:content})
        else:
            print("Outdated content update")
    
    def add_sucessor(self, sucessor, updatetime, index):
        if self.sucessors_time < updatetime: 
            if len(self.sucessors) == self.sucessors_max : 
                self.sucessors.pop(self.sucessors_max-1)
            if index < self.sucessors_max:
                if not sucessor in self.sucessors and sucessor != self.peerID:
                    self.sucessors.insert(index,sucessor)       
                    self.sucessors_time = updatetime
                    print("Adicionei um sucessor")
            else:
                print("Sucessor index out of bounds") 
        else:
            print("Outdated sucessor uptade")

        self.caches()
    
    def add_ancestor(self, ancestor, updatetime, index):
        if self.ancestors_time < updatetime:
            if len(self.ancestors) == self.ancestors_max:
                self.ancestors.pop(self.ancestors_max-1)
            if index < self.ancestors_max:
                if not ancestor in self.ancestors and ancestor != self.peerID:
                    self.ancestors.insert(index,ancestor)
                    self.ancestors_time = updatetime
                    print("Adicionei um antecessor")
            else:
                print("Ancestor index out of bounds")
        else:
            print("Outdated ancestor update")

        self.caches()

    def sucessor_Exist(self, sucessor):
        for id in self.sucessors:
            if id == sucessor:
                return True
            else:
                return False


    def ancestor_Exist(self, ancestor):
        for id in self.ancestors:
            if id == ancestor:
                return True
            else:
                return False

    def add_repetitions(self, repID, repetition):
        self.repetitions.update({repID:repetition})

    def add_shortcut(self, shortcutID, shortcut):
        self.shortcuts.update({shortcutID:shortcut})

    def remove_content(self,contentID):
        return self.content.pop(contentID)

    def remove_sucessor(self, sucessor):
        self.sucessors.remove(sucessor)

    def remove_ancestor(self, ancestor):
        self.ancestors.remove(ancestor)

    def remove_repetition(self, repID):
        return self.repetitions.pop(repID)

    def remove_shortcut(self,shortcutID):
        return self.shortcuts.pop(shortcutID)

    def sucessors_size(self):
        return len(self.sucessors)

    def ancestors_size(self):
        return len(self.ancestors)

    def content_size(self):
        return len(self.content)

    def get_sucessor(self,index):
        size = self.sucessors_size()
        if size > 0 and index < size:
            return self.sucessors[index]
        else:
            return None
    def get_ancestor(self,index):
        size = self.ancestors_size()
        if size > 0 and index < size:
            return self.ancestors[index]
        else:
            return None
    
    def get_content(self,contentID):
        size = self.content_size()
        if size > 0: 
            return self.content[contentID]
        else:
            return None

    def get_ancestors(self):
        return self.ancestors
    
    def get_sucessors(self):
        return self.sucessors
    
    def get_contents(self):
        return self.content

    def add_ping(self,peerID):
        self.pings.append(peerID)

    def clear_ping(self):
        self.pings = []

    def get_pings(self):
        return self.pings

    def caches(self):
        print(colored("----------------",'white','on_red'))
        print(colored("Sucessors:",'white','on_red'))
        for x in self.sucessors:
            print(colored(x,'white','on_red'))
            print(colored("***",'white','on_red'))

        print(colored("Ancestors:",'white','on_red'))
        for x in self.ancestors:
            print(colored(x,'white','on_red'))
            print(colored("***",'white','on_red'))






