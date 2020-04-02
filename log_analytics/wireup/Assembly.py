from LogParser import LogParser
from LineValidator import LineValidator
from ParsingManager import ParsingManager
from Regexper import Regexper
import FilterColl as coll
import FilterSPMIx as spmix
import FilterUCX as ucx


class Assembly:

    H_FIELD = "function"

    def __init__(self, state):
        self.state = state

    def validator(self):
        regex_chk = "^\[\S+\]"
        return LineValidator(regex_chk)

    def build_parser(self):

        regex = "^\[\S+\] \[(\S+)\]\s*debug:\s*\[(\S+):(\d+)\]\s*\[(\S+)]\s*\[(\S+):(\d+):(\S+)\]\s*mpi/pmix:\s(.*)"

        fdescr = {}
        fdescr["jobid"] = 1
        fdescr["hostname"] = 2
        fdescr["nodeid"] = 3
        fdescr["timestamp"] = 4
        fdescr["file"] = 5
        fdescr["line"] = 6
        fdescr["function"] = 7
        fdescr["logline"] = 8

        base_parser = Regexper(regex, fdescr)

        job_id = self.state.set.jobid
        parser = LogParser(job_id, "function", self.validator(), base_parser)
        return parser

    def modules(self):
        return [coll.CollModule, spmix.SPMIxModule, ucx.UCXModule]

    def parse_mgr(self):
        parser = self.build_parser()
        mgr = ParsingManager(self.state, self.H_FIELD, parser)
        mgr.register_modules(self.modules())

        return mgr
