CREATE TABLE person(
    fullname text NOT NULL PRIMARY KEY,
    friend REFERENCES person(fullname)
);