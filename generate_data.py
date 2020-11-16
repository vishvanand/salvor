import random
import string
import sys
import math
import heapq
import datetime


class Restrict:
    def __init__(self, base, name, bound):
        self.type = type(base)
        self.name = name
        if self.type == int:
            self.value = random.randint(0, bound)
        elif self.type == str:
            self.value = ''.join([random.choice(string.ascii_uppercase) for _ in range(bound)])
        elif self.type == bool:
            self.value = bool(random.getrandbits(1))
    
    def __str__(self):
        return self.name + ': ' + str(self.value) + '\n'

"""
restrict_spec 
    1. base
    2. name
    3. bound
"""

class Point:
    def __init__(self, id, restrict_spec):
        self.id = id
        self.restricts = [] 
        for restrict in restrict_spec:
            self.restricts.append(Restrict(restrict[0], restrict[1], restrict[2]))
        
    def __str__(self):
        part = 'Point: ' + str(self.id) + '\n'
        restricts = ''
        for restrict in self.restricts:
            restricts += '\t' + restrict.name + ': ' + str(restrict.value) + '\n'
        
        return part + restricts

'''
skip_ptr = { pos : next_val }
'''
class SkipLinkedList:
    class Iterator:
        def __init__(self, lst, skip_ptrs):
            self.pos = 0
            self.list = lst
            self.sqrt_length = int(math.sqrt(len(lst)))
            self.skip_ptrs = skip_ptrs
        
        def val(self):
            if (self.pos < len(self.list)):
                return self.list[self.pos]
            else:
                return None

        def val_and_next(self):
            if (self.pos + 1 < len(self.list)):
                self.pos += 1
                return self.list[self.pos]

            return None
        
        def next(self):
            if (self.pos + 1 < len(self.list)):
                self.pos += 1
        
        def find_gte(self, val):
            closest_mod = self.pos - (self.pos % self.sqrt_length)

            while(closest_mod + self.sqrt_length in self.skip_ptrs and self.skip_ptrs[closest_mod + self.sqrt_length] < val):
                closest_mod += self.sqrt_length
            
            # print('mod', self.pos, closest_mod)
            self.pos = max(self.pos, closest_mod)


            while(self.pos < len(self.list) and self.list[self.pos] < val):
                self.pos += 1

            if self.pos >= len(self.list):
                return None
            
            return self.list[self.pos]

            

    def __init__(self, lst):
        self.list = lst
        self.skip_ptrs = {}
        self.sqrt_length = 0

        self.gen_skip_ptrs_()

    def gen_skip_ptrs_(self):
        self.sqrt_length = int(math.sqrt(len(self.list)))
        for i in range(0, len(self.list)):
            if i % self.sqrt_length == 0:
                if (i + self.sqrt_length) < len(self.list):
                    index = int(i + self.sqrt_length)
                    self.skip_ptrs[index] = self.list[index]

    def get_iterator(self):
        return self.Iterator(self.list, self.skip_ptrs)
    
    def __str__(self):
        return self.list.__str__() + '\n' + self.skip_ptrs.__str__()


def RestrictKey(restrict):
    return restrict.name + ':' + str(restrict.value)

def ConstructInvertedIndex(points):
    index = {}

    for point in points:
        for restrict in point.restricts:
            key = RestrictKey(restrict)
            if key in index:
                index[key].append(point.id)
            else:
                index[key] = [point.id]
    
    return index

class SkipListIndex():
    def __init__(self, index):
        self.posting_lists = {}
        for k in index.keys():
            self.posting_lists[k] = SkipLinkedList(index[k])

    def exists_one_match(self, restricts):
        keys = []
        doc_map = {}

        for restrict in restricts:
            keys.append(RestrictKey(restrict))

        max_val = 0
        max_pos = 0

        iters = [self.posting_lists[key].get_iterator() for key in keys if key is not None]

        while(True):
            doc_map = {}
            for i in range(len(iters)):
                # print(keys[i], 'iters', iters[i].val())
                if iters[i].val() == None:
                    return None
                
                if iters[i].val() >= max_val:
                    max_val = iters[i].val()
                    max_pos = i

                if iters[i].val() in doc_map:
                    doc_map[iters[i].val()] += 1
                else:
                    doc_map[iters[i].val()] = 1 
                
            if len(doc_map) == 1:
                return [x for x in doc_map.keys()][0]
            else:
                for i in range(len(iters)):
                    if i != max_pos:
                        # print('call', keys[i], max_val)
                        iters[i].find_gte(max_val)

    def __str__(self):
        val = ''
        for k,v in self.posting_lists.items():
            val += k + ': ' + v.__str__() + '\n'

        return val   

restrict_spec = [
    (0, 'feed', 10),
    (True, 'policy', 0),
    (False, 'safe', 0),
    (1, 'geo', 10),
    ('', 'country', 1),
    ('', 'lang', 1)
]     

points = []
for i in range(0, 1000000):
    points.append(Point(i, restrict_spec))

print('done generating points')


index = ConstructInvertedIndex(points)

print('done generating index')

# print(index)
sli = SkipListIndex(index)
feed = Restrict(0, 'feed', 10)
feed.value = 0

print('done generating search index')
geo = Restrict(True, 'geo', 0)
geo.value = 9

to = datetime.datetime.now().timestamp()
sli.exists_one_match([feed, geo])
tn = datetime.datetime.now().timestamp()
print((tn-to)*10**6)