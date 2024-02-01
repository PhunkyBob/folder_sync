from dataclasses import dataclass
import datetime
from enum import Enum
from typing import List, Optional


class PathType(Enum):
    UNKNOWN = -1
    FILE = 0
    FOLDER = 1

    def __str__(self):
        return self.name if self != PathType.UNKNOWN else ""


class SharedStatus(Enum):
    UNKNOWN = -1
    NOT_SHARED = 0
    SHARED = 1

    def __str__(self):
        return self.name if self != SharedStatus.UNKNOWN else ""


@dataclass
class UploadedFile:
    name: str = ""
    local_label: str = ""
    local_path_type: PathType = PathType.UNKNOWN
    local_full_path: str = ""
    local_size: Optional[int] = None
    local_date: Optional[datetime.datetime] = None
    mega_account: str = ""
    mega_path_type: PathType = PathType.UNKNOWN
    mega_full_path: str = ""
    mega_size: Optional[int] = None
    mega_date: Optional[datetime.datetime] = None
    # mega_id: str = ""
    mega_shared: SharedStatus = SharedStatus.UNKNOWN
    mega_link: str = ""
    status: str = ""

    @staticmethod
    def get_fields() -> List:
        return [field.name for field in UploadedFile.__dataclass_fields__.values()]
