from ipaddress import ip_address

import pytest
from koalified.types import (
    country,
    date,
    date_time,
    floating_number,
    ip,
    match,
    number,
    one_of,
    phonenumber,
    postal,
    strict_date,
    strict_datetime,
    string,
    string_boolean,
)


def test_string_boolean():
    assert string_boolean("f") == False
    assert string_boolean("t") == True
    assert string_boolean("False") == False
    assert string_boolean("True") == True
    assert string_boolean("0") == False
    assert string_boolean("1") == True
    assert string_boolean("10") == True
    assert string_boolean("") == False
    assert string_boolean("Anything Else") == True

    with pytest.raises(AttributeError):
        string_boolean({"Not": "a string"})


def test_number():
    assert number("1") == 1
    assert number("0") == 0
    with pytest.raises(ValueError):
        number("a")

    with pytest.raises(ValueError):
        number("10", minimum=11)
    assert number("10", minimum=10) == 10
    assert number("10", minimum=11, pad=True) == 11

    with pytest.raises(ValueError):
        number("10", minimum=1, maximum=9)

    assert number("10", minimum=1, maximum=9, cut=True) == 9
    assert number("10", minimum=0, maximum=0, cut=True, pad=True) == 0
    assert number("10", minimum=11, maximum=0, cut=True, pad=True) == 11


def test_floating_number():
    assert floating_number("1.1") == 1.1
    assert floating_number("0.0") == 0.0
    with pytest.raises(ValueError):
        floating_number("a")

    with pytest.raises(ValueError):
        floating_number("10", minimum=11.0)
    assert floating_number("10", minimum=10.0) == 10.0
    assert floating_number("10", minimum=11.0, pad=True) == 11.0

    with pytest.raises(ValueError):
        floating_number("10", minimum=1.0, maximum=9.0)

    assert floating_number("10", minimum=1.0, maximum=9.0, cut=True) == 9.0
    assert floating_number("10", minimum=0.0, maximum=0.0, cut=True, pad=True) == 0.0
    assert floating_number("10", minimum=11.0, maximum=0.0, cut=True, pad=True) == 11.0


def test_string():
    assert string("text") == "text"

    with pytest.raises(ValueError):
        string("text", shortest=10)
    assert string("text", shortest=10, pad="0") == "text000000"
    assert string("text", shortest=10, pad="0", align=">") == "000000text"
    assert string("text", shortest=10, pad="0", align="^") == "000text000"

    with pytest.raises(ValueError):
        string("text", longest=3)
    assert string("text", longest=3, cut=True) == "tex"
    assert string("TEXt", lower=True) == "text"
    assert string("tExt", upper=True) == "TEXT"
    assert string("text", longest=3, cut=True, upper=True) == "TEX"
    assert string("   text   ", strip=True) == "text"


def test_match():
    assert match("a", "[A-z]") == "a"
    with pytest.raises(ValueError):
        match("1", "[A-z]")


def test_ip():
    assert ip("2001:cdba:0000:0000:0000:0000:3257:9652") == ip_address(
        "2001:cdba:0000:0000:0000:0000:3257:9652"
    )
    assert ip("192.168.0.1") == ip_address("192.168.0.1")
    with pytest.raises(ValueError):
        ip("text")

    with pytest.raises(ValueError):
        ip("2001:cdba:0000:0000:0000:0000:3257:9652", version=4)
    with pytest.raises(ValueError):
        ip("192.168.0.1", version=6)

    with pytest.raises(ValueError):
        ip("192.168.0.1", minimum=ip("192.168.0.2"))
    assert ip("192.168.0.1", minimum=ip("192.168.0.2"), pad=True) == ip_address("192.168.0.2")

    with pytest.raises(ValueError):
        ip("192.168.0.2", maximum=ip("192.168.0.1"))
    assert ip("192.168.0.2", maximum=ip("192.168.0.1"), cut=True) == ip_address("192.168.0.1")


def test_one_of():
    assert one_of("bacon", "reeses", "bacon", "cheese") == "bacon"
    assert one_of("reeses", "reeses", "bacon", "cheese") == "reeses"
    with pytest.raises(ValueError):
        one_of("none of the above", "reeses", "bacon", "cheese")


def test_date():
    assert date("2013-05-11T21:23:58.970460+00:00") == "2013-05-11"
    with pytest.raises(Exception):
        date("not a date")


def test_date_time():
    assert date_time("2013-05-11T21:23:58.970460+00:00") == "2013-05-11 21:05"
    with pytest.raises(Exception):
        date("not a date")


def test_strict_date():
    with pytest.raises(Exception):
        strict_date("2013-05-11T21:23:58.970460+00:00")

    assert strict_date("2013-05-11") == "2013-05-11"


def test_strict_datetime():
    with pytest.raises(Exception):
        strict_datetime("2013-05-11T21:23:58.970460+00:00")

    assert strict_datetime("2013-05-11 21:04") == "2013-05-11 21:04"


def test_postal():
    with pytest.raises(ValueError):
        postal("rtstsrnsaierntsraieantsritsr")
    with pytest.raises(ValueError):
        postal("")
    with pytest.raises(ValueError):
        postal("410-212-7618")
    with pytest.raises(ValueError):
        postal("               98103                 ")
    with pytest.raises(ValueError):
        postal("-zipcode")
    with pytest.raises(ValueError):
        postal("zipcode-")
    with pytest.raises(ValueError):
        postal("(*#)")

    assert postal("98103") == "98103"
    assert postal("AA-9999") == "AA-9999"
    assert postal("  98103   ", strip=True) == "98103"


def test_phonenumber():
    assert phonenumber("410-212-7618", "US") == "14102127618"
    with pytest.raises(Exception):
        phonenumber("not a number")


def test_country():
    assert country("United States") == "USA"
    assert country("Russian Federation") == "RUS"
    assert country("USA") == "USA"

    with pytest.raises(Exception):
        country("NOT A COUNTRY")
    with pytest.raises(Exception):
        country(21332121)
