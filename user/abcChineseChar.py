# -*- coding: utf8 -*-
import os
import sqlite3
import itertools

def insertionSort(array):
    i = 1
    while i < len(array):
        j = i
        while j > 0 and array[j][0] < array[j-1][0]:
            array[j-1], array[j] = array[j], array[j-1]
            j = j - 1
        i = i + 1

def rescoreSorted(array, start=0):
    i = 0
    score = start
    newarray=[]
    while i < len(array):
        if  i > 0 and array[i][0] == array[i-1][0]:
            score = score - 1
        newarray.append((score,  array[i][1]))
        score = score + 1
        i = i + 1
    return newarray

def scoreCount(array):
    i = 0
    count = 0
    while i < len(array):
        count = count + array[i][0]
        i = i + 1
    return count

class abcChineseChar:
    '''
        BH = Bi Hua (Stroke)
        TY = Tong Yin (Reading)
        YT = Yi Ti (other writing form)
        DP = Decompositions
        DE = Extended Decompositions
    '''
    TYPES = ['BH',  'TY',  'YT',  'DP',  'DE']
    TYPE2START = {'BH':1, 'TY': 0,  'YT':2,  'DP':0,  'DE':0}
    LONGWORD = 4
    CHARVARNUM = 3
    def __init__(self, filename='abcChinese.db'):
        if not os.path.exists(filename):
            raise exception.NoInformationError(
                " can't find the db file %s" % filename)

        self.conn = sqlite3.connect(filename)
        self.conn.row_factory = sqlite3.Row
        self.cache = {}

    def close(self):

        self.conn.cursor().close()
        self.conn.close()

    def getDbVariantChar(self,  char):
        c = self.conn.cursor()
        q = "SELECT Variant, Type, Score FROM AllinoneCharacterVariant WHERE ChineseCharacter = ?"
        rows = c.execute(q, (char, )).fetchall()
        return rows

    def getCacheVariantChar(self,  char):
        try:
            memo = self.cache[char]
        except:
            memo = self.cache[char] = {}
            rows = self.getDbVariantChar(char)
            for row in rows:
                typelist = memo.setdefault(row[1], [])
                typelist.append((row[2], row[0]))
            for key in memo.keys():
                insertionSort(memo[key])
                # tuple can't modify inside, have to new a tuple with new score
                memo[key] = rescoreSorted(memo[key], self.TYPE2START[key])
        return memo

    def getVariantChar(self, char, types, maxnum=-1):
        memo = self.getCacheVariantChar(char)
        alist = []
        for type in types:
            if type in memo.keys():
                alist.extend(memo[type])
        insertionSort(alist)
        if maxnum > 0 and maxnum < len(alist):
            alist = alist[0 : maxnum+1]
        return alist

    def getAllCharVariant(self, word, types, chars_vars):
        maxnum=-1
        if len(word) > self.LONGWORD:
            maxnum=self.CHARVARNUM
        chars_list = []
        for char in word:
            x = chars_vars.setdefault(char, [])
            if not x:
                char_vars = self.getVariantChar(char, types, maxnum)
                if not char_vars:
                    x = [(0, char)]
                else:
                    x = char_vars
            chars_list.append(x)
        return chars_list

    def getHxCharacters(self, char, includes=[],  excludes=['DE', 'BH'], maxnum=-1):

        if includes and excludes:
            print " input parameter can't have includes and excludes at same time"
            return

        if not includes and not excludes:
            types = self.TYPES
        elif includes:
            types = [type for type in self.TYPES if type in includes]
        elif excludes:
            types = [type for type in self.TYPES if type not in excludes]

        alist = self.getVariantChar(char, types, maxnum=maxnum)
        return [ x[1] for x in alist ]

    def getHxWords(self, word, includes=[],  excludes=['DE', 'BH'], maxnum=-1):
        chars_vars={}

        if includes and excludes:
            print " input parameter can't have includes and excludes at same time"
            return

        if len(word) > self.LONGWORD:
            print " input parameter string exceed supported max length %d", self.LONGWORD
            return

        if not includes and not excludes:
            types = self.TYPES
        elif includes:
            types = [type for type in self.TYPES if type in includes]
        elif excludes:
            types = [type for type in self.TYPES if type not in excludes]

        chars_list = self.getAllCharVariant(word, types, chars_vars)
        combines = list(itertools.product(*chars_list))
        sorted = []
        for combine in combines:
            sorted.append((scoreCount(combine), combine))
        insertionSort(sorted)

        count = 0
        for score, combine in sorted:
            if maxnum >= 0 and count >= maxnum:
                break
            fulltext = ""
            for item in combine:
                if len(item[1]) > 1:
                    fulltext += '<' + item[1].replace(" ", "") + '>'
                else:
                    fulltext += item[1]
            count += 1
            yield fulltext


