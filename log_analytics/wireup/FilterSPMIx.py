#!/usr/bin/python

import re

# SPMIx Module
class SPMIxModule:
    @staticmethod
    def register(mgr):

        filter = FilterSPMIx(mgr.state.cluster, mgr.state.wireup_mtx)

        hostname_srv = SPMIxHostnameService(filter)
        mgr.add(hostname_srv.fields, hostname_srv)

        wireup_start_srv = SPMIxWireupStartService(filter)
        mgr.add(wireup_start_srv.fields, wireup_start_srv)

        wireup_thread_srv = SPMIxWireupThreadService(filter)
        mgr.add(wireup_thread_srv.fields, wireup_thread_srv)

        wireup_connected_srv = SPMIxWireupConnectedService(filter)
        mgr.add(wireup_connected_srv.fields, wireup_connected_srv)

    def update(self, line, ts, nodeid):
        print "abstract method"

# SPMIx services
class SPMIxService(SPMIxModule):
    def __init__(self, filter):
        self.filter = filter

    def update(self, pline, ts, nodeid):
        print "abstract method"

# Set the hostname for the nodeid
class SPMIxHostnameService(SPMIxService):
    fields = {"function": "_agent_thread"}

    def update(self, pline, ts, nodeid):
        self.filter.lfilter(pline, FilterSPMIx.HOSTNAME, ts, nodeid)

# Record Early Wireup start
class SPMIxWireupStartService(SPMIxService):
    fields = {"function": "pmixp_server_wireup_early"}

    def update(self, pline, ts, nodeid):
        self.filter.lfilter(pline, FilterSPMIx.EARLY_WIREUP_START, ts, nodeid)

# Record Early Wireup thread
class SPMIxWireupThreadService(SPMIxService):
    fields = {"function": "_wireup_thread"}

    def update(self, pline, ts, nodeid):
        self.filter.lfilter(pline, FilterSPMIx.EARLY_WIREUP_THREAD, ts, nodeid)

# Record Early Wireup thread
class SPMIxWireupConnectedService(SPMIxService):
    fields = {"function": "pmixp_dconn_connect"}

    def update(self, pline, ts, nodeid):
        self.filter.lfilter(pline, FilterSPMIx.WIREUP_CONNECTED, ts, nodeid)

# FilterSPMIx
class FilterSPMIx:
    HOSTNAME = 1
    EARLY_WIREUP_START = 2
    EARLY_WIREUP_THREAD = 3
    WIREUP_CONNECTED = 4

    def __init__(self, cluster, chan):
        self.cl = cluster
        self.ch = chan
        self.send_msg_id = 0
        self.recv_msg_id = 0

    def lfilter(self, pline, fid, ts, nodeid):

        hostname = pline["hostname"]

        if ( fid == self.HOSTNAME ):
            if( pline["logline"].find("Start agent thread") != -1 ):
                #print "Set the hostname of nodeid=", nodeid, " to ", pline["hostname"]
                n = self.cl.start(nodeid, hostname, ts)
                return 1

        if ( fid == self.EARLY_WIREUP_START ):
            if( pline["logline"].find("WIREUP/early: start") != -1 ):
                #print "Record early wireup beginning on nodeid=", nodeid
                n = self.cl.wireup_start(nodeid, ts)
                return 1

        if ( fid == self.EARLY_WIREUP_THREAD ):
            if( pline["logline"].find("WIREUP/early: complete") != -1 ):
                #print "Record early wireup finishing on nodeid=", nodeid
                n = self.cl.wireup_init(nodeid, ts)
                return 1
            elif( pline["logline"].find("WIREUP/early: sending initiation message to nodeids:") != -1 ):
                l1 = pline["logline"].split(":")
                l2 = l1[2].strip().split(" ")
                for dst in l2:
                    self.send_msg_id += 1
                    self.ch.update(nodeid, dst, "send", "completed", self.send_msg_id, 0, ts)
                return 1

        if ( fid == self.WIREUP_CONNECTED ):
            regex_tmp = "\s*WIREUP: Connect to (\d+).*"
            t = re.compile(regex_tmp)
            m = t.match(pline["logline"])
            if( m != None ):
                src = int(m.group(1))
                self.recv_msg_id += 1
                self.ch.update(src, nodeid, "recv", "completed", self.recv_msg_id, 0, ts)
                return 1
        return 0
