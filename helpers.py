import json

from entities import Survey
from pysondb.db import JsonDatabase


def survey_load(data: dict) -> Survey:
    return Survey.Schema().loads(json.dumps(data))


def survey_save(o: Survey, db: JsonDatabase) -> int:
    j = json.loads(Survey.Schema().dumps(o))
    return db.add(j)


def survey_update(o: Survey, db: JsonDatabase) -> int:
    j = json.loads(Survey.Schema().dumps(o))
    return db.updateById(o.id, j)


def get_survey(db: JsonDatabase, survey_id: int):
    survey_raw = db.getById(survey_id)
    return survey_load(survey_raw)
