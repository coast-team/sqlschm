from sqlschm import tok


def test_interned_consistent_val() -> None:
    for val, token in tok.INTERNED.items():
        assert token.val == val
