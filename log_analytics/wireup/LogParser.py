class LogParser:

    def __init__(self, job_id, hfield, validator, base_parser):
        self.job_id = job_id
        self.hfield = hfield
        self.validator = validator
        self.base_parser = base_parser

    def parse(self, line):
        if not self.validator.validate(line):
            return None
        parsed_line = self.base_parser.parse(line)
        if parsed_line == None:
            return None
        if float(parsed_line["jobid"]) != self.job_id:
            return None

        return parsed_line