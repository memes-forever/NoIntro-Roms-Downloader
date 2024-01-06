# Qt
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

# Helpers
from _constants import *
from _platforms import PlatformsHelper
from _settings import SettingsHelper
from _debug import *


class CacheGenerator():
  class PlatformWorker(QObject):
    platform = []
    finished = pyqtSignal(str)


    def __init__(self, platform: dict, output_cache_json: dict):
      super().__init__(None)
      self.platform = platform
      self.output_cache_json = output_cache_json


    def run(self):
      self.id_name = self.platform['name']
      self.format = self.platform['format']
      self.sub_dir = self.platform['sub_dir']
      self.parts = self.platform.get('parts', 1)
      self.short_link = self.platform['short_link']

      if 'parts' not in self.platform: # SINGLE PART
        self.url = f"https://archive.org/details/{self.short_link}&output=json"
        self.output_cache_json[self.id_name] = {}
        DebugHelper.print(DebugType.TYPE_DEBUG, f"Processing <{self.id_name}>", "CACHE")
        self._ProcessPart(part_id=self.short_link)
      elif 'parts' in self.platform: # MULTI PART
        self.output_cache_json[self.id_name] = {}
        
        DebugHelper.print(DebugType.TYPE_DEBUG, f"Processing <{self.id_name}>", "CACHE")
        for i in range(1, self.parts+1):
          parts_id = str(self.short_link).replace('$$', str(i))
          self.url = f"https://archive.org/details/{parts_id}&output=json"
          self._ProcessPart(part_id=parts_id, part_number=i)
      self.finished.emit(self.id_name)


    def _ProcessPart(self, part_id: str, part_number: int = 1):
      import requests, json
      try:
        content_request = requests.get(self.url).content
        content_json = json.loads(content_request)
        part_files = content_json['files']
        for file in part_files:
          # if str(file).find(self.format) != -1:
          output_file = {
            "source_id": part_id,
            "size": int(part_files[file]['size']),
            "md5": part_files[file]['md5'],
            "crc32": part_files[file]['crc32'],
            "sha1": part_files[file]['sha1'],
            "format": part_files[file]['format'],
            "sub_dir": self.sub_dir,
          }
          self.output_cache_json[self.id_name][file[1:]] = output_file  # -(len(self.format)+1)
      except: pass


  app: QApplication = None
  parent: QSplashScreen = None
  output_cache_json = {}
  threads = []
  workers = []
  download_completed = 0


  def __init__(self, app: QApplication, parent: QSplashScreen) -> None:
    self.app = app
    self.parent = parent


  def run(self):
    import pickle

    # Create workers and run them in separate threads (for speed)
    [self.threads.append(QThread()) for _ in range(len(ARCHIVE_PLATFORMS_DATA))]

    for i in range(len(ARCHIVE_PLATFORMS_DATA)):
      self.workers.append(CacheGenerator.PlatformWorker(ARCHIVE_PLATFORMS_DATA[i], self.output_cache_json))
      self.workers[i].moveToThread(self.threads[i])
      self.threads[i].started.connect(self.workers[i].run)
      self.workers[i].finished.connect(self._updateMessage)
      self.workers[i].finished.connect(self.threads[i].quit)
      self.threads[i].finished.connect(self.threads[i].deleteLater)
      self.threads[i].start()

    # Wait until workers finished
    while self.download_completed != len(self.threads): self.app.processEvents()
    
    # Sort the data before writing
    temp_dict = sorted(self.output_cache_json)
    new_output_cache_json = {}
    for i in range(len(temp_dict)):
      temp_name = temp_dict[i]
      for j in range(len(self.output_cache_json)):
        output_name = list(self.output_cache_json)[j]
        if temp_name == output_name:
          new_output_cache_json[temp_name] = {}
          new_output_cache_json[temp_name] = self.output_cache_json[temp_name]
    self.output_cache_json = new_output_cache_json
    
    # And finally write to file
    with open("database_cache.dat", "wb") as fp: pickle.dump(self.output_cache_json, fp)


  def _updateMessage(self, platform_name: str):
    self.download_completed += 1
    self.parent.showMessage(f"({self.download_completed}/{len(self.threads)}) [{platform_name}] completed.",
      color=Qt.GlobalColor.white,
      alignment=(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
    )



class RomDownload(QThread):
  platform_name = ""
  rom_name = ""
  rom_url = ""
  rom_format = ""

  setTotalProgress = pyqtSignal(int)
  setCurrentProgress = pyqtSignal(int)
  setCurrentSpeed = pyqtSignal(str)
  setCurrentJob = pyqtSignal(str)
  succeeded = pyqtSignal()

  def __init__(self, settings: SettingsHelper, platforms: PlatformsHelper, platform: str, rom_index: int) -> None:
    super().__init__()

    import requests
    from urllib.parse import quote

    self.settings = settings
    self.platform_name = platform
    self.rom_name = platforms.getRomName(platform, rom_index)
    self.rom_format = platforms.getRom(platform, self.rom_name)['format']
    self.sub_dir = platforms.getRom(platform, self.rom_name)['sub_dir']
    self.rom_url = f"https://archive.org/download/{platforms.getRom(platform, self.rom_name)['source_id']}/{quote(self.rom_name)}"
    DebugHelper.print(DebugType.TYPE_INFO, f"Downloading [{self.platform_name}] {self.rom_name}", "downloader")
    # with open(os.path.join(settings.get('download_path'), f"{self.rom_name}.{self.rom_format}"), "wb") as of:
    #   DebugHelper.print(DebugType.TYPE_DEBUG, f"Downloading from [{self.rom_url}]", "downloader")
    #   of.write(requests.get(self.rom_url).content)

    self._file_path = os.path.join(settings.get('download_path'), self.sub_dir, f"{self.rom_name}")
    self._link = self.rom_url
    self._session = requests

  def run(self):
    import pathlib, time
    start = time.time()
    url, filename, session = self._link, self._file_path, self._session

    self.setCurrentJob.emit(self.rom_name)

    response = session.get(url, stream=True, allow_redirects=True)
    if response.status_code != 200:
      response.raise_for_status()  # Will only raise for 4xx codes, so...
      raise RuntimeError(f"Request to {url} returned status code {response.status_code}")

    file_size = int(response.headers.get('Content-Length', 0))

    if os.path.exists(filename):
      if pathlib.Path(filename).stat().st_size == file_size:
        DebugHelper.print(DebugType.TYPE_INFO, f'File exist! {filename}')
        return
      pr = f'File with error, redownload! '
    else:
      pr = ''

    path = pathlib.Path(filename).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    desc = "(Unknown total file size) " if file_size == 0 else ""
    desc += pr

    self.setTotalProgress.emit(file_size)

    all_size = 0
    with open(filename, 'wb') as file:
      for data in response.iter_content(chunk_size=1024):
        size = file.write(data)
        all_size += size
        self.setCurrentProgress.emit(all_size)
        self.setCurrentSpeed.emit(f"{round((all_size // (time.time() - start))/1000, 3)} Kb/s")

    if self.settings.get('unzip'):
      self.setCurrentSpeed.emit(f"Unzip ...")
      Unzip(self._file_path)

    self.setCurrentSpeed.emit(f"Done.")
    self.succeeded.emit()


class Unzip():
  def __init__(self, full_path: str) -> None:
    path = os.path.join(*tuple(os.path.split(full_path)[:-1]))
    DebugHelper.print(DebugType.TYPE_INFO, f"Unzipping [{full_path}]...", "unzip")
    try:
      from py7zr import SevenZipFile
      SevenZipFile(full_path).extractall(path)
    except:
      import zipfile
      with zipfile.ZipFile(full_path, 'r') as zip_ref:
        zip_ref.extractall(path)
    os.remove(full_path)


class Tools():
  def convertSizeToReadable(size: int) -> str:
    if size < 1000:
      return '%i' % size + 'B'
    elif 1000 <= size < 1000000:
      return '%.1f' % float(size/1000) + ' KB'
    elif 1000000 <= size < 1000000000:
      return '%.1f' % float(size/1000000) + ' MB'
    elif 1000000000 <= size < 1000000000000:
      return '%.1f' % float(size/1000000000) + ' GB'
    elif 1000000000000 <= size:
      return '%.1f' % float(size/1000000000000) + ' TB'


  def isCacheValid(validity_days: int) -> bool:
    import os
    from datetime import datetime, timedelta

    cache_mdate = os.path.getmtime("database_cache.dat")
    cache_mdate = datetime.fromtimestamp(cache_mdate)
    today_date = datetime.today()
    expiration_date = cache_mdate + timedelta(days=validity_days)

    if expiration_date > today_date: return True
    else: return False
