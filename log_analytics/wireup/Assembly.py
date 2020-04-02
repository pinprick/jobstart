import LogParser
import LineValidator
import Regexper
import ParsingManager
import FilterColl as cflt

class Assembly:

    def __init__(self, state):
        self.state = state

    def build_parser(self, job_id):

        regex_chk = "^\[\S+\]"
        validator = LineValidator(regex_chk)

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

        # job_id = self.state.set.jobid
        parser = LogParser(job_id, "function", validator, base_parser)
        return parser

    def build_parse_mgr(self):
        mgr = ParsingManager(self.state, "function")
        mgr.register_modules([cflt.CollFilter])
