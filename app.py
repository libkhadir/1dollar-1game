import requests
import json

def save_checkpoint(value):
    with open(".process", "w") as file:
        file.write(str(value))


def get_checkpoint():
    with open(".process", "r") as file:
        return int(file.read())


def get_applications():
    return requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v0002/").json()


def filter_by_price(appids):
    priceDict = {}
    threshold = len(appids) - 1
    checkpoint = get_checkpoint()
    if checkpoint == threshold:
        save_checkpoint(0)
        checkpoint = 0
    appsParam = ""
    for index, app in enumerate(appids):
        if index > 0 and index > checkpoint and (index == threshold or index % 100 == 0):
            try:
                priceResponse = requests.get("https://store.steampowered.com/api/appdetails?filters=price_overview&appids={}".format(appsParam)).json()
            except:
                priceResponse = None
            appsParam = ""
            if priceResponse is None:
                continue
            else:
                for appKey in priceResponse:
                    if 'data' in priceResponse[appKey] \
                            and 'price_overview' in priceResponse[appKey]['data'] \
                            and priceResponse[appKey]['data']['price_overview']['final'] <= 100:
                        priceDict[appKey] = priceResponse[appKey]['data']['price_overview']
            if index % 1000 == 0:
                save_checkpoint(index)
                break
        else:
            appsParam = appsParam + str(app) if len(appsParam) == 0 else appsParam + "," + str(app)
    return priceDict

if __name__ == "__main__":
    apps = get_applications()

    appDict = {}
    for app in apps['applist']['apps']:
        appDict[app["appid"]] = app["name"]
    appids = appDict.keys()

    priceDict = filter_by_price(appids)

    for appKey in priceDict:
        priceDict[appKey]['name'] = appDict[int(appKey)]

    previous = {}
    with open("result.json", "r") as inputfile:
        json.load(inputfile)
    result = previous | priceDict

    with open("result.json", "w") as outfile:
        json.dump(result, outfile)

    for appKey in priceDict:
        with open("export.csv", "a") as outfile:
            outfile.write(appKey + ";" + priceDict[appKey]['name'] + ";" + priceDict[appKey]['final_formatted'] + "\n")