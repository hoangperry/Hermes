import re


def entity_to_dict(entity):
    """
    Convert entity (object) to dictionary
    :param entity:
    :return:
    """
    return dict((col, getattr(entity, col)) for col in entity.__table__.columns.keys())


def dict_to_object(d):
    top = type('new', (object,), d)
    seqs = tuple, list, set, frozenset
    for i, j in d.items():
        if isinstance(j, dict):
            setattr(top, i, dict_to_object(j))
        elif isinstance(j, seqs):
            setattr(
                top, i,
                type(j)(dict_to_object(sj) if isinstance(sj, dict) else sj for sj in j)
            )
        else:
            setattr(top, i, j)
    return top


def to_float(s, max_length=5):
    try:

        if len(s) > max_length:
            s = re.sub(r'[^0-9]', '', s)

        return float(s)
    except Exception:
        return None


def to_int(s):
    try:
        return int(s)
    except Exception:
        return None


def optimize_dict(my_dict):
    """
    Remove table prefix, table, selenium in dictionary
    :param my_dict:
    :return:
    """
    ob_dict = dict()
    for key, value in my_dict.items():
        if not key.startswith("pre_") and not key.endswith("_table") and not key == 'use_selenium':
            ob_dict[key] = value

    return ob_dict
