from typing import List

import youtube_dl
from bs4 import BeautifulSoup

from postprocess import FFmpegImageExtractorPP


def get_from_html(html):
    """
    Gets all video URLs from a YT html segment.
    :param html: raw html
    :return: set of video URLs
    """
    soup = BeautifulSoup(html, "lxml")
    return {"https://youtube.com" + x.get("href") for x in soup.find_all(id="video-title")}


def extract_videos(urls: List[str]):
    ydl_ops = {
        "format": "bestvideo[ext=webm]/bestvideo"
    }
    with youtube_dl.YoutubeDL(ydl_ops) as ydl:
        ydl.add_post_processor(FFmpegImageExtractorPP(width=768, height=768, interval=10, delete_video=True))
        ydl.download(urls)


html_path = "./thingy.html"
with open(html_path) as fp:
    data = get_from_html(fp.read())
extract_videos(list(data)[:100])
