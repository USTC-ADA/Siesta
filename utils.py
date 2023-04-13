def inverseDict(m: dict) -> dict:
    return dict(zip(m.values(), m.keys()))

def add_seprate_symbol_after_path(s: str) -> str:
    if len(s) < 1:
        return ""
    if s[-1] != '/':
        s += '/'
    return s