import sys
import os
from pathsim import *
import csv
import urllib
import gzip

def ip_in_as(ip, subnets):
    """
    Returns True if {ip} is in the range of one of the {subnets},
    Returns False otherwise.
    """
    ipv4 = [int(n) for n in ip.split('.')]
    for subnets_ranges in subnets:
        range_start_full, range_end_full = subnets_ranges.split(',')
        range_start = [int(n) for n in range_start_full.split('.')]
        range_end = [int(n) for n in range_end_full.split('.')]
        if ipv4[0] == range_start[0] and ipv4[0] == range_end[0]:
            if ipv4[1] == range_start[1] and ipv4[1] == range_end[1]:
                if ipv4[2] == range_start[2] and ipv4[2] == range_end[2]:
                    if range_start[3] <= ipv4[3] <= range_end[3]:
                        return True
                elif range_start[2] <= ipv4[2] <= range_end[2]:
                    if ipv4[2] == range_start[2]:
                        if ipv4[3] >= range_start[3]:
                            return True
                    elif ipv4[2] == range_end[2]:
                        if ipv4[3] <= range_end[3]:
                            return True
                    else:
                        return True
            elif range_start[1] <= ipv4[1] <= range_end[1]:
                if ipv4[1] == range_start[1]:
                    if ipv4[2] == range_start[2]:
                        if ipv4[3] >= range_start[3]:
                            return True
                    elif ipv4[2] >= range_start[2]:
                        return True
                elif ipv4[1] == range_end[1]:
                    if ipv4[2] == range_end[2]:
                        if ipv4[3] <= range_end[3]:
                            return True
                    elif ipv4[2] <= range_end[2]:
                        return True
                else:
                    return True
        elif range_start[0] <= ipv4[0] <= range_end[0]:
            if ipv4[0] == range_start[0]:
                if ipv4[1] == range_start[1]:
                    if ipv4[2] == range_start[2]:
                        if ipv4[3] >= range_start[3]:
                            return True
                    elif ipv4[2] >= range_start[2]:
                        return True
                elif ipv4[1] >= range_start[1]:
                    return True
            elif ipv4[0] == range_end[0]:
                if ipv4[1] == range_end[0]:
                    if ipv4[2] == range_end[2]:
                        if ipv4[3] <= range_end[3]:
                            return True
                    elif ipv4[2] <= range_end[2]:
                        return True
                elif ipv4[1] <= range_end[1]:
                    return True
            else:
                return True
    return False

if __name__ == '__main__':
    usage = 'Usage: as_inference.py [AS number] [logs_in_dir] [top_guards_file] [top_exits_file]\n\
            Extracts the guard/exit IPs contained in [logs_in_dir] belonging to AS[AS number], and writes them in \
            [top_guards_file] (guard IPs) and [top_exits_file] (exit IPs)'

    if (len(sys.argv) < 4):
        print(usage)
        sys.exit(1)

    searched_as_number = sys.argv[1]
    in_dir = sys.argv[2]
    guards_file = sys.argv[3]
    exits_file = sys.argv[4]
    log_files = []
    for dirpath, dirnames, filenames in os.walk(in_dir, followlinks=True):
        for filename in filenames:
            if (filename[0] != '.'):
                log_files.append(os.path.join(dirpath,filename))
    log_files.sort(key = lambda x: os.path.basename(x))

    # Prepare the AS subnets in DictReader
    subnets_as_file = urllib.URLopener()
    subnets_as_file.retrieve("https://iptoasn.com/data/ip2asn-v4.tsv.gz", "ip2asn-v4.tsv.gz")
    subnets = []
    with gzip.open('ip2asn-v4.tsv.gz', 'rb') as csvfile:
        asreader = csv.DictReader(csvfile, ['range_start', 'range_end', 'AS_number', 'country_code', 'AS_description'], dialect='excel-tab')
        for row in asreader:
            if row['AS_number'] == searched_as_number:
                subnets.append(row['range_start']+','+row['range_end'])

    # Add guards and exits belonging to the searched AS for the guards/exits IP contained in log_files
    as_guards = []
    as_exits = []
    i = 0
    for log_file in log_files:
        print('Processing log file '+i+'/'+len(log_files))
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
                    if ip_in_as(guard_ip, subnets):
                        as_guards.append(guard_ip)
                if exit_ip not in as_exits:
                    if ip_in_as(exit_ip, subnets):
                        as_exits.append(exit_ip)
        lf.close()
        print('log file '+i+'/'+len(log_files)+' processed.')
        i += 1


    with open(guards_file, 'w') as gf, open(exits_file, 'w') as ef:
        # Write all the AS IPs to the specified files
        for as_guard in as_guards:
            gf.write("%s\n" % as_guard)
        for as_exit in as_exits:
            ef.write("%s\n" % as_exit)
    gf.close()
    ef.close()
    csvfile.close()