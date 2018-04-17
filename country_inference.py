import sys
import os
from pathsim import *
import csv
import urllib
import gzip

def ip_in_country(ip, subnets):
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
    usage = 'Usage: as_inference.py [country code] [logs_in_dir] [results_out_dir] \n\
            Extracts the guard/exit IPs contained in [logs_in_dir] belonging to the country [country code], and writes them in\
            [results_out_dir/[country code]_guards] (guard IPs) and [results_out_dir/[country code]_exits] (exit IPs)'

    if (len(sys.argv) < 4):
        print(usage)
        sys.exit(1)

    searched_country_code = sys.argv[1]
    in_dir = sys.argv[2]
    out_dir = sys.argv[3]
    log_files = []
    for dirpath, dirnames, filenames in os.walk(in_dir, followlinks=True):
        for filename in filenames:
            if (filename[0] != '.'):
                log_files.append(os.path.join(dirpath,filename))
    log_files.sort(key = lambda x: os.path.basename(x))

    # Prepare the country subnets in DictReader
    subnets_country_file = urllib.URLopener()
    subnets_country_file.retrieve("https://iptoasn.com/data/ip2country-v4.tsv.gz", "ip2country-v4.tsv.gz")
    subnets = []
    with gzip.open('ip2country-v4.tsv.gz', 'rb') as csvfile:
        countryreader = csv.DictReader(csvfile, ['range_start', 'range_end', 'country_code'], dialect='excel-tab')
        for row in countryreader:
            if row['country_code'] == searched_country_code:
                subnets.append(row['range_start']+','+row['range_end'])

    # Add guards and exits belonging to the searched country for the guards/exits IP contained in log_files
    country_guards = []
    country_exits = []
    i = 0
    for log_file in log_files:
        with open(log_file, 'r') as lf:
            lf.readline() # read header line
            for line in lf:
                line = line[0:-1] # cut off final newline
                line_fields = line.split('\t')
                id = int(line_fields[0])
                time = float(line_fields[1])
                guard_ip = line_fields[2]
                exit_ip = line_fields[3]

                if guard_ip not in country_guards:
                    if ip_in_country(guard_ip, subnets):
                        country_guards.append(guard_ip)
                if exit_ip not in country_exits:
                    if ip_in_country(exit_ip, subnets):
                        country_exits.append(exit_ip)
        lf.close()
        i += 1

    guards_file = os.path.join(out_dir,searched_country_code+"_guards")
    exits_file = os.path.join(out_dir,searched_country_code+"_exits")
    with open(guards_file, 'w') as gf, open(exits_file, 'w') as ef:
        # Write all the Country IPs to the specified files
        for country_guard in country_guards:
            gf.write("%s\n" % country_guard)
        for country_exit in country_exits:
            ef.write("%s\n" % country_exit)
    gf.close()
    ef.close()
    csvfile.close()