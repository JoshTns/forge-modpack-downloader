'''
    Auto download mods
    from a modlist using
    manifest and modlist
'''


import json
import requests
import time
import os


# Find string between two strings
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
    

# Find string after string
def find_after( s, first ):
    try:
        start = s.index( first ) + len( first )
        return s[start:len(s)]
    except ValueError:
        return ""
    

# Fancy way of formatting a number how we want
def GetFormattedInt(guhh: str, lenn: int) -> str:

    guh = str(guhh)
    if len(guh) == lenn:
        return guh

    retstr = guh
    for i in range(lenn - len(guh)):
        retstr += " "

    return retstr


# Generate the list of modinfo dicts
def GenerateModInfoList() -> list:

    # List of projectid + fileid
    projectids = []
    fileids    = []

    # Read the manifest file to get data
    with open('manifest.json') as f:
        d = json.load(f)
        for item in d["files"]:
            projectids.append(item["projectID"])
            fileids.append(item["fileID"])

    # Confirm they are the same size
    if len(projectids) == len(fileids):
        print("Got a matching number of names, projects and files!")
    else:
        print("Data mismatch! Count is: \n" + "\nProjectIDs: " + str(len(projectids)) + "\nFileIDs: " + str(len(fileids)))

    # No mismatch, make the retlist
    retlist = []
    for i in range(len(projectids)):
        retlist.append({
            "projectID": projectids[i],
            "fileID": fileids[i]
        })
    return retlist


# Get a download url for a given modID and fileID
def GetDownloadUrlForMod(modID: str, fileID: str, token: str) -> str:

    hheaders = {
        'Accept': 'application/json',
        'x-api-key': token
    }

    # Track the number of times we failed
    FailCount = 0

    # Incase we don't get a response, we want to try again
    while True:

        r = requests.get(f'https://api.curseforge.com/v1/mods/{modID}/files/{fileID}/download-url', headers = hheaders)

        # Fail count is too high, give up
        if FailCount > 3:
            print("Failed to download mod, moving on..")
            return None

        # If we didn't get a good response, try again
        if (r.status_code != 200):
            print(f"Failed getting url, code {r.status_code}, trying again!")
            FailCount += 1
            time.sleep(4)
            continue

        return r.json()["data"]


# Get our token
OurToken = input("Please enter your Forge studios API token: ")

# Verify the mods folder exists
if not os.path.exists("./mods"):
    os.makedirs("./mods")

# Get info
ModList = GenerateModInfoList()

# How many mods we got?
TotalMods = len(ModList)
CurrMod = 0

# Download all the mods
for mod in ModList:

    # Get the download url 
    url = GetDownloadUrlForMod(mod["projectID"], mod["fileID"], OurToken)

    # Failed? Move on
    if url == None:
        continue

    # Python trickery to extrack name from the url
    guh = str(mod["fileID"])
    fileidd = int(guh[len(guh) - 3:])
    modname = find_between(url, f"/{fileidd}/", ".jar")

    print(f"{GetFormattedInt(CurrMod, len(str(TotalMods)))} of {TotalMods}  |  Downloading {modname}")

    r = requests.get(url, allow_redirects=True)
    
    # Check we got a good response code
    if r.status_code != 200:
        print(f"[ERROR] Error downloading mod {modname} using url {url}")

    open(f'./mods/{modname.strip().replace(" ", "-")}.jar', 'wb').write(r.content)
    CurrMod += 1

# Do the math
print(f"Done downloading {TotalMods} mods, failed to download {TotalMods - CurrMod} mods")