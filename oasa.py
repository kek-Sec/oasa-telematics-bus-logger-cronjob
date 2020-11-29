#!/usr/bin/python3
import json
import requests
import asyncio
import aiohttp
import sys
import signal

loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)
LineCodesList = {}  # contains all available LineCodes
RouteCodesList = {}  # contains all corresponding RouteCodes to the LineCodesList
BusesList = {}  # contains all buses


async def get_json(client, url):
    async with client.get(url) as response:
        assert response.status == 200
        return await response.read()


async def getLineCodes(client):
    to_return = {}
    c = 0
    res = await get_json(client, "http://telematics.oasa.gr/api/?act=webGetLines")
    items = json.loads(res)
    for item in items:
        to_return[c] = item["LineCode"]
        c += 1
    return to_return


async def getRouteCodes(linesList, client):
    to_return = {}
    c = 0
    for i in range(len(linesList)):
        res = await get_json(
            client,
            "http://telematics.oasa.gr/api/?act=getRoutesForLine&p1="
            + str(linesList[i]),
        )
        items = json.loads(res)
        d = 0
        if items:
            for item in items:
                if d > 0:
                    to_return[c] = to_return[c] + "," + item["route_code"]
                else:
                    to_return[c] = item["route_code"]
                d += 1
            c += 1
    return to_return


async def getBuses(routesList, client):
    to_return = {}
    c = 0
    for i in range(len(routesList)):
        x = routesList[i].split(",")
        for route in x:
            res = await get_json(
                client, "http://telematics.oasa.gr/api/?act=getBusLocation&p1=" + route
            )
            items = json.loads(res)
            for item in items:
                f = open("buses/" + item["VEH_NO"], "a")
                data = {
                    "timestamp": item["CS_DATE"],
                    "lat": item["CS_LAT"],
                    "lng": item["CS_LNG"],
                }
                data_json = json.dumps(data, indent=4, sort_keys=True)
                f.write(data_json)
                f.close()
                c += 1
    return to_return


def signal_handler(signal, frame):
    loop.stop()
    client.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


async def init(client):
    LineCodesList = await getLineCodes(client)
    print(LineCodesList)
    RouteCodesList = await getRouteCodes(LineCodesList, client)
    print(RouteCodesList)
    BusesList = await getBuses(RouteCodesList, client)
    print(BusesList)


# 0- Entry point -0
loop.run_until_complete(init(client))
loop.close()