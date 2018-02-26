import sys
import os
from pathsim import *
import math



def consensusname(log_file):
  return log_file.split('.')[1]

def build_prob_matrix(log_file):

  prob_matrix = {}
  exits = {}
  guards = {}
  counter_line = 0.0
  from collections import defaultdict
  previous_node = defaultdict(dict)
  with open(log_file, 'r') as lf:
    lf.readline() #skip header
    for line in lf:
      line = line[0:-1]
      line_fields = line.split('\t')
      sample = int(line_fields[0])
      guard_ip = line_fields[2]
      exit_ip = line_fields[4]
      if guard_ip not in guards :
        guards[guard_ip] = 0
      if exit_ip not in exits:
        exits[exit_ip] = 0

      if guard_ip not in prob_matrix:
        prob_matrix[guard_ip] = {}
        prob_matrix[guard_ip][exit_ip] = 1
      elif exit_ip not in prob_matrix[guard_ip]:
        prob_matrix[guard_ip][exit_ip] = 1
      else:
        prob_matrix[guard_ip][exit_ip] += 1
      exits[exit_ip] += 1
      guards[guard_ip]+= 1

      counter_line +=1.0
      #if int(counter_line) % 100000 == 0:
      #print counter_line


  return (counter_line, prob_matrix, guards, exits)


def guessing_entropy(log_file):

  (counter_lines, prob_matrix, guards, exits) = build_prob_matrix(log_file)

  all_nodes = len(guards)
  for exit in exits:
    if exit not in guards:
      all_nodes+=1
  prob_list = []
  guards_marg_probs = {}
  exits_marg_probs = {}
  #for guard, exit_dic in prob_matrix.items():
  # guards_marg_probs[guard] = sum(exit_dic.values())/counter_line
  #for guard2, exit_dic2 in prob_matrix.items():
  # for exit in exit_dic.keys():
  #	if exit in exit_dic2:
  #	  if exit not in exits_marg_probs:
  #	    exits_marg_probs[exit] = prob_matrix[guard2][exit]/counter_line
  #	  else:
  #	    exits_marg_probs[exit] += prob_matrix[guard2][exit]/counter_line
  i = 2

  #pdb.set_trace()
  (maximum, guard_ip, exit_ip) = get_max(prob_matrix)
  prob_list.append(0)
  prob_list.append(maximum/counter_lines)
  guards_controlled = {}
  exits_controlled = {}
  guards_controlled[guard_ip] = guard_ip
  exits_controlled[exit_ip] = exit_ip
  if guard_ip in exits :
    exits_controlled[guard_ip] = guard_ip
  if exit_ip in guards:
    guards_controlled[exit_ip] = exit_ip
  #pdb.set_trace()
  #print "second step"

  counter_both = 0
  counter_guards = 0
  counter_exits = 0
  while i < all_nodes:
    (node_ip, maximum) = get_max_marg_prob(prob_matrix, guards_controlled, \
                                           exits_controlled)
    #print "{0}/{1} done".format(i, all_nodes)

    prob_list.append(maximum/counter_lines)
    if node_ip in guards and node_ip in exits:
      counter_both += 1
    elif node_ip in exits:
      counter_exits += 1
    elif node_ip in guards:
      counter_guards +=1
    i+=1

  guessing_entropy = 0
  i = 1
  #pdb.set_trace()
  #prob_list.sort(reverse=True)
  while i < all_nodes:
    guessing_entropy += (i)*prob_list[i-1]
    i+=1

  #print "number of nodes compromised only flagged guards {0}".format(counter_guards)
  #print "number of nodes compromised only flagged exits {0}".format(counter_exits)
  #print "number of nodes compromised flagged both  {0}".format(counter_both)
  return guessing_entropy

def get_max_marg_prob(prob_matrix, guards, exits):
  max_guard = 0
  max_exit = 0
  max_both = 0
  guard_node = ""
  exit_node = ""
  exit_seen = {}
  node_both = ""
  for guard in prob_matrix:
    acc = 0
    if guard not in guards:
      for exit in exits:
        if exit in prob_matrix[guard]:
          acc += prob_matrix[guard][exit]
      if acc > max_guard:
        max_guard = acc
        guard_node = guard
    for exit, nbr_seen in prob_matrix[guard].items():
      #pdb.set_trace()
      if exit not in exit_seen and exit not in exits:
        exit_seen[exit] = exit;
        acc = 0
        for guard2 in guards:
          if exit in prob_matrix[guard2]:
            acc+= prob_matrix[guard2][exit]
        if acc > max_exit:
          max_exit = acc
          exit_node = exit

          #for guard in prob_matrix:

    exit = guard
    for guard2 in prob_matrix:
      #verify that the guard-exit is not already taken
      if exit in prob_matrix[guard2] and guard2 not in guards and exit \
              not in exits:
        acc_guard = 0
        acc_exit = 0
        for exit2 in exits:
          #horizontal line
          if exit2 in prob_matrix[guard]:
            acc_guard += prob_matrix[guard][exit2]
        for guard2 in guards:
          #vertical line
          if exit in prob_matrix[guard2]:
            acc_exit+= prob_matrix[guard2][exit]
        acc = acc_guard + acc_exit
        if acc > max_both:
          node_both = guard
          max_both = acc

  #pdb.set_trace()
  if max(max_both, max(max_exit, max_guard)) == max_both:
    guards[node_both] = node_both
    exits[node_both] = node_both

    return (node_both, max_both)
  elif max(max_both, max(max_exit, max_guard)) == max_exit:
    exits[exit_node] = exit_node
    return (exit_node, max_exit)
  else:
    guards[guard_node] = guard_node
    return (guard_node, max_guard)




def get_max(prob_matrix):
  """ prob_matrix is a dict of dict
      return the maximum value inside the matrix
  """
  maxi = 0
  max_guard = ""
  max_exit = ""
  for (guard, exits_dic) in prob_matrix.items():
    new_maxi = max(maxi, max(exits_dic.values()))
    if new_maxi > maxi:
      maxi = new_maxi
      max_guard = guard
      max_exit = max(exits_dic, key=exits_dic.get)

  return (maxi, max_guard, max_exit)


def degree_uniformity_in_circuit(log_file):

  guard_dic = {}
  exit_dic = {}
  guard_exit_dic = {}
  counter_line = 0
  #mean_guard_set_size = 0
  #mean_exit_set_size = 0
  from collections import defaultdict
  previous_node  = defaultdict(dict)
  count_guard = 0
  count_exit = 0
  count_both = 0
  with open(log_file, 'r') as lf:
    lf.readline()

    for line in lf:
      line = line[0:-1]
      line_fields = line.split('\t')
      sample = line_fields[0]

      guard_ip = line_fields[2]
      exit_ip = line_fields[4]
      #mean_guard_set_size += int(line_fields[3])
      #if is_mptcp:
      #  mean_exit_set_size += int(line_fields[6])
      #else:
      #  mean_exit_set_size += int(line_fields[5])
      if guard_ip not in guard_dic :
        guard_dic[guard_ip] = {'seen':1}
        count_guard+=1
      else:
        guard_dic[guard_ip]['seen']+=1

      if exit_ip not in exit_dic:
        exit_dic[exit_ip] = {'seen':1}
      else:
        exit_dic[exit_ip]['seen'] +=1

      if guard_ip+exit_ip not in guard_exit_dic:
        guard_exit_dic[guard_ip+exit_ip] = {'seen':1}
      else:
        guard_exit_dic[guard_ip+exit_ip]['seen'] +=1

      counter_line+=1
  #size_set_guards = len(guard_dic)
  #size_set_exits = len(exit_dic)
  #mean_guard_set_size = float(mean_guard_set_size)/float(counter_line)
  #mean_exit_set_size = float(mean_exit_set_size)/float(counter_line)
  count_guard = counter_line
  count_exit = counter_line
  count_both = counter_line
  #for guard_ip in guard_dic:
  #guard_dic[guard_ip]['seen_prob'] =\
  #float(guard_dic[guard_ip]['seen'])/float(count_guard)
  #for exit_ip in exit_dic:
  #exit_dic[exit_ip]['seen_prob'] =\
  #float(exit_dic[exit_ip]['seen'])/float(count_exit)

  for guard_ip in guard_dic:
    for exit_ip in exit_dic:
      if guard_ip+exit_ip in guard_exit_dic:
        guard_exit_dic[guard_ip+exit_ip]['seen_prob'] = \
          float(guard_exit_dic[guard_ip+exit_ip]['seen'])/float(count_both)
      else:
        guard_exit_dic[guard_ip+exit_ip] = {'seen_prob':0.0}
  #guard_list = guard_dic.items()
  #exit_list = exit_dic.items()
  guard_exit_list = guard_exit_dic.items()
  #guard_list.sort(key = lambda x: x[1]['seen_prob'], reverse=True)
  #exit_list.sort(key = lambda x: x[1]['seen_prob'], reverse=True)
  guard_exit_list.sort(key = lambda x: x[1]['seen_prob'], reverse=True)
  #guard_effectif_set = compute_effective_set_anonymity(guard_list)
  #exit_effectif_set = compute_effective_set_anonymity(exit_list)
  guard_exit_effectif_set = compute_effective_set_anonymity(guard_exit_list)

  #print "degree of uniformity ..."


  return guard_exit_effectif_set/math.log(len(guard_dic)*len(exit_dic),2)



def compute_effective_set_anonymity(node_list):
  N = len(node_list)
  accu = 0.0
  for node in node_list:
    if node[1]['seen_prob'] > 0.0:
      accu += node[1]['seen_prob']*math.log(node[1]['seen_prob'], 2)
  return -accu

if __name__ == "__main__":

  usage = "" #todo

  if len(sys.argv) < 2 :
    print(usage)
    sys.exit(1)

  command = sys.argv[1]

  if command != 'guessing-entropy' and command != "degree-uniformity":
    print(usage)
  elif command == 'guessing-entropy':
    log_file = sys.argv[2]
    print "{0} {1}".format(consensusname(log_file), guessing_entropy(log_file))
  elif command == 'degree-uniformity':
    log_file = sys.argv[2]
    print "{0} {1}".format(consensusname(log_file), degree_uniformity_in_circuit(log_file))
