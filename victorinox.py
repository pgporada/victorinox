#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
import re
from http import HTTPStatus
from urllib.parse import parse_qs

import icalendar
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger('victorinox')

headers = requests.utils.default_headers()
headers.update(
    {
        'Connection': 'close',
        'User-Agent': 'Victorinox/0.3 (https://github.com/pgporada/victorinox)'
    }
)

everyone = re.compile(r' \- everyone:everyone$')


def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', '?')
    remote = environ.get('HTTP_X_REAL_IP', environ.get('REMOTE_ADDR', '-'))
    qs = parse_qs(environ.get('QUERY_STRING', ''))

    if path == '/':
        accept = environ.get('HTTP_ACCEPT', '')
        if 'text/html' in accept:
            with open('index.html', 'rb') as f:
                body = f.read()
            start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        else:
            body = b'Victorinox - on-call calendar proxy\n\nReplace your VictorOps calendar subscription URL host with this one.\nExample: https://example.com/victorinox/webcal/...\n'
            start_response('200 OK', [('Content-Type', 'text/plain; charset=utf-8')])
        logger.info(f'{remote} {method} {path} 200')
        return [body]

    try:
        request = requests.get(f'https://portal.victorops.com{path}', headers=headers, timeout=5)

        phrase = HTTPStatus(request.status_code).phrase
        status = f'{request.status_code} {phrase}'

        cal = icalendar.Calendar.from_ical(request.content.decode('utf-8'))

        user = qs.get('user', [None])[0]
        if user:
            cal.subcomponents[:] = [
                comp for comp in cal.subcomponents
                if not (comp.name == 'VEVENT' and (everyone.search(comp['SUMMARY']) or not comp['SUMMARY'].startswith(f'{user} - ')))
            ]
        else:
            cal.subcomponents[:] = [
                comp for comp in cal.subcomponents
                if not (comp.name == 'VEVENT' and everyone.search(comp['SUMMARY']))
            ]

        output = cal.to_ical()

        start_response(status, [('Content-Type', request.headers['Content-Type'])])
        logger.info(f'{remote} {method} {path} {request.status_code}')
        return [output]

    except Exception:
        logger.exception(f'{remote} {method} {path} 500')
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [b'Failed']
