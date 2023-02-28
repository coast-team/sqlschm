# Copyright (c) 2022 Victorien Elvinger
# Licensed under the MIT License (https://mit-license.org/)

import os
import black
from sqlschm.parser import parse_schema

CORPUS = "tests_corpus/valid/"


def test_valid_schema() -> None:
    files = list(os.listdir(CORPUS))
    files.sort()
    for schm_name in files:
        if schm_name.endswith(".sql"):
            out_name = CORPUS + schm_name[:-4] + ".ast"
            with open(CORPUS + schm_name, encoding="utf-8") as schm, open(
                out_name, encoding="utf-8"
            ) as out:
                schm_content = schm.read()
                out_content = out.read()
            ast = parse_schema(schm_content)
            computed_content = black.format_str(repr(ast), mode=black.mode.Mode())
            assert computed_content == out_content
