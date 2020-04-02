#!/usr/bin/python

import re

# UCX Module
class UCXModule:
    @staticmethod
    def register(mgr):

        filter = FilterUCX(mgr.state.ucx_mtx)
        module = UCXModule(filter)

        mgr.add({"function": "_ucx_send"}, module)
        mgr.add({"function": "send_handle"}, module)
        mgr.add({"function": "_ucx_progress"}, module)

    def __init__(self, filter):
        self.filter = filter

    def update(self, pline, ts, nodeid):
        self.filter.lfilter(pline, nodeid, ts)

# UCX FilterUCX
class FilterUCX:
    def __init__(self, chan):
        self.ch = chan

    def lfilter(self, pline, ts, nodeid):
        regex_tmp = ".*UCX:\s*(\S+)\s*\[(\S+)\]\s*nodeid=(\d+),\s*mid=(\d+),\s*size=(\d+)"
        t = re.compile(regex_tmp)
        m = t.match(pline["logline"])
        if( m != None ):
            side = m.group(1)
            mtype = m.group(2)
            peer = int(m.group(3))
            mid = int(m.group(4))
            size = int(m.group(5))
            if (side == "send"):
                src = nodeid
                dst = peer
            elif (side == "recv"):
                src = peer
                dst = nodeid
            else:
                assert (False), ("Unsupported UCX operation type: " + side + "; Only 'recv' and 'send' are supported")

            self.ch.update(src, dst, side, mtype, mid, size, ts)
            # Ensure that all possible states are covered
            if( "completed" == mtype ):
                mtype = "enqueued"
                if( None == self.ch.get_ts(src, dst, side, mtype, mid) ):
                    self.ch.update(src, dst, side, mtype, mid, size, ts)
            if( (side == "send") and ("enqueued" == mtype) ):
                mtype = "pending"
                if( None == self.ch.get_ts(src, dst, side, mtype, mid) ):
                    self.ch.update(src, dst, side, mtype, mid, size, ts)
            return 1
        return 0
