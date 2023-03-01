import pickle
from datetime import datetime, timedelta, timezone

SUPPORTED_SYNTAX = dict( link = ('%LINK{###}', '%LINK{') )

def syntax_replace(input_, template, key):

    str_input = str(input_)
    if str_input.startswith(key) and str_input.endswith('}'):
        return str_input

    return template.replace('###', str_input)

def syntax_converter(input_, syntax):
    if not syntax:
        return input_

    if not isinstance(input_, dict):
        return syntax_replace(input_, *syntax)

    return { k: syntax_replace(v, *syntax) for k,v in input_.items() }

def massage_meta(input_, syntax = None):

    # no input or empty input
    if not input_:
        return {}

    supported_syntax = SUPPORTED_SYNTAX.get(syntax, None)
    if syntax and not supported_syntax:
        raise AttributeError('Status Meta [%s] contains unrecognized syntax '
                             '[%s] ' % input_, syntax)
    try:
        pickle.dumps(input_)
    except pickle.PicklingError as e:
        raise AttributeError('Status Meta [%s] contains unpicklable value'
                             % input_, e)

    # populate key, datetime in isoformat with utz timezone
    key = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    # if not dictionary
    if not isinstance(input_, dict):
        return { key: syntax_converter(input_, supported_syntax) }

    # loop over dictionary and validate all keys
    for k in input_.keys():
        try:
            str_to_datetime(k)
        except Exception:
            break
    else:
        # all keys are datetime string
        return input_
    # wrap with datetime key
    return { key: syntax_converter(input_, supported_syntax) }

def str_to_datetime(input_):
    # convert from datetime str to datetime instance
    dt, _, us = input_.partition(".")
    dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    dt.replace(tzinfo=timezone.utc)
    us = int(us.rstrip("Z"), 10)
    return dt + timedelta(microseconds = us)
