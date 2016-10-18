#!/usr/bin/python
import papi
import getpass
import json
import sys
import getopt
import time
import re

def get_snaps (cluster, user, password,resume):
  if resume is None:
    path = "/platform/1/snapshot/snapshots"
  else:
    path = "/platform/1/snapshot/snapshots?resume="+resume
  (status, reason, resp) = papi.call (cluster, '8080', 'GET', path, '', 'any', 'application/json', user, password)
  if status != 200:
    err_string = "ERROR: Bad Status: " + str(status)
    sys.stderr.write (err_string)
    exit (status)
  return (json.loads(resp))

def byte_convert (bytes,raw):
  if raw == True:
    return (str(bytes))
  if (bytes < 1024):
    bytes_s =  str(bytes)
  elif (bytes >= 1024 and bytes < 1048576):
    bytes = float(bytes) / 1024
    bytes_s = str("%.2f" % bytes) + "K"
  elif (bytes >= 1048576 and bytes < 1073741824):
    bytes = float(bytes) / 1024 / 1024
    bytes_s = str("%.2f" % bytes) + "M"
  elif (bytes >= 1073741824 and bytes < 1099511627776):
    bytes = float(bytes) / 1024 / 1024 / 1024
    bytes_s = str("%.2f" % bytes) + "G"
  else:
    bytes = float(bytes) / 1024 / 1024 / 1024 / 1024
    bytes_s = str("%.2f" % bytes) + "T"
  return (bytes_s)


def usage ():
  sys.stderr.write ("Usage: snap_report[.py] -c cluster [-p search_path] [-r] [-o file]\n")
  sys.stderr.write ("    -c | --cluster : Name or IP of a node in the cluster\n")
  sys.stderr.write ("    -p | --path    : Path of the snapshot\n")
  sys.stderr.write ("    -r | --raw     : Use Raw byte numbers\n")
  sys.stderr.write ("    -o | --output  : Specify an output file for the csv\n")

def oprint (out, file, first):
  if file == "**STDOUT**":
    print out
  else:
    if first == True:
      with open (file, 'w') as of:
        of.write (out)
        of.write ("\n")
    else:
      with open (file, "a") as of:
        of.write (out)
        of.write ("\n")
    of.close()

cluster = ''
search_path = ''
total = 0
raw = False
ofile = "**STDOUT**"
first = True
done = False
resume = None

optlist, args = getopt.getopt (sys.argv[1:], 'c:hro:p:', ['cluster=', "help" ,"raw", "output=", "path="])
for opt, a in optlist:
  if opt in ('-c', '--cluster'):
    cluster = a
  if opt in ('-h', '--help'):
    usage()
    sys.exit (0)
  if opt in ('-r', '--raw'):
    raw = True
  if opt in ('-o', '--output'):
    ofile = a
  if opt in ('-p', '--path'):
    search_path = a


user = raw_input ("User: ")
password = getpass.getpass ("Password: ")
oprint ("name,path,size", ofile, first)
first = False
while done == False:
  snap_list = get_snaps (cluster, user, password, resume)
  resume = snap_list['resume']
  if snap_list['resume'] is None:
    done = True
  for i, s in enumerate (snap_list['snapshots']):
    if search_path != "":
      pattern = re.compile (search_path)
      if re.match (pattern, snap_list['snapshots'][i]['path']) == None:
        continue
    size = byte_convert (snap_list['snapshots'][i]['size'], raw)
    output = snap_list['snapshots'][i]['name'] + "," + snap_list['snapshots'][i]['path'] + "," + str(size)
    oprint (output, ofile, first)
    total = total + snap_list['snapshots'][i]['size']
    total_s = byte_convert (total,raw)
total_p = "\nTotal:,," + str (total_s)
oprint (total_p, ofile, first)

