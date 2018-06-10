

# Obtain diversity score

## Setup
First, create the network states from archives obtained
from CollecTor with: [create_network_state.sh](diversity_script/create_network_state.sh)

## Compute score

Use the [pathsim_slim.py](pathsim_slim.py) file code to compute the diversity scores.

Example 1: compute the diversity scores with vanilla network with ABWRS
```
python pathsim_slim.py score --nsf_dir some_path/network-states/ tor
```

Example 2: compute the diversity scores with vanilla network with Waterfilling (with optimal weights)
```
python pathsim_slim.py score --nsf_dir some_path/network-states/ --wf_optimal tor-wf
```

Example 3: compute the diversity scores with modified network with DeNASA,
by adding 5 exits nodes located in the United States of 20000 of consensus each
```
nohup pypy pathsim_slim.py score --nsf_dir some_path/network-states/ --location US --num_custom_exits 5 --custom_exit_cons_bw 20000 tor-denasa
```

Example 4: compute the guessing entropy with vanilla network
```
python pathsim_slim.py guessing-entropy --nsf_dir some_path/network-states/ tor
```

## Results

The results are stored in the output directory specified with an argument with
the following format:

- "score_algorithm" if no node was added
- "score_added_location_algorithm" if node(s) was (were) added

The files are stored in a directory named (excepted for the guessing entropy results):

- "Adversaries-AS['AS_adversary']_['Country_adversary']_['Tier1AS_adversary']"

Each file contain a line that describe the informations/scores in that order:

[node(s) added position], [adversary], [number of nodes added], [consensus by node],
Number of paths compromised by AS adversary, Time to first compromise by AS adversary, Guessing entropy at AS-level,
Number of paths compromised by Country adversary, Time to first compromise by Country adversary, Guessing entropy at Country-level
Number of paths compromised by Tier-1 AS adversary, Time to first compromise by Tier-1 AS adversary, Guessing entropy at Tier-1 AS-level

