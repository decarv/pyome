import pytest


parse_tests = [
    "limit buy 10 100",
    "limit sell 20 100",
    "limit sell 20 200",
    "market buy 150",
    "makret buy 150"
]

engine.parse_order(parse_tests[3])
