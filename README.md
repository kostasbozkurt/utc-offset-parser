# UTC Offset Parser

Parses human-written UTC offsets like `GMT-5`, `+0530`, and `UTC+02:00` into Python `datetime.timezone` objects.

```python
from utc_offset_parser import parse_utc_offset, OffsetParseError

try:
    tz = parse_utc_offset("GMT-5")
except OffsetParseError as e:
    ...  # not a supported offset form
```

## Why

Standard library `datetime` accepts `timezone(timedelta(...))` but offers no parser for the string forms humans actually write — `GMT-5`, `+0530`, `UTC+02:00`. Date headers, log lines, and config files are full of these. This library turns one such string into a `timezone` object with no third-party dependencies and a strict contract: it either parses cleanly or raises `OffsetParseError`.

The trade-off is scope. Only the `GMT`/`UTC`-prefixed and bare `±HH[:MM]` forms are supported. There is no support for named zones (`America/New_York`), military letters (`Z`, `A`–`J`), or locale-dependent names. If you need those, use `zoneinfo` with the IANA database.

## The awkward edge

When hours are a single digit and minutes follow without a colon — `+130` — the result is ambiguous (`+1:30` or `+13:00`). The parser refuses to guess: it requires a colon after one-digit hours when minutes are present, and raises `OffsetParseError` otherwise. Two-digit hours work in compact form (`+0530`).

## API

- `parse_utc_offset(text: str) -> datetime.timezone` — parse a supported offset string.
- `OffsetParseError(ValueError)` — raised when `text` is not a supported form.

Run tests with `PYTHONPATH=src python -m unittest discover -s tests`.
