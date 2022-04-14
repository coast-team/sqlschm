CREATE TABLE person(
    fullname NOT NULL,
    birthday DEFAULT NULL,
    PRIMARY KEY (fullname COLLATE BINARY ASC)
);