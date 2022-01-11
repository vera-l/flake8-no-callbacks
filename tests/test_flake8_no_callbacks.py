import ast
from typing import Set

from flake8_no_callbacks import Plugin


def _results(s: str) -> Set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_wrong_method_name_case():
    code = '''
self.some_method(
    'http://api.example.com',
    '/v1/abc',
    callback=cb
)
'''
    assert _results(code) == set()


def test_no_callback_case():
    code = '''
self.put_url(
    'http://api.example.com',
    '/v1/abc',
)
'''
    assert _results(code) == set()


def test_has_callback_as_keyword_case():
    code = '''
def cb():
    pass
self.get_url(
    'http://api.example.com',
    '/v1/abc',
    callback=cb
)
'''
    ret = _results(code)
    assert ret == {
        ('4:0 NOC101 Callbacks are deprecated. Use coroutines instead of callbacks.')}


def test_has_callback_as_argument_case():
    code = '''
# see frontik handler code
def callback():
    pass
self.get_url(
    host, uri, name, data, headers, follow_redirects, connect_timeout, 
    request_timeout, max_timeout_tries, callback
)
'''
    ret = _results(code)
    assert ret == {
        ('5:0 NOC101 Callbacks are deprecated. Use coroutines instead of callbacks.')}


def test_has_parent_and_child_callback():
    code = '''
def cb():
    self.get_url(
        'http://api.example.com',
        '/v1/abc',
        callback=cb2
    )
self.get_url(
    'http://api.example.com',
    '/v1/abc',
    callback=cb
)
'''
    ret = _results(code)
    assert ret == {
        ('8:0 NOC101 Callbacks are deprecated. Use coroutines instead of callbacks.'),
        ('3:4 NOC101 Callbacks are deprecated. Use coroutines instead of callbacks.')
    }
