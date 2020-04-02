import os


class ParsingManager:

    def __init__(self, state, hfield, log_parser):
        self.state = state
        self.hfield = hfield
        self.parser = log_parser
        self.filters = {}

    def add(self, fields, module):
        if not (self.hfield in fields.keys()):
            print "Cannot import filter: hash field is not provided"
            os.abort()
        field = fields[self.hfield]
        if not (field in self.filters.keys()):
            self.filters[field] = []

        self.filters[field].append(module)

    def register_modules(self, modules):
        for module in modules:
            module.register(self)

    def apply(self, line):
        pline = self.parser.parse(line)

        if None == pline:
            print "lFilter: WARNING: The file line is corrupted: \"", line, "\""
            return 0

        h = pline[self.hfield]
        if not h in self.filters.keys():
            return 0

        nodeid = int(pline["nodeid"])
        hostname = pline["hostname"]
        ts = self.state.sync.global_ts(nodeid, hostname, float(pline["timestamp"]))

        filter_list = self.filters[h]
        for module in filter_list:
            module.update(pline, ts, nodeid)
        return 0
