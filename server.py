import threading
import sqlite3
import datetime
import random

from xmlrpc.server import SimpleXMLRPCServer

# Components
SERVER = 'localhost'
PORT = 9999
ADDR = (SERVER, PORT)
UNITID = ['SCI1125', 'CSP1150', 'MAT1252', 'CSI1241', 'CSG1105', 'CSI1101', 'ENS1161', 'CSG1207', 'CSP2348', 'CSP2104',
          'CSG2341', 'CSG2344', 'CSI3344', 'CSP3341', 'CSG3101', 'CSI3345', 'CSP2108', 'CSP2312', 'CSI2441', 'CSI2343',
          'CSI3105', 'CSI3106', 'CSI2108', 'CSG2305', 'MAT3120', 'CSI3207', 'CSI3208', 'CSG3309', 'CSG2132', 'CSP2101']

# Create DB
conn = sqlite3.connect('hepas.db', isolation_level=None, check_same_thread=False)
c = conn.cursor()


# Delete tables if the tables exists in the database
def drop_table():
    c.execute("DROP TABLE IF EXISTS students")
    c.execute("DROP TABLE IF EXISTS units")


# Create table
def create_table():
    c.execute(
        "CREATE TABLE IF NOT EXISTS students (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, userId text NOT NULL, password text "
        "NOT NULL, lastName text NOT NULL, email text)")
    c.execute(
        "CREATE TABLE IF NOT EXISTS units (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, unitId text NOT NULL, unitMark real NOT "
        "NULL, userId text, FOREIGN KEY(userId) REFERENCES students(userId))")


# Initiate DB
def inser_values():
    c.execute(
        "INSERT INTO students(userId, password, lastName, email) VALUES ('abc123', 'qwe123', 'James', 'james123@eou.edu.au')")
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
        print(f"[{datetime.datetime.now()}] -- [SERVER] Server is listening on port 9999")

        # register functions into server.
        self.local_server.register_function(authenticate_login)
        self.local_server.register_function(alert)
        self.local_server.register_function(sign_up_eou)
        self.local_server.register_function(sign_up)
        self.local_server.register_function(manual_add)
        self.local_server.register_function(inquiry_mark)
        self.local_server.register_function(average_mark)
        self.local_server.register_function(best_mark)
        self.local_server.register_function(best_mark_avg)
        self.local_server.register_function(evaluation_criteria)

    # server continuously runs unless interference
    def run(self):
        self.local_server.serve_forever()


'''
Functions get parameters from the clients.
Every single interaction has timestamp 
'''


def alert(login_id):
    print(f"[{datetime.datetime.now()}] -- [AUTH] {login_id} is logout")


def authenticate_login(login_id, login_pw):
    # get user id from db
    c.execute("SELECT userId FROM students WHERE userId=?", (login_id,))
    tup1 = c.fetchone()
    check_id = ''.join(tup1)

    # get user password from db
    c.execute("SELECT password FROM students WHERE userId=?", (login_id,))
    tup2 = c.fetchone()
    check_password = ''.join(tup2)

    # compare with data from client and data from db
    if login_id == check_id and login_pw == check_password:
        print(f"[{datetime.datetime.now()}] -- [AUTH] {login_id} is logged")
        return True  # send token true
    else:
        print(f"[{datetime.datetime.now()}] -- [AUTH] {login_id} is failed to login")
        return False


# Insert values into db for EOU students
def sign_up_eou(id, pw, name, email):
    c.execute("INSERT INTO students(userId, password, lastName, email) VALUES (?, ?, ?, ?)", (id, pw, name, email))

    # create random range 12 ~ 30 units (no redundant unit)
    unit_distribution = random.sample(UNITID, random.randint(12, 30))

    # Insert unit mark into units table (0 ~ 100)
    for data in unit_distribution:
        c.execute("INSERT INTO units(unitId, unitMark, userId) VALUES (?, ?, ?)", (data, random.randint(0, 100), id,))
    print(f"[{datetime.datetime.now()}] -- [ADD] {len(unit_distribution)} units are imported")
    print(f"[{datetime.datetime.now()}] -- [SIGN-UP] {id}(EOU) is signed up")


# Insert values into students table for Non-EOU students
def sign_up(id, pw, name):
    c.execute("INSERT INTO students(userId, password, lastName) VALUES (?, ?, ?)", (id, pw, name))
    print(f"[{datetime.datetime.now()}] -- [SIGN-UP] {id}(Non-EOU) is signed up")


# Insert unit marks into units table
def manual_add(list_unit, list_mark, id):
    for unit, mark in zip(list_unit, list_mark):
        c.execute("INSERT INTO units(unitId, unitMark, userId) VALUES (?, ?, ?)", (unit, mark, id))
    sentence = "To add manually is successful."
    return sentence


# get <unit_id, unit_mark> data from db
def inquiry_mark(login_id):
    c.execute("SELECT unitId, unitMark FROM units WHERE userId=?", (login_id,))
    row_tuple = c.fetchall()
    print(f"[{datetime.datetime.now()}] -- [SEND] Inquiry Mark -> {login_id}")
    return row_tuple


# get average data from db
def average_mark(login_id):
    # to get count the number of units
    c.execute("SELECT unitId, unitMark FROM units WHERE userId=?", (login_id,))
    length = c.fetchall()

    # to get sum of unit marks
    c.execute("SELECT SUM(unitMark) FROM units WHERE userId=?", (login_id,))
    row_list = c.fetchone()
    average = row_list[0] / len(length)
    print(f"[{datetime.datetime.now()}] -- [SEND] Average Mark -> {login_id}")
    return round(average, 2)  # converts float value to 2 decimal places


# get best mark limit 8 units
def best_mark(login_id):
    c.execute("SELECT unitId, unitMark FROM units Where userId=? ORDER BY unitMark DESC LIMIT 8", (login_id,))
    row_best = c.fetchall()
    print(f"[{datetime.datetime.now()}] -- [SEND] Best Mark -> {login_id}")
    return row_best


# get the average of best 8 marks
def best_mark_avg(login_id):
    c.execute("SELECT SUM(unitMark) FROM (SELECT unitMark FROM units Where userId=? ORDER BY unitMark DESC LIMIT 8)",
              (login_id,))
    row_list = c.fetchone()
    average = row_list[0] / 8
    print(f"[{datetime.datetime.now()}] -- [SEND] Average Best 8 Mark -> {login_id}")
    return round(average, 2)  # converts float value to 2 decimal places


# get the number of fail units
def fail_count(login_id):
    c.execute("SELECT COUNT(*) from units where userId = ? and unitMark < 50 order by unitMark desc", (login_id,))
    count = c.fetchone()
    result = count[0]
    print(f"[{datetime.datetime.now()}] -- [SEND] Get count of fail mark -> {login_id}")
    return result


# get HEPa Evaluation Criteria
def evaluation_criteria(login_id):
    fail = fail_count(login_id)
    avg = average_mark(login_id)
    best_avg = best_mark_avg(login_id)
    if fail >= 6:
        statement = f"{login_id}, {avg}, with 6 or more Fails! DOES NOT QUALIFY FOR HONORS STUDY!"
        print(f"[{datetime.datetime.now()}] -- [SEND] Get Evaluation Criteria -> {login_id}")
        return statement
    elif avg >= 70:
        statement = f"{login_id}, {avg}, QUALIFIED FOR HONOURS STUDY!"
        print(f"[{datetime.datetime.now()}] -- [SEND] Get Evaluation Criteria -> {login_id}")
        return statement
    elif 65 <= avg < 70 or best_avg >= 80:
        statement = f"{login_id}, {avg}, QUALIFIED FOR HONOURS STUDY!"
        print(f"[{datetime.datetime.now()}] -- [SEND] Get Evaluation Criteria -> {login_id}")
        return statement
    elif 65 <= avg < 70 or best_avg < 80:
        statement = f"{login_id}, {avg}, {best_avg}, MAY HAVE GOOD CHANCE! NEED further assessment!"
        print(f"[{datetime.datetime.now()}] -- [SEND] Get Evaluation Criteria -> {login_id}")
        return statement
    elif 60 <= avg < 65 and best_avg > 80:
        statement = f"{login_id}, {avg}, {best_avg}, MAY HAVE A CHANCE! Must be carefully reassessed and get the " \
                    f"coordinator's permission! "
        print(f"[{datetime.datetime.now()}] -- [SEND] Get Evaluation Criteria -> {login_id}")
        return statement
    else:
        statement = f"{login_id}, {avg}, DOES NOT QUALIFY FOR HONORS STUDY!"
        print(f"[{datetime.datetime.now()}] -- [SEND] Get Evaluation Criteria -> {login_id}")
        return statement


# Server start
if __name__ == '__main__':
    server = ServerThread()
    try:
        print(f"[{datetime.datetime.now()}] -- [HELP] Use Control+c to exit")
        server.start()
        drop_table()
        create_table()
        inser_values()
    except KeyboardInterrupt:
        print(f"[{datetime.datetime.now()}] -- [SERVER] Server is closing")
