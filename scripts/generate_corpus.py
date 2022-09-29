from sqlschm.parser import parse_schema
from sqlschm.generator import generate_schema
from sqlschm.sql import Dialect
import black
from black import mode
import os
from pathlib import Path

CORPUS = "tests_corpus/valid/"


def main() -> None:
    files = list(os.listdir(CORPUS))
    files.sort()
    for schm_name in files:
        if schm_name.endswith(".sql"):
            print("Generating... " + schm_name[:-4])
            astFilename = Path(CORPUS + schm_name[:-4] + ".ast")
            astFilename.touch(exist_ok=True)
            outFilename = Path(CORPUS + schm_name[:-4] + ".out")
            outFilename.touch(exist_ok=True)
            with open(CORPUS + schm_name) as schm, open(
                astFilename, "w+"
            ) as astFile, open(CORPUS + schm_name) as schm, open(
                outFilename, "w+"
            ) as outFile:
                content = schm.read()
                schema = parse_schema(content)
                astFile.write(black.format_str(repr(schema), mode=mode.Mode()))
                outFile.write(generate_schema(schema, Dialect.SQLITE))


if __name__ == "__main__":
    main()
