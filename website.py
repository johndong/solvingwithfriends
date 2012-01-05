#!/usr/bin/env python

import web
from solvingwithfriends import *
import json
from urllib import unquote
import math

urls = (
    '/solve/(.*)/(.*)', "solve",
    '/.*', "index"
    )

render = web.template.render("templates/")

class solve:
  def GET(self, pattern, used_letters):
    def format_matches(matches, letter):
      from cStringIO import StringIO
      s = StringIO()
      num = 0
      print >>s, "<ol>"
      for m in matches:
        print >>s, "<li>%s</li>" % m.replace(letter,"<b>%s</b>" % letter)
        num += 1
        if num >= 36:
          break
      print >>s, "</ol>"        
      return s.getvalue()
    pattern = unquote(pattern)
    used_letters = unquote(used_letters)
    pattern = "".join([i for i in pattern if i.isalpha() or i == '?']).lower()
    used_letters = "".join(set([i for i in used_letters if i.isalpha()])).lower()
    matches = get_matches(pattern, used_letters)
    expected_strikes_left = int(math.floor(get_expected_strikes_left(matches)))
    best_guesses = map(lambda l: l.upper(),
            get_best_letter_guesses(score_guess_maxlife, matches, pattern,
                used_letters))
    if matches:
      resp = {'best_guesses': " ".join([best_guesses[0]] + best_guesses[1:]),
              'num_matches': str(len(matches)), 'matches':
              format_matches(sorted(list(matches)), best_guesses[0]),
              'expected_strikes_left': str(expected_strikes_left)
             }
    else:
      resp = {'best_guesses': "???", 'num_matches': str(len(matches)),
              'matches': "", 'expected_strikes_left': ""
               }
    web.header('Content-Type', 'application/json')
    return '(' + json.dumps(resp) + ')'

class index:
  def GET(self):
    return render.index()

if __name__ == "__main__":
  init()
  app = web.application(urls, globals())
  main = app.cgirun()
