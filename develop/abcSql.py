# -*- coding: utf8 -*-
import collections
import logging
import math
import os
import random
import re
import sqlite3
import time
import types

class abcSql:
    """Database functions to support a Cobe brain. This is not meant
    to be used from outside."""
    def __init__(self, filename):
        if not os.path.exists(filename):
            self.init(filename)

        self.conn = sqlite3.connect(filename)
        self.conn.row_factory = sqlite3.Row

    def commit(self):
        ret = self.conn.commit()
        return ret
        
    def close(self):
        
        self.conn.cursor().close()
        self.conn.close()
    
    def recreate_stroke_order(self):
        c = self.conn.cursor()
        c.execute("DROP TABLE IF EXISTS FullStrokeOrder")
        self.commit() 
        
        c.execute("""
    CREATE TABLE FullStrokeOrder (
  ChineseCharacter VARCHAR(1) NOT NULL,  
  IDC VARCHAR(1) NOT NULL, 
  StrokeOrder VARCHAR(1) NOT NULL, 
  PRIMARY KEY (ChineseCharacter)) """)        
        self.commit() 

    def recreate_char_variant(self):
        c = self.conn.cursor()
        c.execute("DROP TABLE IF EXISTS FullCharacterVariant")
        self.commit() 
        
        c.execute("""
CREATE TABLE FullCharacterVariant (
	ChineseCharacter VARCHAR(1) NOT NULL, 
	Variant VARCHAR(1) NOT NULL, 
	Type VARCHAR(1) NOT NULL, 
    Score INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY ("ChineseCharacter", "Variant", "Type"))""")

        c.execute("""
CREATE INDEX FullCharacterVariant__ChineseCharacter ON FullCharacterVariant (ChineseCharacter)
        """)        
        self.commit() 


    def recreate_tongyin_variant(self):
        c = self.conn.cursor()
        c.execute("DROP TABLE IF EXISTS TongyinCharacterVariant")
        self.commit() 
        
        c.execute("""
CREATE TABLE TongyinCharacterVariant (
	ChineseCharacter VARCHAR(1) NOT NULL, 
	Variant VARCHAR(1) NOT NULL, 
	Type VARCHAR(1) NOT NULL, 
    Score INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY ("ChineseCharacter", "Variant", "Type"))""")

        c.execute("""
CREATE INDEX TongyinCharacterVariant__ChineseCharacter ON TongyinCharacterVariant (ChineseCharacter)
        """)        
        self.commit() 
        
    def recreate_default_variant(self):
        c = self.conn.cursor()
        c.execute("DROP TABLE IF EXISTS DefaultCharacterVariant")
        self.commit() 
        
        c.execute("""
CREATE TABLE DefaultCharacterVariant (
	ChineseCharacter VARCHAR(1) NOT NULL, 
	Variant VARCHAR(1) NOT NULL, 
	Type VARCHAR(1) NOT NULL, 
    Score INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY ("ChineseCharacter", "Variant", "Type"))""")

        c.execute("""
CREATE INDEX DefaultCharacterVariant__ChineseCharacter ON DefaultCharacterVariant (ChineseCharacter)
        """)        
        self.commit() 

    def recreate_decomp_variant(self):
        c = self.conn.cursor()
        c.execute("DROP TABLE IF EXISTS DecompCharacterVariant")
        self.commit() 
        
        c.execute("""
CREATE TABLE DecompCharacterVariant (
	ChineseCharacter VARCHAR(1) NOT NULL, 
	Variant VARCHAR(1) NOT NULL, 
	Type VARCHAR(1) NOT NULL, 
    Score INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY ("ChineseCharacter", "Variant", "Type"))""")

        c.execute("""
CREATE INDEX DecompCharacterVariant__ChineseCharacter ON DecompCharacterVariant (ChineseCharacter)
        """)        
        self.commit() 

    def recreate_decompext_variant(self):
        c = self.conn.cursor()
        c.execute("DROP TABLE IF EXISTS DecompextCharacterVariant")
        self.commit() 
        
        c.execute("""
CREATE TABLE DecompextCharacterVariant (
	ChineseCharacter VARCHAR(1) NOT NULL, 
	Variant VARCHAR(1) NOT NULL, 
	Type VARCHAR(1) NOT NULL, 
    Score INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY ("ChineseCharacter", "Variant", "Type"))""")

        c.execute("""
CREATE INDEX DecompextCharacterVariant__ChineseCharacter ON DecompextCharacterVariant (ChineseCharacter)
        """)        
        self.commit() 
        
    def insert_stroke_order(self,  word, idc, order):

        c = self.conn.cursor()
        q = "INSERT INTO FullStrokeOrder (ChineseCharacter,IDC, StrokeOrder) VALUES (?, ?, ?)"
        c.execute(q, (word, idc, order))
        # will not commit it for performance reason
        return

    def fetch_stroke_order(self, word):

        c = self.conn.cursor()
        q = "SELECT StrokeOrder FROM FullStrokeOrder WHERE ChineseCharacter = ?"
        row = c.execute(q, (word, )).fetchone()
        if row:
            return row[0]

    def fetch_stroke_orders(self):

        c = self.conn.cursor()
        q = "SELECT ChineseCharacter, IDC, StrokeOrder FROM FullStrokeOrder"
        rows = c.execute(q, ()).fetchall()

        return dict((row[0], (row[1], row[2].split("|"))) for row in rows)

    def insert_char_variant(self,  word, other, score):
        c = self.conn.cursor()
        q = "INSERT INTO FullCharacterVariant (ChineseCharacter, Variant, Type, Score) VALUES (?, ?, ?, ?)"
        c.execute(q, (word, other, "BH", score))
        # will not commit it for performance reason
        return

    def insert_tongyin_char_variant(self,  word, other, score):
        c = self.conn.cursor()
        q = "INSERT INTO TongyinCharacterVariant (ChineseCharacter, Variant, Type, Score) VALUES (?, ?, ?, ?)"
        c.execute(q, (word, other, "TY", score))
        # will not commit it for performance reason
        return

    def insert_default_char_variant(self,  word, other, score):
        c = self.conn.cursor()
        q = "INSERT INTO DefaultCharacterVariant (ChineseCharacter, Variant, Type, Score) VALUES (?, ?, ?, ?)"
        # YT = Yi4 Ti3
        c.execute(q, (word, other, "YT", score))
        # will not commit it for performance reason
        return

    def insert_decomp_char_variant(self,  word, other, score):
        c = self.conn.cursor()
        q = "INSERT INTO DecompCharacterVariant (ChineseCharacter, Variant, Type, Score) VALUES (?, ?, ?, ?)"
        c.execute(q, (word, other, "DP", score))
        # will not commit it for performance reason
        return

    def insert_decompext_char_variant(self,  word, other, score):
        c = self.conn.cursor()
        q = "INSERT INTO DecompextCharacterVariant (ChineseCharacter, Variant, Type, Score) VALUES (?, ?, ?, ?)"
        c.execute(q, (word, other, "DE", score))
        # will not commit it for performance reason
        
    def fetch_char_variants(self, word):

        c = self.conn.cursor()
        q = "SELECT Variant, Type, Score FROM FullCharacterVariant WHERE ChineseCharacter = ?"
        rows = c.execute(q, (word, )).fetchall()
        return rows
    
    
    def init(self, filename):

        self.conn = sqlite3.connect(filename)
        c = self.conn.cursor()
        c.execute("""
    CREATE TABLE FullStrokeOrder (
  ChineseCharacter VARCHAR(1) NOT NULL,  
  IDC VARCHAR(1) NOT NULL,   
  StrokeOrder VARCHAR(1) NOT NULL, 
  PRIMARY KEY (ChineseCharacter)) """)

        c.execute("""
CREATE TABLE FullCharacterVariant (
	ChineseCharacter VARCHAR(1) NOT NULL, 
	Variant VARCHAR(1) NOT NULL, 
	Type VARCHAR(1) NOT NULL, 
    Score INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY ("ChineseCharacter", "Variant", "Type"))""")

        c.execute("""
CREATE INDEX FullCharacterVariant__ChineseCharacter ON FullCharacterVariant (ChineseCharacter)
 """)
        self.commit()
        self.close()

def main():
    xxx = abcSql("abc.db")
#    xxx.insert_stroke_order(u"爱", "HH|HH|AADE")    
#    row = xxx.fetch_stroke_order(u"爱")
#    print row
#    xxx.insert_char_variant(u"爱",  u"恨", 30)
#    xxx.insert_char_variant(u"爱",  u"鬼", 40)    
#    row = xxx.fetch_char_variants(u"爱")
#    print row
    
    rows = xxx.fetch_stroke_orders()
    for row in rows:
        print row
        print "==="
if __name__ == "__main__":
    main()
