import stem.descriptor.reader as reader
import stem.descriptor
from stem import Flag
import os
import datetime
import sys
import bw_analysis
import pdb
import matplotlib.pyplot

def plot_count_guards(x, normal_count, without_wfu, with_stability, with_stability_and_unmeasured):

  
  matplotlib.pyplot.plot(x[len(with_stability)-len(normal_count):len(with_stability)],\
      normal_count, color="red", label="0.98 WFU and min 250 KBs")
  matplotlib.pyplot.plot(x[len(with_stability)-len(without_wfu):len(with_stability)],\
      without_wfu, label="no stability constrains", color="blue")
  matplotlib.pyplot.plot(x, with_stability, label="Flag Stable", color="black")
  matplotlib.pyplot.plot(x, with_stability_and_unmeasured, label="Flag Stable and nodes unmeasured", color="green")
  matplotlib.pyplot.legend()
  matplotlib.pyplot.xlabel("Bandwidth")
  matplotlib.pyplot.ylabel("Number of Guards")
  matplotlib.pyplot.show()

def count_guards(cons_rel_stats, bw_start, bw_end, bw_step, uptime):
  """ count the number of possible guards with different constraints """

  def count_normal_guards(cons_rel_stats, bw):
    c = 0
    for relay in cons_rel_stats:
      rel_stat = cons_rel_stats[relay]
      if Flag.GUARD in rel_stat.flags and rel_stat.bandwidth >= bw:
        c+=1
    return c
  def count_without_wfu(cons_rel_stats, bw):
    c = 0
    for relay in cons_rel_stats:
      rel_stat = cons_rel_stats[relay]
      if rel_stat.bandwidth >= bw:
        c+=1
    return c
  def count_with_stability(cons_rel_stats, bw):
    c = 0
    for relay in cons_rel_stats:
      rel_stat = cons_rel_stats[relay]
      if (rel_stat.bandwidth >= bw and Flag.STABLE in rel_stat.flags):
        c+=1
    return c

  def count_with_stability_and_unmeasured(cons_rel_stats,  bw):
    c = 0
    for relay in cons_rel_stats:
      rel_stat = cons_rel_stats[relay]
      if (rel_stat.bandwidth >= bw and Flag.STABLE in rel_stat.flags) or\
         (rel_stat.is_unmeasured and Flag.STABLE in rel_stat.flags and\
         descriptors[relay].adv_mean_bandwidth/1000.0 >= bw):
        c+=1
    return c
  normal_count, without_wfu, with_stability, with_stability_and_unmeasured = [], [], [], []
 
  for bw in range(bw_start, bw_end, bw_step):
    if bw >= 250:
      normal_count.append(count_normal_guards(cons_rel_stats, bw))
    with_stability.append(count_with_stability(cons_rel_stats, bw))
    without_wfu.append(count_without_wfu(cons_rel_stats, bw))
    with_stability_and_unmeasured.append(count_with_stability_and_unmeasured(cons_rel_stats, bw))
  
  x = range(bw_start, bw_end, bw_step)
  plot_count_guards(x, normal_count, without_wfu, with_stability, with_stability_and_unmeasured)
  
  #print("Possible Guards set length: {0}".format(len(possible_guards)))
  #print("Guards set length: {0}".format(len(guards)))
  #print("Possible guards - guards = {0}".format(len(possible_guards)-len(guards)))




if __name__ == "__main__":

  (cons_valid_after, cons_fresh_until, cons_bw_weights,\
    cons_bwweightscale, cons_rel_stats, hibernating_statuses,\
    descriptors) = bw_analysis.get_network_state(sys.argv[1])
  bw_start = int(sys.argv[2])
  bw_end  = int(sys.argv[3])
  bw_step = int(sys.argv[4])
  uptime = int(sys.argv[5])
  count_guards(cons_rel_stats, bw_start, bw_end, bw_step, uptime)

