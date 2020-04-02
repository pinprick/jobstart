#!/usr/bin/python
# Copyright (c) 2020      Mellanox Technologies, Inc.
#                         All rights reserved. *


import re
import sys
import os

# Filtering 
class LFilter:
    default_field = "LF_DEFAULT"
    class FilterInt:
        def __init__(self, fields, obj, fid):
            self.fields = fields
            self.obj = obj
            self.fid = fid

    def __init__(self, jobid, regex_chk, regex, fdescr, hfield):
        self.jobid = jobid
        print "JOBID = ", jobid
        self.filters = { }
        self.template_empty = re.compile("^\s*")
        self.template_chk = re.compile(regex_chk)
        self.template = re.compile(regex)
        self.template.match("test")
        self.fdescr = fdescr
        if( len(fdescr) == 0 ):
            print "ERROR: empty field data"
            os.abort();
        if (not ( hfield in fdescr.keys())):
            print "ERROR: hash field not found:"
            print "Hash Field = ", hfield
            print "Description: ", fdescr
            print "Using the first field, may not be efficient!: ", fdescr.keys()[0]
            self.hfield = fdescr.keys()[0]
        else:
            self.hfield = hfield

    def add(self, fields, obj, fid):
        if ( not (self.hfield in fields.keys())):
            print "Cannot import filter: hash field is not provided"
            os.abort()
        field = fields[self.hfield]
        f = self.FilterInt(fields, obj, fid);
        if ( not (field in self.filters.keys()) ):
            self.filters[field] = []
        #print "lFilter: Append to ", field, " fields = ", fields
        self.filters[field].append(f)


    def _parse_int(self, line_in):
        line = line_in.strip()
        if( len(line) == 0 ):
            return
        m = self.template_chk.match(line)
        if( m == None ):
            # TODO: output to the error log
            print "lFilter: WARNING: The file line is corrupted: \"", line, "\""
        m = self.template.match(line)
        if( m != None ):
            pline = {}
            for field in self.fdescr.keys():
                pline[field] = m.group(self.fdescr[field])
            return pline
        else:
            return None

    def apply(self, line):
        pline = self._parse_int(line)
        if (pline == None):
            return 0
        if  ( float(pline["jobid"]) != self.jobid ) :
            return 0;
        h = pline[self.hfield]
        if( not (h in self.filters.keys())):
            return 0
        flist = self.filters[h]
        for flt in flist:
            ret = 0
            for field in flt.fields.keys():
                ret += (pline[field] != flt.fields[field] );
            if( not ret ):
                if( flt.obj.lfilter(pline, flt.fid) ):
                    return 1
        return 0
