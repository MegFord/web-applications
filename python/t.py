#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

"""
This code implements a basic, Twitter-aware tokenizer.

A tokenizer is a function that splits a string of text into words. In
Python terms, we map string and unicode objects into lists of unicode
objects.

There is not a single right way to do tokenizing. The best method
depends on the application.  This tokenizer is designed to be flexible
and this easy to adapt to new domains and tasks.  The basic logic is
this:

1. The tuple regex_strings defines a list of regular expression
   strings.

2. The regex_strings strings are put, in order, into a compiled
   regular expression object called word_re.

3. The tokenization is done by word_re.findall(s), where s is the
   user-supplied string, inside the tokenize() method of the class
   Tokenizer.

4. When instantiating Tokenizer objects, there is a single option:
   preserve_case.  By default, it is set to True. If it is set to
   False, then the tokenizer will downcase everything except for
   emoticons.

The __main__ method illustrates by tokenizing a few examples.

I've also included a Tokenizer method tokenize_random_tweet(). If the
twitter library is installed (http://code.google.com/p/python-twitter/)
and Twitter is cooperating, then it should tokenize a random
English-language tweet.
"""

__authors__ = "Christopher Potts, Meg Ford"
__copyright__ = "Copyright 2011, Christopher Potts \n Copyright 2014 Meg Ford"
__credits__ = []
__license__ = "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License: http://creativecommons.org/licenses/by-nc-sa/3.0/"
__version__ = "1.0"
__maintainer__ = "Christopher Potts"
__email__ = "See the author's website"

######################################################################

import collections
from collections import defaultdict
import csv
import htmlentitydefs
import json
import operator
import os
from os import listdir
from os.path import isfile, join
import re

######################################################################
# The following strings are components in the regular expression
# that is used for tokenizing. It's important that phone_number
# appears first in the final regex (since it can contain whitespace).
# It also could matter that tags comes after emoticons, due to the
# possibility of having text like
#
#     <:| and some text >:)
#
# Most imporatantly, the final element should always be last, since it
# does a last ditch whitespace-based tokenization of whatever is left.

# This particular element is used in a couple ways, so we define it
# with a name:
emoticon_string = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth    
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""
username_string = r"""(?:@[\w_]+)"""
hashtag_string = r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
sentence_end =  r"""(?:[\.\?!])""" 
url_string =  r"""(?:[htp]+[s]?[:/]+[a-z0-9]+[\w\d\.a-z/\?\=\&%\-]*)""" 
apo_dash = r"""(?:[a-z][a-z'\-_]+[a-z])"""       
elip_word = r"""(?:\.(?:\s*\.){1,})"""
nums = r"""(?:[+\-]?\d+[,/.:-]\d+[+\-]?)""" 
# The components of the tokenizer:
regex_strings = (
    # Phone numbers:
    r"""
    (?:
      (?:            # (international)
        \+?[01]
        [\-\s.]*
      )?            
      (?:            # (area code)
        [\(]?
        \d{3}
        [\-\s.\)]*
      )?    
      \d{3}          # exchange
      [\-\s.]*   
      \d{4}          # base
    )"""
    ,
    # Emoticons:
    emoticon_string
    ,    
    # HTML tags:
     r"""<[^>]+>"""
    ,
    # Twitter username:
    username_string
    ,
    # Twitter hashtags:
    hashtag_string
    ,
    # Last word in a sentence
    sentence_end
    ,
    #url
    url_string
    ,
    # Words with apostrophes or dashes.
    apo_dash
    ,
    # Numbers, including fractions, decimals.
    nums
    ,
    # Remaining word types:
    r"""
    (?:[\w_]+)                     
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots. 
    #| 
    #(?:\S)                         # Everything else that isn't whitespace.
    """
    )

######################################################################
# This is the core tokenizing regex:
    
word_re = re.compile(r"""(%s)""" % "|".join(regex_strings), re.VERBOSE | re.I | re.UNICODE)

# The special strings gets their own regexes so that we can tag them as needed:
emoticon_re = re.compile(regex_strings[1], re.VERBOSE | re.I | re.UNICODE)
username_re = re.compile(regex_strings[3], re.VERBOSE | re.I | re.UNICODE)
hashtag_re = re.compile(regex_strings[4], re.VERBOSE | re.I | re.UNICODE)
sentence_end_re = re.compile(regex_strings[5], re.VERBOSE | re.I | re.UNICODE)
url_re = re.compile(regex_strings[6], re.VERBOSE | re.I | re.UNICODE)
punct_re = re.compile(regex_strings[7], re.VERBOSE | re.I | re.UNICODE)
num_re = re.compile(regex_strings[9], re.VERBOSE | re.I | re.UNICODE)

# These are for regularizing HTML entities to Unicode:
html_entity_digit_re = re.compile(r"&#\d+;")
html_entity_alpha_re = re.compile(r"&\w+;")
amp = "&amp;"

######################################################################

class Tokenizer:
    def __init__(self, preserve_case=False):
        self.preserve_case = preserve_case

    def tokenize(self, s):
        """
        Argument: s -- any string or unicode object
        Value: a tokenize list of strings; conatenating this list returns the original string if preserve_case=False
        """        
        # Try to ensure unicode:
        try:
            s = unicode(s)
        except UnicodeDecodeError:
            s = str(s).encode('string_escape')
            s = unicode(s)
        # Fix HTML character entitites:
        s = self.__html2unicode(s)
        # Tokenize:
        words = word_re.findall(s)
        # Possible alter the case, but avoid changing emoticons like :D into :d:
        if not self.preserve_case:
          words = map(lambda x : self.replace_special(x), words)
        return words

    def tokenize_random_tweet(self):
        """
        If the twitter library is installed and a twitter connection
        can be established, then tokenize a random tweet.
        """
        try:
            import twitter
        except ImportError:
            print "Apologies. The random tweet functionality requires the Python twitter library: http://code.google.com/p/python-twitter/"
        from random import shuffle
        api = twitter.Api()
        tweets = api.GetPublicTimeline()
        if tweets:
            for tweet in tweets:
                if tweet.user.lang == 'en':            
                    return self.tokenize(tweet.text)
        else:
            raise Exception("Apologies. I couldn't get Twitter to give me a public English-language tweet. Perhaps try again")

    def __html2unicode(self, s):
        """
        Internal metod that seeks to replace all the HTML entities in
        s with their corresponding unicode characters.
        """
        # First the digits:
        ents = set(html_entity_digit_re.findall(s))
        if len(ents) > 0:
            for ent in ents:
                entnum = ent[2:-1]
                try:
                    entnum = int(entnum)
                    s = s.replace(ent, unichr(entnum))	
                except:
                    pass
        # Now the alpha versions:
        ents = set(html_entity_alpha_re.findall(s))
        ents = filter((lambda x : x != amp), ents)
        for ent in ents:
            entname = ent[1:-1]
            try:            
                s = s.replace(ent, unichr(htmlentitydefs.name2codepoint[entname]))
            except:
                pass                    
            s = s.replace(amp, " and ")
        return s
       
    def replace_special(self, word):
        if url_re.search(word):
            word = "url " #+ word
        elif emoticon_re.search(word):
            word = "emoticon " # +word (for testing)
        elif username_re.search(word):
            word = "username " #+ word
        elif hashtag_re.search(word):
            word = "hashtag " #+ word
            
        word = re.sub(",", " ", word)
        return word.lower()


class NGram_Helpers:   
    
    hash_dict = {}
    forum_dict = {}
    forum_three_dict = {}
    forum_two_dict = {}
    forum_one_dict = {}
    METHOD_NAME = { 'PARSE':0, 'TOKENIZE':1, 'SPLIT':2, 'COUNT':3, 'HASH':4, 'REPLACE':5 }
        
        
    def __init__(self,samples):
        self.unigrams = self.loop(samples,1,1)
        self.bigrams = self.loop(samples,2,1)
        self.trigrams = self.loop(samples,3,1)
        self.total_words = sum(self.unigrams.values())
        
    """
    loop tokenizes tweets before building ngrams
    """
    #refactor along with build_forum     
    def loop(self, samples, num, method_name):
        n_list = []
        n_dict = {}    
        for s in samples:
            n_list = self.build_tweet(s, num, method_name)
            n_list = self.build_ngrams(n_list, num)
            self.hash_dict.update(self.count_gram(n_list, self.hash_dict))
            n_dict.update(self.count_gram(n_list, n_dict))
        return  n_dict

    def build_forum(self, samples, num, method_name):
        self.clear_dicts()
        parsed = []
        if method_name == self.METHOD_NAME.get('COUNT'):
            parsed = self.build_tweet(samples, num, 2)
            return parsed
        else:
            parsed = self.build_tweet(samples, num, 5)
            self.forum_three_dict.update(self.count_gram(self.build_ngrams(parsed, num), self.forum_three_dict))
            self.forum_two_dict.update(self.count_gram(self.build_ngrams(parsed, num-1), self.forum_two_dict))
            self.forum_one_dict.update(self.count_gram(self.build_ngrams(parsed, num-2), self.forum_one_dict))  
    
    """
    Method to return individual sentences, sorted by highest probability
    """        
    def test_data(self, samples, num, method_name):
        self.clear_dicts()
        parsed_sentence = []
        for s in samples:
            parsed_sentence += self.build_tweet(samples, num, 4)
            
    def build_tweet(self, s, num, method_name):
        tokenized = []
        for i in range(0, num - 1):
            tokenized += ["*"]
        if method_name == self.METHOD_NAME.get('TOKENIZE'):
            tokenized += tok.tokenize(s)
        elif method_name == self.METHOD_NAME.get('PARSE'):
            tokenized += s.split()
        elif method_name == self.METHOD_NAME.get('SPLIT'):
            for single_line in s:
            	tokenized += single_line.split()
        tokenized += ["~STOP~"]  
        return tokenized          
    
    def clear_dicts(self):
        self.forum_three_dict.clear()
        self.forum_two_dict.clear()
        self.forum_one_dict.clear()     
        
    def build_ngrams(self, tokenized, num):
        hash_list = []   
        for i in range(len(tokenized)-(num-1)):
    	    hash_gram = "_".join(tokenized[i:i+num])
            hash_list.append(hash_gram)
            #print hash_list.count(hash_gram)
        return hash_list
        
    def count_gram(self, ngram_list, hash_gram):
        for gram in ngram_list:
            #print gram
            #re-write to use 1gram (first word) as key, store 3grams + counts as values, so 2grams can be re-constructed?
            #what are the trade-offs of storage vs. retrieval costs?
            hash_gram[gram] = hash_gram.get(gram, 0) + 1
            #print hash_gram.get(gram)
        return hash_gram

    def pr_gram(self, r_gram_dict, string_input):
        count_list = []
        special_case = []
        for i in string_input:
           if str(i).find("*") >= 0 and i in r_gram_dict:
              special_case.append(r_gram_dict.get(i))
           elif not str(i).find('*') >= 0 and i in r_gram_dict:
              count_list.append(r_gram_dict.get(i))
           else:
              count_list.append(0.0) 
        return special_case, count_list

    def probability(self, count_3gram, count_2gram,count_1gram, l1, l2, l3, l4, total_words):
        feq = [self.get_ratio(x, y, z, l1, l2, l3, l4, total_words) for x, y, z in zip(count_3gram, count_2gram, count_1gram)]
        if len(feq) > 0:
            return reduce(operator.imul, feq)
        else:
            return l4 * 1/(2 * total_words)
        
    def start_probability(self, count_3gram, count_2gram, l1, l4, total_words):
        feq = [self.get_start_ratio(x, y, l1, l4, total_words) for x, y in zip(count_3gram[:len(count_2gram)], count_2gram)]
        if len(feq) > 0:
            return reduce(operator.imul, feq)
        else:
            return l4 * 1/(2 * total_words)
        
    def get_start_ratio(self, x, y, l1, l4, total_words):
        p_3gram = 0        
        if(y != 0):
            p_3gram = x/y
        return (l1 * p_3gram) + (l4 * 1/(2 * total_words))     

    # smoothing so we don't end up with div by zero
    def get_ratio(self, x, y, z, l1, l2, l3, l4, total_words):
        p_3gram = 0
        p_2gram = 0
        p_1gram = 0
        if(y != 0):
            p_3gram = x/y
        if(z != 0):
            p_2gram = y/z       
            p_1gram = z/total_words
        return (l1 * p_3gram) + (l2 * p_2gram) + (l3 * p_1gram) + (l4 * 1/(2 * total_words))       
            
class File_Utils:
    
    def crawl_directory(self, root_dir="~/Tweets"):
        file_group = []
        tweet_path = os.path.expanduser(root_dir)
        file_group = [f for f in os.listdir(tweet_path) if os.path.isfile(os.path.join(tweet_path, f))] 
        return file_group
     
    def create_samples(self, file_group, root_dir="~/Tweets"):
        samples = [] 
        tweet_path = os.path.expanduser(root_dir)
        for tweet_file in file_group:
            samples.extend(open(os.path.join(tweet_path, tweet_file)))
        return samples
        
    def gather(self, samples, root_dir="~/Tweets"):
        tweet_path = os.path.expanduser(root_dir)
        for tweet_file in samples:
            samples = []
            t = ""
            samples.extend(open(os.path.join(tweet_path, tweet_file)))
            for s in samples:
                t += self.clean_posts(s)
            with open(os.path.join(tweet_path, tweet_file), 'w') as outfile:
                outfile.write(t)
                
    def clean_posts(self, word):       
        word = re.sub(r'_________________________', "", word)
        return word
        
    def remove_punct(self, samples):
        temp = []
        for s in samples:
            if s != '\n':
                if sentence_end_re.search(s):
                    temp += re.split(sentence_end_re, s)
                else:
                    temp += [s]            
        return temp
        
    def write_json(self, term_doc_matrix, file_name, root_dir='~/forumPost'):
        tweet_path = os.path.expanduser(root_dir)
        with open(os.path.join(tweet_path, file_name), 'w') as outfile:
            h = json.JSONEncoder().encode(term_doc_matrix)
            json.dump(h, outfile, ensure_ascii=False)
        
    def read_json(self, file_name, root_dir="~/forumPost"):        
        tweet_path = os.path.expanduser(root_dir)
        with open(os.path.join(tweet_path, file_name)) as f:
            d = json.load(f)
            d = json.JSONDecoder().decode(d)
        return d
        
    def write_prob(self, sentence, file_name, root_dir='~/forumPost'):
        write_path = os.path.expanduser(root_dir)
        writer = csv.writer(open(os.path.join(write_path, file_name), 'wb'))
        #sort ordered dict highest to lowest probability
        items = sentence.items()
        items.reverse()
        for key, value in sentence.items():
            writer.writerow([key, value])

###############################################################################

if __name__ == '__main__':
    tok = Tokenizer(preserve_case=False)
    fi = File_Utils()

    samples = []
    posts = []
    temp = []
    prob = collections.OrderedDict()
    L1 = 0.85
    L2 = 0.1
    L3 = 0.04
    L4 = 0.01
    st_pr = 0.0
    training_dir = "~/forums"
    out_path = '~/forumPost'
    test_path = '~/testData'
    """
    #clean data  
    file_group = fi.crawl_directory("~/forum1")
    fi.gather(file_group,"~/forum1")
    file_group2 = fi.crawl_directory("~/forum2")
    fi.gather(file_group2,"~/forum2")
    forum_samples = fi.crawl_directory(test_path)
    fi.gather(forum_samples, test_path)

    #Section to create training data
    training_dir = "~/forums"
    file_group = fi.crawl_directory("~/forum1")
    file_group2 = fi.crawl_directory("~/forum2")
   
    samples += fi.create_samples(file_group,"~/forum1")
    samples += fi.create_samples(file_group2,"~/forum2") 
    
    samples = fi.remove_punct(samples)
    #print samples
    n = NGram_Helpers(samples)
    fi.write_json(n.trigrams, "threeGram.json")
    fi.write_json(n.bigrams, "twoGram.json")
    fi.write_json(n.unigrams, "oneGram.json")
    #end section to create training data
    """
    #section to find prob of individual sentences from test data
    lineThreeGram = fi.read_json("threeGram.json")
    lineTwoGram = fi.read_json("twoGram.json")
    lineOneGram = fi.read_json("oneGram.json") 

    forum_samples = fi.crawl_directory(test_path)
    posts += fi.create_samples(forum_samples, test_path)
    #print posts
    forum_samples = fi.remove_punct(posts)
    n = NGram_Helpers(forum_samples)
    for f in forum_samples:
        ngram_base = n.build_tweet(f, 3, 1)
        tri_gram = n.build_ngrams(ngram_base, 3)
        duo_gram = n.build_ngrams(ngram_base, 2)
        uno_gram = n.build_ngrams(ngram_base, 1)
        length = sum(lineOneGram.values())

        count_3_list = n.pr_gram(lineThreeGram, tri_gram)
        count_2_list = n.pr_gram(lineTwoGram, duo_gram[:len(tri_gram)])
        count_1_list = n.pr_gram(lineOneGram, uno_gram[:len(tri_gram)])
        if len(count_3_list[0]) > 0:
            st_pr = n.start_probability(count_3_list[0], count_2_list[0], L1, L4, length)
        if len(count_3_list[1]) > 0:
            pr = n.probability(count_3_list[1], count_2_list[1], count_1_list[1], L1, L2, L3, L4, length)
        if st_pr != 0.0 and pr != 0.0:
            pr = st_pr * pr
        prob[f] = pr
    fi.write_prob(prob,"probability.csv")
    #end test data section
   
    """
    fi.write_json(tri_gram, "forumThreeGram.json")
    fi.write_json(duo_gram, "forumTwoGram.json")
    fi.write_json(uno_gram, "forumOneGram.json")
    """
    #now test the test
    """
    lineThreeGram = fi.read_json("threeGram.json")
    lineOneGram = fi.read_json("oneGram.json") 
    lineTwoGram = fi.read_json("twoGram.json") 
    inputTwoGram = fi.read_json("forumTwoGram.json")
    inputOneGram = fi.read_json("forumOneGram.json")  
    inputThreeGram = fi.read_json("forumThreeGram.json") 
    """
    
    #ask for user input
    
    #train with 90% of forum data test with 10% of forum data what is the average probability of a sentence
    # output 50 probabilities and save to excel
    
    #test with tweets and find average
    # output 50 probabilities and save to excel

    
