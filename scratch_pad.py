#!/usr/bin/env python3.8
import requests


r = requests.get('https://www.spotternetwork.org/feeds/gr.txt')
print(r.text)
print(r.status_code)
print(type(r.status_code))
