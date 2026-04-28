#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import re
from http import HTTPStatus

import icalendar
import requests

headers = requests.utils.default_headers()
headers.update(
    {
        'Connection': 'close',
        'User-Agent': 'Victorinox/0.3 (https://github.com/pgporada/victorinox)'
    }
)

everyone = re.compile(r' \- everyone:everyone$')

def application(environ, start_response):
    if environ['REQUEST_URI'] == '/':
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b':)\n']
    try:
        request = requests.get(f"https://portal.victorops.com{environ['REQUEST_URI']}", headers=headers, timeout=5)

        phrase = HTTPStatus(request.status_code).phrase
        status = f'{request.status_code} {phrase}'

        cal = icalendar.Calendar.from_ical(request.content.decode('utf-8'))
        cal.subcomponents[:] = [comp for comp in cal.subcomponents if not (comp.name == 'VEVENT' and everyone.search(comp['SUMMARY']))]

        output = cal.to_ical()

        start_response(status, [('Content-Type', request.headers['Content-Type'])])

        return [output]
    except Exception:
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [b'Failed']
