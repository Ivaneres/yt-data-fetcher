import os
import subprocess
import time
from concurrent.futures.thread import ThreadPoolExecutor

from youtube_dl.postprocessor.ffmpeg import FFmpegPostProcessor
from youtube_dl.utils import sanitize_filename


class FFmpegImageExtractorPP(FFmpegPostProcessor):
    def __init__(self, downloader=None, interval=1, outdir="./img", start=None, duration=None, ar=1, width=None,
                 height=None, delete_video=True):
        """
        The start and end parameters will only affect ffmpeg postprocessing - the entire video will still be downloaded.
        It is possible to change this if necessary: see https://unix.stackexchange.com/questions/230481/how-to-download-portion-of-video-with-youtube-dl-command

        This was not implemented for this specific postprocessor as a design decision, as for the use-case of fetching
        data from ML most of the video will be used.
        :param delete_video:
        :param downloader:
        :param interval: interval between each frame in seconds
        :type interval: int
        :param outdir: output directory name
        :type outdir: str
        :param start: start time UNIMPLEMENTED
        :type start: Union[int, str], optional
        :param duration: duration to record for  UNIMPLEMENTED
        :type duration: Union[int, str], optional
        :param ar: aspect ratio. Images will be cropped to this.
        :type ar: int
        :param width: preferred output image width
        :type width: int, optional
        :param height: preferred output image height
        :type height: int, optional
        :param delete_video: delete video after finish
        :type delete_video: bool
        """
        self._interval = interval
        self._outdir = outdir
        self._start = start  # unimplemented
        self._duration = duration  # unimplemented
        self._ar = ar
        self._width = width
        self._height = height
        self._delete_video = delete_video
        super().__init__(downloader)

    def run(self, information):
        video_path = f'{self._outdir}/{sanitize_filename(information["title"])}'
        if not os.path.exists(self._outdir):
            os.mkdir(self._outdir)
        if os.path.exists(video_path):
            print("[extractor] Folder with this name already exists. Stopping")
            return [], information
        else:
            os.mkdir(video_path)
        path = information['filepath']
        options = ['-vf']
        if self._width is not None or self._height is not None:
            if self._width is None:
                self._width = self._height
            elif self._height is None:
                self._height = self._width
            vid_height = information["height"]
            vid_width = information["width"]
            new_width = vid_height * self._ar
            crop_pos_x = abs(vid_width - new_width) // 2 if self._ar >= 1 else 0
            options.append(f'crop={new_width}:{vid_height}:{crop_pos_x}:0,scale={self._width}:{self._height}')
        timer = time.time()
        print(f"[extractor] Starting conversion")
        images = 0
        with ThreadPoolExecutor(max_workers=10) as executor:
            for i in range(0, information["duration"] // self._interval):
                cmd = ["ffmpeg", "-accurate_seek", "-ss", str(i * self._interval), "-i", path, "-frames:v", "1"] + \
                      options + \
                      [f"{video_path}/{i}.jpg"]
                executor.submit(subprocess.call, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                images += 1
        print(f"[extractor] Produced {images} images in {round(time.time() - timer, 3)}s")
        if self._delete_video:
            return [information['filepath']], information
        else:
            return [], information
