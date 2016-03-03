import sys
import os
import shutil
import pdb
def consensus_chosen(network_case, nbr_experiments, year_from,\
        year_to, month_from, month_to, path_to_networkcase_info):
    
    filenames = []
    pathnames = []
    for dirpath, dirnames, fnames in os.walk(path_to_networkcase_info):
        for fname in fnames:
            pathnames.append(os.path.join(dirpath, fname))
    pathnames.sort()
    #remove fname out date range
    start_range = False
    end_range = False
    new_pathnames = []
    for pathname in pathnames:
        if month_from < 10:
            if '{0}-0{1}'.format(year_from, month_from) in pathname or start_range and\
                    not end_range:
                start_range = True
                new_pathnames.append(pathname)
        else:
            if '{0}-{1}'.format(year_from, month_from) in pathname or start_range and\
                    not end_range:
                start_range = True
                new_pathnames.append(pathname)
        if month_to < 10:

            if '{0}-0{1}'.format(year_to, month_to) in pathname:
                end_range = True
        else:
            if '{0}-{1}'.format(year_to, month_to) in pathname:
                end_range = True
    pathnames = new_pathnames
    counter = 0
    for pathname in pathnames:
        f = open(pathname, "r")
        for line in f:
            if network_case in line:
                counter+=1
        f.close()
    if counter < nbr_experiments:
         step = 1
    else:
        step = int(counter/nbr_experiments)
    i = 0
    for pathname in pathnames:
        f = open(pathname, "r")
        for line in f:
            if network_case in line:
                if i == step:
                    filename = line.split(network_case)[1].split(' ')[1]
                    if len(filenames) < nbr_experiments:
                        filenames.append(filename)
                    i=0
                i+=1
        f.close()

    return filenames

if __name__ == "__main__":
    """setup directories in with appropriate
    cons files for experiments"""
    network_case = sys.argv[1]
    nbr_experiments_max = int(sys.argv[2])
    path_in = sys.argv[3]
    path_out = sys.argv[4]
    path_to_networkcase_info = sys.argv[5]
    year_from = int(sys.argv[6])
    year_to = int(sys.argv[7])
    month_from = int(sys.argv[8])
    month_to = int(sys.argv[9])
    
    root_path = ''.join([path_out,'/', network_case.replace(" ", ""), '/{0}.{1}-{2}.{3}/'.format(year_from,\
            month_from, year_to, month_to)])
    try:
        os.makedirs(root_path)
    except OSError:
        pass #ouuuu ugly
    filenames = consensus_chosen(network_case, nbr_experiments_max, year_from,\
            year_to, month_from, month_to, path_to_networkcase_info)
    pdb.set_trace()
    for filename in filenames:
        try:
            os.mkdir(''.join([root_path, filename]))
        except OSError:
            pass

        #then copy the consensus
        shutil.copyfile(''.join([path_in, '/', filename]), ''.join([root_path, filename, '/', filename]))



