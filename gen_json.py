#
# Copyright (C) 2023, lifehackerhansol
# SPDX-License-Identifier: Apache-2.0
#

import json
import os
import sys

from datetime import datetime
from hashlib import sha256
from time import mktime

def build_json(file: str, url: str):
    checksum = sha256()
    # template response
    # assume anyone using this is unofficial ROM, since official
    # devices do their own thing :D
    response = {
        "datetime": 0,
        "filename": "",
        "id": "",
        "romtype": "unofficial",
        "size": 0,
        "url": "",
        "version": ""
    }
    # get file name first
    response["filename"] = os.path.basename(file)
    # get variables from file name
    project, version, date, romtype, device = response["filename"].split('-')
    # workaround above line causing device to be `device.zip`
    device = device.split('.')[0]

    # datetime: UNIX timestamp of build date in file name
    # generally one would read /system/build.prop, but I'm lazy
    response["datetime"] = int(mktime(datetime.strptime(date, '%Y%m%d').timetuple()))

    # ID: we're using SHA256 checksum as ID
    # aligns with official LOS
    with open(file, "rb") as f:
        # maybe this is a waste of memory
        checksum.update(f.read())
        response["id"] = checksum.hexdigest()

    # size: size of the update in bytes
    response["size"] = os.path.getsize(file)

    # URL: download location
    # Get base URL from function argument, then just append the file name
    response["url"] = f'{url}/{response["filename"]}'

    # version: ROM version
    response["version"] = version

    output = {
        "response": [
            response
        ]
    }
    with open(f"api/{device}.json", 'w') as f:
        json.dump(output, f, indent=2)

    return


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"usage: {sys.argv[0]} /path/to/builds <base url>")
        print(f"note this script expects all device builds to be uploaded to same base URL")
        sys.exit()

    for i in os.listdir(sys.argv[1]):
        if os.path.isfile(f"{sys.argv[1]}/{i}"):
            build_json(f"{sys.argv[1]}/{i}", sys.argv[2])

