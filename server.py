import threading
from xmlrpc.server import SimpleXMLRPCServer

# Basic Constants
SERVER = 'localhost'
PORT = 9999
ADDR = (SERVER, PORT)


# Thread
class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.local_server = SimpleXMLRPCServer(ADDR, allow_none=True)
        print("[SERVER] Server is listening on port 9999")
        self.local_server.register_function(authorize_login)

    def run(self):
        self.local_server.serve_forever()


# Functions
def authorize_login(login_id, login_pw):
    if login_id == "abc" and login_pw == "123":
        return True
    else:
        return False


# Server start
if __name__ == '__main__':
    server = ServerThread()
    try:
        print("[HELP] Use Control+c to exit")
        server.start()
    except KeyboardInterrupt:
        print("[SERVER] Server is closing")
