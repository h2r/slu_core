def assertExactlyOne(*args):
    assert len([a for a in args if a != None]) == 1, args
        