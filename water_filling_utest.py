import unittest
import pathsim
import pdb
import stem
from stem import Flag
import matplotlib.pyplot


class TestWaterFilling(unittest.TestCase):

    def setUp(self):
        ns_files = ["out/ns-2015-25-5-11cons/2015-05-25-10-00-00-network_state"]
        self.network_states = []
        self.list_relays = []
        self.descriptors = []
        self.cons_bw_weights = []
        self.pivots = []
        self.bwws_remaining = []
        for ns_file in ns_files:
            self.network_states.append(pathsim.get_network_state(ns_file))
        for network_state in self.network_states:
            cons_valid_after = network_state.cons_valid_after
            cons_fresh_until = network_state.cons_fresh_until
            cons_bw_weights = network_state.cons_bw_weights
            self.cons_bw_weights.append(cons_bw_weights)
            self.weightscale = []
            cons_bwweightscale = network_state.cons_bwweightscale
            self.weightscale.append(cons_bwweightscale)
            cons_rel_stats = network_state.cons_rel_stats
            hibernating_statuses = network_state.hibernating_statuses
            new_descriptors = network_state.descriptors
            self.descriptors.append(new_descriptors)
            #pdb.set_trace()
            weights = pathsim.detect_network_cases(cons_bwweightscale, cons_bw_weights)
            (pivots, bwws_remaining) = pathsim.apply_water_filling(cons_rel_stats,\
                    new_descriptors, weights, cons_bw_weights, cons_bwweightscale)
            #pdb.set_trace()
            self.pivots.append(pivots)
            self.bwws_remaining.append(bwws_remaining)
            self.list_relays.append(cons_rel_stats)

    def test_weight(self):
        for cons_rel_stats in self.list_relays:
            relays = cons_rel_stats.values()
            relays.sort(key=lambda x:x.bandwidth, reverse=True)
            i = 0
            for w in ("Wgg", "Wee", "Wed", "Wgd", "Wmd"):
                if w in relays[0].wf_bw_weights:
                    i+=1
            #pdb.set_trace()
            self.assertGreaterEqual(i, 0)

    def test_constraint_equality(self):
        i = -1
        for w in ("Wgg", "Wd", "Wee"):
            j = -1
            i+=1
            for cons_rel_stats in self.list_relays:
                j+=1
                if w == "Wgg":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.GUARD]
                    no_flags = [Flag.EXIT]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[j], flags,\
                            no_flags)
                    if "Wgg" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        i-=1
                        continue
                elif w == "Wee":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.EXIT]
                    no_flags = [Flag.GUARD]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[j], flags,\
                            no_flags)
                    if "Wee" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        i-=1
                        continue
                elif w == "Wd":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.EXIT, Flag.GUARD]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[j], flags,\
                            [])
                    if "Wed" not in cons_rel_stats[relays_f[0]].wf_bw_weights and\
                       "Wgd" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        i-=1
                        continue
                else:
                    raise ValueError("Weight not recognized {0}".format(w))

                relays_f.sort(key=lambda x: cons_rel_stats[x].bandwidth, reverse=True)
                if w == "Wd":
                    previous_weight = (cons_rel_stats[relays_f[0]].wf_bw_weights["Wed"]+\
                            cons_rel_stats[relays_f[0]].wf_bw_weights["Wgd"],\
                            cons_rel_stats[relays_f[0]].bandwidth)
                else:

                    previous_weight = (cons_rel_stats[relays_f[0]].wf_bw_weights[w],\
                        cons_rel_stats[relays_f[0]].bandwidth)
                pivot = 0
                for relay in relays_f:
                    relay = cons_rel_stats[relay]
                    if w == "Wd":
                        e1 = (float(relay.bandwidth)*(relay.wf_bw_weights["Wed"]+\
                                relay.wf_bw_weights["Wgd"]))
                    else:
                        e1 = (float(relay.bandwidth)*relay.wf_bw_weights[w])
                    e2 = (float(previous_weight[1])*previous_weight[0])
                    if approx_equal(e1, e2):
                        pivot += 1
                        if w == "Wd":
                            previous_weight = (relay.wf_bw_weights["Wed"]+\
                                    relay.wf_bw_weights["Wgd"], relay.bandwidth)
                        else:
                            previous_weight = (relay.wf_bw_weights[w], relay.bandwidth)
                    else:
                        #pdb.set_trace()
                        self.assertGreaterEqual(pivot, self.pivots[j][i])
                        break
            

    def test_constraint_bound(self):
        i = 0
        for cons_rel_stats in self.list_relays:
            for w in ("Wgg", "Wee", "Wd"):
                relays = cons_rel_stats.values()
                if w == "Wd":
                    if "Wed" not in relays[0].wf_bw_weights and "Wgd" not in\
                            relays[0].wf_bw_weights:
                        continue
                for relay in relays:
                    if w not in relay.wf_bw_weights and w != "Wd":
                        continue
                    if w == "Wd":
                        weight = relay.wf_bw_weights["Wed"] + relay.wf_bw_weights["Wgd"]
                    else:
                        weight = relay.wf_bw_weights[w]
                    self.assertGreaterEqual(weight, 0)
                    self.assertLessEqual(weight, self.weightscale[i])
            i+=1
    def test_constraint_unity(self):
        i = 0
        for cons_rel_stats in self.list_relays:
            j = -1
            for w in ("Wgg", "Wd", "Wee"):
                j+=1
                if w == "Wgg":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.GUARD]
                    no_flags = [Flag.EXIT]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[i], flags,\
                            no_flags)
                    if "Wgg" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        j-=1
                        continue
                elif w == "Wee":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.EXIT]
                    no_flags = [Flag.GUARD]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[i], flags,\
                            no_flags)
                    if "Wee" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        j-=1
                        continue
                elif w == "Wd":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.EXIT, Flag.GUARD]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[i], flags,\
                            [])
                    if "Wed" not in cons_rel_stats[relays_f[0]].wf_bw_weights and\
                       "Wgd" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        j-=1
                        continue
                else:
                    raise ValueError("Weight not recognized {0}".format(w))
                k=0
                relays_f.sort(key=lambda x: cons_rel_stats[x].bandwidth, reverse=True)
                for relay in relays_f[self.pivots[i][j]+1:-1]:
                    if w not in cons_rel_stats[relay].wf_bw_weights and w != "Wd":
                        continue
                    if w == "Wd":
                        weight = cons_rel_stats[relay].wf_bw_weights["Wed"] +\
                                cons_rel_stats[relay].wf_bw_weights["Wgd"]
                    else:
                        weight = cons_rel_stats[relay].wf_bw_weights[w]

                    self.assertTrue(approx_equal(weight, self.weightscale[i]))
            i+=1
    
    def test_constraint_sum_bwweight(self):
        j=0
        for cons_rel_stats in self.list_relays:
            relays = cons_rel_stats.values()
            relays_f = []
            i=0
            for w in ("Wgg", "Wd", "Wee"):
                if w == "Wgg":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.GUARD]
                    no_flags = [Flag.EXIT]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[j], flags,\
                            no_flags)
                    if "Wgg" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        continue
                elif w == "Wee":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.EXIT]
                    no_flags = [Flag.GUARD]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[j], flags,\
                            no_flags)
                    if "Wee" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        continue
                elif w == "Wd":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.EXIT, Flag.GUARD]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[j], flags,
                            [])
                    if "Wed" not in cons_rel_stats[relays_f[0]].wf_bw_weights and\
                       "Wgd" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        continue
                else:
                    raise ValueError("Weight not recognized {0}".format(w))
            
                relays_f.sort(key=lambda x: cons_rel_stats[x].bandwidth, reverse=True)
                accu = 0
                accu2 = 0
                for relay in relays_f:
                    if w != "Wd":
                        accu += cons_rel_stats[relay].wf_bw_weights[w] *\
                            cons_rel_stats[relay].bandwidth
                        accu2 += cons_rel_stats[relay].bandwidth*self.cons_bw_weights[j][w]
                    else:
                        accu += (cons_rel_stats[relay].wf_bw_weights['Wed']+\
                                cons_rel_stats[relay].wf_bw_weights['Wgd']) * \
                                cons_rel_stats[relay].bandwidth
                        accu2 += cons_rel_stats[relay].bandwidth*\
                                (self.cons_bw_weights[j]['Wed']+self.cons_bw_weights[j]['Wgd'])
                e = accu-accu2 - self.bwws_remaining[j][i]
                self.assertTrue(approx_equal(e, 0.0))
                i+=1
            j+=0
    def test_global_view(self):
        
        j = 0
        for cons_rel_stats in self.list_relays:
            relays = cons_rel_stats.values()
            relays_f = []
            for w in ("Wgg", "Wd", "Wee"):
                if w == "Wgg":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.GUARD]
                    no_flags = [Flag.EXIT]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[j], flags,\
                            no_flags)
                    if "Wgg" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        continue
                elif w == "Wee":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.EXIT]
                    no_flags = [Flag.GUARD]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[j], flags,\
                            no_flags)
                    if "Wee" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        continue
                elif w == "Wd":
                    flags = [Flag.RUNNING, Flag.VALID, Flag.EXIT, Flag.GUARD]
                    relays_f = pathsim.filter_flags(cons_rel_stats, self.descriptors[j], flags,\
                            [])
                    if "Wed" not in cons_rel_stats[relays_f[0]].wf_bw_weights and\
                       "Wgd" not in cons_rel_stats[relays_f[0]].wf_bw_weights:
                        continue
                else:
                    raise ValueError("Weight not recognized {0}".format(w))

                relays_f.sort(key=lambda x: cons_rel_stats[x].bandwidth, reverse=True)
                if w != "Wd":
                    y = [cons_rel_stats[relay].bandwidth*\
                            cons_rel_stats[relay].wf_bw_weights[w]/float(self.weightscale[j])\
                            for relay in relays_f]
                else:
                    y = [cons_rel_stats[relay].bandwidth*\
                            (cons_rel_stats[relay].wf_bw_weights['Wed']+\
                            cons_rel_stats[relay].wf_bw_weights['Wgd'])/float(self.weightscale[j])\
                            for relay in relays_f]
                    
                y2 = [cons_rel_stats[relay].bandwidth for \
                        relay in relays_f]
                if w != "Wd":
                    y3 = [cons_rel_stats[relay].bandwidth*self.cons_bw_weights[j][w]/\
                            float(self.weightscale[j]) for relay in relays_f]
                else:
                    y3 = [cons_rel_stats[relay].bandwidth*\
                            (self.cons_bw_weights[j]['Wed']+self.cons_bw_weights[j]['Wgd'])/\
                            float(self.weightscale[j]) for relay in relays_f]
                x = range(0, len(y))
                pdb.set_trace()
                matplotlib.pyplot.plot(x,y2, label='BW_i', linestyle='dashed')
                matplotlib.pyplot.plot(x,y3, label='BW_i*{0}'.format(w), linestyle='dotted',\
                        linewidth='3')
                matplotlib.pyplot.plot(x,y, label='BW_i*{0}_i'.format(w))
                matplotlib.pyplot.fill_between(x, y, y3, color='grey')
                matplotlib.pyplot.ylim(ymax=200000)
                matplotlib.pyplot.xlim(xmin=0, xmax=1300)
                if w == "Wgg":
                    matplotlib.pyplot.xlabel("Guard flagged nodes sorted by bandwidth decreasing")
                elif w == "Wee":
                    matplotlib.pyplot.xlabel("Exit flagged nodes sorted by bandwidth decreasing")
                elif w == "Wd":
                    matplotlib.pyplot.xlabel("Guard+Exit flagged nodes sorted by bandwidth decreasing")
                matplotlib.pyplot.ylabel("Bandwidth * weight")
                matplotlib.pyplot.legend()

                matplotlib.pyplot.show()
            j+=1



## Method approx equal borrowed from
## http://code.activestate.com/recipes/577124-approximately-equal/ 
def _float_approx_equal(x, y, tol=1e-5, rel=None):
    if tol is rel is None:
        raise TypeError('cannot specify both absolute and relative errors are None')
    tests = []
    if tol is not None: tests.append(tol)
    if rel is not None: tests.append(rel*abs(x))
    assert tests
    return abs(x - y) <= max(tests)

def approx_equal(x, y, *args, **kwargs):
    """approx_equal(float1, float2[, tol=1e-18, rel=1e-7]) -> True|False
    approx_equal(obj1, obj2[, *args, **kwargs]) -> True|False

    Return True if x and y are approximately equal, otherwise False.

    If x and y are floats, return True if y is within either absolute error
    tol or relative error rel of x. You can disable either the absolute or
    relative check by passing None as tol or rel (but not both).

    For any other objects, x and y are checked in that order for a method
   __approx_equal__, and the result of that is returned as a bool. Any
    optional arguments are passed to the __approx_equal__ method.

    __approx_equal__ can return NotImplemented to signal that it doesn't know
    how to perform that specific comparison, in which case the other object is
    checked instead. If neither object have the method, or both defer by
    returning NotImplemented, approx_equal falls back on the same numeric
    comparison used for floats.
    """
    
    if not (type(x) is type(y) is float):
        # Skip checking for __approx_equal__ in the common case of two floats.
        methodname = '__approx_equal__'
        # Allow the objects to specify what they consider "approximately equal",
        # giving precedence to x. If either object has the appropriate method, we
        # pass on any optional arguments untouched.
        for a,b in ((x, y), (y, x)):
            try:
                method = getattr(a, methodname)
            except AttributeError:
                continue
            else:
                result = method(b, *args, **kwargs)
                if result is NotImplemented:
                    continue
                return bool(result)
    # If we get here without returning, then neither x nor y knows how to do an
    # approximate equal comparison (or are both floats). Fall back to a numeric
    # comparison.
    return _float_approx_equal(x, y, *args, **kwargs)

def suite():
    tests = ['test_weight', 'test_constraint_equality', 'test_constraint_bound',\
             'test_constraint_unity', 'test_constraint_sum_bwweight' ,'test_global_view']
    #tests = ['test_weight', 'test_constraint_equality', 'test_constraint_bound',\
             #'test_constraint_unity','test_global_view']
    return unittest.TestSuite(map(TestWaterFilling, tests))


if __name__ == "__main__":

    unitest = suite()
    unitest.debug()
