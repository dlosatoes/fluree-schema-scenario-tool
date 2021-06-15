#!/usr/bin/python3
import requests
import subprocess
r = requests.get("https://api.github.com/repos/fluree/ledger/releases")
latest_date = ""
latest_release = None
for release in r.json():
    if release["published_at"] > latest_date:
        latest_date = release["published_at"]
        latest_release = release
command = ["/usr/bin/git", "clone", "--depth", "1", "--branch", latest_release["tag_name"], "https://github.com/fluree/ledger.git"]
with open("fluree.version", "w") as flureeversion:
    flureeversion.write(latest_release["tag_name"])
print(" ".join(command))
subprocess.run(command)
