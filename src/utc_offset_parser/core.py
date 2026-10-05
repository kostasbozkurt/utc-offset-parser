from __future__ import annotations

import datetime
import re

__all__ = ["OffsetParseError", "parse_utc_offset"]


class OffsetParseError(ValueError):
    """Raised when an input string is not a supported UTC offset form."""


# Matches "GMT" / "UTC" (optional, case-insensitive) then a sign, then
# H[:MM] or HH[:MM], with optional leading whitespace only. We deliberately
# reject trailing content (including internal whitespace) so callers get a
# tight contract: a clean parse or a clean failure."""
_PATTERN = re.compile(
    r"\A\s*(?:GMT|UTC)?\s*([+-])(\d{1,2})(?::?(\d{2}))?\s*\Z",
    re.IGNORECASE,
)


def parse_utc_offset(text: str) -> datetime.timezone:
    """Parse a human-written UTC offset string into a ``timezone`` object.

    Supported examples (whitespace around the whole token is ignored):
        +05:30   GMT-5   UTC+02:00   -0800-not-supported
        +0530    +05    UTC-03:00
    The colon between hours and minutes is optional when the hours field is
    two digits wide; a colon is required to separate one-digit hours from
    two-digit minutes so the parser never has to guess whether "+130" means
    "+1:30" or "+13:00".

    Raises:
        OffsetParseError: if *text* is not a string, is empty, or does not
            match one of the supported forms.
    """
    if not isinstance(text, str):
        raise OffsetParseError(
            f"expected a string, got {type(text).__name__}"
        )

    match = _PATTERN.match(text)
    if match is None:
        raise OffsetParseError(f"not a UTC offset: {text!r}")

    sign_str, hours_str, minutes_str = match.group(1), match.group(2), match.group(3)

    hours = int(hours_str)
    minutes = int(minutes_str) if minutes_str is not None else 0

    # Ambiguity guard: a 3-digit compact form like "+130" could mean +1:30 or
    # +13:00. Require a colon after one-digit hours when minutes are present.
    if len(hours_str) == 1 and minutes_str is not None and ':' not in text:
        raise OffsetParseError(f"ambiguous compact offset: {text!r}")

    if hours > 23:
        raise OffsetParseError(
            f"offset hours out of range [0, 23]: {hours}"
        )
    if minutes > 59:
        raise OffsetParseError(
            f"offset minutes out of range [0, 59]: {minutes}"
        )

    total = datetime.timedelta(hours=hours, minutes=minutes)
    if sign_str == "-":
        total = -total

    if total == datetime.timedelta(0):
        # Keep a single canonical ``timezone.utc`` instance for offset zero.
        return datetime.timezone.utc
    return datetime.timezone(total, name=f"UTC{sign_str}{hours_str}:{minutes_str or '00'}")
