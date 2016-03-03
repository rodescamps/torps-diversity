

Obtaining Figures on anonymity metrics
======================================

First, setup directories:

pypy setup_experiments.py "3 a E=S G > M" 20 ../out/ns-2015-01-2015-05
../out/simulate cons_network_case 2015 2015 1 5

ns-2015-01-2015-05 contains all network_consensus object created by
pathsim.py process command
f

cons_network_case contains files created by consensus_stat.py explore
command

Then, run script:

 ./run_simulations_waterfilling2.sh /home/frochet/Tor/torps_git-crypto/torps/ simple=6 tor-wf
   out/simulate/3aE\=SGM/2015.1-2015.5/
some variables might need to be modified inside the script, such as the
name of the network case. This script launches 20 simulations in paralell and output in 
/out/simulate/$PATH_ALG/$NETWORKCASE/ 

