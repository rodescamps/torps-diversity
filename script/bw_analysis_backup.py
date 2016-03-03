import pdb
import stem.descriptor.reader as reader
import stem.descriptor
from stem import Flag
import os
import cPickle as pickle
import datetime
from utils import RouterStatusEntry
from utils import NetworkStatusDocument
from utils import ServerDescriptor
import matplotlib
import math
import matplotlib.pyplot
import sys
""" 
Part of the code has been borrowed from the TorPS
(at least a big part of parse_decriptors() below and some utils function)

"""
router_max_age = 60*60*48

def  parse_descriptors(in_dirs):
  """Parse relay decriptors and extra-info relay descriptors """
  must_be_running = False #For bandwidth analysis, we need non-running relays
  slim = True
  descriptors = {}
  for in_consensuses_dir, in_descriptors, desc_out_dir in in_dirs:
    num_descriptors = 0
    num_relays = 0
    with reader.DescriptorReader(in_descriptors, validate=True) as r:
      for desc in r:
        if desc.fingerprint not in descriptors:
          descriptors[desc.fingerprint] = {}
        #keep all descriptors and take the most adequate after, for each fingerprint
        descriptors[desc.fingerprint][timestamp(desc.published)] = desc
    #Parsing consensus now

    pathnames = []
    for dirpath, dirnames, fnames in os.walk(in_consensuses_dir):
      for fname in fnames:
        pathnames.append(os.path.join(dirpath, fname))
    pathnames.sort()
    for pathname in pathnames:
      filename = os.path.basename(pathname)
      if filename[0] == ".":
        continue
      cons_f = open(pathname, 'rb')
      descriptors_out = {}
      hibernating_statuses = [] # (time, fprint, hibernating)
      cons_valid_after = None
      cons_valid_until = None
      cons_bw_weights = None
      cons_bwweightscale = None
      cons_fresh_until = None
      relays = {}
      num_not_found = 0
      num_found = 0
      for r_stat in stem.descriptor.parse_file(cons_f, validate=True):
        #skip non-running relays if flag is set
        if must_be_running and stem.Flag.RUNNING not in r_stat.flags:
          continue
        if cons_valid_after == None:
          cons_valid_after = r_stat.document.valid_after
          valid_after_ts = timestamp(cons_valid_after)
        if cons_fresh_until == None:
          cons_fresh_until = r_stat.document.fresh_until
          fresh_until_ts = timestamp(cons_fresh_until)
        if cons_bw_weights == None:
          cons_bw_weights = r_stat.document.bandwidth_weights
        if cons_bwweightscale == None and ('bwweightscale' in r_stat.document.params):
          cons_bwweightscale = r_stat.document.params['bwweightscale']
        relays[r_stat.fingerprint] = RouterStatusEntry(r_stat.fingerprint, r_stat.nickname,\
            r_stat.flags, r_stat.bandwidth, r_stat.is_unmeasured)

        #Now lets find more recent descritors and extra-infos with this consensus

        pub_time = timestamp(r_stat.published)
        desc_time = 0
        descs_while_fresh = []
        desc_time_fresh = None
                # get all descriptors with this fingerprint
        if (r_stat.fingerprint in descriptors):
          for t,d in descriptors[r_stat.fingerprint].items():
            # update most recent desc seen before cons pubtime
            # allow pubtime after valid_after but not fresh_until
            if (valid_after_ts-t < router_max_age) and\
                (t <= pub_time) and (t > desc_time) and\
                (t <= fresh_until_ts):
                  desc_time = t
                        # store fresh-period descs for hibernation tracking
            if (t >= valid_after_ts) and \
                (t <= fresh_until_ts):
                  descs_while_fresh.append((t,d))                                
                        # find most recent hibernating stat before fresh period
                        # prefer most-recent descriptor before fresh period
                        # but use oldest after valid_after if necessary
            if (desc_time_fresh == None):
              desc_time_fresh = t
            elif (desc_time_fresh < valid_after_ts):
              if (t > desc_time_fresh) and\
                  (t <= valid_after_ts):
                    desc_time_fresh = t
            else:
              if (t < desc_time_fresh):
                desc_time_fresh = t

                # output best descriptor if found
        if (desc_time != 0):
          num_found += 1
                    # store discovered recent descriptor
          desc = descriptors[r_stat.fingerprint][desc_time]
          if slim:
            descriptors_out[r_stat.fingerprint] = \
                ServerDescriptor(desc.fingerprint, \
                desc.hibernating, desc.nickname, \
                desc.family, desc.address, \
                desc.exit_policy, desc.average_bandwidth, desc.observed_bandwidth,\
                desc.uptime)
          else:
            descriptors_out[r_stat.fingerprint] = desc

          # store hibernating statuses
          if (desc_time_fresh == None):
            raise ValueError('Descriptor error for {0}:{1}.\n Found  descriptor before published date {2}: {3}\nDid not find descriptor for initial hibernation status for fresh period starting {4}.'.format(r_stat.nickname, r_stat.fingerprint, pub_time, desc_time, valid_after_ts))
          desc = descriptors[r_stat.fingerprint][desc_time_fresh]
          cur_hibernating = desc.hibernating
          # setting initial status
          hibernating_statuses.append((0, desc.fingerprint,\
            cur_hibernating))
          if (cur_hibernating):
            print('{0}:{1} was hibernating at consenses period start'.format(desc.nickname, desc.fingerprint))
          descs_while_fresh.sort(key = lambda x: x[0])
          for (t,d) in descs_while_fresh:
            if (d.hibernating != cur_hibernating):
              cur_hibernating = d.hibernating
              hibernating_statuses.append(\
                  (t, d.fingerprint, cur_hibernating))
              if (cur_hibernating):
                print('{0}:{1} started hibernating at {2}'\
                    .format(d.nickname, d.fingerprint, t))
              else:
                print('{0}:{1} stopped hibernating at {2}'\
                    .format(d.nickname, d.fingerprint, t))
        else:
          num_not_found += 1

    # output pickled consensus, recent descriptors, and
    # hibernating status changes
      if (cons_valid_after != None) and (cons_fresh_until != None):
        if slim:
          consensus = NetworkStatusDocument(\
            cons_valid_after, cons_fresh_until, cons_bw_weights,\
            cons_bwweightscale, relays)
        hibernating_statuses.sort(key = lambda x: x[0],\
            reverse=True)
        outpath = os.path.join(desc_out_dir,\
            cons_valid_after.strftime(\
            '%Y-%m-%d-%H-%M-%S-network_state'))
        f = open(outpath, 'wb')
        pickle.dump(consensus, f, pickle.HIGHEST_PROTOCOL)
        pickle.dump(descriptors_out,f,pickle.HIGHEST_PROTOCOL)
        pickle.dump(hibernating_statuses,f,pickle.HIGHEST_PROTOCOL)
        f.close()

        print('Wrote descriptors for {0} relays.'.\
          format(num_found))
        print('Did not find descriptors for {0} relays\n'.\
          format(num_not_found))
      else:
        print('Problem parsing {0}.'.format(filename))
    #num_consensuses += 1

      cons_f.close()

def update_list_from_consensus(bw_nodes_tot, bw_nodes):
  for node in bw_nodes:
    if node not in bw_nodes_tot:
      bw_nodes_tot[node] = [bw_nodes[node]]
    else:
     bw_nodes_tot[node].append(bw_nodes[node])


def analyse_bw(network_state_files, outpath):
  
  """ Collect observed bandwith data 24h past to a consensus file and adver-
      tised bandwidth of all nodes in the processed consensus
      
      Compute approximation of bandwidh used for each position of each nodes
      based on relay selection probabilities
      """
  adv_bw_nodes_tot, guard_fraction_bw_tot, middle_fraction_bw_tot, exit_fraction_bw_tot = {}, {}, {}, {}

  measured_bw_nodes_tot, measured_guard_fraction_bw_tot, measured_middle_fraction_bw_tot,\
      measured_exit_fraction_bw_tot = {}, {},{}, {}
  guard_weights_tot, middle_weights_tot, exit_weights_tot = {}, {}, {}
  obs_bw_nodes, obs_fraction_guard_bw, obs_fraction_middle_bw, obs_fraction_exit_bw = {}, {}, {}, {}
  i = 0
  for network_state_file in network_state_files:
    (cons_valid_after, cons_fresh_until, cons_bw_weights,\
        cons_bwweightscale, cons_rel_stats, hibernating_statuses,\
        descriptors) = get_network_state(network_state_file)

    adv_bw_nodes, guard_fraction_bw, middle_fraction_bw, exit_fraction_bw = {}, {}, {}, {}

    measured_bw_nodes, measured_guard_fraction_bw, measured_middle_fraction_bw, measured_exit_fraction_bw = {}, {},{}, {}

  # Compute weights and selection probability for each position
    guards = filter_guards(cons_rel_stats, descriptors)
    exits = filter_exits(cons_rel_stats, descriptors)

    guard_weights = get_position_weights(guards, cons_rel_stats, 'g',\
        cons_bw_weights, cons_bwweightscale)
    middle_weights = get_position_weights(cons_rel_stats.keys(), cons_rel_stats, 'm',\
        cons_bw_weights, cons_bwweightscale)
    #pdb.set_trace()
    exit_weights = get_position_weights(exits, cons_rel_stats, 'e',\
        cons_bw_weights, cons_bwweightscale)
    total_guard_weight = compute_total_weight(guards, guard_weights)
    total_middle_weight = compute_total_weight(cons_rel_stats, middle_weights)
    total_exit_weight = compute_total_weight(exits, exit_weights)
    guard_prob = compute_probability(guards, cons_rel_stats, guard_weights, total_guard_weight)
    middle_prob = compute_probability(cons_rel_stats.keys(), cons_rel_stats, middle_weights,\
        total_middle_weight)
    exit_prob = compute_probability(exits, cons_rel_stats, exit_weights, total_exit_weight)
    update_list_from_consensus(guard_weights_tot, guard_weights)
    update_list_from_consensus(middle_weights_tot, middle_weights)
    update_list_from_consensus(exit_weights_tot, exit_weights)
    #pdb.set_trace()
    #fraction of bandwidth for guard and exit position for each node, based on selection
    #probability
    guard_fraction, middle_fraction, exit_fraction = compute_weighted_bw_fraction(cons_rel_stats, guards, exits, guard_prob,\
       middle_prob, exit_prob)
    for relay in cons_rel_stats:
      measured_bw_nodes[relay] = (cons_rel_stats[relay].bandwidth,\
        cons_rel_stats[relay].is_unmeasured)
      measured_middle_fraction_bw[relay] = (middle_fraction[relay]*cons_rel_stats[relay].bandwidth,\
        cons_rel_stats[relay].is_unmeasured)
      if relay in descriptors:
        adv_bw_nodes[relay] = descriptors[relay].adv_mean_bandwidth
        middle_fraction_bw[relay] = middle_fraction[relay]*descriptors[relay].adv_mean_bandwidth
        if i == len(network_state_files):
          obs_fraction_middle_bw[relay] = descriptors[relay].observed_bandwidth *middle_fraction[relay]
          obs_bw_nodes[relay] = descriptors[relay].observed_bandwidth
      else:
        del adv_bw_nodes[relay]
        del measured_bw_nodes[relay]
        print("Relay %s not in descriptors".format(relay))
    update_list_from_consensus(measured_bw_nodes_tot, measured_bw_nodes)
    update_list_from_consensus(measured_middle_fraction_bw_tot, measured_middle_fraction_bw_tot)
    update_list_from_consensus(adv_bw_nodes_tot, adv_bw_nodes)
    update_list_from_consensus(middle_fraction_bw_tot, middle_fraction_bw)
    for relay in guards:
      measured_guard_fraction_bw[relay] = (guard_fraction[relay]*cons_rel_stats[relay].bandwidth,\
          cons_rel_stats[relay].is_unmeasured)
      if relay in descriptors:
        guard_fraction_bw[relay] = guard_fraction[relay]*descriptors[relay].adv_mean_bandwidth
        if i == len(network_state_files):
          obs_fraction_guard_bw[relay] = descriptors[relay].observed_bandwidth * guard_fraction[relay]
      else:
        del guard_fraction[relay]
        del measured_guard_fraction_bw[relay]
        print("Relay %s not in descriptors".format(relay))
    update_list_from_consensus(measured_guard_fraction_bw_tot, measured_guard_fraction_bw)
    update_list_from_consensus(guard_fraction_bw_tot, guard_fraction_bw)
    for relay in exits:
      measured_exit_fraction_bw[relay] = (exit_fraction[relay]*cons_rel_stats[relay].bandwidth,
          cons_rel_stats[relay].is_unmeasured)
      if relay in descriptors:
        exit_fraction_bw[relay] = exit_fraction[relay]*descriptors[relay].adv_mean_bandwidth
        if i == len(network_state_files):
          obs_fraction_exit_bw[relay] = descriptors[relay].observed_bandwidth * exit_fraction[relay]
      else:
        #relay not in descriptors but in consensus ?
        print("Relay %s not in descriptors".format(relay))
        del measured_exit_fraction_bw[relay]
        del exit_fraction_bw[relay]
    update_list_from_consensus(measured_exit_fraction_bw_tot, measured_exit_fraction_bw)
    i+=1
    #pdb.set_trace()
  #compute means
  def compute_means(node_bw, new_node_bw, is_a_measured_list):
    for node, list_bw in node_bw.items():
      if is_a_measured_list:
        bw_tot = 0
        tot_unmeasured = 0
        for (bw, is_unmeasured) in list_bw:
          if not is_unmeasured:
            bw_tot += bw
          tot_unmeasured += is_unmeasured
        if tot_unmeasured == 0:
          new_node_bw[node] = (float(bw_tot)/(float(len(list_bw))), list_bw[0][1])
        elif tot_unmeasured == len(list_bw):
          new_node_bw[node] = (list_bw[0][0], list_bw[0][1])
        else:
          # -1 means that the bandwidth of the node started to be measured
          # during the day. We just compute the average on measured values
          new_node_bw[node] = (float(bw_tot)/(float(len(list_bw)-tot_unmeasured)), -1)
      else:
        new_node_bw[node] = float(sum(list_bw))/float(len(list_bw))
  adv_bw_nodes, guard_fraction_bw, middle_fraction_bw, exit_fraction_bw = {}, {}, {}, {}
  measured_bw_nodes, measured_guard_fraction_bw, measured_middle_fraction_bw, measured_exit_fraction_bw = {}, {},{}, {}
  
  compute_means(adv_bw_nodes_tot, adv_bw_nodes, 0)
  compute_means(guard_fraction_bw_tot, guard_fraction_bw, 0)
  compute_means(middle_fraction_bw_tot, middle_fraction_bw, 0)
  compute_means(exit_fraction_bw_tot, exit_fraction_bw, 0)
  compute_means(measured_bw_nodes_tot, measured_bw_nodes, 1)
  compute_means(measured_guard_fraction_bw_tot, measured_guard_fraction_bw, 1)
  compute_means(measured_middle_fraction_bw_tot, measured_middle_fraction_bw, 1)
  compute_means(measured_exit_fraction_bw_tot, measured_exit_fraction_bw, 1)
  compute_means(guard_weights_tot, guard_weights, 0)
  compute_means(middle_weights_tot, middle_weights, 0)
  compute_means(exit_weights_tot, exit_weights, 0)
  pdb.set_trace()
  f = open(outpath, 'wb')
  pickle.dump(adv_bw_nodes, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(guard_fraction_bw, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(middle_fraction_bw, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(exit_fraction_bw, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(measured_bw_nodes, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(measured_guard_fraction_bw, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(measured_middle_fraction_bw, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(measured_exit_fraction_bw, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(obs_bw_nodes, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(obs_fraction_guard_bw, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(obs_fraction_middle_bw, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(obs_fraction_exit_bw, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(guard_weights, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(middle_weights, f, pickle.HIGHEST_PROTOCOL)
  pickle.dump(exit_weights, f, pickle.HIGHEST_PROTOCOL)
  f.close()



def set_guards_for_multipath():
  pass

def set_weights_for_multipath():
  pass

def plot_bw_comparaison(adv_bw, measured_bw, obs_bw, weights):
  
  #Sort nodes first
  #pdb.set_trace()
  measured_bw_list = measured_bw.items()
  measured_bw_list.sort(key=lambda x: x[1][0], reverse=True)
  y = [bw for (key, (bw, is_unmeasured)) in measured_bw_list]
  x = range(0, len(y))
  obs_bw_list = obs_bw.items()
  #sort obs_bw values according to sorted adv_bw_list 
  x2, y2 = [], []
  i=0
  for (relay, bw) in measured_bw_list:
    if relay in obs_bw:
      y2.append(obs_bw[relay]/1000.0)
      x2.append(i)
    i+=1
  y3 = [adv_bw[relay]/1000.0 for (relay, bw) in measured_bw_list]
  if len(weights) > 0:
    y4 = [weights[relay] for (relay, bw) in measured_bw_list]
  #pdb.set_trace()
  x_unmeasured = []
  y_unmeasured = []
  i = 0
  for (key, (bw, is_unmeasured)) in measured_bw_list:
    if is_unmeasured == 1:
      x_unmeasured.append(i)
      y_unmeasured.append(bw)
    i+=1
  #pdb.set_trace()
  matplotlib.pyplot.scatter(x2, y2, color="red", s=1)
  matplotlib.pyplot.scatter(x, y3, color="orange", s=1)
  matplotlib.pyplot.scatter(x, y, color="blue", s=1)
  if len(weights) > 0:
    matplotlib.pyplot.scatter(x, y4, color="brown", s=1)
  matplotlib.pyplot.scatter(x_unmeasured, y_unmeasured, color="green", s=10)
  matplotlib.pyplot.ylim(0,50000)
  matplotlib.pyplot.grid()
  matplotlib.pyplot.show()

def plot_bw(log_file):
  f = open(log_file)
  adv_bw_nodes = pickle.load(f)
  guard_fraction_bw = pickle.load(f)
  middle_fraction_bw = pickle.load(f)
  exit_fraction_bw = pickle.load(f)
  measured_bw_nodes = pickle.load(f)
  measured_guard_fraction_bw = pickle.load(f)
  measured_middle_fraction_bw = pickle.load(f)
  measured_exit_fraction_bw = pickle.load(f)
  obs_bw_nodes = pickle.load(f)
  obs_fraction_guard_bw = pickle.load(f)
  obs_fraction_middle_bw = pickle.load(f)
  obs_fraction_exit_bw = pickle.load(f)
  guard_weights = pickle.load(f)
  middle_weights = pickle.load(f)
  exit_weights = pickle.load(f)
  f.close()
  #pdb.set_trace()
  plot_bw_comparaison(adv_bw_nodes, measured_bw_nodes, obs_bw_nodes, {})
  plot_bw_comparaison(guard_fraction_bw, measured_guard_fraction_bw, obs_fraction_guard_bw, guard_weights)
  plot_bw_comparaison(middle_fraction_bw, measured_middle_fraction_bw, obs_fraction_middle_bw, middle_weights)
  plot_bw_comparaison(exit_fraction_bw, measured_exit_fraction_bw, obs_fraction_exit_bw, exit_weights)


##############################################"

# UTILS FUNCTION

##############################################

def compute_weighted_bw_fraction(cons_rel_stats, guards, exits, guard_prob, middle_prob,\
    exit_prob):
  guard_fraction = {}
  middle_fraction = {}
  exit_fraction = {}
  for relay in cons_rel_stats:
    if relay in guards:
      guard_fraction[relay] = guard_prob[relay]/(guard_prob[relay] + middle_prob[relay] +\
         exit_prob[relay])
    if relay in exits:
      if exit_prob[relay] > 0.0:
        exit_fraction[relay] = exit_prob[relay]/(exit_prob[relay]+guard_prob[relay]+\
            middle_prob[relay])
      else:
        exit_fraction[relay] = 0.0
    if middle_prob[relay] > 0.0:
      middle_fraction[relay] = middle_prob[relay]/(exit_prob[relay]+guard_prob[relay]+\
        middle_prob[relay])
    else:
      middle_fraction[relay] = 0.0


  return guard_fraction, middle_fraction, exit_fraction

def compute_probability(nodes, cons_rel_stats, weights, total_weight):
  prob = {}
  for node in cons_rel_stats:
    if node in nodes:
      prob[node] = weights[node]/total_weight
    else:
      prob[node] = 0.0
  return prob


def get_network_state(ns_file):

  with open(ns_file, 'r') as nsf:
    consensus = pickle.load(nsf)
    descriptors = pickle.load(nsf)
    hibernating_statuses = pickle.load(nsf)
  cons_valid_after = timestamp(consensus.valid_after)
  cons_fresh_until = timestamp(consensus.fresh_until)
  cons_bw_weights = consensus.bandwidth_weights
  if consensus.bwweightscale == None:
    cons_bwweightscale =  10000 #default value, torspec
  else:
    cons_bwweightscale = consensus.bwweightscale

  return (cons_valid_after, cons_fresh_until, cons_bw_weights,\
      cons_bwweightscale, consensus.relays, hibernating_statuses, descriptors)

def get_position_weights(nodes, cons_rel_stats, position, bw_weights,\
    bwweightscale):
    """Computes the consensus "bandwidth" weighted by position weights."""
    weights = {}
    for node in nodes:
        bw = float(cons_rel_stats[node].bandwidth)
        weight = float(get_bw_weight(cons_rel_stats[node].flags,\
            position,bw_weights)) / float(bwweightscale)
        weights[node] = bw * weight
    return weights

def get_bw_weight(flags, position, bw_weights):
    """Returns weight to apply to relay's bandwidth for given position.
        flags: list of Flag values for relay from a consensus
        position: position for which to find selection weight,
             one of 'g' for guard, 'm' for middle, and 'e' for exit
        bw_weights: bandwidth_weights from NetworkStatusDocumentV3 consensus
    """
    if (position == 'g'):
        if (Flag.GUARD in flags) and (Flag.EXIT in flags):
            return bw_weights['Wgd']
        elif (Flag.GUARD in flags):
            return bw_weights['Wgg']
        elif (Flag.EXIT not in flags):
            return bw_weights['Wgm']
        else:
            raise ValueError('Wge weight does not exist.')
    elif (position == 'm'):
        if (Flag.GUARD in flags) and (Flag.EXIT in flags):
            return bw_weights['Wmd']
        elif (Flag.GUARD in flags):
            return bw_weights['Wmg']
        elif (Flag.EXIT in flags):
            return bw_weights['Wme']
        else:
            return bw_weights['Wmm']
    elif (position == 'e'):
        if (Flag.GUARD in flags) and (Flag.EXIT in flags):
            return bw_weights['Wed']
        elif (Flag.GUARD in flags):
            return bw_weights['Weg']
        elif (Flag.EXIT in flags):
            return bw_weights['Wee']
        else:
            return bw_weights['Wem']
    else:
        raise ValueError('get_weight does not support position {0}.'.format(
            position))

def compute_total_weight(nodes, weight):
  total_weight = 0
  for node in nodes:
    total_weight += weight[node]
  return total_weight

def timestamp(t):
    """Returns UNIX timestamp"""
    td = t - datetime.datetime(1970, 1, 1)
    ts = td.days*24*60*60 + td.seconds
    return ts
def filter_guards(cons_rel_stats, descriptors):
  """Returns relays filtered by general (non-client-specific) guard criteria.
  In particular, omits checks for IP/family/subnet conflicts within list.
  """
  guards = []
  for fprint in cons_rel_stats:
      rel_stat = cons_rel_stats[fprint]
      if (Flag.RUNNING in rel_stat.flags) and\
          (Flag.VALID in rel_stat.flags) and\
          (Flag.GUARD in rel_stat.flags) and\
          (fprint in descriptors):
          guards.append(fprint)   
  return guards

def filter_exits(cons_rel_stats, descriptors):
  exits = []
  for fprint in cons_rel_stats:
    rel_stat = cons_rel_stats[fprint]
    if (Flag.RUNNING in rel_stat.flags) and\
        (Flag.VALID in rel_stat.flags) and\
        (Flag.EXIT in rel_stat.flags) and\
        (fprint in descriptors):
          exits.append(fprint)
  return exits
 

if __name__ == "__main__":

  if sys.argv[1] == "process":
    #Process just one month file
    in_dirs = [(sys.argv[2], sys.argv[3], sys.argv[4])]
    parse_descriptors(in_dirs)
  elif sys.argv[1] == "analyse_bw":
    #must be out/ns-yyyy-mm
    files_dir = sys.argv[2]
    year = sys.argv[2][7:11]
    month = sys.argv[2][12:14]
    day_ori = int(sys.argv[3])
    day = day_ori
    cons_nbr = int(sys.argv[4])
    ns_files = []
    for i in range(0, 25):
      nbr_cons = (cons_nbr + i) % 24
      if nbr_cons < 10:
        nbr_cons = "0{0}".format(nbr_cons)
      if cons_nbr + i > 23:
        day = day_ori+1
      if day < 10:
        day = "0{0}".format(day)
      ns_files.append("{0}/{1}-{2}-{3}-{4}-00-00-network_state".format(files_dir, year, month, day, nbr_cons))

    analyse_bw(ns_files, sys.argv[5])
  elif sys.argv[1] == "plot_bw":
    plot_bw(sys.argv[2])
else:
    raise ValueError("Command %s does not exist".format(sys.argv[1]))
