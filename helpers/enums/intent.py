from enum import Enum


class Intent(Enum):
    GENRE = "Genre"
    KEYWORD = "Keyword"
    PERSON = "Person"
    TITLE = "Title"
    NONE_INTENT = "NoneIntent"
