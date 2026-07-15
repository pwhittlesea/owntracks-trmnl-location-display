from typing import Annotated
from fastapi import BackgroundTasks, FastAPI, Header
from pydantic import BaseModel
from decimal import Decimal
from html2image import Html2Image
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from math import sin, sqrt, asin, cos, radians

import json
import boto3
import logging
import datetime


# TODO remove hard coded list of people
usernames = ["phill", "sam_w"]
# Locations
locations = [
    {"venue": "Arcade Workshop", "lat": 52.042864, "lon": -2.376695},
    {"venue": "Arts", "lat": 52.041029, "lon": -2.377984},
    {"venue": "Bench", "lat": 52.040525822108805, "lon": -2.3755373730148506},
    {"venue": "Bodgeham-on-Wye", "lat": 52.04122799874966, "lon": -2.3756540184625123},
    {"venue": "com:LAAG", "lat": 52.04328480344839, "lon": -2.375319064727364},
    {"venue": "Drop-in Workshop", "lat": 52.0415113, "lon": -2.37670327},
    {"venue": "Family Workshop", "lat": 52.04077636, "lon": -2.37771729},
    {
        "venue": "Forge & Craft / HackWimbledon",
        "lat": 52.04324498273803,
        "lon": -2.374558309851807,
    },
    {"venue": "Foundry Zero", "lat": 52.040685174287376, "lon": -2.3771225134481995},
    {
        "venue": "Friends of the Moon",
        "lat": 52.04233013444053,
        "lon": -2.3756379552964972,
    },
    {
        "venue": "Furry High Commission",
        "lat": 52.042565988104656,
        "lon": -2.3751908859429136,
    },
    {
        "venue": "Glasgow Hackerspace",
        "lat": 52.04225450312194,
        "lon": -2.375299956134171,
    },
    {"venue": "Irish Embassy", "lat": 52.042066542255355, "lon": -2.375355265776193},
    {"venue": "Lasertag", "lat": 52.04352193271029, "lon": -2.3761647324126045},
    {
        "venue": "Lock Picking Village",
        "lat": 52.03995156285009,
        "lon": -2.3782719475608474,
    },
    {
        "venue": "Loitering Within Tent",
        "lat": 52.03988232283791,
        "lon": -2.3782872140040183,
    },
    {"venue": "Lounge", "lat": 52.04190332, "lon": -2.37819773},
    {"venue": "Maths Village", "lat": 52.04323517880556, "lon": -2.374975935438556},
    {"venue": "Milliways", "lat": 52.042549545934605, "lon": -2.376155388881557},
    {
        "venue": "Ministry of Chaos",
        "lat": 52.042497987731224,
        "lon": -2.3756102125883842,
    },
    {
        "venue": "Nationwide village",
        "lat": 52.040627864924176,
        "lon": -2.3766409584789585,
    },
    {"venue": "NoobSpace", "lat": 52.040059684972874, "lon": -2.3788046477521902},
    {
        "venue": "Nottingham Hackspace",
        "lat": 52.04198458781886,
        "lon": -2.3755091779832753,
    },
    {"venue": "NullSector", "lat": 52.04356, "lon": -2.37692},
    {"venue": "NullSector Night Market", "lat": 52.0435045, "lon": -2.3769458},
    {"venue": "Outside the Bar", "lat": 52.0413622, "lon": -2.3780529},
    {"venue": "Robot Arms (Bar)", "lat": 52.0413752, "lon": -2.3775637},
    {
        "venue": "Scottish Consulate",
        "lat": 52.04217658855947,
        "lon": -2.375312869894657,
    },
    {
        "venue": "South London Makerspace",
        "lat": 52.04180622077425,
        "lon": -2.375680762025837,
    },
    {"venue": "Stage A", "lat": 52.0395553, "lon": -2.3786758},
    {"venue": "Stage B", "lat": 52.0419, "lon": -2.37664},
    {"venue": "Stage C", "lat": 52.0405, "lon": -2.37765},
    {"venue": "Stage D", "lat": 52.0422, "lon": -2.377592},
    {
        "venue": "Tekhnē-cal Village",
        "lat": 52.04028161496325,
        "lon": -2.378171671045834,
    },
    {
        "venue": "Traditional Crafts",
        "lat": 52.04021573219916,
        "lon": -2.378190036110169,
    },
    {
        "venue": "Unaffiliated Village",
        "lat": 52.04088122563019,
        "lon": -2.3762667465684046,
    },
    {"venue": "Workshop 1 (Furry High Commission)", "lat": 52.04259, "lon": -2.37515},
    {"venue": "Workshop 2 (Field-FX)", "lat": 52.04292731, "lon": -2.37594559},
    {
        "venue": "Workshop 3 (Hardware Hacking Area)",
        "lat": 52.04179935,
        "lon": -2.37539965,
    },
    {"venue": "Workshop 4 (Maths Village)", "lat": 52.04308967, "lon": -2.37495635},
    {
        "venue": "Workshop 5 (Nationwide Village)",
        "lat": 52.04055045,
        "lon": -2.37660994,
    },
    {"venue": "Workshop 6 (Bodgeham-on-Wye)", "lat": 52.04111064, "lon": -2.3757523},
    {"venue": "Main Gate", "lat": 52.038722, "lon": -2.378396},
    {"venue": "Construction Workshop", "lat": 52.039717, "lon": -2.376525},
    {"venue": "Family Lounge", "lat": 52.040851, "lon": -2.377425},
    {"venue": "Welfare", "lat": 52.040961, "lon": -2.378718},
    {"venue": "Planetarium", "lat": 52.0415273, "lon": -2.376931},
    {"venue": "Greenhouse", "lat": 52.041836, "lon": -2.378432},
    {"venue": "Volunteer Kitchen", "lat": 52.042218, "lon": -2.376869},
    {"venue": "Badge", "lat": 52.042146, "lon": -2.375106},
    {"venue": "Manchampton", "lat": 52.040623, "lon": -2.375605},
]


class Location(BaseModel):
    _type: str | None = None
    # acc Accuracy of the reported location in meters without unit (iOS,Android/integer/meters/optional)
    acc: int | None = None
    # batt Device battery level (iOS,Android/integer/percent/optional)
    batt: int | None = None
    # bs Battery Status 0=unknown, 1=unplugged, 2=charging, 3=full (iOS, Android)
    bs: int | None = None
    # lat latitude (iOS,Android/float/degree/required)
    lat: float | None = None
    # lon longitude (iOS,Android/float/degree/required)
    lon: float | None = None
    # tid Tracker ID used to display the initials of a user (iOS,Android/string/optional) required for http mode
    tid: str | None = None
    # tst UNIX epoch timestamp in seconds of the location fix (iOS,Android/integer/epoch/required)
    tst: int | None = None


app = FastAPI(docs_url=None, redoc_url=None)
dynamo = boto3.resource("dynamodb").Table("emf-trmnl-locations")
s3 = boto3.client("s3")


@app.post("/owntrack/locations", status_code=200)
async def push_location(
    location: Location,
    background_tasks: BackgroundTasks,
    x_authenticateduser: Annotated[str | None, Header()] = None,
):
    dynamo.put_item(
        Item={
            "username": x_authenticateduser,
            "tst": location.tst,
            "latitude": float_to_decimal(location.lat),
            "longitude": float_to_decimal(location.lon),
            "accuracy": location.acc,
            "battery_level": location.batt,
            "battery_status": ["unknown", "unplugged", "charging", "full"][location.bs],
            "tracker_id": location.tid,
        }
    )

    print(
        f"{location.tst}: Got location from user {location.tid}/{x_authenticateduser}: {location.lat}, {location.lon} (accuracy {location.acc}m) and battery status: {location.batt}% ({location.bs})"
    )
    background_tasks.add_task(get_locations)
    return []


@app.get("/owntrack/locations", status_code=200)
async def get_locations():
    final_locations = []

    for username in usernames:
        response = dynamo.query(
            KeyConditionExpression=Key("username").eq(username),
            ScanIndexForward=False,  # descending order
            Limit=1,
        )
        latest_position = response["Items"][0] if response["Items"] else None
        if latest_position is not None:
            person_lat = latest_position["latitude"]
            person_lon = latest_position["longitude"]

            distances = []
            for location in locations:
                location_lat = location["lat"]
                location_lon = location["lon"]
                distance = calculate_distance(
                    person_lat, person_lon, location_lat, location_lon
                )
                distances.append({"venue": location["venue"], "distance": distance})

            # Sort by distance, nearest first
            distances.sort(key=lambda x: x["distance"], reverse=False)

            # Assume 50 meter circles around venues
            closest_venue = distances[0]["venue"]
            distance_m = round(distances[0]["distance"] * 1000, 2)

            if distance_m > 50:
                message = "The Outer Wilds"
            else:
                message = closest_venue

            final_locations.append(
                {
                    "username": username,
                    "message": message,
                    "lat": decimal_to_float(person_lat),
                    "lon": decimal_to_float(person_lon),
                    "nearest": {
                        "name": closest_venue,
                        "distance": distance_m,
                    },
                }
            )

    generate_image(final_locations)
    generate_json(final_locations)

    return []


def generate_image(final_locations: dict):
    hti = Html2Image(
        size=(800, 480),
        output_path="/tmp",
        custom_flags=["--no-sandbox"],
        disable_logging=True,
    )
    with open("/code/app/display.html", "r") as file:
        html = file.read()
        tableContent = ""
        for data in final_locations:
            tableContent += "<tr>"
            tableContent += f"<td><span class=\"title\">{data['username']}</span></td>"
            if data["message"] != data["nearest"]["name"]:
                tableContent += f"<td><span class=\"title\">Near-ish {data['nearest']['name']} ({data['nearest']['distance']}m)</span></td>"
            else:
                tableContent += f"<td><span class=\"title\">{data['nearest']['name']} ({data['nearest']['distance']}m)</span></td>"
            tableContent += "</tr>"
        html = html.replace("TABLE_CONTENT", tableContent)
        hti.screenshot(html_str=html, save_as="dashboard.png")

    try:
        s3.upload_file(
            "/tmp/dashboard.png",
            "trmnl-images-179627667852-eu-west-2-an",
            "dashboard.png",
        )
    except ClientError as e:
        logging.error(e)

    print("Updated dashboard.png")


def generate_json(final_locations: dict):
    json_payload = {
        "statusCode": 200,
        "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "body": final_locations,
    }
    with open("/tmp/dashboard.json", "w") as f:
        json.dump(json_payload, f)
    try:
        s3.upload_file(
            "/tmp/dashboard.json",
            "trmnl-images-179627667852-eu-west-2-an",
            "dashboard.json",
        )
    except ClientError as e:
        logging.error(e)

    print("Updated dashboard.json")


def float_to_decimal(value):
    if isinstance(value, float):
        return Decimal(str(value))
    return value


def decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km
