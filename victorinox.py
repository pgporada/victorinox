
#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
import os
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

MAX_UPSTREAM_BYTES = 262144
MAX_QUERY_STRING_BYTES = 2048
MAX_USER_PARAM_BYTES = 128
INDEX_HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')


def _sanitize_for_log(s):
    """Strip control characters from a string before logging to prevent log injection."""
    return re.sub(r'[\x00-\x1f\x7f]', '', s)


def _error(start_response, code, remote, method, uri):
    phrase = HTTPStatus(code).phrase
    body = f'{code} {phrase}'.encode()
    start_response(f'{code} {phrase}', [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('Content-Length', str(len(body))),
    ])
    logger.info('%s %s %s %d', remote, method, uri, code)
    return [body]


def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', '?')
    remote = environ.get('HTTP_X_REAL_IP', environ.get('REMOTE_ADDR', '-'))
    query = environ.get('QUERY_STRING', '')
    uri = _sanitize_for_log(f'{path}?{query}' if query else path)

    if method not in ('GET', 'HEAD'):
        return _error(start_response, 405, remote, method, uri)

    if len(query) > MAX_QUERY_STRING_BYTES:
        return _error(start_response, 414, remote, method, uri)

    qs = parse_qs(query)

    if path == '/':
        accept = environ.get('HTTP_ACCEPT', '')
        if 'text/html' in accept:
            with open(INDEX_HTML_PATH, 'rb') as f:
                body = f.read()
            start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        else:
            body = b'Victorinox - on-call calendar proxy\n\nReplace your VictorOps calendar subscription URL host with this one.\nExample: https://example.com/victorinox/webcal/...\n'
            start_response('200 OK', [('Content-Type', 'text/plain; charset=utf-8')])
        logger.info('%s %s %s 200', remote, method, uri)
        return [body]

    user = qs.get('user', [None])[0]
    if user and len(user) > MAX_USER_PARAM_BYTES:
        return _error(start_response, 400, remote, method, uri)

    try:
        resp = requests.get(
            f'https://portal.victorops.com{path}',
            headers=headers,
            timeout=5,
        )

        if len(resp.content) > MAX_UPSTREAM_BYTES:
            return _error(start_response, 502, remote, method, uri)

        phrase = HTTPStatus(resp.status_code).phrase
        status = f'{resp.status_code} {phrase}'

        cal = icalendar.Calendar.from_ical(resp.content.decode('utf-8'))

        if user:
            cal.subcomponents[:] = [
                comp for comp in cal.subcomponents
                if not (comp.name == 'VEVENT' and (everyone.search(str(comp['SUMMARY'])) or not str(comp['SUMMARY']).startswith(f'{user} - ')))
            ]
        else:
            cal.subcomponents[:] = [
                comp for comp in cal.subcomponents
                if not (comp.name == 'VEVENT' and everyone.search(str(comp['SUMMARY'])))
            ]
        output = cal.to_ical()

        start_response(status, [
            ('Content-Type', 'text/calendar; charset=utf-8'),
            ('Content-Length', str(len(output))),
        ])
        logger.info('%s %s %s %d', remote, method, uri, resp.status_code)
        return [output]

    except requests.exceptions.Timeout:
        return _error(start_response, 504, remote, method, uri)

    except (requests.exceptions.RequestException, ValueError) as e:
        logger.warning('%s %s %s upstream_error: %s', remote, method, uri, type(e).__name__)
        return _error(start_response, 502, remote, method, uri)

    except Exception:
        logger.exception('%s %s %s 500', remote, method, uri)
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [b'Failed']
