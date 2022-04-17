from os.path import exists

with open("cache/skinName", "r") as f:
    skinName = f.read()
    print(skinName)
    f.close()


def getSkinFilename(fileName: str):
    if exists(f"skins/{skinName}/{fileName}"):
        return f"skins/{skinName}/{fileName}"
    else:
        return f"skins/Default/{fileName}"
