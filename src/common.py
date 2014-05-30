import os

script_dir = os.path.abspath(os.path.dirname(__file__))

def nonempty(lst):  return filter(lambda x: x != '', lst)

def ppset(s): return reduce(lambda acc,el: acc + ',' + el, s)
