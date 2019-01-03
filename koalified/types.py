import re
from ipaddress import ip_address
from datetime import datetime

import arrow
import validators
import phonenumbers
import pycountry

built_in = {}


def _register(name):
    def add_type(function):
        built_in[name] = function
        return function
    return add_type


@_register('bool')
def string_boolean(value):
    """Determines the boolean value for a specified string"""
    if value.lower() in ('false', 'f', '0', ''):
        return False
    else:
        return True


@_register('int')
def number(value, minimum=None, maximum=None, cut=False, pad=False):
    """Returns back an integer from the given value"""
    value = int(value)
    if minimum is not None and value < minimum:
        if pad:
            return minimum
        raise ValueError('Provided value of {} is below specified minimum of {}'.format(value, minimum))
    if maximum is not None and value > maximum:
        if cut:
            return maximum
        raise ValueError('Provided value of {} is above specified maximum of {}'.format(value, maximum))
    return value


@_register('float')
def floating_number(value, minimum=None, maximum=None, cut=False, pad=False):
    """Returns back a float from the given value"""
    value = float(value)
    if minimum is not None and value < minimum:
        if pad:
            return minimum
        raise ValueError('Provided value of {} is below specified minimum of {}'.format(value, minimum))
    if maximum is not None and value > maximum:
        if cut:
            return maximum
        raise ValueError('Provided value of {} is above specified maximum of {}'.format(value, maximum))
    return value


@_register('str')
def string(value, shortest=None, longest=None, cut=False, lower=False, upper=False, strip=False, pad=False, align='<'):
    """Returns back a string from the given value"""
    value = str(value)
    if shortest is not None and len(value) < shortest:
        if pad:
            value ='{message:{fill}{align}{width}}'.format(message=value, fill=pad, align=align, width=shortest)
        else:
            raise ValueError('Provided value of {} is shorter than specified shortest length of {}'.format(value,
                                                                                                           shortest))
    if longest is not None and len(value) > longest:
        if cut:
            value = value[:longest]
        else:
            raise ValueError('Provided value of {} is longer than specified longest length of {}'.format(value,
                                                                                                         longest))
    if lower:
        value = value.lower()
    if upper:
        value = value.upper()
    if strip:
        value = value.strip()
    return value


@_register('match')
def match(value, regex):
    """Returns back a string if it matches the given regex"""
    if not re.match(regex, value):
        raise ValueError('Provided value of {} does not match specified regular expression {}'.format(value, regex))

    return value


@_register('ip')
def ip(value, minimum=None, maximum=None, cut=False, pad=False, version=None):
    """Returns back an IP Address, potentially within a minimum/maximum range"""
    address = ip_address(value)
    if version and address.version != version:
        raise ValueError('IP Address provided of {} is IPv{} only IPv{} is supported'.format(value, address.version,
                                                                                             version))
    if minimum and address < minimum:
        if pad:
            return minimum
        raise ValueError('IP Address provided of {} is below specified minimum of {}'.format(value, minimum))
    if maximum and address > maximum:
        if cut:
            return maximum
        raise ValueError('IP Address provided of {} is above specified maximum of {}'.format(value, maximum))

    return address


@_register('phone')
def phonenumber(value, default_country=None, format='E164', digits_only=True):
    number = phonenumbers.parse(value, default_country)
    if format:
        number = phonenumbers.format_number(number, getattr(phonenumbers.PhoneNumberFormat, format))
    if digits_only:
        number = ''.join((character for character in str(number) if character.isdigit()))

    return number


@_register('one_of')
def one_of(value, *values, case_insensitive=True):
    check_value = value
    if case_insensitive:
        check_value = value.lower()
        values = [value.lower() for value in values]
    if check_value not in values:
        raise ValueError('Provided value of {} is not one of the supported values: {}'.format(value, ', '.join(values)))
    return value


@_register('date')
def date(value, format='YYYY-MM-DD'):
    return arrow.get(value).format(format)


@_register('datetime')
def date_time(value, format='YYYY-MM-DD HH:MM'):
    return date(value, format)


@_register('strict_date')
def strict_date(value, input_format='%Y-%m-%d', output_format=None):
    if not output_format:
        output_format = input_format
    return datetime.strptime(value, input_format).strftime(output_format)


@_register('strict_datetime')
def strict_datetime(value, input_format='%Y-%m-%d %H:%S', output_format=None):
    return strict_date(value, input_format, output_format)


@_register('postal')
def postal(value, strip=False):
    """A very generic postal code validator that is meant to allow all international postal codes through"""
    if strip:
        value = value.strip()

    length = len(value)
    if length < 2:
        raise ValueError('Provided value {} is shorter than any official postal code standard allows'.format(value))
    elif length > 15:
        raise ValueError('Provided value {} is longer than any official postal code standard allows'.format(value))

    seen_separator = False
    for index, character in enumerate(value):
        if character in ('-', ' '):
            if seen_separator:
                raise ValueError('Provided value contains more than one separator: {}'.format(character))
            if index == 0 or index == (length - 1):
                raise ValueError('Provided value starts or ends with an invalid postal character: {}'.format(character))
            else:
                seen_separator = True
        elif not character.isalnum():
            raise ValueError('Provided value {} contains an invalid postal character: {}'.format(value, character))

    return value


@_register('country')
def country(value, output_format='alpha_3'):
    return getattr(pycountry.countries.lookup(value), output_format)


_register('email')(validators.email)
_register('domain')(validators.domain)
_register('mac')(validators.mac_address)
_register('md5')(validators.md5)
_register('sha1')(validators.sha1)
_register('sha224')(validators.sha224)
_register('sha256')(validators.sha256)
_register('sha512')(validators.sha512)
_register('uuid')(validators.uuid)
_register('slug')(validators.slug)
_register('iban')(validators.iban)
_register('dict')(dict)
_register('list')(list)
_register('tuple')(tuple)
_register('set')(set)
