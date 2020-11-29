#!/usr/bin/python3
import json
import asyncio
import sys
import signal
import time
import glob
import re

loop = asyncio.get_event_loop()


async def write_to_file(file, data):
    x = open(file, "w")
    x.write(data)
    print("Writing to -> " + str(file))
    x.close()


async def readfileLines(file):
    a = open(file, "r")
    to_return = a.readlines()
    a.close()
    return to_return


async def getBusesInFolder(folder):
    return glob.glob(folder)


async def clear_lats(lats):
    to_return = {}
    for i in range(len(lats)):
        to_return[i] = re.findall("\d+\.\d+", lats[i])
    return to_return


async def clear_longs(lngs):
    to_ret = {}
    for i in range(len(lngs)):
        to_ret[i] = re.findall("\d+\.\d+", lngs[i])
    return to_ret


async def clear_timestamps(tmps):
    to_ret = {}
    for i in range(len(tmps)):
        to_ret[i] = re.findall("[01][0-9]:[0-5][0-9]:[0-5][0-9]", tmps[i])
    return to_ret


async def getParsed():
    files = await getBusesInFolder("/home/palm/Desktop/buses/*")
    for file in files:
        print("Reading -> " + str(file))
        lats = {}
        lngs = {}
        timestamps = {}
        c = 9  # start from line 10
        i = 0
        lines = await readfileLines(file)

        while c < len(lines):
            try:
                lats[i] = lines[c]
                lngs[i] = lines[c + 1]
                timestamps[i] = lines[c + 2]
            except:
                print("error at -> " + file)
            i += 1
            c += 4
        lats = await clear_lats(lats)
        lngs = await clear_longs(lngs)
        timestamps = await clear_timestamps(timestamps)
        i = 0
        c = 0
        to_return = {}
        while i < len(lats):
            try:
                x = {
                    "from_lat": lats[i][0],
                    "from_lng": lngs[i][0],
                    "to_lat": lats[i + 1][0],
                    "to_lng": lngs[i + 1][0],
                    "time_a": timestamps[i][0],
                    "time_b": timestamps[i + 1][0],
                }
                to_return[c] = x
            except:
                print("error at " + file)
            i += 2
            c += 1
        data = json.dumps(to_return, indent=4, sort_keys=True)
        a = await write_to_file(file, data)
    print("done")


async def init():
    LineCodesList = await getParsed()


loop.run_until_complete(init())
loop.close()

