from constants import *
import sqlite3, time

class sqlite:
#    conn = sqlite3.connect(vvars["db_dir"]+vvars["db_name"])
#    cursor = conn.cursor()
    def init():
        try:
            #create table if not exist
            print("create table if not exist")
            conn = sqlite3.connect(vvars["db_dir"]+vvars["db_name"])
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS clients (name TEXT NOT NULL, status INTEGER DEFAULT 0, last INTEGER DEFAULT 0, privatekey TEXT, publickey TEXT, ip TEXT, timeout INTEGER DEFAULT 60, allowedips TEXT, endpoint TEXT, creation_date INTEGER);")
            cursor.execute("CREATE TABLE IF NOT EXISTS config (tg_status TEXT);")
            cursor.execute(f"INSERT INTO config (tg_status) VALUES ('0');")
            conn.commit()
            conn.close()
            return 0
        except Exception:
            print("LOG: DB init error")
    def show(name=None, line=None):
        print(f"cl_sqlite.show name={name}, line={line}")
        try:
            #show client or client list
            conn = sqlite3.connect(vvars["db_dir"]+vvars["db_name"]) #select DB file
            cursor = conn.cursor() #connect 2 DB
            print("db connected")
        except Exception:
            print("Connection to DB failed!")
            return 1
        try:
            if name == "all":
                print("Select all clients")
                sql_request=f"SELECT name FROM clients;"
                res=cursor.execute(sql_request).fetchall()
                result=[]
                for i in res:
                    result.append(i[0])
                print(result)
                return(result)
            elif line == "ip" and name == None:
                print("Select all IPs")
                sql_request=f"SELECT ip FROM clients;"
                res=cursor.execute(sql_request).fetchall()
                result=[]
                for i in res:
                    result.append(i[-1])
                print(result)
                return(result)
            elif name != "all" and line != None:
                print(f"Select {line} client {name}")
                sql_request=f"SELECT {line} FROM clients WHERE name='{name}';"
                result=cursor.execute(sql_request).fetchall()[0][0]            
                print(result)
                return result
        except Exception:
            print("LOG: DB 'show' error")
        conn.commit()
        conn.close()
    def add(client_name, ip, publickey, privatekey, timeout, allowed_ips, endpoint):
        #add client to db if not exists
        conn = sqlite3.connect(vvars["db_dir"]+vvars["db_name"])
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT name FROM clients WHERE name = '{client_name}';").fetchall()[0][0]
            print("Client already exists")
        except Exception:
            epoch=int(time.time())
            cursor.execute(f"INSERT INTO clients (name, ip, privatekey, publickey, timeout, allowedips, endpoint, creation_date) values (\"{client_name}\", \"{ip}\", \"{publickey}\", \"{privatekey}\", {timeout}, \"{allowed_ips}\", \"{endpoint}\", {epoch});")
            print(f"Client {client_name} has been added successfully")
        conn.commit()
        conn.close()
    def remove(client_name):
        #delete client from db
        conn = sqlite3.connect(vvars["db_dir"]+vvars["db_name"])
        cursor = conn.cursor()
        try:
            cursor.execute(f"DELETE FROM clients WHERE name='{client_name}';")
            print(f"Client {client_name} has been removed from DB successfully;")
        except Exception:
            print(f"Client {client_name} has not been found in DB;")
        conn.commit()
        conn.close()
    def tg_status(action, value=0):
        conn = sqlite3.connect(vvars["db_dir"]+vvars["db_name"])
        cursor = conn.cursor() 
        if action == 'get':
            try:
                return int(cursor.execute("SELECT tg_status FROM config;").fetchall()[0][0])
            except Exception:
                print("cl_sqlite.tg_status failed to get tg_status from DB")
        elif action == "set":
            try:
                cursor.execute(f"UPDATE config set tg_status = '{value}';")
                return 0
            except Exception:
                print("cl_sqlite.tg_status failed to change tg_status in DB")
        conn.commit()
        conn.close()

