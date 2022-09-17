#!/usr/bin/python3

import requests
import sqlite3
import xml.etree.ElementTree as ET
from getmac import get_mac_address,getmac
import os,time

def scanning():
          try:
                    ip = []
                    mac = []
                    name = []
                    response = requests.get("<routers clients table page URL>")
                    data = response.text
                    file = open(".data.xml","w")
                    file.write(data)
                    file.close()
                    tree = ET.parse(".data.xml")
                    root = tree.getroot()
                    
                    for x in root.findall('user_list'):
                              for y in x.findall('user'):
                                        name.append( y.find('name').text)
                                        ip.append(y.find('ip').text)
                                        mac.append(y.find('mac').text)
                    database()
                    update(ip,mac,name)


          except requests.exceptions.ConnectionError:
                    print("[-] Request timeout please check you conneted to router")
                    exit(1)
          except KeyboardInterrupt:
                    print("[-] You Pressed [ Ctrl + C ]")
                    exit(1)

#database create
def database():
          try:
                    conn = sqlite3.connect('database1.db')
                    cursor = conn.cursor()
                    query = "CREATE TABLE IF NOT EXISTS data(IP TEXT,MAC TEXT,NAME TEXT)"
                    cursor.execute(query)
          except sqlite3.Error as error:
                    print("faild to create",error)
                    exit(1)

#update data's to database
def update(ip,mac,name):
          try:
                    conn = sqlite3.connect('database1.db')
                    cur = conn.cursor()
                    cur.execute('DELETE FROM data')
                    for i in range(len(ip)):
                              ip2 = ip[i]
                              mac2 = mac[i]
                              name2 = name[i]
                              cur.execute(' INSERT INTO data(IP,MAC,NAME) VALUES(?,?,?)',(ip2,mac2,name2))
                    print("###############################")
                    print("ARP-TABLE updated into Database")
                    print("###############################")
                    conn.commit()
                    admin_mac = str(getmac.get_mac_address())
                    print( "admin MAC : ",admin_mac)
                    admin_mac = admin_mac.upper()
                    print(admin_mac)
                    admin_mac_add = admin_mac.replace(":","-")
                    print("formated MAC: ",admin_mac_add)
                    try:
                              cur.execute("DELETE  FROM data WHERE MAC= (?)",(admin_mac_add,))
                              conn.commit()
                              print("Admin MAC removed from Database") 
                              cur.close()

                    except sqlite3.Error as error:
                              print("Error while Delete admin mac,",error)
                              exit(1)

          except sqlite3.Error as error:
                    print("Error while insertion", error)
                    exit(1)
          
# Fetch all MAC and IP from database table and do operation
def fetch():
          try:
                    conn = sqlite3.connect('database1.db')
                    cur = conn.cursor()
                    cur.execute("SELECT *  from data")
                    rows = cur.fetchall()
                    
                    iplist= []
                    print("\n#-----------Data from table ---------------#")
                    for row in rows:
                              iplist.append(row[0])
                              print("Ip : ",row[0])
                              print("MAC:  ",row[1] )
                              print("Name :",row[2])
                    print("#--------- Data from table End ------------#")
                    if len(iplist) != 0:
                              print("IP address list :",iplist)
                    else:
                              print("No clients found")
                              exit(1)
                    _size = len(iplist)
                    repeted_ip = []
                    for i in range(_size):
                              k = i+1
                              for j in range(k,_size):
                                        if iplist[i] == iplist[j] and iplist[i] not in repeted_ip:
                                                  repeted_ip.append(iplist[i])
                    print("Suspected IP Address is : ",repeted_ip)
                    if repeted_ip:
                              sus_mac_list = []
                              cur.execute("SELECT MAC FROM data WHERE IP=(?)",(repeted_ip[0],))
                              vals = cur.fetchall()
                              for mac in vals:
                                        sus_mac_list.append(mac)
                              print("Suspected MAC's are : ",sus_mac_list)
                              conn.commit()
                              original_mac = get_mac_address(ip=repeted_ip[0])
                              orinal_upper = original_mac.upper()
                              innocent_mac = orinal_upper.replace(":","-")
                              for i in range(len(sus_mac_list)):
                                        print("check att mac : ",sus_mac_list[i])
                                        if sus_mac_list[i] == innocent_mac:
                                                  print("Victim's MAC address : ",sus_mac_list[i])
                                        else:
                                                  _attacker_mac = sus_mac_list[i]
                                                  print("Attacker MAC : ",_attacker_mac)
                              interface = "wlan0mon"
                              print("Normal Attacker mac : ",_attacker_mac)
                              blocker_mac = str(_attacker_mac)
                              blocker_mac = blocker_mac.replace("-",":")
                              print("This is our normal mac to block : ", blocker_mac)

                              print("Deauthentication Started.. Here.......",blocker_mac)
                              os.system("xterm -T 'De-authenticating Attacker' -fa manaco -fs 10 -bg black -e 'aireplay-ng --deauth 100 -a' "+(blocker_mac)+" "+(interface))

          except KeyboardInterrupt:
                    print("[ - ] You pressed [ Ctrl + C ]")
                    exit(1)

#main functin
if __name__ == "__main__":
          while True:
                    try:
                              scanning()
                              fetch()
                              time.sleep(5)
                    except KeyboardInterrupt:
                              print("[-] You Pressed [ Ctrl + C ]")
                              print("[-] ARP-SPOOF DETECTER OFF")
                              exit(1)
