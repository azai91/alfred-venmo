"""
Basic util library
"""

import json

# pylint: disable=relative-import, invalid-name, bare-except

def validate_amount(amount):
    """
    Validate user input to float format with two decimal

    Args:
        amount, user input string

    Returns:
        a string in correct format, or False if string cannot be

    """

    return '{:.2f}'.format(float(amount))

def create_post_message(friend):
    """
    """

    try:
        friend = json.loads(friend)
    except:
        pass

    display_name = friend['display_name']

    # removes negative sign
    amount = friend['amount'] if not friend['amount'][0].startswith('-') else friend['amount'][1:]
    action = 'received' if not friend['amount'].startswith('-') else 'was charged'

    note = friend['note']

    return "%s %s $%s for %s" % (display_name, action, amount, note)

def format_amount(amount):
    """
    Formats user input amount

    Args:
        amount, a user inputted value

    Returns:
        a string formatted as such, $x.xx or -$x.xx

    """

    amount = validate_amount(abs(float(amount)))
    return '$%s' % amount

