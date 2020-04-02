#!/usr/bin/python
import Regexper

# Filters
class CollFilter:
    def filter(self, log_line):
        print "abstract method"

class RingLocalFilter(CollFilter):

    regex = "\s(0x[0-9a-fA-F]+):\sctx=(0x[0-9a-fA-F]+),\scontrib/loc:\scollseq=(\d+),\sstate=(\d+),\scontrib=(\d+),\ssize=(\d+)"

    def filter(self, log_line):

        fdescr = {}
        fdescr["cptr"] = 1
        fdescr["ctxptr"] = 2
        fdescr["cseq"] = 3
        fdescr["state"] = 4
        fdescr["contrib_id"] = 5
        fdescr["size"] = 6

        regexper = Regexper(self.regex, fdescr)
        parsed_dict = regexper.parse(log_line)

        return parsed_dict

class RingRemoteFilter(CollFilter):

    regex = "\s(0x[0-9a-fA-F]+):\sctx=(0x[0-9a-fA-F]+)\scontrib/nbr:\scollseq=(\d+),\sstate=(\S+),\snodeid=(\d+),\scontrib=(\d+),\shopseq=(\d+),\ssize=(\d+)"

    def filter(self, log_line):
        fdescr = {}
        fdescr["cptr"] = 1
        fdescr["ctxptr"] = 2
        fdescr["cseq"] = 3
        fdescr["state"] = 4
        fdescr["src"] = 5
        fdescr["contrib_id"] = 6
        fdescr["hopseq"] = 7
        fdescr["size"] = 8

        regexper = Regexper(self.regex, fdescr)
        parsed_dict = regexper.parse(log_line)

        return parsed_dict

# CollModule
class CollModule:

    def register(mgr):
        local_Module = CollLocalModule(mgr.state)
        mgr.add(local_Module.fields, local_Module)
        remote_module = CollRemoteModule(mgr.state)
        mgr.add(remote_module.fields, remote_module)

    def update(self, line, ts, nodeid):
        service = self.service()
        filter = self.filter()
        converter = self.converter()

        pline = filter.filter(line)
        dto = converter.convert(pline)
        dto.set_ts(ts)
        dto.set_nodeid(nodeid)

        service.update(dto)

    def service(self):
        print("abstract method")
    def filter(self):
        print("abstract method")
    def converter(self):
        print("abstract method")

class CollLocalModule(CollModule):

    fields = {"function": "pmixp_coll_ring_local"}

    def __init__(self, coll):
        self.coll = coll

    def service(self):
        return CollLocalService(self.coll)
    def filter(self):
        return RingLocalFilter()
    def converter(self):
        return CollLocalConverter()


class CollRemoteModule(CollModule):

    fields = {"function": "pmixp_coll_ring_neighbor"}

    def __init__(self, coll):
        self.coll = coll

    def service(self):
        return CollRemoteService()

    def filter(self):
        return RingRemoteFilter()

    def converter(self):
        return CollRemoteConverter()

# Collective service

class CollLocalService:

    def __init__(self, coll):
        self.coll = coll

    def update_coll(self, coll_operation):
        self.coll.update(
            "ring",
            coll_operation.cseq,
            coll_operation.contrib_id,
            coll_operation.size,
            coll_operation.ts,
            coll_operation.nodeid
        )

class CollRemoteService:

    def __init__(self, coll):
        self.coll = coll

    def update_coll(self, coll_operation):
        self.coll.update(
            "ring",
            coll_operation.cseq,
            coll_operation.contrib_id,
            coll_operation.size,
            coll_operation.ts,
            coll_operation.nodeid,
            coll_operation.src
        )

# Converters

class CollLocalConverter:
    def convert(self, fdescr):
        return LocalColl(
            fdescr["cseq"],
            fdescr["contrib_id"],
            fdescr["size"]
        )

class CollRemoteConverter:
    def convert(self, fdescr):

        return RemoteColl(
            fdescr["cseq"],
            fdescr["contrib_id"],
            fdescr["size"],
            fdescr["src"]
        )

# Data transfer objects (DTO)

class LocalColl:

    def __init__(self, cseq, contrib_id, size):
        self.cseq = cseq
        self.contrib_id = contrib_id
        self.size = size
        self.ts = None
        self.nodeid = None

    def set_ts(self, ts):
        self.ts = ts

    def set_nodeid(self, nodeid):
        self.nodeid = nodeid

class RemoteColl:

    def __init__(self, cseq, contrib_id, size, src):
        self.cseq = cseq
        self.contrib_id = contrib_id
        self.size = size
        self.ts = None
        self.nodeid = None
        self.src = src

    def set_ts(self, ts):
        self.ts = ts

    def set_nodeid(self, nodeid):
        self.nodeid = nodeid
