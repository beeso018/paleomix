#!/usr/bin/python -3
#
# Copyright (c) 2012 Mikkel Schubert <MSchubert@snm.ku.dk>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from __future__ import print_function

import sys
import time

from pypeline.common.utilities import fragment


_DESC = "Processed {Reads} reads in {Time}. Last {ReadsDelta} reads in {TimeDelta}, last read at {Contig}: {Position} ..."
_FINAL = "Processed {Reads} reads in {Time}. Last {ReadsDelta} reads in {TimeDelta} ..."

class BAMTimer:
    def __init__(self, bamfile, desc = _DESC, final = _FINAL, step = 1e6, out = sys.stderr):
        self._bam   = bamfile
        self._out   = out
        self._desc  = desc
        self._final = final
        self._step  = step
        self._count = 0
        self._last_count = 0
        self._last_time  = time.time()
        self._start_time = self._last_time


    def increment(self, count = 1, read = None):
        self._count += count
        if (self._count - self._last_count) >= self._step:
            current_time = time.time()
            self._print(self._desc, current_time, read)
            self._last_time  = current_time
            self._last_count = self._count
        return self


    def finalize(self):
        self._print(self._final, time.time(), None)


    def _print(self, desc, current_time, read):
        contig, position = "NA", "NA"
        if read and self._bam:
            contig   = self._bam.references[read.tid]
            position = (",".join(fragment(3, str(read.pos + 1)[::-1])))[::-1]

        print(desc.format(Reads      = self._count,
                          ReadsDelta = self._count - self._last_count,
                          Time       = self._format(current_time - self._start_time),
                          TimeDelta  = self._format(current_time - self._last_time),
                          Contig     = contig,
                          Position   = position),
            file = self._out)


    def _format(self, ftime):
        utc = time.gmtime(ftime)
        return "%02i:%02i:%02is" % (utc.tm_hour, utc.tm_min, utc.tm_sec)

