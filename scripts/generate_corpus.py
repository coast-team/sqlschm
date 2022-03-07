from sqlschm.parser import parse_schema
import black
from black import mode
import os
from pathlib import Path

CORPUS = "tests_corpus/valid/"


def main():
    files = list(os.listdir(CORPUS))
    files.sort()
    for schm_name in files:
        if schm_name.endswith(".sql"):
            print("Generating... " + schm_name)
            outFile = Path(CORPUS + schm_name[:-4] + ".ast")
            outFile.touch(exist_ok=True)
            with open(CORPUS + schm_name) as schm, open(outFile, "w+") as out:
                content = schm.read()
                ast = parse_schema(content)
                out.write(black.format_str(repr(ast), mode=mode.Mode()))


if __name__ == "__main__":
    main()
