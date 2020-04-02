import os

class ParsingManager:

    # line_parser
    # ucx_module
    # coll_module
    # PMIx_module

    def __init__(self, state, hfield, log_parser):
        self.state = state
        self.hfield = hfield
        self.parser = log_parser
        self.filters = {}

    def add(self, fields, module):
        if ( not (self.hfield in fields.keys())):
            print "Cannot import filter: hash field is not provided"
            os.abort()
        field = fields[self.hfield]
        if ( not (field in self.filters.keys()) ):
            self.filters[field] = []

        self.filters[field].append(module)

    def register_modules(self, modules):
        for module in modules:
            module.register(self)

    def start(self, line):
        self.parser.apply(line)