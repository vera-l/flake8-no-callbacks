# flake8-no-callbacks

Tornado `callback`-argument of http-client was deprecated in tornado 5.1 and removed in version 6.0.
This plugin highlights callbacks to replace them by coroutines.

## The problem

Bad:

```python
def _cb(json, response):
    if not response.error and json is not None:
        self.json.put(json)

self.get_url(
    someHost,
    '/path/to',
    data={
        'id': self.get_argument('id'),
    },
    callback=_cb,
)
```

Good:

```python
result = await self.get_url(
    someHost,
    '/path/to',
    data={
        'id': self.get_argument('id'),
    },
)
if not result.failed:
    self.json.put(result.data)
```

## Rules

-   `NOC101` - Callbacks are deprecated. Use coroutines instead.

## Installation

```console
python3 setup.py istall
```

## Usage

```console
flake8 --select NOC101 .

my_project/pages/path/to/__init__.py:246:13: NOC101 Callbacks are deprecated. Use coroutines instead.
            self.post_url(
            ^
...
```

## Developing

Use astpretty to see formatted ast nodes:

```console
astpretty --no-show-offsets /dev/stdin <<< "not a == b"
```

Run tests:

```console
pytest -vv tests
```
