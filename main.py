import binascii
import json
import random
import uvicorn
import os

from Crypto.Cipher import AES
from fastapi import FastAPI, Response, Request

dns_file_path = "dns.json"

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


def get_custom_value(number):
    values = {
        0: "19fe",
        1: "164f",
        2: "25cb",
        3: "55ec",
        4: "945d",
        5: "888c",
        6: "02de",
        7: "199e",
        8: "423f",
        9: "978d",
    }

    number_string = str(number)
    result = ""

    for digit in number_string:
        if int(digit) in values:
            result += values[int(digit)]

    return result


def encrypt(data, key):
    iv = b"R5tghjg^999(@#Gg"
    cipher = AES.new(key.encode("utf-8")[:32], AES.MODE_CBC, iv)

    padding_length = 16 - (len(data) % 16)
    data += chr(padding_length) * padding_length

    encrypted = cipher.encrypt(data.encode("utf-8"))
    return binascii.hexlify(encrypted).decode("utf-8")


def generate_random_key():
    return "".join(str(random.randint(0, 9)) for _ in range(32))


def fake_encryption():
    characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    random_string = ""
    characters_length = len(characters)
    for _ in range(500):
        random_string += characters[random.randint(0, characters_length - 1)]
    return random_string


def run_encryption(data):
    hex_data = binascii.hexlify(data.encode("utf-8")).decode("utf-8")
    return hex_data[::-1]


def generate_tivimate_response(user_id="default"):
    with open(dns_file_path, encoding="utf-8") as file:
        dns_data = json.load(file)

    portals = []
    if user_id in dns_data:
        for i, dns in enumerate(dns_data[user_id]):
            portals.append({"id": i + 1, "name": dns["title"], "url": dns["url"]})

    final_data = {
        "portals": portals,
        "intro_url": "",
        "message_one": "",
        "message_two": "",
        "message_three": "",
    }

    sulanga = json.dumps(final_data)

    en_key = generate_random_key()
    encrypted_data = get_custom_value(en_key) + encrypt(sulanga, en_key)

    output_json = {
        "dns_backup": fake_encryption(),
        "portals": encrypted_data,
        "url_backup": fake_encryption(),
    }

    final_json = run_encryption(json.dumps(output_json))

    return final_json


@app.get("/")
async def root(response: Response):
    response.headers["Content-Type"] = "application/json; charset=UTF-8"
    return Response(content=generate_tivimate_response(), media_type="application/json")


@app.get("/{user_id}/")
async def user_dns(user_id: str, response: Response):
    response.headers["Content-Type"] = "application/json; charset=UTF-8"
    return Response(
        content=generate_tivimate_response(user_id), media_type="application/json"
    )


def decode_char(c):
    c = c.lower()
    if "0" <= c <= "9":
        return int(c)
    elif "a" <= c <= "z":
        return ord(c) - ord("a") + 10
    else:
        raise ValueError(f"Invalid character for conversion: {c}")


def string_to_number(s):
    if not s:
        return 103651

    result = 0
    factor = 16
    threshold = 16

    for char in s:
        try:
            value = decode_char(char)
            if value <= threshold:
                result = result * factor + value
        except ValueError as e:
            print(
                f"Warning: Skipping invalid character '{char}' in string \"{s}\" due to error: {e}"
            )
            continue

    return result


def get_check_response(request: Request, response: Response):
    x = request.headers.get("x-parse-app-data", "")
    magic_number = string_to_number(x)

    data = {
        "result": {
            "newApkUrl": "",
            "newVersionName": "",
            "shouldUpdateGooglePlayVersion": False,
            "forceAutoUpdate": False,
            "stagedRolloutDays": 0,
            "isActivated": True,
            "deviceName": "TV",
            "account": "ez@golden.industries",
            "responseToken": magic_number,
        }
    }

    response.headers["Content-Type"] = "application/json; charset=UTF-8"
    return Response(content=json.dumps(data), media_type="application/json")


@app.post("/check.php")
async def check(request: Request, response: Response):
    return get_check_response(request, response)

@app.post("/{user_id}/check.php")
async def check(request: Request, response: Response):
    return get_check_response(request, response)


if __name__ == "__main__":
    if not os.path.exists(dns_file_path):
        example_data = {
            "default": [
                {"title": "Server 1", "url": "http://exemple1.com"},
                {"title": "Server 2", "url": "http://exemple2.com"},
            ],
            "user1": [
                {"title": "Custom Server 1", "url": "http://custom1.com"},
                {"title": "Custom Server 2", "url": "http://custom2.com"},
            ],
        }

        with open(dns_file_path, "w", encoding="utf-8") as file:
            json.dump(example_data, file, indent=4)

        print(
            f'Example file "{dns_file_path}" created with sample user configurations.'
        )

    uvicorn.run(app, host="127.0.0.1", port=1337)
