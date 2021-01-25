import json
import re
from typing import List

import requests
from bs4 import BeautifulSoup
from data_grabber_yt.src.img_grab import get_data


def get_first_30(url):
    """
    Gets first 30 video IDs from a YT channel.
    :param url: URL must be of form https://www.youtube.com/channel/xxx/videos
    :return: set of video IDs
    """
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"There was an error: {r.status_code}")
    soup = BeautifulSoup(r.text, "lxml")
    script = [x for x in soup("script") if "ytInitialData =" in str(x)][0].string
    data = json.loads(script.replace("var ytInitialData = ", "")[:-1])
    ids = set()
    for line in json.dumps(data, indent=1).split("\n"):
        if "videoId" in line:
            if "[" in line:
                continue
            line = re.sub(r"[,\"':]|videoId*", "", line)
            ids.add(line.strip())
    return ids


def get_from_html(html):
    """
    Gets all video URLs from a YT html segment.
    :param html: raw html
    :return: set of video URLs
    """
    soup = BeautifulSoup(html, "lxml")
    return {"https://youtube.com" + x.get("href") for x in soup.find_all(id="video-title")}


def run_yt_grab(videos: List[str]):
    for i, video in enumerate(videos):
        print(f"Running video {i}")
        with open("index.txt", "w") as fp:
            fp.write(str(i))
        get_data(video, interval=600)


html_path = "./thingy.html"
with open(html_path) as fp:
    data = get_from_html(fp.read())
run_yt_grab(list(data))
