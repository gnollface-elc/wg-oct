from constants import *
import requests

class tg:
  def notify(action, name):
    if action == 'add':
      text=f"New client {name} added!\n"
    elif action == 'remove':
      text=f"New client {name} added!\n"
    else:
      print("tg.notify wrong action!")
    for chat_id in vvars['chat_id']:
      print(chat_id)
      try:
        params = {'chat_id': chat_id, 'text': text}
        print(params,  vvars["tg_url"])
        requests.post(vvars["tg_url"], params).json()
      except Exception:
        print("Notify error")
    return False;
#DONE