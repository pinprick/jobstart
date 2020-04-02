import re

class Regexper:

    #def __init__(self, pattern: basestring, field_descriptor: {basestring: int}):
    def __init__(self, pattern, field_descriptor):
        self.pattern = pattern
        self.field_descriptor = field_descriptor

    def parse(self, line):
        template = re.compile(self.pattern)
        match = template.match(line)
        if (match != None):
            parsed_line = {}
            for field in self.field_descriptor.keys():
                parsed_line[field] = match.group(self.field_descriptor[field])
            return parsed_line
        else:
            return None