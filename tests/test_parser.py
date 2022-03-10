from sqlschm import parse_schema
import black
from black import mode
import os

CORPUS = "tests_corpus/valid/"


def test_valid_schema():
    files = list(os.listdir(CORPUS))
    files.sort()
    for schm_name in files:
        if schm_name.endswith(".sql"):
            out_name = CORPUS + schm_name[:-4] + ".ast"
            with open(CORPUS + schm_name) as schm, open(out_name) as out:
                schm_content = schm.read()
                out_content = out.read()
            ast = parse_schema(schm_content)
            computed_content = black.format_str(repr(ast), mode=mode.Mode())
            assert computed_content == out_content
