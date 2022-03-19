from hmac import trans_5C
from re import A
from constants import *
from base64 import b64encode
from string import ascii_uppercase, ascii_lowercase, digits
from nacl.public import PrivateKey, PublicKey
from cl_sqlite import sqlite as db
import os, shutil, qrcode, sys

class client:

    def __init__(self, name, server_pub_key, config):
        print("H1")
        if_client=db.show(config, name,"name")
        print("H2")
        if not if_client:
            priv_key, pub_key=self.genkey() #generating new client's keys (public and private)
            os.makedirs(f"{config['keys_dir']}{name}")
            print(f"{config['keys_dir']}{name}/{name}.priv")
            with open(f"{config['keys_dir']}{name}/{name}.priv", "w") as f: # rewriting wg config without deleted client
                f.write(priv_key)
            with open(f"{config['keys_dir']}{name}/{name}.pub", "w") as f: # rewriting wg config without deleted client
                f.write(pub_key)
            print("LOG: Client keys created successfully")
            # check used IPs and set IP for new client
            print("H3")
            ip=self.set_ip(config) # list of used IPs
            print("New client's IP: " + ip)
            # create new client in wg config, db and generate client's config and qr-code
            self.add(name=name, ip=ip, publickey=pub_key, privatekey=priv_key, srv_pub=server_pub_key, config=config)
        else:
            print(f"Client {name} already exists")


    def restart_wg():
        try:
            os.system('wg-quick down client && wg-quick up client')
        except Exception:
            print("ERROR: Failed to restart WG server!")

    def suspend(name, status, config):
        if status:
            print(f"Suspend client {name}")
            try: ## add new client to main wg config.
                wg_config=config['wg_config'] #path to wg config
                with open(wg_config, "r+") as f: #reading wg config
                    config = f.readlines()
                name_wg=f"#{name}\n" # client's name in wg config
                index_num=config.index(name_wg)+3 # last line of client's block in wg config
                for x in range(4): #suspend client's block in wg config
                    susp_line="#"+config[index_num] #comment every line of suspending client in config
                    config[index_num] = susp_line #rewrite config list with commented lines
                    index_num=index_num-1
                with open(wg_config, "w") as f: # rewriting wg config with suspended client
                    for line in config:
                        f.write(line)
            except Exception:
                print(f"ERROR: Failed to suspend user {name}")
        elif not status:
            print(f"Resume client {name}")
            try: ## add new client to main wg config.
                wg_config=config['wg_config'] #path to wg config
                with open(wg_config, "r+") as f: #reading wg config
                    config = f.readlines()
                name_wg=f"##{name}\n" # client's name in wg config
                index_num=config.index(name_wg)+3 # last line of client's block in wg config
                for x in range(4): #resume client's block in wg config
                    susp_line=str(config[index_num]).replace('#','', 1) #comment every line of resuming client in config
                    config[index_num] = susp_line #rewrite config list with commented lines
                    index_num=index_num-1
                with open(wg_config, "w") as f: # rewriting wg config with resumed client
                    for line in config:
                        f.write(line)
            except Exception:
                print(f"ERROR: Failed to resume user {name}")

    def genkey(self):
        try:
            pk = PrivateKey.generate()
            priv_key = b64encode(bytes(pk)).decode("ascii")
            pub_key = b64encode(bytes(pk.public_key)).decode("ascii")
            print("NEW CLIENT KEYS:")
            print("Priv: ", priv_key)
            print("Pub: ", pub_key)
        except Exception:
            print("client.genkey failed")
        return (priv_key, pub_key)

    
    def set_ip(self, config): #DONE
        print("H4 " + config['FCI'])
        try:
            ip_list=(db.show(config=config, name="all", ip="*")) #getting all IPs in use
            print("DEBUG: IP_list = ", ip_list)
        except Exception:
            print("ERROR: failed to get ip_list")
            sys.exit()
        ip_base=config['net'][:-1]
        print("DEBUG: IP_list = ", ip_base)
        if not ip_list: # if all IPs are free (no clients created for now)
            print("All IPs are free!")
            ip=ip_base+str(config['FCI'])
        else: # if there are already created clients and some IPs already in use
            print(int(ip_list[-1][1].split('.')[-1])+1)
            new_ip=int(ip_list[-1][1].split('.')[-1])+1 # new last IP octet for new client is last used ip +1
            ip=ip_base+str(new_ip) # set new client's IP
        print("Trace: return ip = "+ ip)
        return ip


    def add(self, name, ip, publickey, privatekey, srv_pub, config, timeout=60, allowed_ips="10.1.1.0/24", endpoint="54.36.241.190:35053"):
        try: ## add new client to main wg config.
            print("DEBUG:")
            print("CL_CLIENT.add publickey:", publickey)
            print("CL_CLIENT.add privkey:", privatekey)
            print("CL_CLIENT.add srv_pub:", srv_pub)
            client_server_config=f'\n#{name}\n[Peer]\nPublicKey = {publickey}\nAllowedIPs = {ip}'+'/32\n' # gen text
            with open(config['wg_config'], "a") as f: # rewriting wg config without deleted client
                f.write(client_server_config)
        except Exception:
            print("ERROR: client.add_client2config failed while adding client to config")
            sys.exit()
        try: ## add new client to db
            db.add(name, ip, publickey, privatekey, timeout, allowed_ips, endpoint, config)
        except Exception:
            print("ERROR: client.add_client2config failed while addig client to DB")
            sys.exit()
        try:
            self.gen_client_config(name, ip, publickey, privatekey, timeout, allowed_ips, endpoint, srv_pub, config)
        except Exception:
            print("client.add call gen_client_config failed")

    def remove(name, config):
        try: ## add new client to main wg config.
            print("Client remove")
            if_suspended=db.show(config=config, name=name, check="suspend")
            print(if_suspended)
            if int(if_suspended) == 0:
                name_wg=f"#{name}\n" # client's name in wg config
            else:
                name_wg=f"##{name}\n" # client's name in wg config
            print(name_wg)
            with open(config['wg_config'], "r+") as f: #reading wg config
                wg_config = f.readlines()
            index_num=wg_config.index(name_wg)+4 # last line of client's block in wg config
            for x in range(5): #delete client's block in wg config
                del wg_config[index_num]
                index_num=index_num-1
            print("DEBUG: delete from wg_config: ", wg_config)
            with open(config['wg_config'], "w") as f: # rewriting wg config without deleted client
                for line in wg_config:
                    f.write(line)
        except Exception:
            print("ERROR: client.remove_client error while deleting client from config")
        db.remove(name, config) #remove client from db
        try:
            if os.path.exists(f"{config['configs_dir']}{name}") == True:
                shutil.rmtree(f"{config['configs_dir']}{name}")
            else:
                print(f"{name}'s config files not found")
        except Exception:
            print(f"Error while removing config files of client {name}")


    def gen_client_config(self, name, ip, srv_publickey, privatekey, timeout, allowed_ips, endpoint, server_pub_key, config):
        if not "/32" in ip:
            ip=ip+'/32'
        text=f"#{name}\n[Interface]\nAddress = {ip}\nPrivateKey = {privatekey}\n\n[Peer]\nPublicKey = {server_pub_key}AllowedIPs = {allowed_ips}\nEndpoint = {endpoint}\nPersistentKeepalive = {timeout}" #generating client config
        try:
            os.makedirs(f"{vvars['configs_dir']}{name}")
            config=f"{vvars['configs_dir']}{name}/{name}.conf" #define client config file path
            conf_file = open(config, 'a')
            conf_file.write(text) # add config to client's config file;
            conf_file.close()
        except Exception:
            print("client.gen_client_config error generating client'q config file")
        try:
            print("QRCODE!")
            print(text)
            qr_conf=qrcode.make(text) #generate qr-code
            qr_conf.save(f"{vvars['configs_dir']}{name}/{name}.png") #and save it as png image
        except Exception:
            print("client.gen_client_config error generating client's config qr-code")
