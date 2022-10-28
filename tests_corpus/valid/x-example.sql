CREATE TABLE contact_groups(
   contact_id INTEGER,
   group_id INTEGER,
   PRIMARY KEY (contact_id, group_id),
   FOREIGN KEY (contact_id) 
      REFERENCES contacts (contact_id) 
         ON DELETE CASCADE 
         ON UPDATE NO ACTION,
   FOREIGN KEY (group_id) 
      REFERENCES groups (group_id) 
         ON DELETE CASCADE 
         ON UPDATE NO ACTION
);

CREATE UNIQUE INDEX contact_groups_group_index ON contact_groups(group_id);

CREATE TABLE contacts(
   contact_id INTEGER PRIMARY KEY
);

CREATE TABLE groups(
   group_id INTEGER PRIMARY KEY
);
