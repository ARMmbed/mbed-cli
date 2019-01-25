# mbed debug trace transformer, handling memory trace information
# Author: Matthias L. Jugel (@thinkberg)
#
# Copyright (c) 2018 ubirch GmbH, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.

import re
import sys

from serial.tools.miniterm import Transform

def debug(s):
    sys.stderr.write("D "+repr(s)+"\n")

class MbedTransform(Transform):
    mem = {}
    allocated = 0
    reset = None
    buffer = ""

    def __init__(self, reset_str=None):
        self.reset = reset_str
        if self.reset is not None:
            sys.stderr.write("memory tracing enabled: resetting on '{}'\n".format(self.reset))

        self.r_malloc = re.compile("([^#]*)#m:0x([0-9a-f]+);0x([0-9a-f]+)-(\\d+)")
        self.r_calloc = re.compile("([^#]*)#c:0x([0-9a-f]+);0x([0-9a-f]+)-(\\d+);(\\d+)")
        self.r_realloc = re.compile("([^#]*)#r:0x([0-9a-f]+);0x([0-9a-f]+)-0x([0-9a-f]+);(\\d+)")
        self.r_free = re.compile("([^#]*)#f:0x([0-9a-f]+);0x([0-9a-f]+)-0x([0-9a-f]+)")

    def rx(self, rx_input):
        # collect lines
        out = ""
        for c in rx_input:
            if c == '\r' or c == '\n':
                if len(self.buffer):
                    out += self.trace_line(self.buffer)
                else:
                    out += "\n"
                self.buffer = ""
                continue
            else:
                self.buffer += c
                continue
        return out

    def trace_line(self, line):
        # strip newline and carriage return
        line = line.rstrip('\n').rstrip('\r')

        # if we detect the reset keyword, rest the map and memory counter
        if self.reset is not None and self.reset in line:
            self.mem = {}
            self.allocated = 0
            line += "\n\n\033[91m>> RESET HEAP COUNTERS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\033[0m\n"
            line += "\033[4m   (NUM)    TOTAL [ ADDRESS] CHANGE  (COMMENT)\033[0m"
            return line

        # match malloc, realloc and free
        m = self.r_malloc.search(line)
        if m:
            out = ""
            if len(m.group(1)):
                out += m.group(1)
            if m.group(2) == "0x0":
                out += "\033[1m!! (%03d) \033[31mmalloc failed\033[0m (%s)\n" % (len(self.mem), line)
            else:
                self.mem[m.group(2)] = int(m.group(4))
                self.allocated += int(m.group(4))
                out += "\033[1m== (%03d) \033[34m%8d\033[0m [%8x] \033[31m+%-6d\033[0m (%s)" % \
                       (len(self.mem), self.allocated, int(m.group(2), 16), int(m.group(4)), line.replace(m.group(1), ""))
                return out

        m = self.r_calloc.search(line)
        if m:
            out = ""
            if len(m.group(1)):
                out += m.group(1)
            if m.group(2) == "0x0":
                out += "\033[1m!! (%03d) \033[31mcalloc failed\033[0m (%s)\n" % (len(self.mem), line)
            else:
                total = int(m.group(4)) * int(m.group(5))
                self.mem[m.group(2)] = total
                self.allocated += total
                out += "\033[1m== (%03d) \033[34m%8d\033[0m [%8x] \033[31m+%-6d\033[0m (%s)" % \
                                 (len(self.mem), self.allocated, int(m.group(2), 16), total, line.replace(m.group(1), ""))
            return out

        m = self.r_realloc.search(line)
        if m:
            out = ""
            if len(m.group(1)):
                out += m.group(1)
            diff = 0
            if self.mem.has_key(m.group(2)):
                diff = int(m.group(5)) - self.mem[m.group(2)]
                self.mem[m.group(2)] = int(m.group(5))
            else:
                out += "\033[33m!! (%03d) WARN: realloc() without previous allocation\033[0m (%s)\n" % (len(self.mem), line)
            self.allocated += diff
            out += "\033[1m== (%03d) \033[34m%8d\033[0m [%8x] \033[35m+%-6d\033[0m (%s)" % \
                             (len(self.mem), self.allocated, int(m.group(2), 16), diff, line.replace(m.group(1), ""))
            return out

        m = self.r_free.search(line)
        if m:
            out = ""
            if len(m.group(1)):
                out += m.group(1)
            freed = 0
            if self.mem.has_key(m.group(4)):
                freed = self.mem[m.group(4)]
                self.allocated -= freed
                del self.mem[m.group(4)]
            else:
                out += "\033[33m!! (%03d) WARN: free(0x%s)\033[0m\n" % (len(self.mem), m.group(4))
            out += "\033[1m== (%03d) \033[34m%8d\033[0m [%8x] \033[92m-%-6d\033[0m (%s)" % \
                             (len(self.mem), self.allocated, int(m.group(4), 16), freed, line.replace(m.group(1), ""))
            return out

        # print all other lines as is, so we can still use the log functionality
        return line
