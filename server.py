import threading
import sqlite3
from xmlrpc.server import SimpleXMLRPCServer

# Basic Constants
SERVER = 'localhost'
PORT = 9999
ADDR = (SERVER, PORT)

# DB connect to memory
conn = sqlite3.connect('hepas.db', isolation_level=None, check_same_thread=False)
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS students")
c.execute("DROP TABLE IF EXISTS units")

# Create table
c.execute("CREATE TABLE IF NOT EXISTS students (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, userId text NOT NULL, password text "
          "NOT NULL, lastName text NOT NULL, email text NOT NULL)")
c.execute("CREATE TABLE IF NOT EXISTS units (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, unitId text NOT NULL, unitMark real NOT "
          "NULL, userId text, FOREIGN KEY(userId) REFERENCES students(userId))")

# Initiate DB
c.execute("INSERT INTO students(userId, password, lastName, email) VALUES ('abc123', 'qwe123', 'James', 'james123@eou.edu.au')")
c.execute("INSERT INTO units(unitId, unitMark, userId) VALUES ('SCI1125', 85, 'abc123'), ('CSP1150', 50, 'abc123'),"
          "('MAT1252', 78, 'abc123'), ('CSI1241', 73, 'abc123'), ('CSG1105', 90, 'abc123'),"
          "('CSI1101', 45, 'abc123'), ('ENS1161', 95, 'abc123'), ('CSG1207', 65, 'abc123'),"
          "('CSP2348', 58, 'abc123'), ('CSG2341', 92, 'abc123'), ('CSG2344', 87, 'abc123'),"
          "('CSI3344', 72, 'abc123')")


# Thread
class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.local_server = SimpleXMLRPCServer(ADDR, allow_none=True)
        print("[SERVER] Server is listening on port 9999")
        self.local_server.register_function(authorize_login)
        self.local_server.register_function(inquiry_mark)
        self.local_server.register_function(average_mark)
        self.local_server.register_function(best_mark)
        self.local_server.register_function(best_mark_avg)
        self.local_server.register_function(evaluation_criteria)

    def run(self):
        self.local_server.serve_forever()


# Functions
def authorize_login(login_id, login_pw):
    c.execute("SELECT userId FROM students WHERE userId=?", (login_id, ))
    tup1 = c.fetchone()
    check_id = ''.join(tup1)
    c.execute("SELECT password FROM students WHERE userId=?", (login_id, ))
    tup2 = c.fetchone()
    check_password = ''.join(tup2)
    if login_id == check_id and login_pw == check_password:
        print(f"[AUTH] {login_id} is logged")
        return True
    else:
        print(f"[AUTH] {login_id} is failed to login")
        return False


def inquiry_mark(login_id):
    c.execute("SELECT unitId, unitMark FROM units WHERE userId=?", (login_id, ))
    row_tuple = c.fetchall()
    print("[SEND] Inquiry Mark -> ", login_id)
    return row_tuple


def average_mark(login_id):
    c.execute("SELECT unitId, unitMark FROM units WHERE userId=?", (login_id,))
    length = c.fetchall()
    c.execute("SELECT SUM(unitMark) FROM units WHERE userId=?", (login_id, ))
    row_list = c.fetchone()
    average = row_list[0] / len(length)
    print("[SEND] Average Mark -> ", login_id)
    return average


def best_mark(login_id):
    c.execute("SELECT unitId, unitMark FROM units Where userId=? ORDER BY unitMark DESC LIMIT 8", (login_id, ))
    row_best = c.fetchall()
    print("[SEND] Best Mark -> ", login_id)
    return row_best


def best_mark_avg(login_id):
    c.execute("SELECT SUM(unitMark) FROM (SELECT unitMark FROM units Where userId=? ORDER BY unitMark DESC LIMIT 8)", (login_id,))
    row_list = c.fetchone()
    average = row_list[0] / 8
    print("[SEND] Average Best 8 Mark -> ", login_id)
    return average


def fail_count(login_id):
    c.execute("SELECT COUNT(*) from units where userId = ? and unitMark < 50 order by unitMark desc", (login_id,))
    count = c.fetchone()
    result = count[0]
    print("[SEND] Get count of fail mark -> ", login_id)
    return result


def evaluation_criteria(login_id):
    fail = fail_count(login_id)
    avg = average_mark(login_id)
    best_avg = best_mark_avg(login_id)
    if fail >= 6:
        statement = f"{login_id}, {avg}, with 6 or more Fails! DOES NOT QUALIFY FOR HONORS STUDY!"
        print("[SEND] Get Evaluation Criteria -> ", login_id)
        return statement
    elif avg >= 70:
        statement = f"{login_id}, {avg}, QUALIFIED FOR HONOURS STUDY!"
        print("[SEND] Get Evaluation Criteria -> ", login_id)
        return statement
    elif 65 <= avg < 70 or best_avg >= 80:
        statement = f"{login_id}, {avg}, QUALIFIED FOR HONOURS STUDY!"
        print("[SEND] Get Evaluation Criteria -> ", login_id)
        return statement
    elif 65 <= avg < 70 or best_avg < 80:
        statement = f"{login_id}, {avg}, {best_avg}, MAY HAVE GOOD CHANCE! NEED further assessment!"
        print("[SEND] Get Evaluation Criteria -> ", login_id)
        return statement
    elif 60 <= avg < 65 and best_avg > 80:
        statement = f"{login_id}, {avg}, {best_avg}, MAY HAVE A CHANCE! Must be carefully reassessed and get the " \
                    f"coordinator's permission! "
        print("[SEND] Get Evaluation Criteria -> ", login_id)
        return statement
    else:
        statement = f"{login_id}, {avg}, DOES NOT QUALIFY FOR HONORS STUDY!"
        print("[SEND] Get Evaluation Criteria -> ", login_id)
        return statement


# Server start
if __name__ == '__main__':
    server = ServerThread()
    try:
        print("[HELP] Use Control+c to exit")
        server.start()
    except KeyboardInterrupt:
        print("[SERVER] Server is closing")
