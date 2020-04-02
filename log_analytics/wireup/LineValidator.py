import re

class LineValidator:

    def __init__(self, regex_chk):
        self.template_chk = re.compile(regex_chk)

    def validate(self, line_in):
        line = line_in.strip()
        if (len(line) == 0):
            return False

        m = self.template_chk.match(line)
        if (m == None):
            # TODO: output to the error log
            print "lFilter: WARNING: The file line is corrupted: \"", line, "\""
            return False

        return True