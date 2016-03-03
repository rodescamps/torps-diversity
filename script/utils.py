"""

Class defining router, network status document and descriptors with fields needed but not more

Borrowed from pathim.py of TorPS

"""
class RouterStatusEntry:
    """
    Represents a relay entry in a consensus document.
    Slim version of stem.descriptor.router_status_entry.RouterStatusEntry.
    """
    def __init__(self, fingerprint, nickname, flags,\
            bandwidth, is_unmeasured):
        self.fingerprint = fingerprint
        self.nickname = nickname
        self.flags = flags
        #measured bandwidth from consensus document
        self.bandwidth = bandwidth
        self.is_unmeasured = is_unmeasured
    

class NetworkStatusDocument:
    """
    Represents a consensus document.
    Slim version of stem.descriptor.networkstatus.NetworkStatusDocument.
    """
    def __init__(self, valid_after, fresh_until, bandwidth_weights, \
        bwweightscale, relays):
        self.valid_after = valid_after
        self.fresh_until = fresh_until
        self.bandwidth_weights = bandwidth_weights
        self.bwweightscale = bwweightscale
        self.relays = relays


class ServerDescriptor:
    """
    Represents a server descriptor.
    Slim version of stem.descriptor.server_descriptor.ServerDescriptor.
    """
    def __init__(self, fingerprint, hibernating, nickname, family, address,\
        exit_policy, adv_bw,ob_bandwidth, burst_bw, uptime):
        self.fingerprint = fingerprint
        self.hibernating = hibernating
        self.nickname = nickname
        self.family = family
        self.address = address
        self.exit_policy = exit_policy
        #average rate it's willing to relay in bytes/s
        self.adv_mean_bandwidth = adv_bw
        #estimated capacity based on previous 24h usage in byte/s
        self.observed_bandwidth = ob_bandwidth
        self.burst_bw = burst_bw
        self.uptime = uptime
