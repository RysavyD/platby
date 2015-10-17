#!/usr/bin/python
# -*- coding: utf-8 -*-

default_application = 'platby'    # ordinarily set in base routes.py
default_controller = 'default'  # ordinarily set in app-specific routes.py
default_function = 'index'      # ordinarily set in app-specific routes.py

routes_in = (
  ('/$anything', '/platby/$anything'),
  ('*./favicon.ico', '/platby/static/images/favicon.ico'),
  ('*./favicon.png', '/platby/static/images/favicon.png'),
  ('*./robots.txt', '/platby/static/robots.txt'),
  )

routes_out = [(x, y) for (y, x) in routes_in[:-3]]
