
def is_integer(nr):
    try:
        int(nr)
        return True
    except ValueError:
        return False
