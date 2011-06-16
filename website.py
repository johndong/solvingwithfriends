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
    pattern = unquote(pattern)
    used_letters = unquote(used_letters)
    pattern = "".join([i for i in pattern if i.isalpha() or i == '?']).lower()
    used_letters = "".join(set([i for i in used_letters if i.isalpha()])).lower()
    matches = get_matches(pattern, used_letters)
    best_guesses = get_best_letter_guesses(score_guess_maxlife, matches, pattern, used_letters)
    resp = {'best_guesses': best_guesses}
    return '(' + json.dumps(resp) + ')'

class index:
  def GET(self):
    return render.index()

if __name__ == "__main__":
  init()
  app = web.application(urls, globals())
  app.run()
