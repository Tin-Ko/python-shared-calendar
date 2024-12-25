#sever.py
import socket
import threading
import pickle
import time

lock = threading.Lock()

def catch(service_client_socket,addr):
    if not addr in user: #確認請求連線的是不再正在使用者名單的,傳送起始檔案
        user[addr]=addr
        server_socket[addr]=service_client_socket
        print('new')
    while True:
        d = service_client_socket.recv(1024)
        if(d.decode('utf-8')=='exit'):
            lock.acquire()
            msg='exit'
            print(service_client_socket,"exit")
            service_client_socket.send(msg.encode('utf-8'))
            user.pop(addr)
            server_socket.pop(addr)
            lock.release()
            break
        elif(d.decode('utf-8')=='load'):
            lock.acquire()
            print(service_client_socket,"load")
            with open('tasks.pkl','rb') as file1: #計算檔案大小送出告知要收幾次
                i=0
                for line in file1:
                    i+=1
                service_client_socket.send(str(i).encode('utf-8'))
                time.sleep(2)
            with open('tasks.pkl','rb') as file1:
                for line in file1:
                    service_client_socket.send(line)
                    time.sleep(2)
            lock.release()
        elif(d.decode('utf-8')=='save'):
            lock.acquire()
            print(service_client_socket,"save")
            count=0
            with open('tasks.pkl','wb') as file: #收取客戶端來的檔案並改寫服務器上的檔案
                count = int(service_client_socket.recv(1024))
                for i in range(count):
                    d = service_client_socket.recv(1024)
                    file.write(d)
            lock.release()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = socket.gethostname()
port = 8088
s.bind((host,port))
s.listen(5)
server_socket={}
user={}
while True:
    service_client_socket, addr = s.accept()
    print("來自伺服器" + str(addr) + "的訊息:")
    r = threading.Thread(target=catch, args=(service_client_socket,addr), daemon=True) 
    r.start()
