#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
import re
import sys , os , getpass
import pickle
import webbrowser
from tabulate import tabulate
import xml.etree.ElementTree as ET






def check_files():
  try:
      config = open("config.ini", "r").readlines()
  except(IOError):
    print "\n\033[1;31m[!] Sir Please run slaves.py --config for configuration script . \033[0;37m\n"
    sys.exit(1)

def configure_script():
    # Configure XML elements
    top = ET.Element('config') #configure XML elements
    username = ET.SubElement(top, 'username')

    # Asks user for input to popluate and save XML file.
    username.text = raw_input("\n[+] Please enter your name sir : ")

    # Configure encryption
    password = getpass.getpass("[+] Please enter a password. You'll need this next time you run this script: ")

    key = hashlib.md5(password.encode('utf-16')).digest()

    BLOCK_SIZE = 32

    PADDING = '{'

    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))

    cipher = AES.new(key)

    #Encrypt and save data to file
    stringtowrite = ET.tostring(top).decode("utf-8")

    datatowrite = EncodeAES(cipher, stringtowrite)

    pickle.dump(datatowrite, open('config.ini', 'wb',0))
    open('db.enc', 'wb',0)



def get_config(password):

  # Open file and get encrypted data
  try:
      datafromfile = pickle.load(open('config.ini', 'rb'))
  except IOError as err:
      print("\n[!] Unable open configuration file. please check file permission!")
      sys.exit(2)

  # Configure encryption
  key = hashlib.md5(password.encode('utf-16')).digest()

  BLOCK_SIZE = 32

  PADDING = '{'

  pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

  DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

  cipher = AES.new(key)


  # Decrypt data from file.

  plaintext = DecodeAES(cipher, datafromfile)

  # Pull out XML string only.
  try:
      rawdata = re.findall(r'(<config>.+</config>)', str(plaintext))[0]
  except IndexError:
      print("\n\033[1;31m[!]OOps Wrong Password ! :D\033[0;37m\n ")
      sys.exit(2)

  # Rebuild XML element tree.
  configdictionary = {}
  configdata = ET.fromstring(rawdata)

  # Build dictionary of configuration information.
  for child in configdata:
      configdictionary[child.tag] = child.text

  return configdictionary

#db jobs like add, del , edit , command , list

def command():

  try:
    slaves = open('db.enc', "r").readlines()
  except(IOError):
    menu("[-] Error: Check your database file\n")
    return FALSE

  print ""
  ID = raw_input("   [+]Please enter slave id for running command :  ")

  cnt = 0
  for slave in slaves:
      cnt += 1
      if(str(cnt) == ID):
        decoded = decode(password , slave)
        URL , IMPORTANT ,  NOTE  = decoded.split('|')

  while True:
    cmd = raw_input("   [+]Your Command (for exit type 'exit') :  ")
    if len(cmd) > 0:
        cmd = cmd.upper()
        if cmd != "exit":
            print "Reboot"
        else:
            break
  menu("")


def add():
  print ""
  url = raw_input("   [+]boss please enter your new slave URL : ")
  important = raw_input("   [+]is this slave importatn for you (y,n) ? ")
  note = raw_input("   [+]please enter a description for this slave : ")
  datatoenc = url +"|"+important+"|"+note
  datatowrite = encode(password ,datatoenc)
  print datatowrite
  file = open('db.enc','a',0)
  file.writelines(datatowrite + '\n')
  file.close
  result = "   \033[1;31m[!]Your new slave success added to db . sir !\033[0;37m \n"
  menu(result)

def delete():
  print ""
  ID = raw_input("   [+]Please enter slave id for delete :  ")

  slaves =  open('db.enc', "r",0).readlines()


  file = open("db.enc","w",0)
  cnt = 0
  for slave in slaves:
    cnt += 1
    print cnt ," | " , ID
    if (str(cnt) != ID):
      file.write(slave)
  file.close
  result = "   \033[1;31m[!]Your slave success deleted from db . sir !\033[0;37m \n"
  menu(result)

def list():
  try:
    slaves = open('db.enc', "r").readlines()
  except(IOError):
    print "[-] Error: Check your database file\n"
    sys.exit(1)

  cnt = 0
  report = []
  for slave in slaves:
      cnt += 1
      decoded = decode(password , slave)
      URL , IMPORTANT ,  NOTE  = decoded.split('|')
      report +=   [[str(cnt) , URL ,  IMPORTANT ,  NOTE]]

  print ""
  print  tabulate(report,headers=["ID","URL", "IMPORTANT","NOTE"],tablefmt="grid")
  raw_input("\n   [!]Please ENTER to continue !")
  menu("")




# End db jobs **************************************************************

def open_slave():
  try:
    slaves = open('db.enc', "r").readlines()
  except(IOError):
    menu("[-] Error: Check your database file\n")
    return FALSE

  print ""
  ID = raw_input("   [+]Please enter slave id for open :  ")

  cnt = 0
  for slave in slaves:
      cnt += 1
      if(str(cnt) == ID):
        decoded = decode(password , slave)
        URL , IMPORTANT ,  NOTE  = decoded.split('|')
        webbrowser.open(URL)
  menu("")

def auth():
  passwd = getpass.getpass ("\n[!] Hi sir can i ask your password ? ")
  config = get_config(passwd)

  global name
  global password

  name =  config['username']
  password = key = hashlib.md5(passwd.encode('utf-16')).digest()

def menu(result) :

  os.system('tput reset')
  print "   .--------------------------------------------------.---\033[0;38m[INFO]\033[0;37m--------------------------\033[0;38m[DB]\033[0;37m------------------------."
  print "   |MY _______  _        _______           _______    | list - all of your slaves     | search - DB's serch           |"
  print "   |  (  ____ \( \      (  ___  )|\     /|(  ____ \   | check - available slaves      | report - :|                   |"
  print "   |  | (    \/| (      | (   ) || )   ( || (    \/   | imp - view importants         | clear - Remove duplicates     |"
  print "   |  | (_____ | |      | (___) || |   | || (__       | stat - Status                 | destroy - clear anything O.o  |"
  print "   |  (_____  )| |      |  ___  |( (   ) )|  __)      |---\033[0;38m[SLAVES]\033[0;37m------------------------\033[0;38m[OTHERS]\033[0;37m--------------------| "
  print "   |        ) || |      | (   ) | \ \_/ / | (         | add - new slave               | ftp - backup to ftp           |"
  print "   |  /\____) || (____/\| )   ( |  \   /  | (____/\   | del - so ...                  | exp - export to file          |"
  print "   |  \_______)(_______/|/     \|   \_/   (_______/   | open - open a slave           | ---                           |"
  print "   |                                               S  | cmd - run command on slave    | exit - Quits                  |"
  print "   '--------------------------------------------------'---------------------------------------------------------------'"

  print result
  choose = raw_input("   [!]my boss  , what can i do for you ? ")
  choose = choose.strip()

  if (choose == 'add'):
      add()
  elif (choose == 'del'):
      delete()
  elif (choose == 'edit'):
      delete()
  elif (choose == 'cmd'):
      command()
  elif (choose == 'list'):
      list()
  elif (choose == 'open'):
      open_slave()
  elif (choose == 'exit'):
      os.system('tput reset')
      sys.exit(2)
  else:
      menu('   \033[1;31m[!]Sorry boss but i can not find your order :(\033[0;37m \n')



if (len(sys.argv) != 1):
    if(sys.argv[1] == '--config') :
      print '\n[!] Starting configuration script ... '
      configure_script()
      print '\n[!] Well Done sir ! '
      sys.exit(2)


if __name__ == "__main__":
  check_files()
  auth()
  result = '   \033[1;31m[!]Welcome my boss ' + name + '\033[0;37m \n'
  menu(result)


