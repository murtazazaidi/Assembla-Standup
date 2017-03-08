#!/usr/bin/env python
# Author: Murtaza Zaidi
# File: standup.py, Help you fill your daily standup - the easy way

"""
 URLs for Assembla API v1
 ticket details: "https://api.assembla.com/v1/spaces/" + E_SPACE_ID +
 "/tickets/"+TICKET_ID+".json"
 user details: "https://api.assembla.com/v1/user.json"
 tickets: https://api.assembla.com/v1/spaces/_space_id/tickets/my_active.json
"""

import sys
import json
import requests
import time

# Fill in the blanks - START
E_SPACE_ID = ""

CLIENT = {
    "client_id": "",
    "client_secret": ""
}

TOKENS = {
    "access_token": "",
    "refresh_token": ""
}
# Fill in the blanks - END

SCRIPT_ACTIONS = {
    "post_report": "post_report",
    "generate_token": "generate_token"
}


# To refresh token, first hit pincode_url, get pin_code from there
# Then hit POST call at token_url with updated pin_code, get access
# and refresh_tokens
# Update token in the script and run script with param generate_token. Voila !!
def generate_refresh_token():
    """ Refreshes Auth Token """
    pincode_url = "https://api.assembla.com/authorization?client_id=" +\
    CLIENT['client_id'] + "&response_type=pin_code"
    token_url = "https://" + CLIENT['client_id'] + ":" +\
    CLIENT['client_secret'] +\
    "@api.assembla.com/token?grant_type=pin_code&pin_code=9391393dummypin"
    refresh_url = "https://" + CLIENT['client_id'] + ":" +\
    CLIENT['client_secret'] +\
    "@api.assembla.com/token?grant_type=refresh_token&refresh_token=" +\
     TOKENS["refresh_token"]
    print "Pincode URL: %s" % pincode_url
    print "Token URL: %s" % token_url
    result = requests.post(refresh_url)
    return result.json()


HEADERS = {
    "Authorization": "Bearer " + generate_refresh_token()["access_token"]
}

def get_tickets_associated():
    """ Gets tickets associated with user """
    url = "https://api.assembla.com/v1/spaces/" + E_SPACE_ID +\
    "/tickets/my_active.json"
    result = requests.get(url, headers=HEADERS)
    return result.json()

def get_user():
    """ Gets user details """
    url = "https://api.assembla.com/v1/user.json"
    result = requests.get(url, headers=HEADERS)
    return result.json()

def get_standup():
    """ Gets submitted standup for current date """
    # param = {
    #     "date": time.strftime("%d-%m-%Y")
    # }
    params = {}
    day = int(time.strftime("%d")) - 1
    month_year = time.strftime("/%m/%Y")
    if time.strftime("%A") == "Monday":
        day = int(day) - 2
        if day < 10:
            day = "0" + str(day)

    params["date"] = str(day) + month_year
    url = "https://api.assembla.com/v1/spaces/" + E_SPACE_ID +\
    "/standup_report.json"
    result = requests.get(url, headers=HEADERS, params=params)
    return result.text

def post_standup(name, data):
    """ Posts today's standup report """
    print "Posting Standup ..."
    HEADERS["Accept"] = "application/json"
    HEADERS["Content-Type"] = "application/json"
    url = "https://api.assembla.com/v1/spaces/" + E_SPACE_ID +\
    "/standup_report.json"
    payload = {
        "standup_report": {
            "what_i_will_do": data
        }
    }
    payload = json.dumps(payload)
    result = requests.post(url, headers=HEADERS, data=payload)
    print "Standup Posted Successfully for %s" % name
    print result.status_code

#### SCRIPT FUNCTIONALITY STARTS HERE ####

# default task
TASK = SCRIPT_ACTIONS["post_report"]
if len(sys.argv) > 1 and sys.argv[1] == SCRIPT_ACTIONS["generate_token"]:
    TASK = SCRIPT_ACTIONS["generate_token"]

if TASK == SCRIPT_ACTIONS["post_report"]:
    ACCEPT = []
    WORK = []
    REVIEW = []

    USERNAME = get_user().get("name")
    print "Hello " + USERNAME + "!!"
    print "Generating Report for %s" % time.strftime("%x")

    for ticket in get_tickets_associated():
        to_add = "#" + str(ticket.get("number")) + ": " + ticket.get("summary")
        status = ticket.get("status")
        if status == "Accepted":
            ACCEPT.append(to_add)
        elif status == "InWork":
            WORK.append(to_add)
        elif status == "Review":
            REVIEW.append(to_add)

    STANDUP = ""
    if len(WORK) > 0:
        STANDUP += "*Working on:*\r\n"
        for obj in WORK:
            STANDUP += obj + "\r\n"

    if len(REVIEW) > 0:
        STANDUP += "\r\n*Will review the following:*\r\n"
        for obj in REVIEW:
            STANDUP += obj + "\r\n"

    if len(ACCEPT) > 0:
        STANDUP += "\r\n*Will start working on*\r\n"
        for obj in ACCEPT:
            STANDUP += obj + "\r\n"

    print STANDUP

    USER_INPUT = raw_input("Should I post this standup for you (y/n): ")
    if USER_INPUT[0] in ["y", "Y"]:
        post_standup(name=USERNAME, data=STANDUP)
    else:
        print "Didn't post standup !!"

elif TASK == SCRIPT_ACTIONS["generate_token"]:
    print str(generate_refresh_token())
