"""
If no DB is found, this will initialize it
"""


import mysql.connector

# TODO - Create this

"""
Create Banned Table
CREATE TABLE "banned_users" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"discordID"	INTEGER NOT NULL,
	"BannedBy"	TEXT NOT NULL,
	"BannedReason"	TEXT,
	PRIMARY KEY("ID" AUTOINCREMENT)
);

CREATE TABLE "urls" (
	"id"	TEXT NOT NULL UNIQUE,
	"creator_discordID"	INTEGER,
	"short_link"	TEXT NOT NULL UNIQUE,
	"url"	TEXT NOT NULL,
	"slug"	TEXT NOT NULL UNIQUE,
	"comment"	TEXT,
	"expires_date"	INTEGER,
	"created_date"	INTEGER NOT NULL,
	"updated_date"	INTEGER NOT NULL,
	PRIMARY KEY("id")
);

"""