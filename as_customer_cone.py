import sys
import os
from pathsim import *
import csv
import urllib
import json
import gzip

def is_included(range_start, range_end, reduced_customer_cone_prefixes):
    for reduced_customer_cone_prefix in reduced_customer_cone_prefixes:
        reduced_range_start_full, reduced_range_end_full = reduced_customer_cone_prefix.split(',')
        reduced_range_start = [int(n) for n in reduced_range_start_full.split('.')]
        reduced_range_end = [int(n) for n in reduced_range_end_full.split('.')]

        if range_start[0] > reduced_range_start[0] and range_end[0] < reduced_range_end[0]:
            return True
        elif range_start[0] == reduced_range_start[0] and range_end[0] == reduced_range_end[0]:
            if range_start[1] > reduced_range_start[1] and range_end[1] < reduced_range_end[1]:
                return True
            elif range_start[1] == reduced_range_start[1] and range_end[1] == reduced_range_end[1]:
                if range_start[2] > reduced_range_start[2] and range_end[2] < reduced_range_end[2]:
                    return True
                elif range_start[2] == reduced_range_start[2] and range_end[2] == reduced_range_end[2]:
                    if range_start[3] >= reduced_range_start[3] and range_end[3] <= reduced_range_end[3]:
                        return True
    return False

def extend(range_start, range_end, reduced_customer_cone_prefixes):

    for reduced_customer_cone_prefix in reduced_customer_cone_prefixes:
        reduced_range_start_full, reduced_range_end_full = reduced_customer_cone_prefix.split(',')
        reduced_range_start = [int(n) for n in reduced_range_start_full.split('.')]
        reduced_range_end = [int(n) for n in reduced_range_end_full.split('.')]

        # 3 cases: extend start and end, extend start, extend end

        # (1) We extend the start of range and end of range

        # Prepare subnet format in case it is added
        range_start_full = ""
        for n in range_start:
            range_start_full += str(n)
            range_start_full += "."
        range_start_full = range_start_full[:-1]
        range_end_full = ""
        for n in range_end:
            range_end_full += str(n)
            range_end_full += "."
        range_end_full = range_end_full[:-1]
        prefix_to_add = range_start_full + "," + range_end_full

        if range_start[0] < reduced_range_start[0] and range_end[0] > reduced_range_end[0]:
            reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)
        elif range_start[0] == reduced_range_start[0] and range_end[0] == reduced_range_end[0]:
            if range_start[1] < reduced_range_start[1] and range_end[1] > reduced_range_end[1]:
                reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)
            elif range_start[1] == reduced_range_start[1] and range_end[1] == reduced_range_end[1]:
                if range_start[2] < reduced_range_start[2] and range_end[2] > reduced_range_end[2]:
                    reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)
                elif range_start[2] == reduced_range_start[2] and range_end[2] == reduced_range_end[2]:
                    if range_start[3] < reduced_range_start[3] and range_end[3] > reduced_range_end[3]:
                        reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)

        # (2) We extend the start of range

        # Prepare subnet format in case it is added
        range_start_full = ""
        for n in range_start:
            range_start_full += str(n)
            range_start_full += "."
        range_start_full = range_start_full[:-1]
        prefix_to_add = range_start_full + "," + reduced_range_end_full

        if range_start[0] < reduced_range_start[0] <= range_end[0] <= reduced_range_end[0]:
            reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)
        elif range_start[0] == reduced_range_start[0] and range_end[0] == reduced_range_end[0]:
            if range_start[1] < reduced_range_start[1] <= range_end[1] <= reduced_range_end[1]:
                reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)
            elif range_start[1] == reduced_range_start[1] and range_end[1] == reduced_range_end[1]:
                if range_start[2] < reduced_range_start[2] <= range_end[2] <= reduced_range_end[2]:
                    reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)
                elif range_start[2] == reduced_range_start[2] and range_end[2] == reduced_range_end[2]:
                    if range_start[3] < reduced_range_start[3] <= range_end[3] <= reduced_range_end[3]:
                        reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)

        # (3) We extend the end of range

        # Prepare subnet format in case it is added
        range_end_full = ""
        for n in range_end:
            range_end_full += str(n)
            range_end_full += "."
        range_end_full = range_end_full[:-1]
        prefix_to_add = reduced_range_start_full + "," + range_end_full

        if reduced_range_start[0] <= range_start[0] <= reduced_range_end[0] < range_end[0]:
            reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)
        elif range_start[0] == reduced_range_start[0] and range_end[0] == reduced_range_end[0]:
            if reduced_range_start[1] <= range_start[1] <= reduced_range_end[1] < range_end[1]:
                reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)
            elif range_start[1] == reduced_range_start[1] and range_end[1] == reduced_range_end[1]:
                if reduced_range_start[2] <= range_start[2] <= reduced_range_end[2] < range_end[2]:
                    reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)
                elif range_start[2] == reduced_range_start[2] and range_end[2] == reduced_range_end[2]:
                    if reduced_range_start[3] <= range_start[3] <= reduced_range_end[3] < range_end[3]:
                        reduced_customer_cone_prefixes.remove(reduced_customer_cone_prefix)
    return False, reduced_customer_cone_prefixes

def reduce_prefixes(customer_cone_prefixes):

    reduced_customer_cone_prefixes = []

    i = 1
    for customer_cone_prefix in customer_cone_prefixes:
        range_start_full, range_end_full = customer_cone_prefix.split(',')
        range_start = [int(n) for n in range_start_full.split('.')]
        range_end = [int(n) for n in range_end_full.split('.')]

        # If we do not extend existing subnet range and we are not included in existing subnet range, add prefix
        is_extended, reduced_customer_cone_prefixes = extend(range_start, range_end, reduced_customer_cone_prefixes)
        if not is_included(range_start, range_end, reduced_customer_cone_prefixes):
            reduced_customer_cone_prefixes.append(customer_cone_prefix)
            #print("{} added".format(customer_cone_prefix))
            """

            range_start_full, range_end_full = customer_cone_prefix.split(',')
            range_start = [int(n) for n in range_start_full.split('.')]
            range_end = [int(n) for n in range_end_full.split('.')]

            is_extended, reduced_customer_cone_prefixes = extend(range_start, range_end, reduced_customer_cone_prefixes)
            if is_extended:
                reduced_customer_cone_prefixes.remove(prefix)
                j += 1
            """
            #print("{} discarded".format(customer_cone_prefix))
        #print(reduced_customer_cone_prefixes)
        if i % 1000 == 0:
            print("{}/{}".format(i, len(customer_cone_prefixes)))
        i += 1
        #if i == 1000: break

    return reduced_customer_cone_prefixes

def compute_customer_cone(searched_as_number, out_dir):
    list_as = []
    customer_cone_as = []
    customer_cone_prefixes = []

    # Prepare the AS subnets in DictReader
    if not os.path.isfile("ip2asn-v4.tsv.gz"):
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

        url = "http://as-rank.caida.org/api/v1/asns/"+str(searched_as_number)+"/links"
        print(url)
        response = urllib.urlopen(url)
        links = json.loads(response.read())
        i = 1
        for link in links["data"]:
            if link["relationship"] == "customer":
                customer_as = link["asn"]
                if customer_as not in customer_cone_as:
                    customer_cone_as.append(customer_as)
                    add_prefixes(str(customer_as))
            if searched_as_number == sys.argv[1]:
                print("{}/{}".format(i, len(links["data"])))
                i += 1

    add_prefixes(searched_as_number)

    # Following code optimizes subnets list by generating only unique range that do not overlap
    # Takes a long time, and the reduction is only a few percent for the biggest ASes
    """
    reduced_customer_cone_prefixes = reduce_prefixes(customer_cone_prefixes)
    """

    customer_cone_file = os.path.join(out_dir,searched_as_number+"_customer_cone_prefixes")
    with open(customer_cone_file, 'w') as ccf:
        # Write all the prefixes to the specified file
        for prefix in customer_cone_prefixes:
            ccf.write("%s\n" % prefix)
    ccf.close()

if __name__ == '__main__':
    usage = 'Usage: as_customer_cone.py [AS number] [results_out_dir] \n\
            Exports in [results_out.dir]/[AS number]_customer_cone_prefixes all the prefixes in its customer cone \
            according to caida.org'

    if (len(sys.argv) < 2):
        print(usage)
        sys.exit(1)

    searched_as_number = sys.argv[1]
    out_dir = sys.argv[2]

    compute_customer_cone(searched_as_number, out_dir)