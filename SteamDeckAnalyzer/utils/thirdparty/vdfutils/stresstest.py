import time
from random import SystemRandom
from collections import OrderedDict

from vdfutils import parse_vdf, format_vdf

ITERATIONS = 10000
ENTRIES = 500

CHAR_POOL = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUM_POOL = '0123456789'

r = SystemRandom()


def random_chars(n):
    return ''.join(r.sample(CHAR_POOL, r.randrange(0, n)))
    
    
def random_nums(n):
    return ''.join(r.sample(NUM_POOL, r.randrange(0, n)))


d = OrderedDict(reservations=OrderedDict())

for i in xrange(ENTRIES):
    header = "XVIS-{}".format(i)
    d['reservations'][header] = OrderedDict(
            (
                ('reserved', str(r.randint(0, 1))),
                ('user', random_chars(10)),
                ('clean', str(r.randint(0, 1))),
                ('startTime', random_nums(10)),
                ('endTime', random_nums(10)),
                (
                    'password',
                    OrderedDict(
                            (
                                ('salt', random_chars(10)),
                                ('hash', random_chars(10)),
                            )
                        ),
                ),
            )
        )
        
        
print "Iterations:", ITERATIONS
print "Entries:", ENTRIES

now = time.time()
for i in xrange(ITERATIONS):
    format_vdf(d)
    
total = time.time() - now
avg = total / float(ITERATIONS)

print "Format Total:", total
print "Format Avg:", avg


data = format_vdf(d)

now = time.time()
for i in xrange(ITERATIONS):
    parse_vdf(data)
    
total = time.time() - now
avg = total / float(ITERATIONS)

print "Parse Total:", total
print "Parse Avg:", avg
