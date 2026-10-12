
import json
import urllib.request
import urllib.error


def get_data(url):
    try:
        response = urllib.request.urlopen(url, timeout=10)
        data = json.loads(response.read().decode("utf-8"))
        response.close()
        return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


with open("requirements.txt", "r") as file:
    packages = [line.strip() for line in file if line.strip()]

total = len(packages)
not_found = 0
bad_versions = 0
oldest = None

for package in packages:
    name, version = package.split("==", 1)

    try:
        url = "https://pypi.org/pypi/" + name + "/json"
        data = get_data(url)

        if data is None:
            not_found += 1
            continue

        url = "https://pypi.org/pypi/" + name + "/" + version + "/json"
        data = get_data(url)

        if data is None:
            bad_versions += 1
            continue

        files = data.get("urls", [])

        if len(files) == 0:
            continue

        date = files[0].get("upload_time")

        if not date:
            continue

        if oldest is None or date < oldest["date"]:
            oldest = {
                "name": name,
                "version": version,
                "year": date[:4],
                "date": date
            }

    except Exception as e:
        print("Error checking", name, ":", e)

print("Dependencies checked:", total)
print("Packages not on PyPI:", not_found)
print("Versions not on PyPI:", bad_versions)

if oldest is not None:
    print(
        "Oldest pinned release:",
        oldest["name"] + "==" + oldest["version"],
        "(" + oldest["year"] + ")"
    )
else:
    print("Oldest pinned release: None")
