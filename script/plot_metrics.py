"""
When plotting time series, e.g., financial time series, one often wants
to leave out days on which there is no data, eh weekends.  The example
below shows how to use an 'index formatter' to achieve the desired plot
"""
import matplotlib.pyplot as plt
import datetime
import sys
import os
import pdb


def parse_metric_file(metric_file):
  with open(metric_file, 'r') as mf:
    dates_metrics = {}
    for line in mf:
        strline = line.split(' ')
        consensus_date = strline[0].split('/')[0][0:19]
        metric = float(strline[1])
        dates_metrics[datetime.datetime.strptime(consensus_date, '%Y-%m-%d-%H-%M-%S')] = \
                metric
    r_value = dates_metrics.items()
    r_value.sort(key = lambda x: x[0])
    return r_value 


if __name__ == "__main__":
  
  #metrics = {'key_sh_guard':[], 'key_sh_guard_m':[], 'key_sh_exit': [],\
             #'key_deg_uni_guard':[], 'key_sh_exit_m':[], 'key_deg_uni_guard_m':[],\
             #'key_deg_uni_exit':[], 'key_deg_uni_circ':[], 'key_guessing':[],\
             #'key_deg_uni_exit_m': [], 'key_deg_uni_circ_m': [], 'key_guessing_m':[],\
             #'key_bandwidth':[], 'keyexchange':[], 'key_bandwidth_m': [], 'keyexchange_m':[]}
  metrics_dir = sys.argv[1]
  network_case_to_plot = sys.argv[2]
  out_pathname = sys.argv[3]
  if len(sys.argv) > 4:
      yliminG = sys.argv[4]
      ylimaxG = sys.argv[5]
      yliminD = sys.argv[6]
      ylimaxD = sys.argv[7]
      
  pathnames_guessing = {'tor-wf':'', 'tor':''}
  pathnames_uniformity = {'tor-wf':'', 'tor':''}
  for dirpath, pathalgos, fnames in os.walk(os.path.join(metrics_dir, network_case_to_plot)):
    for pathalgo in pathalgos:
      for dirpath3, dirnames2, entropyfiles in os.walk(os.path.join(metrics_dir, network_case_to_plot, pathalgo)):
        for fname in entropyfiles:
          if "guessing" in fname:
            pathnames_guessing[pathalgo] = os.path.join(dirpath3, fname)
          else:
            pathnames_uniformity[pathalgo] = os.path.join(dirpath3, fname)

  #with open(metrics_file, 'r') as mf:
    #key = None
    #for line in mf:
      #line = line[0:-1] #cut off final new line
      #if "key" in line:
	#key = line
      #elif key is not None:
        #metrics[key].append(line)
      #else: continue


      # parse metrics file in following order: shannon entropy
      # for Guard, exit. Degree of uniformity for Guard, Exit
      # Degree of uniformity of circuit selection
      # guessing entropy
      # bandwidth
      # number of key-exchange protocol run
 
  line_styles = ['-v', '-o', '-s', '-*']
  line_labels = ["Tor path selection - Guessing entropy", "Waterfilling path selection - Guessing entropy",\
          "Tor path selection - Degree of uniformity", "Waterfilling path selection - Degree of uniformity"]
  #little improvement: parsing file with metrics and dates accordingly
  #and not hard-coding them (yes, i'm lazy).
  #dates = [datetime.date(2013, 2, 15), datetime.date(2013, 4, 15),\
           #datetime.date(2013, 6, 15), datetime.date(2013, 8, 15),\
           #datetime.date(2013, 10, 15), datetime.date(2013, 12, 16),\
           #datetime.date(2014, 2, 15), datetime.date(2014, 4, 15),\
           #datetime.date(2014, 6, 15), datetime.date(2014, 8, 16),\
           #datetime.date(2014, 10, 16), datetime.date(2015, 1, 15)]  
  parsed_guessing_tor = parse_metric_file(pathnames_guessing['tor'])
  parsed_guessing_tor_wf = parse_metric_file(pathnames_guessing['tor-wf'])
  
  fig, ax1 = plt.subplots()
  h1 = ax1.plot([date_tor for (date_tor, _) in parsed_guessing_tor], [guessing_tor for\
          (_, guessing_tor) in parsed_guessing_tor], line_styles[0], label=line_labels[0], color='blue')
  h2 = ax1.plot([date_tor_wf for (date_tor_wf, _) in parsed_guessing_tor_wf], [guessing_tor_wf for\
          (_, guessing_tor_wf) in parsed_guessing_tor_wf], line_styles[1], label=line_labels[1], color='blue')
  ax1.set_ylabel('Guessing entropy')
  #now plot degree uniformity
  ax2 = ax1.twinx()
  parsed_degree_tor = parse_metric_file(pathnames_uniformity['tor'])
  parsed_degree_tor_wf = parse_metric_file(pathnames_uniformity['tor-wf'])
  h3 = ax2.plot([date_tor for (date_tor, _) in parsed_degree_tor], [degree_tor for (_, degree_tor)\
          in parsed_degree_tor], line_styles[2], label=line_labels[2], color='green')
  h4 = ax2.plot([date_tor_wf for (date_tor_wf, _) in parsed_degree_tor_wf], [degree_tor_wf for\
          (_, degree_tor_wf) in parsed_degree_tor_wf], line_styles[3], label=line_labels[3], color='green')
  ax2.set_ylabel('Degree of uniformity')

  handles, labels = ax1.get_legend_handles_labels()
  handles2, labels = ax2.get_legend_handles_labels()
  handles.extend(handles2)
  fig.autofmt_xdate()
  plt.legend(handles,(line_labels[0], line_labels[1], line_labels[2], line_labels[3]), loc='best')
  #plt.tight_layout()
# next we'll write a custom formatter
  plt.title("Anonymity metrics for network case load {0}".format(network_case_to_plot))
  plt.show()
  #plt.savefig(out_pathname)
