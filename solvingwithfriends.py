#!/usr/bin/env python


import sys
import re
from math import log
import string
import readline
import code

class HistConsole(code.InteractiveConsole):
   def __init__(self, histfile):
      self.histfile=histfile
      code.InteractiveConsole.__init__(self, None, histfile)
      self.init_history()
   def init_history(self):
      readline.clear_history()
      try:
         readline.read_history_file(self.histfile)
      except IOError: pass
   def save_history(self):
      readline.write_history_file(self.histfile)
      
wordlist=set()
letter_freq = {}


def init():
    build_wordlist()
    global letter_freq
    freq = [8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406, 6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074]
    letter_freq = dict(zip(string.ascii_lowercase, freq))

def build_wordlist():
   global wordlist
   wordlist = open("enable1.txt").read().splitlines()
        

def get_best_letter_guesses(words):
    best_guesses = []
    for letter in string.ascii_lowercase:
        score = score_guess(words, letter)
        #print "Score of letter %s is %f" % (letter, score)
        if not best_guesses or score > best_guesses[0][0]:
            best_guesses = [(score, letter)]
        elif score == best_guesses[0][0]:
            best_guesses.append((score, letter))
    return (sorted([i[1] for i in best_guesses], (lambda i,j: cmp(letter_freq[i], letter_freq[j]))))[::-1]

def get_matches(word_pattern, used_letters):
   "Given a word pattern ('?ots'), return list of all words that match it"
   remaining_letters="".join(set([i for i in string.ascii_lowercase if i not in used_letters and i not in word_pattern]))
   regex=("^%s$" % word_pattern).replace('?',"[%s]" % remaining_letters)
   regex = re.compile(regex)
   return set([w for w in wordlist if regex.match(w)])

def score_guess(possible_words, letter):
   "Give the entropy gain of making the guess 'letter'"
   remaining_words = len([i for i in possible_words if letter in i])
   #print "For guess of %s, remaining_words=%s" % (letter, remaining_words)
   if remaining_words == 0:
      return -1e9999
   p=remaining_words/float(len(possible_words)) + 0.0001
   q=1-p + 0.0001
   entropy_after = -p*log(p, 2) - q*log(q, 2)
   return entropy_after




if __name__ == "__main__":
   init()
   pattern_console=HistConsole("pattern_hist")
   letters_console=HistConsole("letters_hist")
   used_letters = ""
   while True:
      pattern_console=HistConsole("pattern_hist")
      pattern=pattern_console.raw_input("Enter word pattern (like '?ots') > ").strip()
      pattern_console.save_history()
      pattern = "".join([i for i in pattern if i.isalpha() or i == '?']).lower()
      letters_console=HistConsole("letters_hist")
      readline.insert_text(used_letters)
      used_letters = letters_console.raw_input("Enter the wrong letters you've guessed > ").strip()
      letters_console.save_history()
      used_letters = "".join(set([i for i in used_letters if i.isalpha()])).lower()
      matches = get_matches(pattern, used_letters)
      print "There are %d possible words:" % len(matches)
      if len(matches) <= 20:
        print matches
      if len(matches) == 1:
        print "The word is: %s" % list(matches)[0]
      else:
        best_guess = get_best_letter_guesses(matches)
        print "Your best guess is the letter: %s" % best_guess
      