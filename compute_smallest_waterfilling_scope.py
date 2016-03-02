
import pathsim
import sys
import os
from stem import Flag
import network_modifiers

_testing = False

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(\
            description='command to compute min waterlevel')
    parser.add_argument('--adv_guard_cons_bw', type=float,\
            default=0)
    parser.add_argument('--adv_exit_cons_bw', type=float,\
            default=0)
    parser.add_argument('--num_adv_guards', type=int,\
            default=0)
    parser.add_argument('--num_adv_exits', type=int,\
            default=0)
    parser.add_argument('--adv_time', type=int,\
            default=0)
    parser.add_argument('--other_network_modifier', default=None)
    parser.add_argument('--in_dir')
    #directory = sys.argv[1] #N
    args = parser.parse_args()
    directory = args.in_dir

    network_state_files = []
    for dirpath, dirnames, fnames in os.walk(directory):
        for fname in fnames:
            if fname[0] != '.':
                network_state_files.append(os.path.join(\
                        dirpath, fname))

    network_state_files.sort(key = lambda x: os.path.basename(x))
    adv_insertion = network_modifiers.AdversaryInsertion(args, _testing)
    network_modifiers = [adv_insertion]
    # create other network modification object
    if (args.other_network_modifier is not None):
        # dynamically import module and obtain reference to class
        full_classname, class_arg = args.other_network_modifier.split('-')
        class_components = full_classname.split('.')
        modulename = '.'.join(class_components[0:-1])
        classname = class_components[-1]
        network_modifier_module = importlib.import_module(modulename)
        network_modifier_class = getattr(network_modifier_module, classname)
        # create object of class
        other_network_modifier = network_modifier_class(args, _testing)
        network_modifiers.append(other_network_modifier)

    # create iterator that applies network modifiers to nsf list
    network_states = pathsim.get_network_states(network_state_files,
            network_modifiers)

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


