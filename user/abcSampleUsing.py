# -*- coding: utf8 -*-
import abcChineseChar as A

def use_full_db():
    
    print "\n+ Test using Full DB\n" 
    word = u'陈水扁'

    abc = A.abcChineseChar()
    # Test fetching the Character
    print "=" * 20
    ch_test = u'锦'
    print "Test for %s:" % ch_test
    print "=" * 20
    ch_list = abc.getHxCharacters(ch_test)
    for r in ch_list:
        print r

    # Test fetching the Word
    print "=" * 20
    print "Test for %s:" % word
    print "=" * 20
    for word in abc.getHxWords(word,  maxnum=15):
        print word

def use_limit_db():

    print "\n+ Test using Limit DB\n" 
    word = u'陈水扁'

    abc = A.abcChineseChar("abcChineseLimit.db")
    # Test fetching the Character
    print "=" * 20
    ch_test = u'锦'
    print "Test for %s:" % ch_test
    print "=" * 20
    ch_list = abc.getHxCharacters(ch_test)
    for r in ch_list:
        print r

    # Test fetching the Word
    print "=" * 20
    print "Test for %s:" % word
    print "=" * 20
    for word in abc.getHxWords(word,  maxnum=15):
        print word



def main():
    use_full_db()
    use_limit_db()


if __name__ == "__main__":
    main()
