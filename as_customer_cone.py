import sys
import os
from pathsim import *
import csv
import urllib
import json
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
    usage = 'Usage: as_customer_cone.py [AS number] [results_out_dir] \n\
            Exports in [results_out.dir]/[AS number]_customer_cone_prefixes all the prefixes in its customer cone \
            according to caida.org'

    if (len(sys.argv) < 2):
        print(usage)
        sys.exit(1)

    searched_as_number = sys.argv[1]
    out_dir = sys.argv[2]

    list_as = []
    customer_cone_as = []
    customer_cone_prefixes = []

    # Prepare the AS subnets in DictReader
    subnets_as_file = urllib.URLopener()
    subnets_as_file.retrieve("https://iptoasn.com/data/ip2asn-v4.tsv.gz", "ip2asn-v4.tsv.gz")

    with gzip.open('ip2asn-v4.tsv.gz', 'rb') as csvfile:
        asreader = csv.DictReader(csvfile, ['range_start', 'range_end', 'AS_number', 'country_code', 'AS_description'], dialect='excel-tab')
        for row in asreader:
            list_as.append(row)
    csvfile.close()

    def add_prefixes(searched_as_number):

        for row in list_as:
            if row['AS_number'] == searched_as_number:
                prefix_to_add = row['range_start']+','+row['range_end']
                if prefix_to_add not in customer_cone_prefixes:
                    customer_cone_prefixes.append(row['range_start']+','+row['range_end'])
                    print("prefix added")

        url = "http://as-rank.caida.org/api/v1/asns/"+str(searched_as_number)+"/links"
        response = urllib.urlopen(url)
        links = json.loads(response.read())
        i = 1
        for link in links["data"]:
            if link["relationship"] == "customer":
                customer_as = link["asn"]
                if customer_as not in customer_cone_as:
                    customer_cone_as.append(customer_as)
                    print("recursion - AS {}/32383".format(len(customer_cone_as)))
                    add_prefixes(str(customer_as))
            if searched_as_number == sys.argv[1]:
                print("{}/{}".format(i, len(links["data"])))
                i += 1

    add_prefixes(searched_as_number)

    customer_cone_file = os.path.join(out_dir,searched_as_number+"_customer_cone_prefixes")
    with open(customer_cone_file, 'w') as ccf:
        # Write all the prefixes to the specified file
        for prefix in customer_cone_prefixes:
            ccf.write("%s\n" % prefix)
    ccf.close()