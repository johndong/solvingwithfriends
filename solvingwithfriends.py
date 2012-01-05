#!/usr/bin/env python


import sys
import re
from math import log
import string
import readline
import code
import shove
from multiprocessing import Pool


strike_cache = shove.Shove("file://strikes.db")


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
    global letter_freq
    freq = [8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406, 6.749, 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074]
    letter_freq = dict(zip(string.ascii_lowercase, freq))
    build_wordlist()
def cache_word(word):
   return (word, expected_strikes_left(word))
def build_wordlist():
   global wordlist
   wordlist = [i for i in open("enable1.txt").read().splitlines() if len(i) > 3 and len(i) < 9]
   if False: # Update cache
     p = Pool(processes=40)
     p.map(cache_word, wordlist)   
   
   
   

def get_best_letter_guesses(strategy, words, word_pattern, used_letters):
    best_guesses = []
    for letter in string.ascii_lowercase:
        if letter in word_pattern: continue
        score = strategy(words, letter)
        #print "Score of letter %s is %f" % (letter, score)
        if not best_guesses or score > best_guesses[0][0]:
            best_guesses = [(score, letter)]
        elif score == best_guesses[0][0]:
            best_guesses.append((score, letter))
    return (sorted([i[1] for i in best_guesses], (lambda i,j: cmp(letter_freq[i], letter_freq[j]))))[::-1]

def get_expected_strikes_left(possible_words):
    return reduce(lambda acc,val: acc + (1.0/len(possible_words)) * val, map(expected_strikes_left, possible_words), 0)

def get_matches(word_pattern, used_letters):
   "Given a word pattern ('?ots'), return list of all words that match it"
   remaining_letters="".join(set([i for i in string.ascii_lowercase if i not in used_letters and i not in word_pattern]))
   regex=("^%s$" % word_pattern).replace('?',"[%s]" % remaining_letters)
   regex = re.compile(regex)
   return set([w for w in wordlist if regex.match(w) and \
       get_last_vowel_index(w) <= get_last_vowel_index(word_pattern)])

def score_guess_minguesses(possible_words, letter):
   "Give the entropy gain of making the guess 'letter'"
   remaining_words = len([i for i in possible_words if letter in i])
   #print "For guess of %s, remaining_words=%s" % (letter, remaining_words)
   if remaining_words == 0:
      return -1e9999
   p=remaining_words/float(len(possible_words)) + 0.0001
   q=1-p + 0.0001
   entropy_after = -p*log(p, 2) - q*log(q, 2)
   return entropy_after
   
def score_guess_maxlife(possible_words, letter):
   remaining_words = [i for i in possible_words if letter in i]
   return len(remaining_words)

def get_last_vowel_index(word):
    vowels = "aeiou"
    idx=max([word.rfind(i) for i in vowels])
    if idx >= 0:
      return idx
    return None
   
def get_last_vowel(word):
    last_vowel_index = get_last_vowel_index(word)
    if last_vowel_index is not None: return word[last_vowel_index]
    return None

class HangingGame(object):
   def __init__(self, word):
      self.guesses=set()
      last_vowel = get_last_vowel(word)
      if last_vowel is not None:
         self.guesses.add(last_vowel)
      self.word=word
   def __str__(self):
      return "".join(map(lambda i: i if i in self.guesses else "?", self.word))
   def guess_letter(self, letter):
      self.guesses.add(letter)
   def num_strikes(self):
      return len(self.get_wrong_letters())
   def get_wrong_letters(self):
      return set([i for i in self.guesses if i not in self.word])
   def solved(self):
      return "?" not in str(self)
   def clone(self):
      newgame = HangingGame(self.word)
      newgame.guesses = set(self.guesses)

def expected_strikes_left(word):
   '''
   Simulates trying to guess the word.
   
   Returns number of strikes you'd have left by following get_best_letter_guesses()
   '''
   if word in strike_cache:
      return strike_cache[word]
   print >>sys.stderr, "Warning: Cache not available for", word
   game = HangingGame(word)
   while not game.solved():
      matches = get_matches(str(game), game.get_wrong_letters())
      #print matches
      best_guess = get_best_letter_guesses(default_strategy, matches, str(game), game.get_wrong_letters())[0]
      #print "For word", game, "guessing", best_guess, "yielding", game.guess_letter(best_guess)
      #print "(Used guesses: %s)" % "".join(game.get_wrong_letters())
   num_strikes_allowed = 4 + (8 - len(game.word))
   result=num_strikes_allowed - game.num_strikes()
   try:
     strike_cache[word] = result
   except Exception as e:
     print "Error storing cache!", repr(e)
     return expected_strikes_left(word)
   return result


def get_best_word_list(letter_list):
   best_words = []
   for word in wordlist:
      if not can_form_word(letter_list, word):
         continue
      num_strikes_left = expected_strikes_left(word)
      if len(best_words) == 0:
         best_words = [(num_strikes_left, word)]
      else:
         if num_strikes_left == best_words[0][0]:
            best_words.append((num_strikes_left, word))
         elif num_strikes_left < best_words[0][0]:
            best_words = [(num_strikes_left, word)]
   return best_words

def can_form_word(letter_list, word):
   for letter in word:
      if letter_list.count(letter) < word.count(letter):
         return False
   return True
   
def probability_of_strike(word_list, letter):
   after = [i for i in word_list if letter not in i]
   before = word_list
   p = len(after) / float(len(before))
   return p

default_strategy=score_guess_maxlife

if __name__ == "__main__":
   init()
   pattern_console=HistConsole("pattern_hist")
   letters_console=HistConsole("letters_hist")
   used_letters = ""
   mode = "solve"
   while True:
      if mode == "solve":
         pattern_console=HistConsole("pattern_hist")
         pattern=pattern_console.raw_input("Enter word pattern (like '?ots') > ").strip()
         if '!' in pattern:
            mode = 'create'
            continue
         pattern_console.save_history()
         pattern = "".join([i for i in pattern if i.isalpha() or i == '?']).lower()
         letters_console=HistConsole("letters_hist")
         readline.insert_text(used_letters)
         used_letters = letters_console.raw_input("Enter the wrong letters you've guessed > ").strip()
         letters_console.save_history()
         used_letters = "".join(set([i for i in used_letters if i.isalpha()])).lower()
         strikes_given = 4 + (8 - len(pattern))
         strikes_left = strikes_given - len(used_letters)
         print "Strikes left: %d" % strikes_left
         matches = get_matches(pattern, used_letters)
         print "There are %d possible words:" % len(matches)
         if len(matches) <= 20:
           print matches
         if len(matches) == 1:
           print "The word is: %s" % list(matches)[0]
         else:
            best_guess_maxlife = get_best_letter_guesses(score_guess_maxlife, matches, pattern, used_letters)
            print best_guess_maxlife
            best_guess = best_guess_maxlife
            print "Your expected strikes left is: %d" % get_expected_strikes_left(matches)
            print "Your best guess is the letter: %s" % best_guess
      elif mode == "create":
         pattern = raw_input("Enter the letters you were given (including duplicates) > ").strip().lower()
         if '!' in pattern:
            mode = "solve"
            continue
         words = get_best_word_list(pattern)
         print "The best words you can create are: ",
         print words
      
