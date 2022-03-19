from constants import *
import sqlite3, time, sys

class sqlite:
#    conn = sqlite3.connect(config["db_dir"]+"octopus.db")
#    cursor = conn.cursor()
    def init(config):
        print("TRACE: DB.init")
        try:
            #create table if not exist
            conn = sqlite3.connect(config["db_dir"]+"octopus.db")
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS clients (name TEXT NOT NULL, status INTEGER DEFAULT 0, last INTEGER DEFAULT 0, privatekey TEXT, publickey TEXT, ip TEXT, timeout INTEGER DEFAULT 60, allowedips TEXT, endpoint TEXT, creation_date INTEGER);")
            cursor.execute("CREATE TABLE IF NOT EXISTS config (name TEXT, tg_status INTEGER DEFAULT 0, tg_chats TEXT, suspend INTEGER DEFAULT 0);")
#            cursor.execute(f"INSERT INTO config (tg_status) VALUES ('0');")
            conn.commit()
            conn.close()
            return 0
        except Exception:
            print("LOG: DB init error")


    def show(config, name=None, ip=None, key=None, check=None):
        print(f"SELECT clients.name, clients.ip, clients.last, clients.creation_date, config.tg_status, config.suspend from clients INNER JOIN config ON clients.name=config.name;")
        try:
            print("H5")
            #show client or client list
            print("connecting to "+config["db_dir"]+"octopus.db")
            conn = sqlite3.connect(config["db_dir"]+"octopus.db") #select DB file
            cursor = conn.cursor() #connect 2 DB
#            print("db connected")
        except Exception:
            print("Connection to DB failed!")
            sys.exit()
        try:
            # SHOW IF CLIENT SUSPENDED
            if check == "suspend" and name != None and name != "all":
                sql_request=f"SELECT suspend from config where name='{name}';"
                res=cursor.execute(sql_request).fetchall()[0][0] 
                return(res)
            #SHOW ALL NON VULNERABLE INFO
            elif name == "all" or name == None and ip == None and key == None:
                sql_request=f"SELECT clients.name, clients.ip, clients.last, clients.creation_date, config.tg_status, config.suspend from clients INNER JOIN config ON clients.name=config.name;"
                res=cursor.execute(sql_request).fetchall()
                result=[]
                for i in res:
                    result.append(i)
                return(result)
            # SHOW USERS INFO by username
            elif name != None and name != "all" and ip == None and key == None:
                print("Trace: Show by name")
                sql_request=f"SELECT clients.name, clients.ip, clients.last, clients.creation_date, config.tg_status, config.suspend from clients INNER JOIN config ON clients.name=config.name WHERE clients.name='{name}';"
                res=cursor.execute(sql_request).fetchall()
                print(res)
                return(res)
            # SHOW USERS INFO BY IP
            elif name == None and ip != None and key == None:
                print("Trace: Show by ip")
                sql_request=f"SELECT clients.name, clients.ip, clients.last, clients.creation_date, config.tg_status, config.suspend from clients INNER JOIN config ON clients.name=config.name WHERE clients.ip='{ip}';"
                res=cursor.execute(sql_request).fetchall()
                return(res)
            # SHOW USERS INFO BY USER'S PUB KEY
            elif name == None and ip == None and key != None:
                sql_request=f"SELECT clients.name, clients.ip, clients.last, clients.creation_date, config.tg_status, config.suspend from clients INNER JOIN config ON clients.name=config.name WHERE clients.publickey like '%{key}%';"
                res=cursor.execute(sql_request).fetchall()
                print("TRACE: show by key: ", res)
                return(res)
            # SHOW LAST USED IP
            elif name == "all" and ip == '*' and key == None:
                sql_request=f"SELECT clients.ip from clients;"
                res=cursor.execute(sql_request).fetchall()
                return(res)
        except Exception:
            print("LOG: DB 'show' error")
        conn.commit()
        conn.close()

    def add(client_name, ip, publickey, privatekey, timeout, allowed_ips, endpoint, config):
        #add client to db if not exists
        print("DB")
        try:
            conn = sqlite3.connect(config["db_dir"]+"octopus.db")
            print("DB1")
            cursor = conn.cursor()
            print("DB2")
            try:
                cursor.execute(f"SELECT name FROM clients WHERE name = '{client_name}';").fetchall()[0][0]
                print("Client already exists")
            except Exception:
                epoch=int(time.time())
                cursor.execute(f"INSERT INTO clients (name, ip, privatekey, publickey, timeout, allowedips, endpoint, creation_date) values (\"{client_name}\", \"{ip}\", \"{privatekey}\", \"{publickey}\", {timeout}, \"{allowed_ips}\", \"{endpoint}\", {epoch});")
                print(f"Client {client_name} has been added successfully")
                cursor.execute(f"INSERT INTO config (name) values (\"{client_name}\")")
            conn.commit()
            conn.close()
        except Exception:
            print("ERROR: db.add error")

    def remove(client_name, config):
        #delete client from db
        try:
            conn = sqlite3.connect(config["db_dir"]+"octopus.db")
            cursor = conn.cursor()
            try:
                cursor.execute(f"DELETE FROM clients WHERE name='{client_name}';")
                cursor.execute(f"DELETE FROM config WHERE name='{client_name}';")
                print(f"Client {client_name} has been removed from DB successfully;")
            except Exception:
                print(f"Client {client_name} has not been found in DB;")
            conn.commit()
            conn.close()
        except Exception:
            print(f"ERROR: db.remove error {client_name}")

    def suspend(client_name, status, config):
        if status:
            conn = sqlite3.connect(config["db_dir"]+"octopus.db")
            cursor = conn.cursor()
            try:
                cursor.execute(f"UPDATE config SET suspend = 1 WHERE name = '{client_name}';")
            except Exception:
                print(f"ERROR: cl_sqlite.suspend while trying to suspend client '{client_name}';")
        elif not status:
            conn = sqlite3.connect(config["db_dir"]+"octopus.db")
            cursor = conn.cursor()
            try:
                cursor.execute(f"UPDATE config SET suspend = 0 WHERE name = '{client_name}';")
            except Exception:
                print(f"ERROR: cl_sqlite.suspend while trying to suspend client '{client_name}';")
        conn.commit()
        conn.close()


    def telegram(config, name, value=0, chats=''):
        conn = sqlite3.connect(config["db_dir"]+"octopus.db")
        cursor = conn.cursor()
#        if action == 'get':
#            try:
#                return int(cursor.execute(f"SELECT tg_status FROM config WHERE name='{name}';").fetchall()[0][0])
#            except Exception:
#                print("cl_sqlite.tg_status failed to get tg_status from DB")
        print("DEBUG: db.telegram!")
        if not chats:
            print("CHATS VAR IS EMPTY ", chats)
            try:
                cursor.execute(f"UPDATE config SET tg_status = '{value}' WHERE name='{name}';")
            except Exception:
                print("cl_sqlite.tg_status failed to change tg_status in DB")
        else:
            print("CHATS VAR IS NOT EMPTY ", chats)
            try:
                cursor.execute(f"UPDATE config SET tg_status = '{value}' WHERE name='{name}';")
                cursor.execute(f"UPDATE config set tg_chats = '{chats}' WHERE name = '{name}';")
            except Exception:
                print("cl_sqlite.tg_status failed to change telegram chats list in DB")
        conn.commit()
        conn.close()

