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
from abcNLP import *

class abcExtendChar():
    EXTMAP = {
                 u'彡': [u'三'],
                 u'三': [u'彡'], 
              }
    
def generate_tongyin_variant(maxnum=500000):
    abc = abcNLPChar('C')    
    db = abcSql("abcNLP.db")    
    db.recreate_tongyin_variant()
    
    count = 0
    for src in abc.getDomainCharacterIterator():
        if (count >= maxnum):
            print "Max number %d reached!" % count
            break
        try:
            sc = abc.getStrokeCount(src)
            py = abc.getReadingForCharacter(src, 'Pinyin')
            # sorry, only process one Pinyin of each of char
            tongyins = abc.getCharactersForReading(py[0],  'Pinyin')            
        except:
            continue 
        # default, the Pinyin is a variant
        # print "%s --> %s (0)" % (src,  py[0])          
        distances = [ (500, ""),  (500, ""), (500, "")] 
        for ty in tongyins:
            if ty == src:
                continue
            try:
                # distance = abs(abc.getStrokeCount(ty) - sc) ; use difference
                distance = abc.getStrokeCount(ty) # the simple character is better
            except:
                continue
            distances.pop()
            distances.append((distance,  ty))
            insertionSort(distances)
        for distance in distances:
            if distance[0] == 500:
                break
            #print "%s --> %s (%d)" % (src,  distance[1],  distance[0])  
            db.insert_tongyin_char_variant(src,  distance[1],  distance[0])
        count = count + 1

    db.commit() 
    db.close
    
#
# NOTE: include itself.
def get_abc_extend_char(abc, ch):
    work=[]
    total=[]
    work.append(ch)
    total.append(ch)

    while True:
        newwork = []
        for wk in work:
            try:
                rows = abc.getAllCharacterVariants(wk)
            except:
                continue
            for row in rows: 
                if row[0] not in total:
                    newwork.append(row[0])
                    total.append(row[0])
        if newwork:
            work = newwork
        else:
            break
    # Add manual settings
    if ch in abcExtendChar.EXTMAP:
        for ext in abcExtendChar.EXTMAP[ch]:
            if ext in total:
                print "get_extend_char for %s, EXTMAP has duplicate %s" % (ch, ext)
            else:
                total.append(ext)
    return total
    
def generate_default_variant(maxnum=500000):
    abc = abcNLPChar('C')    
    db = abcSql("abcNLP.db")    
    db.recreate_default_variant()
    
    count = 0
    for src in abc.getDomainCharacterIterator():
        if (count >= maxnum):
            print "Max number %d reached!" % count
            break
        try:
            exts = get_abc_extend_char(abc,  src)            
        except:
            continue            
        for ext in exts:
            if ext == src:
                continue
            #print "%s --> %s " % (src,  ext)  
            db.insert_default_char_variant(src,  ext,  0)
            count = count + 1
    db.commit() 
    db.close

def generate_decomp_variant(maxnum=500000, depth=1):
    abc = abcNLPChar('C')    
    db = abcSql("abcNLP.db")    
    if depth == 0:
        db.recreate_decomp_variant()
    elif depth > 0:
        db.recreate_decompext_variant()
        
    count = 0    
    for src in abc.getDomainCharacterIterator(): 
        #  [u'待',  u'法', u'⾽']: 

        if (count >= maxnum):
            print "Max number %d reached!" % count
            break
            
        try:            
            decomps = abc.getDecompositionEntries(src)
        except:          
            continue
            
        level = depth
        decomp = []
        if decomps:
            decomp = decomps[0]            
        if decomp:
            idc = decomp[0]
            if not abc.isBinaryIDSOperator(idc) and not abc.isTrinaryIDSOperator(idc):
                raise exception.NoInformationError("IDC of char %s is error: %s" % (char, idc)) 
            if idc == u'⿰'and type(decomp[1]) == type(()) and type(decomp[2]) == type(()):
                a = decomp[1][0];
                b = decomp[2][0];
                if (a == u'？' or b == u'？'):
                    continue  
                ao,  bo = a,  b                    
                if level > 1: 
                    a = get_abc_extend_char(abc,  a).pop()
                    if ao != a:
                        level = level - 1
                if level > 1:
                    b = get_abc_extend_char(abc,  b).pop()
                    if bo != b:
                        level = level - 1
                # for the reason of level, b may hasn't been changed
                if ao == bo and ao != a:
                    b = a
                chg = not (ao == a and bo == b)
                #print "%s --> <%s%s> %d" % (src,  a,  b,  chg)  
                if depth == 0:
                    db.insert_decomp_char_variant(src,  a+b,  0)
                elif depth > 0:
                    db.insert_decompext_char_variant(src,  a+b,  0)
                count = count + 1
            elif idc == u'⿲' and type(decomp[1]) == type(()) and type(decomp[2]) == type(()) \
                and type(decomp[3]) == type(()):
                a = decomp[1][0];
                b = decomp[2][0];
                c = decomp[3][0];   
                if (a == u'？' or b == u'？' or c == u'？'):
                    continue               
                ao,  bo, co = a,  b,  c                    
                if level > 1: 
                    a = get_abc_extend_char(abc,  a).pop()
                    if ao != a:
                        level = level - 1
                if level > 1:
                    b = get_abc_extend_char(abc,  b).pop()
                    if bo != b:
                        level = level - 1
                if level > 1:
                    b = get_abc_extend_char(abc,  b).pop()
                    if bo != b:
                        level = level - 1                        
                # for the reason of level, b, c may hasn't been changed
                if ao == bo and ao != a:
                    b = a
                if ao == co and ao != a:
                    c = a
                if bo == co and bo != b:
                    c = b
                chg = not (ao == a and bo == b and co == c)
                #print "%s --> <%s%s%s> %d" % (src,  a,  b,  c,  chg)  
                if depth == 0:
                    db.insert_decomp_char_variant(src,  a+b+c,  0)
                elif depth > 0:
                    db.insert_decompext_char_variant(src,  a+b+c,  0)
                count = count + 1
    db.commit() 
    db.close

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["tongyin",  "default", "decomp", "decompext"]:
        print "Usage:",  sys.argv[0],  "tongyin | default | decomp | decompext "
        print " 'tongyin'  to generate tongyin variant table."
        print " 'default' to generate default variant table (same char with deferent form)"
        print " 'decomp' to generate decomp variant table (split char into 2 or 3 parts)"        
        print " 'decompext'  similar to decomp, but each part may also be replaced by variant"        
        return

    opt = sys.argv[1]
    if opt == "tongyin":
        generate_tongyin_variant()
    elif opt == "default":
        generate_default_variant()
    elif opt == "decomp":
        generate_decomp_variant(depth=0)
    elif opt == "decompext":
        # can set depth=2 if needed
        generate_decomp_variant(depth=1)         
    print "OK."

            
if __name__ == "__main__":
    main()
