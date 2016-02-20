#!/usr/bin/python2.7
import requests
import geopy
import geopy.distance
import time
import psycopg2
from datetime import datetime
from datetime import timedelta

routes_url = "http://www.nextconnect.riderta.com/Arrivals.aspx/getRoutes"
vehicles_url = "http://www.nextconnect.riderta.com/GoogleMap.aspx/getVehicles"
default_headers = {
	'Accept': 'application/json',
	'Content-Type': 'application/json'
}

vehicles = {}

class Vehicle:

	def __init__(self, json):
		self.id = int(json["propertyTag"])
		self.history = []
		self.active = False
		self.update(json)
		
	def update(self, json):
		if self.id != int(json["propertyTag"]):
			raise ValueError("expected ID %d, got %d" % (self.id, int(json["propertyTag"])))
		
		
		self.history.append({'location': geopy.Point(json["lat"], json["lon"]), "timestamp": datetime.now()})
	
	def __repr__(self):
		return "Vehicle(%d, %s, %s)" % (self.id, self.history[-1]["location"], self.history[-1]["timestamp"])

def get_db_conn():
	return psycopg2.connect(host="localhost", user="cameron", port=43353, dbname="rta")

def get_db_cursor():
	return get_db_conn().cursor()

def load_routes():
	with get_db_conn() as conn:
		with conn.cursor() as cursor:
			for json in requests.post(routes_url, headers=default_headers).json()["d"]:
				cursor.execute("SELECT 1 FROM core.routes WHERE routeid = %s", (int(json["id"]),))
				if cursor.rowcount == 0:
					cursor.execute("INSERT INTO core.routes (routeid, routename) VALUES (%s, %s)", (int(json["id"]), json["name"]))

def get_vehicles(routeid):
	try:
		return requests.post(vehicles_url, headers=default_headers, data="{routeID: %d}" % routeid).json()["d"]
	except:
		return []

def tick():
	with get_db_conn() as conn:
		with conn.cursor() as cursor:
			cursor.execute("SELECT routeid FROM core.routes WHERE istracked")
			for routeid in cursor.fetchall():
				for json in get_vehicles(routeid):
					id = int(json["propertyTag"])
					cursor.execute("SELECT 1 FROM core.vehicles WHERE vehicleid = %s", (id,))
					if cursor.rowcount == 0:
						cursor.execute("INSERT INTO core.vehicles VALUES (%s)", (id,))
			
					params = {
						'vehicle': id,
						'route': routeid,
						'lat': float(json["lat"]),
						'lon': float(json["lon"])
					}
					cursor.execute(
						"""
							INSERT INTO core.updates (vehicle, route, location)
							VALUES
							(
								%(vehicle)s,
								%(route)s,
								ST_Transform(ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326), 3734)
							)
						""",
						params)

def main():
	load_routes()
	while True:
		tick()
		time.sleep(30)
	return
	
if __name__ == "__main__":
	main()
