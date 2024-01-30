from aiogram.fsm.state import StatesGroup, State


class CreateSurvey(StatesGroup):
    entering_title = State()
    selecting_type = State()


class CreateQuestion(StatesGroup):
    selecting_type = State()
    entering_title = State()
    entering_options = State()

class TakeSurvey(StatesGroup):
    in_survey = State()