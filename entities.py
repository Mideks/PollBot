import json
from pysondb import db

import marshmallow
from marshmallow_dataclass import dataclass

from dataclasses import field


from typing import Optional

from pysondb.db import JsonDatabase


class BaseSchema(marshmallow.Schema):
    class Meta:
        unknown = marshmallow.EXCLUDE


@dataclass(base_schema=BaseSchema)
class Media:
    media_type: str
    source: str


@dataclass(base_schema=BaseSchema)
class Question:
    title: str = field(default="")
    options: list[str] = field(default_factory=list)
    comments: list[str] = field(default_factory=list)
    correct_answer: int = field(default=None)
    media: list[Media] = field(default_factory=list)


@dataclass(base_schema=BaseSchema)
class Survey:
    id: Optional[int] = field(default=None)
    survey_type: str = field(default="survey")
    owner: int = field(default=None)
    title: str = field(default="no")
    questions: Optional[list[Question]] = field(default_factory=list)
    answer_visibility: Optional[bool] = field(default=False)


@dataclass(base_schema=BaseSchema)
class CompletedSurvey:
    survey_id: int
    answers: list[int]


@dataclass(base_schema=BaseSchema)
class User:
    user_id: int
    #owned_surveys: list[int]
    completed_surveys: list[CompletedSurvey]


'''s = Survey()
a = db.getDb("test.json")

# сохранение
j = json.loads(Survey.Schema().dumps(s))
print(type(j))
a.add(j)

# загрузка
o=a.getAll()
s2: Survey = Survey.Schema().loads(json.dumps(o[0]))
print(s2.id)
print(a.getAll())
'''