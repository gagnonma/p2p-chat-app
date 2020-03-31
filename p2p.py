#Max Gagnon
#CIS 457 Project 2

import socket
import threading
import sys
import time
import tkinter as tk
from random import randint

class GUI:
    def print(self,text):
        self.chatlog.config(state=tk.NORMAL)
        self.chatlog.insert(tk.END, text + "\n")
        self.chatlog.config(state=tk.DISABLED)

    def enterMessage(self):
        text = self.userIn.get()
        self.client.sendMsg(self.client.sock,text)
        self.userIn.delete(0,'end')
    
    def createServer(self, port):
        server = Server(port,self)

    def hostServer(self):
        port = int(self.userIn.get())
        sThread = threading.Thread(target=self.createServer, args=(port,))
        sThread.daemon = True
        sThread.start()
        self.client = Client("127.0.0.1",port,self)
        self.userIn.delete(0,'end')


    def createClient(self):
        args = self.userIn.get().split()
        self.client = Client(args[0],int(args[1]),self)
        self.userIn.delete(0,'end')

    def __init__(self):
        self.root = tk.Tk()
        self.chatlog = tk.Text(self.root, height=25, width = 50, state=tk.DISABLED)
        self.userIn = tk.Entry(self.root, width=50)
        self.enter = tk.Button(self.root, text="Enter", command = self.enterMessage)
        self.host = tk.Button(self.root, text="Host", command=self.hostServer)
        self.connect = tk.Button(self.root, text="Connect", command=self.createClient)
        helptext = "To host a chatroom, enter the desired port number and select host\n To connect to a chatroom, enter the ip and port number and hit connect\nTo chat, type in the box and hit enter"
        self.help = tk.Label(self.root, text=helptext)
        self.chatlog.pack()
        self.userIn.pack()
        self.enter.pack()
        self.host.pack()
        self.connect.pack()
        self.help.pack()
        self.root.mainloop()

class Server:
    connections = []
    peers = []
    def __init__(self,port, gui):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0',port))
        sock.listen(1)
        gui.print("Server running")
        while True:
            c, a = sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c,a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            self.peers.append(a[0])
            gui.print(str(a[0]) + ":" + str(a[1]) + " connected")
            self.sendPeers()
    
    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            for connection in self.connections:
                connection.send(data)
            if not data:
                #print(str(a[0]) + ":" + str(a[1]) + " disconnected")
                self.connections.remove(c)
                self.peers.remove(a[0])
                c.close()
                self.sendPeers()
                break
    
    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + ","

        for connection in self.connections:
            connection.send(b'\x11' + bytes(p, "utf-8"))
    
class Client:
    
    def sendMsg(self,sock,text):
        sock.send(bytes(text, "utf-8"))
    
    def recMsg(self, sock, gui):
        while True:
            data = sock.recv(1024)
            if not data:
                break
            if data[0:1] == b'\x11':
                self.updatePeers(data[1:])
            else:
                gui.print(str(data, 'utf-8'))

    
    def __init__(self, address,port,gui):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((address,port))

        rThread = threading.Thread(target=self.recMsg, args=(self.sock,gui))
        rThread.daemon =True
        rThread.start()
    
    def updatePeers(self, peerData):
        p2p.peers = str(peerData, "utf-8").split(",")[:-1]

class p2p:
    peers = []

app = GUI()

