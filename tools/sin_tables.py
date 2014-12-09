#!/usr/bin/env python

import math

steps = (2.0 * math.pi) / 256.0

sin_table = [ "%f" % math.sin(i * steps) for i in xrange(256) ]
cos_table = [ "%f" % math.cos(i * steps) for i in xrange(256) ]

print "#ifndef SIN_H"
print "#define SIN_H"
print "#include <progmem.h>"
print 
print "#define sin_table_entries 256"
print 
print "const float sin_table[sin_table_entries] PROGMEM = { ",
print ",".join(sin_table),
print "};"
print "const float cos_table[sin_table_entries] PROGMEM = { ",
print ",".join(cos_table),
print "};\n"

print "#endif"
