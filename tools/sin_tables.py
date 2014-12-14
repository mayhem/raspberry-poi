#!/usr/bin/env python

import math

entries = 360

sin_table = [ "%f" % math.sin((float(i) / entries) * (2*math.pi)) for i in xrange(entries) ]
cos_table = [ "%f" % math.cos((float(i) / entries) * (2*math.pi)) for i in xrange(entries) ]

print "#ifndef SIN_H"
print "#define SIN_H"
print "#include <progmem.h>"
print 
print "#define sin_table_entries %d" % entries
print 
print "const float sin_table[sin_table_entries] PROGMEM = { ",
print ",".join(sin_table),
print "};"
print "const float cos_table[sin_table_entries] PROGMEM = { ",
print ",".join(cos_table),
print "};\n"

print "#endif"
