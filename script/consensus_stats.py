import datetime
import stem
from stem.descriptor import parse_file, DocumentHandler
import sys
import os
import pdb
from stem import Flag


def find_min_max_median_consweight(in_consensuses_dir, flag,\
        no_flag):
    
    min_cons_weight =  50000000
    max_cons_weight = -1
    average_max_cons_weight = -1
    pdb.set_trace()
    for dirpath, dirnames, fnames in os.walk(in_consensuses_dir):
      for fname in fnames:
        cons_f = open(os.path.join(dirpath, fname), 'rb')
        consensus = next(parse_file(cons_f, validate=False, descriptor_type="network-status-consensus-3 1.0",\
           document_handler = DocumentHandler.DOCUMENT))
        for router in consensus.routers.values():
          if Flag.RUNNING and flag and\
                 not no_flag in router.flags:
            if min_cons_weight > router.bandwidth:
              min_cons_weight = router.bandwidth
            if max_cons_weight < router.bandwidth:
              max_cons_weight = router.bandwidth
        average_max_cons_weight += max_cons_weight
        cons_f.close()
      average_max_cons_weight = float(average_max_cons_weight)\
              /len(pathnames)
    return min_cons_weight, average_max_cons_weight, max_cons_weight



def find_min_max_median(log_file):

  with open(log_file, 'r') as lf:

    list_w = []
    min_w = 10000
    max_w = 0
    for line in lf:
      line = line[0:-1]
      tab = line.split(" ")
      if "2 b 1" in line:
        Wee = int(tab[4].split("=")[1][0:-1])
        list_w.append(Wee)
        if min_w > Wee:
          min_w = Wee
        if max_w < Wee:
          max_w = Wee
    pdb.set_trace()
    list_w.sort()
    median_w = list_w[len(list_w)/2]
  return (min_w, median_w, max_w)


def explore_consensus_files(in_consensuses_dir, out_dir):

  outname = out_dir
  i = 1
  day = 0
  for consensuses_dir in in_consensuses_dir:
    outname = out_dir
    outname += consensuses_dir[-19:]
    outname+="network_case"
    f_out = open(outname, "w")
    pathnames = []
    for dirpath, dirnames, fnames in os.walk(consensuses_dir):
      for fname in fnames:
        pathnames.append(os.path.join(dirpath, fname))
    pathnames.sort()
    for pathname in pathnames:
      filename = os.path.basename(pathname)
      if filename[0] == ".":
        continue
      if i%24 == 0:
        day+=1
        #print("day {0}".format(day))
      i+=1
      cons_f = open(pathname, 'rb')
      consensus = next(parse_file(cons_f, validate=True, descriptor_type="network-status-consensus-3 1.0",\
          document_handler = DocumentHandler.DOCUMENT))
      detect_network_case(consensus,  f_out)
      cons_f.close()
    f_out.close()

def detect_network_case(consensus, f_out):
  weightscale = 10000
  bw_weights = consensus.bandwidth_weights
  
  filename = consensus.valid_after.strftime(\
          '%Y-%m-%d-%H-%M-%S-network_state')

  for w in ('Wmg', 'Wgg', 'Wmd', 'Wed', 'Wgd', 'Wee', 'Wme'):
    if w not in bw_weights:
      return

  if bw_weights['Wmg'] == bw_weights['Wmd'] and bw_weights['Wed'] == weightscale/3:
    #case 1
    f_out.write("1 {0} Wgg={1}, Wee={2}\n".format(filename,\
            bw_weights['Wgg'], bw_weights['Wee']))
  elif bw_weights['Wmd']+bw_weights['Wmg']+bw_weights['Wme'] == 0:
    if bw_weights['Wed'] == weightscale:
      #case 2 subcase 1, E<G
      f_out.write("2 a E<G {0}\n".format(filename))
    else:
      #case 2 subcase 1, E>G
      f_out.write("2 a E>G {0}\n".format(filename))
  elif bw_weights['Wgg'] == weightscale and bw_weights['Wmd'] == bw_weights['Wgd']:
    #Case 2 subcase b
    Wee = bw_weights['Wee']
    Wed = bw_weights['Wed']
    Wgd = bw_weights['Wgd']
    Wmd = bw_weights['Wmd']
    f_out.write("2 b 1 {0} Wee={1}, Wed={2}, Wgd={3}, Wmd={4}\n".format(filename,\
             Wee, Wed, Wgd, Wmd))

  elif bw_weights['Wgg'] == weightscale and bw_weights['Wee'] == weightscale:
    #Case 2 subcase b with another constraints
    Wed = bw_weights['Wed']
    Wgd = bw_weights['Wgd']
    Wmd = bw_weights['Wmd']
    if bw_weights['Wmd'] == 0:
      #last subcase 2, b
      f_out.write("2 b 2 M > T/3 {0} Wed={1}, Wgd={2}, Wmd={3} \n".format(filename,\
              Wed, Wgd, Wmd))
    else:
      f_out.write("2 b 2 M < T/3 {0} Wed={1}, Wgd={2}, Wmd={3} \n".format(filename, Wed, Wgd,\
              Wmd))

  elif bw_weights['Wgd']+bw_weights['Wgg'] == 2*weightscale and bw_weights['Wmd']+\
          bw_weights['Wed']+bw_weights['Wmg'] == 0:
    #case 3 subcase a G =S
    if bw_weights['Wme'] == 0:
      #case 3 subcase a E < M
      f_out.write("3 a G=S E < M {0}\n".format(filename))
    else:
      Wee=bw_weights['Wee']
      f_out.write("3 a G=S E >= M {0} Wee={1}\n".format(filename, Wee))
      #case 3 subcase a E >= M
  elif bw_weights['Wee'] + bw_weights['Wed'] == 2*weightscale and\
      bw_weights['Wmd'] + bw_weights['Wgd'] + bw_weights['Wme'] == 0:
    #Case 3 subcase a E = S
    if bw_weights['Wmg'] == 0:
      #Case 3 subcase a E = S and G < M
      f_out.write("3 a E=S G < M {0}\n".format(filename))
    else:
      Wgg = bw_weights['Wgg']
      f_out.write("3 a E=S G > M {0} Wgg={1}\n".format(filename, Wgg))
      #Case 3 subcase a E = S and G > M
  elif bw_weights['Wgg'] == weightscale and bw_weights['Wmd'] == bw_weights['Wed']:
    #Case 3 subcase b G = S
    Wee = bw_weights['Wee']
    Wgd = bw_weights['Wgd']
    Wmd = bw_weights['Wmd']
    Wed = bw_weights['Wed']
    f_out.write("3 b G=S {0} Wee={1}, Wgd={2}, Wmd={3}, Wed={4}\n".format(filename, Wee, Wgd,\
            Wmd, Wed))
  elif bw_weights['Wee'] == weightscale and bw_weights['Wmd'] == bw_weights['Wgd']:
    #Case 3 subcase b  E=S
    Wgg = bw_weights['Wgg']
    Wgd = bw_weights['Wgd']
    Wmd = bw_weights['Wmd']
    Wed = bw_weights['Wed']
    f_out.write("3 b E=S {0} Wgg={1}, Wgd={2}, Wmd={3}, Wed={4}\n".format(filename, Wgg, Wgd,\
            Wmd, Wed))
  else:
    print("No cases found\n")
    pdb.set_trace()

  
if __name__ == "__main__":
  
  cmd = sys.argv[1]

  if cmd == "explore" or cmd == "consweight":
    start_year = int(sys.argv[2])
    start_month = int(sys.argv[3])
    end_year = int(sys.argv[4])
    end_month = int(sys.argv[5])
    in_dir = sys.argv[6]
    in_dirs = []
    month = start_month
    for year in range(start_year, end_year+1):
      while ((year < end_year) and (month <= 12)) or \
          (month <= end_month):
          if (month <= 9):
              prepend = '0'
          else:
              prepend = ''
          cons_dir = os.path.join(in_dir, 'consensuses-{0}-{1}{2}'.\
              format(year, prepend, month))
          in_dirs.append(cons_dir)
          month += 1
      month = 1
    if cmd == "explore":
      out_dir = sys.argv[7]
      explore_consensus_files(in_dirs, out_dir)
    elif cmd == "consweight":
      flag = sys.argv[7]
      no_flag = sys.argv[8]
      if flag == "guard": flag = Flag.GUARD
      elif flag == "exit": flag = Flag.EXIT
      if no_flag == "guard": no_flag = Flag.GUARD
      elif no_flag == "exit": no_flag = Flag.EXIT
      print find_min_max_median_consweight(in_dirs, flag, no_flag)
  elif cmd == "analyze":
    log_file = sys.argv[2]
    print find_min_max_median(log_file)
