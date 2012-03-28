# -*- coding: utf8 -*-
import math
import logging
import sys
from sqlalchemy import select, union
from sqlalchemy.sql import and_, or_
from cjklib import characterlookup
from cjklib import reading
from cjklib import exception
from cjklib import dbconnector
from cjklib import util
from abcSql import * 

# assume each item is a tuple, and score is the first
def insertionSort(array):
   i = 1
   while i < len(array):
      j = i
      while j > 0 and array[j][0] < array[j-1][0]:
         array[j-1], array[j] = array[j], array[j-1]
         j = j - 1
      i = i + 1

class abcNLPChar(characterlookup.CharacterLookup):
    
    BH = {'WG': 1, 'SWH': 7, 'WSG': 2, 'HP': 12, 'SWG': 47, 'SWZ': 36, 'SZH': 35, 'HG': 33, 'BXG': 5, 'SZZ': 45, 'HZSZH': 9,
           'HXWG': 48, 'PZ': 42, 'NG': 4, 'TN': 44, 'PZH': 43, 'PD': 40, 'SZT': 38, 'PZD': 41, 'HZ': 31, 'HZSZT': 17, 'PG': 50,
           'HZZP': 18, 'HZG': 10, 'D': 30, 'H': 26, 'HZZZ': 23, 'XG': 3, 'N': 25, 'Q': 51, 'HZT': 16, 'HZW': 21, 'T': 0, 'HZS': 32,
           'HZSZHZS': 24, 'HZSZHZP': 19, 'HZZ': 8, 'SZ': 34, 'P': 28, 'SG': 39, 'SP': 29, 'SW': 6, 'S': 27, 'HPWG': 20, 'ST': 37,
            'HZWG': 14, 'HZZZG': 49, 'HZSWH': 22, 'SZWG': 15, 'HZSG': 11, 'SZHZS': 46, 'HZP': 13}

    RL = [0, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 3, 1, 3, 2, 5, 5, 5, 5, 5, 5, 4, 4, 3, 4, 4, 4, 4, 4, 5, 5, 4, 5, 5, 3, 5, 3, 0, 1, 3, 3, 3, 3, 3, 5, 5, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 2, 3, 2, 3, 4, 4, 5, 4, 4, 4, 4, 4, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 4, 5, 3, 1, 0, 3, 3, 3, 3, 3, 5, 5, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 2, 3, 2, 3, 4, 4, 5, 4, 4, 4, 4, 4, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 4, 5, 4, 3, 3, 0, 1, 2, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 2, 4, 5, 4, 5, 4, 5, 5, 5, 4, 4, 4, 4, 4, 3, 4, 4, 4, 4, 3, 5, 5, 3, 5, 5, 5, 5, 4, 3, 3, 1, 0, 2, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 2, 4, 5, 4, 5, 4, 5, 5, 5, 4, 4, 4, 4, 4, 3, 4, 4, 4, 4, 3, 5, 5, 3, 5, 5, 5, 5, 5, 3, 3, 2, 2, 0, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 2, 2, 5, 4, 5, 4, 5, 5, 5, 4, 4, 4, 4, 4, 3, 4, 4, 4, 4, 3, 5, 5, 3, 5, 5, 5, 5, 5, 3, 3, 3, 3, 3, 0, 1, 2, 2, 3, 3, 3, 3, 2, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 3, 4, 2, 4, 3, 4, 4, 4, 5, 1, 1, 3, 2, 2, 3, 3, 3, 3, 3, 3, 5, 5, 3, 5, 5, 5, 5, 5, 3, 3, 3, 3, 3, 1, 0, 2, 2, 3, 3, 3, 3, 2, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 3, 4, 2, 4, 3, 4, 4, 4, 5, 1, 1, 3, 2, 2, 3, 3, 3, 3, 3, 3, 5, 5, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 2, 2, 0, 1, 2, 2, 3, 3, 1, 3, 2, 2, 5, 5, 5, 1, 1, 5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 5, 4, 4, 4, 4, 4, 4, 5, 4, 3, 3, 4, 5, 5, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 2, 2, 1, 0, 2, 2, 3, 3, 1, 3, 2, 2, 5, 5, 5, 1, 1, 5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 5, 4, 4, 4, 4, 4, 4, 5, 4, 3, 3, 4, 5, 5, 3, 3, 5, 5, 5, 5, 3, 3, 5, 5, 5, 3, 3, 2, 2, 0, 1, 3, 3, 4, 3, 3, 3, 5, 5, 3, 4, 4, 5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 5, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 4, 4, 4, 5, 4, 4, 4, 5, 5, 3, 3, 5, 5, 5, 3, 3, 2, 2, 1, 0, 3, 3, 4, 3, 3, 3, 5, 5, 3, 4, 4, 5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 5, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 4, 4, 4, 5, 4, 4, 4, 5, 5, 3, 3, 5, 5, 5, 3, 3, 3, 3, 3, 3, 0, 1, 3, 4, 3, 3, 3, 3, 4, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 5, 5, 3, 3, 5, 5, 5, 3, 3, 3, 3, 3, 3, 1, 0, 3, 4, 3, 3, 3, 3, 4, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 2, 2, 1, 1, 4, 4, 3, 3, 0, 4, 2, 2, 3, 3, 4, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 4, 3, 3, 4, 3, 3, 4, 5, 5, 5, 5, 5, 5, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 0, 4, 4, 4, 4, 4, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 1, 1, 4, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 3, 3, 2, 2, 3, 3, 3, 3, 2, 4, 0, 1, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 4, 5, 5, 5, 3, 3, 4, 5, 5, 5, 5, 5, 4, 4, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 3, 2, 2, 3, 3, 3, 3, 2, 4, 1, 0, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 4, 5, 5, 5, 3, 3, 4, 5, 5, 5, 5, 5, 4, 4, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 3, 3, 4, 3, 3, 0, 1, 2, 3, 3, 2, 2, 4, 4, 4, 4, 4, 4, 3, 3, 4, 5, 5, 5, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 4, 4, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 3, 3, 4, 3, 3, 1, 0, 2, 3, 3, 2, 2, 4, 4, 4, 4, 4, 4, 3, 3, 4, 5, 5, 5, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 4, 4, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 3, 4, 4, 4, 4, 3, 3, 2, 2, 0, 4, 4, 2, 2, 4, 4, 4, 4, 4, 4, 3, 3, 4, 5, 5, 5, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 4, 4, 2, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 4, 4, 5, 5, 3, 5, 4, 4, 3, 3, 4, 0, 1, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 4, 3, 3, 5, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 4, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 4, 4, 5, 5, 3, 5, 4, 4, 3, 3, 4, 1, 0, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 4, 3, 3, 5, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 4, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 4, 4, 4, 2, 2, 2, 4, 4, 0, 1, 4, 4, 4, 4, 4, 4, 3, 3, 4, 5, 5, 5, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 4, 4, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 4, 4, 4, 2, 2, 2, 4, 4, 1, 0, 4, 4, 4, 4, 4, 4, 3, 3, 4, 5, 5, 5, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 4, 4, 1, 5, 5, 4, 5, 5, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 4, 3, 4, 3, 4, 4, 4, 5, 4, 4, 4, 3, 3, 3, 3, 3, 4, 4, 3, 5, 5, 3, 5, 5, 5, 5, 3, 5, 5, 4, 4, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 4, 3, 4, 2, 5, 5, 1, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 3, 2, 2, 5, 5, 5, 2, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 4, 0, 3, 2, 3, 4, 4, 5, 4, 4, 4, 2, 2, 2, 3, 3, 4, 4, 3, 5, 5, 3, 5, 5, 4, 5, 1, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 0, 3, 2, 4, 4, 5, 5, 5, 5, 4, 4, 4, 3, 3, 3, 3, 4, 5, 5, 5, 5, 5, 5, 5, 3, 2, 2, 5, 5, 5, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 4, 2, 3, 0, 3, 4, 4, 5, 5, 5, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 2, 5, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 2, 3, 2, 3, 0, 5, 5, 4, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 3, 5, 5, 5, 5, 5, 4, 5, 5, 4, 4, 5, 5, 5, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 5, 4, 4, 4, 5, 0, 1, 3, 5, 5, 5, 4, 4, 4, 4, 4, 5, 5, 4, 4, 4, 5, 4, 4, 5, 5, 5, 4, 4, 5, 5, 5, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 5, 4, 4, 4, 5, 1, 0, 3, 5, 5, 5, 4, 4, 4, 4, 4, 5, 5, 4, 4, 4, 5, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 1, 5, 5, 5, 4, 3, 3, 0, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 3, 3, 5, 5, 4, 5, 4, 5, 5, 5, 5, 5, 4, 0, 1, 4, 3, 3, 4, 4, 4, 3, 3, 4, 4, 4, 2, 4, 5, 5, 5, 5, 4, 4, 4, 4, 4, 1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 3, 3, 5, 5, 4, 5, 4, 5, 5, 5, 5, 5, 4, 1, 0, 4, 3, 3, 4, 4, 4, 3, 3, 4, 4, 4, 2, 4, 5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 5, 3, 5, 5, 5, 4, 4, 4, 0, 4, 4, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 4, 4, 5, 4, 4, 4, 4, 4, 4, 2, 2, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 4, 4, 4, 4, 4, 4, 4, 3, 5, 2, 4, 3, 4, 4, 4, 5, 3, 3, 4, 0, 1, 2, 3, 3, 4, 4, 3, 5, 5, 4, 4, 5, 4, 5, 4, 4, 4, 4, 4, 4, 2, 2, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 4, 4, 4, 4, 4, 4, 4, 3, 5, 2, 4, 3, 4, 4, 4, 5, 3, 3, 4, 1, 0, 2, 3, 3, 4, 4, 3, 5, 5, 4, 4, 5, 4, 5, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 2, 4, 3, 4, 4, 4, 5, 4, 4, 3, 2, 2, 0, 3, 3, 4, 4, 3, 5, 5, 4, 5, 5, 2, 5, 4, 4, 4, 4, 4, 4, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 5, 3, 3, 4, 4, 4, 4, 5, 4, 4, 4, 3, 3, 3, 0, 1, 2, 2, 3, 5, 5, 4, 5, 5, 3, 5, 4, 4, 4, 4, 4, 4, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 5, 3, 3, 4, 4, 4, 4, 5, 4, 4, 4, 3, 3, 3, 1, 0, 2, 2, 3, 5, 5, 4, 5, 5, 3, 5, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 3, 4, 4, 5, 5, 5, 3, 3, 4, 4, 4, 4, 2, 2, 0, 1, 4, 5, 5, 4, 5, 5, 4, 5, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 3, 4, 4, 5, 5, 5, 3, 3, 4, 4, 4, 4, 2, 2, 1, 0, 4, 5, 5, 4, 5, 5, 4, 5, 4, 4, 4, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 5, 3, 4, 4, 3, 4, 4, 5, 4, 4, 4, 3, 3, 3, 3, 3, 4, 4, 0, 5, 5, 3, 4, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 5, 5, 3, 1, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 1, 4, 5, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 5, 5, 3, 1, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 0, 4, 5, 5, 4, 5, 4, 5, 5, 3, 3, 3, 3, 3, 3, 3, 5, 5, 5, 5, 4, 4, 3, 3, 4, 4, 4, 4, 4, 4, 4, 3, 5, 3, 5, 5, 5, 5, 5, 4, 2, 2, 5, 4, 4, 4, 4, 4, 4, 4, 3, 4, 4, 0, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 3, 4, 4, 4, 4, 3, 5, 4, 4, 4, 4, 4, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 4, 4, 5, 4, 4, 5, 4, 4, 5, 5, 5, 5, 5, 4, 5, 5, 3, 0, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 3, 4, 5, 5, 1, 1, 2, 4, 4, 1, 1, 5, 5, 5, 5, 5, 5, 4, 4, 5, 5, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 0, 4, 5, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 5, 2, 4, 5, 5, 5, 5, 5, 4, 4, 4, 2, 3, 3, 4, 4, 4, 4, 4, 5, 4, 4, 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0]    
    BHLEN = 52
    MAXBHDIS = 5
    
    def getStrokeOrderDict(self, db=None,  maxcount=500000):
        """
        Returns a stroke order dictionary for all characters in the chosen
        *character domain*.

        :rtype: dict
        :return: dictionary of key pair character, *glyph* and value stroke
            order
        """
        if not db:
           raise exception.NoInformationError(
                " need db for stroke order dictionary")
                
        print("Process: getStrokeOrderDict...")        
        tables = [self.db.tables[tableName] \
            for tableName in ['StrokeOrder', 'CharacterDecomposition']]
        # constrain to selected character domain
        if self.getCharacterDomain() != 'Unicode':
            tables = [table.join(self._characterDomainTable,
                table.c.ChineseCharacter \
                    == self._characterDomainTable.c.ChineseCharacter) \
                for table in tables]

        # get all character/glyph pairs for which we have glyph information
        chars = self.db.selectRows(
            union(*[select([table.c.ChineseCharacter, table.c.Glyph]) \
                for table in tables]))

        count = 0
        wcount = 0
        whole = len(chars)
        strokeOrderDict = {}
        cache = {}
        # The following is copied from ...
        for char, glyph in chars:
            if wcount % (whole / 10) == 0:
                per = (wcount/float(whole))*100.0
                print('Progress %d/%d (%02d%%)' % (wcount, whole, per))
            wcount = wcount + 1
            # Only use default glyph
            if glyph != 0:
                continue
            try:
                idc,  strokeOrderAbbrev = self.abcGetStrokeOrderAbbrev(char, glyph,  cache)
            except exception.NoInformationError:
                continue
            strokeOrder = []
            for stroke in strokeOrderAbbrev.replace(' ', '-').split('-'):
                if stroke != '?':
                   strokeOrder.append(stroke)
                else:
                    raise exception.NoInformationError("stroke ? in char %s" % char) 
                    
            if strokeOrder:
                strokestr = "|".join(strokeOrder)
                db.insert_stroke_order(char,  idc,  strokestr)
                count = count + 1
                if count >= maxcount:
                    print("Reach max entry limit(%d) of StrokeOrderDict! " % count)
                    break
        print("Finished with entry (%d) of StrokeOrderDict! " % count)
        return

    def abcGetStrokeOrderAbbrev(self, char, glyph, cache,  includePartial=False):
        """
        Gets the stroke order sequence for the given character as a string of
        *abbreviated stroke names* separated by spaces and hyphens.

        The stroke order is constructed using the character decomposition into
        components.

        :type char: str
        :param char: Chinese character
        :type glyph: int
        :param glyph: *glyph* of the character. This parameter is optional and
            if omitted the default *glyph* defined by
            :meth:`~CharacterLookup.getDefaultGlyph`
            will be used.
        :type includePartial: bool
        :param includePartial: if ``True`` a stroke order sequence will be
            returned even if only partial information is available. Unknown
            strokes will be replaced by a question mark (``?``).
        :rtype: str
        :return: string of stroke abbreviations separated by spaces and hyphens.
        :raise NoInformationError: if no stroke order information available

        .. todo::
            * Lang: Add stroke order source to stroke order data so that in
              general different and contradicting stroke order information
              can be given. The user then could prefer several sources
              that in the order given would be queried.
        """
        idc = u'⼞'
        # Make minimal modification for abcBuildStrokeOrder
        order = self._abcGetStrokeOrderEntry(char, glyph)
        if not order:     
            for decomposition in self.getDecompositionEntries(char, glyph):
                idc = decomposition[0]
                if not self.isBinaryIDSOperator(idc) and not self.isTrinaryIDSOperator(idc):
                    raise exception.NoInformationError("IDC of char %s is error: %s" % (char, idc)) 
                # only do for first decompsition
                break
        #
        strokeOrder = self._abcBuildStrokeOrder(char, glyph, cache, includePartial=includePartial)
        if not strokeOrder:
            raise exception.NoInformationError(
                "Character has no stroke order information")
        else:
            return (idc, strokeOrder)
            
    def getOrderDistance(self, order1, order2):
        distance_min  = 500
        len1 = len(order1)
        len2 = len(order2)
        if len1 < len2:
            order_s = order1
            order_l = order2
            len_s = len1
            len_l = len2
            len_move = len_l - len_s + 1
        else:
            order_s = order2
            order_l = order1
            len_s = len2
            len_l = len1
            len_move = len_l -len_s + 1
        bh_s = [ abcNLPChar.BH[ord] for ord in order_s ]
        bh_l = [ abcNLPChar.BH[ord] for ord in order_l ]

        distance_base = (len_move - 1) * abcNLPChar.MAXBHDIS
        for i in range(0, len_move):
            distance = distance_base
            for j in range (0, len_s):
                if (order_s[j] != order_l[i+j]):
                    distance = distance + abcNLPChar.RL[ bh_s[j] * abcNLPChar.BHLEN + bh_l[i+j] ]
            if (distance < distance_min):
                distance_min = distance
        return distance_min

    def getStrokeOrderSimilar(self, orderDict, db=None,  strict=True,  glyph=None, includePartial=False):
        """
        Gets similar character with tstroke order sequence for the given character.

        The stroke order is constructed using the character decomposition into
        components.

        :type char: str
        :param char: Chinese character
        :type glyph: int
        :param glyph: *glyph* of the character. This parameter is optional and
            if omitted the default *glyph* defined by
            :meth:`~CharacterLookup.getDefaultGlyph`
            will be used
        :type includePartial: bool
        :param includePartial: if ``True`` a stroke order sequence will be
            returned even if only partial information is available. Unknown
            strokes will be replaced by ``None``.
        :rtype: list
        :return: list of Unicode strokes
        :raise NoInformationError: if no stroke order information available
        """
        print("Process: getStrokeOrderSimilar...")
        if not orderDict:
           raise exception.NoInformationError(
                "Character has no stroke order dictionary")
        if not db:
           raise exception.NoInformationError(
                " need db for character variants")
            
        whole = len(orderDict)
        count = 0
        for src, srcValue in orderDict.items():
            distances = [ (500, ""),  (500, ""), (500, ""), (500, ""),  (500, "") ] 

            srcIdc = srcValue[0]
            srcOrder = srcValue[1]
            count = count + 1
            for dst, dstValue in orderDict.items():
                dstIdc = dstValue[0]
                dstOrder = dstValue[1]                
                if (dst == src):
                    continue
                if strict and srcIdc != dstIdc:
                    continue
                distance = self.getOrderDistance(srcOrder, dstOrder)
                distances.pop()
                distances.append((distance,  dst[0]))
                insertionSort(distances)

            if  distances:
                distance = distances[0]
 
            for distance in distances:
                if (distance[0] == 500):
                    break
                #print "%s --> %s (%d)" % (src,  distance[1],  distance[0])
                    
                db.insert_char_variant(src,  distance[1], distance[0])    

            if count % (whole / 100 + 1) == 0:
                per = (count/float(whole))*100.0
                print('Progress %d/%d (%02d%%)' % (count, whole, per))
                      
        return 


    def _abcGetStrokeOrderEntry(self, char, glyph):
        """
        Gets the stroke order sequence for the given character from the
        database's stroke order lookup table.

        :type char: str
        :param char: Chinese character
        :type glyph: int
        :param glyph: *glyph* of the character
        :rtype: str
        :return: string of stroke abbreviations separated by spaces and
            hyphens.
        """
        table = self.db.tables['StrokeOrder']
        return self.db.selectScalar(select([table.c.StrokeOrder],
            and_(table.c.ChineseCharacter == char,
                table.c.Glyph == glyph), distinct=True))

    def _abcBuildStrokeOrder(self, char, glyph, cache,  includePartial=False):
        """
        Gets the stroke order sequence for the given character as a string of
        *abbreviated stroke names* separated by spaces and hyphens.

        The stroke order is constructed using the character decomposition into
        components.

        :type char: str
        :param char: Chinese character
        :type glyph: int
        :param glyph: *glyph* of the character.
        :type includePartial: bool
        :param includePartial: if ``True`` a stroke order sequence will be
            returned even if only partial information is available. Unknown
            strokes will be replaced by a question mark (``?``).
        :type cache: dict
        :param cache: optional dict of cached stroke order entries
        :rtype: str
        :return: string of stroke abbreviations separated by spaces and hyphens.
        """
        def getFromDecomposition(char, glyph):
            """
            Gets stroke order from the tree of a single partition entry.

            :type decompositionTreeList: list
            :param decompositionTreeList: list of decomposition trees to derive
                the stroke order from
            :rtype: str
            :return: string of stroke abbreviations separated by spaces and
                hyphens.
            """
            def getFromEntry(subTree, index=0):
                """
                Goes through a single layer of a tree recursively.

                :type subTree: list
                :param subTree: decomposition tree to derive the stroke order
                    from
                :type index: int
                :param index: index of current layer
                :rtype: list of str
                :return: list of stroke abbreviations of the single components
                """
                strokeOrder = []
                if type(subTree[index]) != type(()):
                    # IDS operator
                    character = subTree[index]
                    if self.isBinaryIDSOperator(character):
                        # check for IDS operators we can't make any order
                        # assumption about
                        if character in [u'⿻']:
                            return None, index
                        # ⿴ should only occur for 囗
                        elif character == u'⿴':
                            so, newindex = getFromEntry(subTree, index+1)
                            if not so: return None, index
                            strokes = [order.replace(' ', '-').split('-')
                                for order in so]
                            if strokes != [['S', 'HZ', 'H']]:
                                #import warnings
                               # warnings.warn(
                               #     "Invalid decomposition entry %r" % subTree)
                                return None, index
                            strokeOrder.append('S-HZ')
                            so, index = getFromEntry(subTree, newindex+1)
                            if not so: return None, index
                            strokeOrder.extend(so)
                            strokeOrder.append('H')
                        # ⿷ should only occur for ⼕ and ⼖
                        elif character == u'⿷':
                            so, newindex = getFromEntry(subTree, index+1)
                            if not so: return None, index
                            strokes = [order.replace(' ', '-').split('-')
                                for order in so]
                            if strokes not in ([['H', 'SZ']], [['H', 'SW']]):
                                import warnings
                                warnings.warn(
                                    "Invalid decomposition entry %r" % subTree)
                                return None, index
                            strokeOrder.append(strokes[0][0])
                            so, index = getFromEntry(subTree, newindex+1)
                            if not so: return None, index
                            strokeOrder.extend(so)
                            strokeOrder.append(strokes[0][1])
                        else:
                            if (character == u'⿶'
                                or (character == u'⿺'
                                    and type(subTree[index+1]) == type(())
                                    and subTree[index+1][0] in u'辶廴乙')):
                                # IDS operators with order right one first
                                subSequence = [1, 0]
                            else:
                                # IDS operators with order left one first
                                subSequence = [0, 1]
                            # Get stroke order for both components
                            subStrokeOrder = []
                            for _ in range(0, 2):
                                so, index = getFromEntry(subTree, index+1)
                                if not so:
                                    return None, index
                                subStrokeOrder.append(so)
                            # Append in proper order
                            for seq in subSequence:
                                strokeOrder.extend(subStrokeOrder[seq])
                    elif self.isTrinaryIDSOperator(character):
                        # Get stroke order for three components
                        for _ in range(0, 3):
                            so, index = getFromEntry(subTree, index+1)
                            if not so:
                                return None, index
                            strokeOrder.extend(so)
                    else:
                        assert False, 'not an IDS character'
                else:
                    # no IDS operator but character
                    char, charGlyph = subTree[index]
                    # if the character is unknown or there is none, raise
                    if char == u'？':
                        return None, index
                    else:
                        # recursion
                        so = self._abcBuildStrokeOrder(char, charGlyph, cache, 
                            includePartial)
                        if not so:
                            if includePartial and self.hasStrokeCount:
                                try:
                                    strokeCount = self.getStrokeCount(char,
                                        charGlyph)
                                    so = '-'.join(['?'
                                        for i in range(strokeCount)])
                                except exception.NoInformationError:
                                    return None, index
                            else:
                                return None, index
                        strokeOrder.append(so)

                return (strokeOrder, index)

            # Try to find a partition without unknown components
            for decomposition in self.getDecompositionEntries(char, glyph):
                so, _ = getFromEntry(decomposition)
                if so:
                    return ' '.join(so)

        if (char, glyph) not in cache:
            # if there is an entry for the whole character return it
            order = self._abcGetStrokeOrderEntry(char, glyph)
            if not order:
                order = getFromDecomposition(char, glyph)
            cache[(char, glyph)] = order

        return cache[(char, glyph)]

def generate_stroke():
    abc = abcNLPChar('C')    
    db = abcSql("abcNLP.db")
    db.recreate_stroke_order()
    abc.getStrokeOrderDict(db=db)
    db.commit() 
    db.close()
    
def generate_variant():
    abc = abcNLPChar('C')    
    db = abcSql("abcNLP.db")    
    
    db.recreate_char_variant()
    dic = db.fetch_stroke_orders()
    stk = abc.getStrokeOrderSimilar(dic,  db=db)
    db.commit() 
    db.close
    
def clear_db():
    db = abcSql("abcNLP.db")
    db.recreate_stroke_order()
    db.recreate_char_variant()    
    db.close
    
def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["stroke",  "variant", "clear"]:
        print "Usage:",  sys.argv[0],  "stroke | variant"
        print " 'stroke'  to generate stroke table."
        print " 'variant' to generate variant table."
        print " 'clear'   to clear DB."        
        return
    opt = sys.argv[1]
    if opt == "stroke":
        generate_stroke()
    elif opt == "variant":
        generate_variant()
    elif opt == "clear":
        clear_db()        
    print "OK."
    
if __name__ == "__main__":
    main()
