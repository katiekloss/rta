---
--- Extensions
---
CREATE EXTENSION postgis;

---
--- Schemas
---
CREATE SCHEMA core;
CREATE SCHEMA fleet;

---
--- Tables
---
CREATE TABLE fleet.manufacturers (
	manufacturercode	varchar(5),
	manufacturername	text		NOT NULL,

	PRIMARY KEY (manufacturercode)
);

CREATE TABLE fleet.models (
	manufacturer	varchar(5),
	modelnumber	varchar(10),
	modelname	text		NOT NULL,

	PRIMARY KEY (manufacturer, modelnumber),
	FOREIGN KEY (manufacturer) REFERENCES fleet.manufacturers (manufacturercode)
);

CREATE TABLE fleet.powertypes (
	powertypecode	char(3),
	powertypename	text		NOT NULL,

	PRIMARY KEY (powertypecode)
);

CREATE TABLE fleet.engines (
	engineid	serial,
	enginename	text		NOT NULL,
	powertype	char(3)		NOT NULL,

	PRIMARY KEY (engineid),
	FOREIGN KEY (powertype) REFERENCES fleet.powertypes (powertypecode)
);

CREATE TABLE fleet.transmissions (
	transmissionid		serial,
	transmissionname	text	NOT NULL,
	powertype		char(3),

	PRIMARY KEY (transmissionid),
	FOREIGN KEY (powertype) REFERENCES fleet.powertypes (powertypecode)
);

CREATE TABLE core.vehicles (
	vehicleid	serial,
	manufacturer	varchar(5),
	modelnumber	varchar(10),
	engine		integer,
	transmission	integer,

	PRIMARY KEY (vehicleid),
	FOREIGN KEY (manufacturer, modelnumber) REFERENCES fleet.models (manufacturer, modelnumber),
	FOREIGN KEY (engine) REFERENCES fleet.engines (engineid),
	FOREIGN KEY (transmission) REFERENCES fleet.transmissions (transmissionid)
);

CREATE TABLE core.routes (
	routeid		serial,
	routename	text		NOT NULL,
	istracked	boolean		NOT NULL DEFAULT FALSE,

	PRIMARY KEY (routeid)
);

CREATE TABLE core.updates (
	timestamp	timestamp(0) with time zone	DEFAULT CURRENT_TIMESTAMP,
	vehicle		integer				NOT NULL,
	route		integer				NOT NULL,

	PRIMARY KEY (timestamp, vehicle),
	FOREIGN KEY (vehicle) REFERENCES core.vehicles (vehicleid),
	FOREIGN KEY (route) REFERENCES core.routes (routeid)
);

SELECT AddGeometryColumn('core', 'updates', 'location', 4326, 'POINT', 2);
