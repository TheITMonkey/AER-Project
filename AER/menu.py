import numpy as np
from peer import Peer
from termcolor import colored
import sys
from threading import Thread

def inputNumber(prompt):
    while True:
        try: 
            num = float(input(prompt))
            break
        except ValueError:
            pass
        
    return num



def displayMenu(items):

    print("\n")
    for i in range(len(items)):
        print("{:d}-> {:s}".format(i+1, items[i]))
    option = 0
    while not (np.any(option == np.arange(len(items))+1)):
        print("\n")
        option = inputNumber(colored("Choose a menu item >> ", 'cyan'))

    return option


if __name__ == "__main__":
    
    peer = Peer()
    menuItems = np.array([colored("Connect to Network",'blue'), colored("Show Content",'blue'), colored("Add Content",'blue')])
    print("\n")
    print(colored("Welcome Peer " + str(peer.peerID),'yellow'))

    while True:
        print("\n")
        #Display Menu
        option = displayMenu(menuItems)

        #Connect
        if option == 1:
            peer.connection()
            #Handle messages
            t = Thread(target=peer.handleMessages).start()
            #Start pings
            t = Thread(target=peer.verify_connections).start()

        #Show_Content
        elif option == 2:
            peer.show_content()

        #Add_Content 
        elif option == 3: 
            #option = input(colored("Enter the Content >>",'cyan'))
            peer.add_content()
        
"""
        #Remove_Content
        elif option == 4:
            option = input(colored("Enter Content ID >> ",'cyan'))
            peer.remove_content(option)

        #Download
        elif option == 5:
            option = input(colored("Enter Content ID for download >> ", 'cyan'))
            peer.download_content(option)
"""    
