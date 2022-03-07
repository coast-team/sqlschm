CREATE TABLE t1(
   a INTEGER PRIMARY KEY,
   b INT,
   c TEXT,
   d INT GENERATED ALWAYS AS (a*abs(b)) VIRTUAL,
   e TEXT AS (substr(c,b,b+1)) STORED
);