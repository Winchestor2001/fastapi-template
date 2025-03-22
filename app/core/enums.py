import enum


class OrderBy(str, enum.Enum):
    id = "id"
    created_at = "created_at"
    updated_at = "updated_at"


class Lang(str, enum.Enum):
    uz = "uz"
    ru = "ru"
    en = "en"

    @classmethod
    def values(cls):
        return {item.value for item in cls}