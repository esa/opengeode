#!/usr/bin/env python3

# run python3 -m cProfile -o profile.out -m opengeode.opengeode -g <files.pr>

import pstats
from pstats import SortKey

p = pstats.Stats("profile.out")

p.sort_stats(SortKey.CUMULATIVE).print_stats(30)




