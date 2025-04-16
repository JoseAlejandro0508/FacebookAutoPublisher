DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE asociatedAccounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  accCookieName TEXT UNIQUE NOT NULL,
  accUsername TEXT UNIQUE NOT NULL,
  accPassword TEXT NOT NULL,
  publicationText Text DEFAULT 'None',
  logs Text DEFAULT 'None',
  groupsConf JSON  DEFAULT '{}',
  publicationConf JSON DEFAULT '{}',

  

  FOREIGN KEY (author_id) REFERENCES user (id)
);