from dataclasses import dataclass, field
import os


@dataclass
class FileItem:
    path: str
    original_name: str = ""
    new_name: str = ""
    extracted_fields: dict[str, str] = field(default_factory=dict)
    status: str = "ok"

    def __post_init__(self):
        if not self.original_name:
            self.original_name = os.path.basename(self.path)
        if not self.new_name:
            self.new_name = self.original_name

    def dirname(self) -> str:
        return os.path.dirname(self.path)

    def new_path(self) -> str:
        return os.path.join(self.dirname(), self.new_name)

    @staticmethod
    def get_ext(filename: str) -> str:
        return os.path.splitext(filename)[1]

    @staticmethod
    def get_stem(filename: str) -> str:
        return os.path.splitext(filename)[0]

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "original_name": self.original_name,
            "new_name": self.new_name,
            "extracted_fields": self.extracted_fields,
            "status": self.status,
        }
