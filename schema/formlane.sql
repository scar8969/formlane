-- 📬 formbackend schema
CREATE TABLE forms(id INTEGER PRIMARY KEY, token TEXT UNIQUE, name TEXT, deliver_json TEXT DEFAULT '{}', spam_json TEXT DEFAULT '{}', created_at DATETIME);
CREATE TABLE submissions(id INTEGER PRIMARY KEY, form_id INTEGER REFERENCES forms(id), fields_json TEXT DEFAULT '{}', ip TEXT, spam INTEGER DEFAULT 0, delivered INTEGER DEFAULT 0, at DATETIME);
