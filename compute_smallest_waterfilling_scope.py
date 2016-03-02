
import pathsim
import sys
import os
from stem import Flag



if __name__ == "__main__":

    
    directory = sys.argv[1] #N
    network_state_files = []
    for dirpath, dirnames, fnames in os.walk(directory):
        for fname in fnames:
            if fname[0] != '.':
                network_state_files.append(os.path.join(\
                        dirpath, fname))

    network_state_files.sort(key = lambda x: os.path.basename(x))

    network_states = pathsim.get_network_states(network_state_files, [])
    min_cons_weight = 1000000
    max_cons_weight = 0
    average_cons_weight = 0
    flags = [Flag.RUNNING, Flag.VALID, Flag.GUARD]
    no_flags = [Flag.EXIT]
    for network_state in network_states:
        
        descriptors = network_state.descriptors
        cons_bwweightscale = network_state.cons_bwweightscale
        cons_bw_weights = network_state.cons_bw_weights
        weights = pathsim.detect_network_cases(cons_bwweightscale, cons_bw_weights)
        cons_rel_stats = network_state.cons_rel_stats
        (pivots, bwws_remaining) = pathsim.apply_water_filling(cons_rel_stats,\
                descriptors, weights, cons_bw_weights, cons_bwweightscale)
        
        nodes = pathsim.filter_flags(cons_rel_stats, descriptors, flags, no_flags)
        nodes.sort(key=lambda x: cons_rel_stats[x].bandwidth, reverse=True)
        pivot = pivots[0]
        
        if cons_rel_stats[nodes[pivot]].bandwidth < min_cons_weight:
            min_cons_weight = cons_rel_stats[nodes[pivot]].bandwidth
        if cons_rel_stats[nodes[pivot]].bandwidth > max_cons_weight:
            max_cons_weight = cons_rel_stats[nodes[pivot]].bandwidth
        average_cons_weight += cons_rel_stats[nodes[pivot]].bandwidth
    average_cons_weight = float(average_cons_weight)/len(network_state_files)
    print min_cons_weight, average_cons_weight, max_cons_weight


