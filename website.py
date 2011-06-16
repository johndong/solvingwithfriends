#!/usr/bin/env python

import web
from solvingwithfriends import *
import json
from urllib import unquote

urls = (
    '/solve/(.*)/(.*)', "solve",
    '/.*', "index"
    )

render = web.template.render("templates/")

class solve:
  def GET(self, pattern, used_letters):
    def format_matches(matches):
      from cStringIO import StringIO
      s = StringIO()
      num = 0
      print >>s, "<ol>"
      for m in matches:
        print >>s, "<li> %s" % m
        num += 1
        if num >= 50:
          print >>s, "<li> ... (too many to list)"
          break
      print >>s, "</ol>"        
      return s.getvalue()
    pattern = unquote(pattern)
    used_letters = unquote(used_letters)
    pattern = "".join([i for i in pattern if i.isalpha() or i == '?']).lower()
    used_letters = "".join(set([i for i in used_letters if i.isalpha()])).lower()
    matches = get_matches(pattern, used_letters)
    best_guesses = get_best_letter_guesses(score_guess_maxlife, matches, pattern, used_letters)
    resp = {'best_guesses': " ".join(best_guesses), 'num_matches': "<b>%s</b>" % str(len(matches)), 'matches': format_matches(sorted(list(matches))),
             }
    web.header('Content-Type', 'application/json')
    return '(' + json.dumps(resp) + ')'

class index:
  def GET(self):
    return render.index()

if __name__ == "__main__":
  init()
  app = web.application(urls, globals())
  app.run()