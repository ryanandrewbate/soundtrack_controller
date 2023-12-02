from dotenv import load_dotenv
import os
import requests
import json
import argparse

account_token = ""
account_email = ""
account_password = ""
login_token = ""
zone_id = ""
schedule_id = ""
parser = None
args = None
api_endpoint = "https://api.soundtrackyourbrand.com/v2"
api_headers = {
    'Content-Type' : 'application/json'
}

def initEnv():
    load_dotenv()
    
    global account_token
    global account_email
    global account_password
    global zone_id
    global schedule_id

    account_token = os.getenv('ACCOUNT_TOKEN')
    account_email = os.getenv('ACCOUNT_EMAIL')
    account_password = os.getenv('ACCOUNT_PASSWORD')
    zone_id = os.getenv('ZONE_ID')
    schedule_id = os.getenv('SCHEDULE_ID')

def doQuery(query):
    req_data = {    
        "query": query
    }
    
    query_headers = api_headers
    if(login_token != ""):
        query_headers['Authorization'] = "Bearer %s" % login_token
    
    
    response = requests.post(api_endpoint, json = req_data, headers = query_headers)
    if(response.status_code == 200):
        print("---- Query success")
        return response
    else:
        print("---- Query failed")

def getLoginToken():
    req_query = """mutation LoginUser {
            loginUser(
                input: {email: "%s", password: "%s"}
            ) {
                token
            }
        }""" % (account_email, account_password)
    
    response = doQuery(req_query)
    
    if response != None:
        return response.json()['data']['loginUser']['token']

def hasAuthToken():
    return account_token != ""

def hasAuthCredentials():
    return (account_email != "") and (account_password != "")

def initAuth():
    global login_token

    if(hasAuthToken() == False and hasAuthCredentials() == True):
        print("No auth token, using credentials, log in")
        login_token = getLoginToken()

    print("********\n\n\n")

def doSetScheduleRequest(zoneId,scheduleId):
    req_query = """mutation SetPlayFrom {
            setPlayFrom(
                input: {soundZone: "%s", source: "%s"}
            ) {
                playFrom {
                    ... on Schedule {
                        id
                        name
                        createdAt
                        updatedAt
                        snapshot
                        description
                        shortDescription
                        presentAs
                    }
                }
            }
        }
        """ % (zoneId, scheduleId)
    
    response = doQuery(req_query)


def doPauseZoneRequest(zoneId):
    req_query = """
        mutation Pause {
            pause(
                input: {soundZone: "%s"}
            ) {
                soundZone
            }
        } """ % (zoneId)

    response = doQuery(req_query)

def doPlayZoneRequest(zoneId):
    req_query = """
        mutation Play {
            play(
                input: {soundZone: "%s"}
            ) {
                soundZone
            }
        } """ % (zoneId)

    response = doQuery(req_query)

def schedule():
    print("Setting schedule...")
    print("Zone ID: %s" % zone_id)
    print("Schedule ID: %s" % schedule_id)
    
    doSetScheduleRequest(zone_id,schedule_id)


def play():
    print("Playing...")
    print("Zone ID: %s" % zone_id)
    
    doPlayZoneRequest(zone_id)

def pause():
    print("Pausing...")
    print("Zone ID: %s" % zone_id)

    doPauseZoneRequest(zone_id)

def initArgs(functionMap):
    global parser
    global args
    global schedule_id

    parser = argparse.ArgumentParser()
    
    parser.add_argument('command', choices=functionMap.keys())
    parser.add_argument("--schedule", nargs=1)
    args = parser.parse_args()
    
    
    if(args.schedule is not None):
        schedule_id = args.schedule[0]




def main():
    functionMap = {
        'play' : play,
        'pause' : pause,
        'schedule' : schedule
    }
    initArgs(functionMap)
    initEnv()
    initAuth()

    # Gogogogo
    func = functionMap[args.command]
    func()

    #doQueueSchedule(schedule_id)


main()