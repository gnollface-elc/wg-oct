#!/usr/bin/python3.8
from constants import *
from cl_notify import tg
from cl_sqlite import sqlite as db
from cl_client import client
from nacl.public import PrivateKey, PublicKey
import os, sys, argparse, json, yaml
from base64 import b64encode

parser = argparse.ArgumentParser(description='Init arguments parse')
parser.add_argument('-c', '--config', metavar='', required=True, help='Path to config file')
parser.add_argument('-m', '--mode', metavar='', required=True, help='Options: http|api|script')
parser.add_argument('-a', '--action', metavar='', help='Options: create|remove|suspend|resume|show')
parser.add_argument('-n', '--name', metavar='', help='User name')
parser.add_argument('--ip', metavar='', help='User ip')
parser.add_argument('-k', '--key', metavar='', help='User pub key'),
parser.add_argument('-f', '--format', metavar='', help='Output format'),
parser.add_argument('--tgchat', metavar='', help='Telegram chat id. "--telegram" argument as "on" or "1" is required'),
parser.add_argument('-t', '--telegram', metavar='', help='Telegram status. "off/on" or "0/1". "--name" argument requied!')





args = parser.parse_args()

### parse config yaml file ###
with open(args.config, 'r') as config_file:
  yaml_conf=yaml.safe_load(config_file)

config={
  "base_dir": f"{yaml_conf['dirs']}",
  "configs_dir": f"{yaml_conf['dirs']['base_dir']}{yaml_conf['dirs']['util_dir']}{yaml_conf['dirs']['configs_dir']}",
  "keys_dir": f"{yaml_conf['dirs']['base_dir']}{yaml_conf['dirs']['util_dir']}{yaml_conf['dirs']['keys_dir']}",
  "db_dir": f"{yaml_conf['dirs']['base_dir']}{yaml_conf['dirs']['util_dir']}db/",
  "db_config": f"{yaml_conf['dirs']['base_dir']}{yaml_conf['dirs']['util_dir']}{yaml_conf['dirs']['db_dir']}{yaml_conf['config']['db_name']}",
  "wg_config": f"{yaml_conf['dirs']['base_dir']}{yaml_conf['config']['wg_conf']}",
  "srv_ip": f"{yaml_conf['config']['network']['srv_ip']}",
  "net": f"{yaml_conf['config']['network']['net']}",
  "netmask": f"{yaml_conf['config']['network']['netmask']}",
  "listen_port": f"{yaml_conf['config']['network']['listen_port']}",
  "FCI": f"{yaml_conf['config']['network']['FCI']}",
  "tg_token": f"{yaml_conf['config']['telegram']['token']}",
  "tg_chat_id": f"{yaml_conf['config']['telegram']['chat_id']}",
  "tg_url": f"{yaml_conf['config']['telegram']['tg_url']}"
}

def init():
  ### CREATE dirs ###
  try:
    if not os.path.exists(config['configs_dir']):
      os.makedirs(config['configs_dir'])
    if not os.path.exists(config['keys_dir']):
      os.makedirs(config['keys_dir'])
    if not os.path.exists(config['db_dir']):
      os.makedirs(config['db_dir'])
    print("LOG: init dirs created")
  except Exception:
    print("ERROR: Creating dirs failed!")
    sys.exit()
  try:
    print(os.path.exists(config['wg_config']))
    print(config['srv_ip'])
    if not os.path.exists(config['wg_config']):
      srvpk = PrivateKey.generate()
      server_priv_key = b64encode(bytes(srvpk)).decode("ascii")
      server_pub_key = b64encode(bytes(srvpk.public_key)).decode("ascii")
      print(f"[Interface]\nAddress = {config['srv_ip']}\nPrivateKey = {server_priv_key}\nListenPort = {config['listen_port']}\n\n")
      print("LOG: server keys created")
      server_config = f"[Interface]\nAddress = {config['srv_ip']}\nPrivateKey = {server_priv_key}\nListenPort = {config['listen_port']}\n\n"
      print(server_config)
      with open(config['wg_config'], "w+") as f: #reading wg config
        f.write(server_config)
      with open(config['configs_dir']+"srv.priv", "w+") as srv_priv_key:
        srv_priv_key.write(server_priv_key)
      with open(config['configs_dir']+"srv.pub", "w+") as srv_pub_key:
        srv_pub_key.write(server_pub_key)
      print("LOG: init wg config file created")
    else:
      print(config['wg_config'])
      with open(config['wg_config'], "r+") as f: #reading wg config
        srv_config = f.readlines()
        print(srv_config)
        server_pub_key = srv_config[2].split(' ')[2]
  except Exception:
    print("ERROR: Creating conf file failed!")
    sys.exit()
  return server_pub_key
# DONE!
 
if __name__ == "__main__":
  print('call init')
  server_pub_key=init()
#  print("IP:", args.ip)
  if args.mode == 'script':
#    print("script mode selected!") 
    if args.action == 'init_db':
      db.init(config)
    #ADD ACTION
    if args.action == 'add':
      print("H0")
      if args.name:
        client(name=args.name, server_pub_key=server_pub_key, config=config)
        client.restart_wg()
      else:
        print("Error: client name is required!\nUse argument '--name' to set name")
    #REMOVE ACTION
    elif args.action == 'remove':
      if args.name:
        client.remove(args.name, config)
        client.restart_wg()
      else:
        print("Error: client name is required!\nUse argument '--name' to set name")
    #SUSPEND ACTION
    elif args.action == 'suspend':
      if args.name:
        client.suspend(args.name, True, config)
        db.suspend(args.name, True, config)
        client.restart_wg()
      else:
        print("Error: client name is required!\nUse argument '--name' to set name")
    #RESUME ACTION
    elif args.action == 'resume':
      if args.name:
        client.suspend(args.name, False, config)
        db.suspend(args.name, False, config)
        client.restart_wg()
      else:
        print("Error: client name is required!\nUse argument '--name' to set name")
    #SHOW ACTION
    elif args.action == 'show':
      if args.name and not args.ip and not args.key:
        client_list=db.show(config=config, name=args.name)
      elif not args.name and args.ip and not args.key:
        client_list=db.show(config=config, ip=args.ip)
      elif not args.name and not args.ip and args.key:
        client_list=db.show(config=config, key=args.key)
      if args.format == "json":
        dict={}
        cl_list=[]
        for i in range(len(client_list)):
          dict['Name']=client_list[i][0]
          dict['IP']=client_list[i][1]
          dict['last']=client_list[i][2]
          dict['created']=client_list[i][3]
          dict['Telegram']=client_list[i][4]
          dict['Suspended']=client_list[i][5]
          cl_list.append(dict)
        print(json.dumps(cl_list))
      else:
        for i in range(len(client_list)):
          print("-----------------------------------")
          print(f"Name:{client_list[i][0]}\nIP:{client_list[i][1]}\nlast:{client_list[i][2]}\ncreated:{client_list[i][3]}\nTelegram:{client_list[i][4]}\nSuspended:{client_list[i][5]}\n")
    elif args.telegram and args.name:
      print("Telegram action called!$$$")
      if args.telegram == 0 or args.telegram == 'off':
        print("TG1")
        db.telegram(config, args.name)
      elif args.telegram == 1 or args.telegram == 'on':
        print("TG2")
        if args.tgchat:
          print("TG2.1")
          print("args.tgchat", args.tgchat)
          db.telegram(config, args.name, 1, args.tgchat)
        else:
          print("TG2.2")
          print("args.tgchat", args.tgchat)
          db.telegram(config, args.name, 1)
    elif args.telegram and not args.name:
      print("Argument --name is required!")
    elif args.action == 'test':
      print("TEST MODE!!!")
      user=db.show(config=config, name=args.name, check="suspend")
      print(user)
          



#      if not args.name and args.ip:
#        client_list=db.show(ip=args.ip)
#        print(client_list)
#      else:
#        print("Error: client name is required!\nUse argument '--name' to set name")