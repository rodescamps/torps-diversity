import sys
import os
import cPickle as pickle
from pathsim import *
import multiprocessing
import re
import requests
import urllib, json



if __name__ == '__main__':
    usage = 'Usage: as_inference.py [AS number] [logs_in_dir] [top_guards_file] [top_exits_file]\n\
            Extracts the guard/exit IPs contained in [logs_in_dir] belonging to AS[AS number], and writes them in \
            [top_guards_file] (guard IPs) and [top_exits_file] (exit IPs)'

    if (len(sys.argv) < 4):
        print(usage)
        sys.exit(1)

    as_number = sys.argv[1]
    in_dir = sys.argv[2]
    guards_file = sys.argv[3]
    exits_file = sys.argv[4]
    log_files = []
    for dirpath, dirnames, filenames in os.walk(in_dir, followlinks=True):
        for filename in filenames:
            if (filename[0] != '.'):
                log_files.append(os.path.join(dirpath,filename))
    log_files.sort(key = lambda x: os.path.basename(x))

    """
    top_guard_ips = read_compromised_relays_file(guards_in_file)
    top_exit_ips = read_compromised_relays_file(exits_in_file)

    args = (top_guard_ips, top_exit_ips, out_dir, out_name)
    simulation_analysis(log_files, compromised_top_relays_process_log, \
                        args)
    """
    as_guards = []
    as_exits = []
    for log_file in log_files:
        with open(log_file, 'r') as lf:
            lf.readline() # read header line
            for line in lf:
                line = line[0:-1] # cut off final newline
                line_fields = line.split('\t')
                id = int(line_fields[0])
                time = float(line_fields[1])
                guard_ip = line_fields[2]
                exit_ip = line_fields[4]

                if guard_ip not in as_guards:
                    """
                    autonomous_system = requests.get('http://ipinfo.io/'+guard_ip+'/org?token=18a079694c3e61').text
                    autonomous_system_number = autonomous_system.split()[0][2:]
                    """
                    url = 'https://api.iptoasn.com/v1/as/ip/'+guard_ip+'/'
                    print(url)
                    response = urllib.urlopen(url)
                    data = json.loads(response.read())
                    print(data)
                    autonomous_system_number = data['as_number']
                    if autonomous_system_number == as_number:
                        as_guards.add(guard_ip)
                if exit_ip not in as_exits:
                    """
                    autonomous_system = requests.get('http://ipinfo.io/'+exit_ip+'/org?token=18a079694c3e61').text
                    autonomous_system_number = autonomous_system.split()[0][2:]
                    """
                    url = 'https://api.iptoasn.com/v1/as/ip/'+exit_ip+'/'
                    response = urllib.urlopen(url)
                    data = json.loads(response.read())
                    autonomous_system_number = data['as_number']
                    if autonomous_system_number == as_number:
                        as_exits.add(exit_ip)
                print("Guards: "+as_guards)
                print("Exits: "+as_exits)


    with open(guards_file, 'w') as gf, open(exits_file, 'w') as ef:
        # Write all the AS IPs to the specified files
        for as_guard in as_guards:
            gf.write("%s\n" % as_guard)
        for as_exit in as_exits:
            ef.write("%s\n" % as_exit)