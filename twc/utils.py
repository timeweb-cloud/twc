"""Common non TWC-specific functions."""


def merge_dicts(a: dict, b: dict, path=None) -> dict:
    """Merge b into a. Return modified a.
    Ref: https://stackoverflow.com/a/7205107
    """
    # pylint: disable=invalid-name
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                a[key] = b[key]  # replace existing key's values
        else:
            a[key] = b[key]
    return a
