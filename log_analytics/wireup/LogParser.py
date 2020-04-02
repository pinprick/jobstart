class LogParser:
    def __init__(self, job_id, hfield, validator, base_parser):
        self.job_id = job_id
        self.hfield = hfield
        self.validator = validator
        self.base_parser = base_parser

    def apply(self, line):
        if (not self.validator.validate(line)):
            return 0
        parsed_line = self.base_parser.parse(line)
        if (parsed_line == None):
            return 0
        if  ( float(parsed_line["jobid"]) != self.job_id ) :
            return 0;
        h = parsed_line[self.hfield]
        if( not (h in self.filters.keys())):
            return 0

        return parsed_line
