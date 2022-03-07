from sqlschm import tok


def test_interned_consistent_val():
    for val in tok.INTERNED:
        assert tok.INTERNED[val].val == val
