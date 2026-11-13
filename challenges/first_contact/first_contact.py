
#!/usr/bin/env python3

import socket
import re
from datetime import datetime, timedelta, timezone

import numpy as np
from skyfield.api import EarthSatellite, wgs84, load

HOST = "154.57.164.71"
PORT = 35478

ELEVATION_LIMIT = 30.0
STEP_SECONDS = 5
DURATION_HOURS = 24

ts = load.timescale()


def get_elevation(satellite, station, dt):
    t = ts.from_datetime(dt)
    difference = satellite - station
    alt, az, distance = difference.at(t).altaz()
    return alt.degrees


def refine_crossing(satellite, station, left, right, rising):
    """Binary search for the exact 30-degree crossing."""

    for _ in range(25):
        middle = left + (right - left) / 2

        left_above = (
            get_elevation(satellite, station, left)
            >= ELEVATION_LIMIT
        )

        mid_above = (
            get_elevation(satellite, station, middle)
            >= ELEVATION_LIMIT
        )

        if left_above == mid_above:
            left = middle
        else:
            right = middle

    return left + (right - left) / 2


def calculate_passes(line1, line2, latitude, longitude):

    satellite = EarthSatellite(
        line1[:69],
        line2[:69],
        "HTB SAT",
        ts
    )

    station = wgs84.latlon(
        latitude_degrees=latitude,
        longitude_degrees=longitude
    )

    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=DURATION_HOURS)

    times = []
    current = start

    while current <= end:
        times.append(current)
        current += timedelta(seconds=STEP_SECONDS)

    elevations = [
        get_elevation(satellite, station, t)
        for t in times
    ]

    passes = []
    rise_time = None

    for i in range(len(times) - 1):

        previous = elevations[i] >= ELEVATION_LIMIT
        following = elevations[i + 1] >= ELEVATION_LIMIT

        # Satellite rises above 30 degrees
        if not previous and following:
            rise_time = refine_crossing(
                satellite, station,
                times[i], times[i + 1], True
            )

        # Satellite falls below 30 degrees
        elif previous and not following:

            if rise_time is not None:
                set_time = refine_crossing(
                    satellite, station,
                    times[i], times[i + 1], False
                )

                passes.extend([rise_time, set_time])
                rise_time = None

    return passes


def extract_challenge(data):

    text = data.decode(errors="ignore")

    tle1 = re.search(r"(?m)^1 [^\r\n]+", text)
    tle2 = re.search(r"(?m)^2 [^\r\n]+", text)

    station = re.search(
        r"\(Lat,Long\):\s*"
        r"([-+]?\d+(?:\.\d+)?)\s*,\s*"
        r"([-+]?\d+(?:\.\d+)?)",
        text
    )

    if not (tle1 and tle2 and station):
        raise ValueError("Could not extract TLE or station coordinates")

    return (
        tle1.group(0).strip()[:69],
        tle2.group(0).strip()[:69],
        float(station.group(1)),
        float(station.group(2))
    )


def main():

    with socket.create_connection((HOST, PORT)) as sock:

        sock.settimeout(60)

        buffer = b""

        while True:

            # Read until the challenge asks for an answer
            while b"When will it be visible next?>" not in buffer:

                chunk = sock.recv(4096)

                if not chunk:
                    print(buffer.decode(errors="replace"))
                    return

                buffer += chunk

            print(buffer.decode(errors="replace"))

            try:
                line1, line2, lat, lon = extract_challenge(buffer)

                print("\n[+] Satellite TLE extracted")
                print(f"[+] Ground station: {lat}, {lon}")

                passes = calculate_passes(
                    line1, line2, lat, lon
                )

                answer = " ".join(
                    t.strftime("%Y-%m-%dT%H:%M:%SZ")
                    for t in passes
                )

                print("[+] Predicted visibility windows:")

                for i in range(0, len(passes), 2):
                    print(
                        passes[i].strftime("%Y-%m-%dT%H:%M:%SZ"),
                        passes[i + 1].strftime("%Y-%m-%dT%H:%M:%SZ")
                    )

                if not answer:
                    print("[-] No complete visibility windows found")

                print("\n[+] Sending:", answer)

                sock.sendall((answer + "\n").encode())

            except Exception as e:
                print("[-] Error:", e)
                return

            buffer = b""


if __name__ == "__main__":
    main()
