from typing import Literal

from aiogram.filters.callback_data import CallbackData


class MenuButton(CallbackData, prefix="menu_button"):
    is_locked: bool = False


class NavigateButton(MenuButton, prefix="navigate"):
    go_to: str = ""


class BackButton(MenuButton, prefix="back"):
    back_location: str


class SelectSurveyTypeButton(MenuButton, prefix="type"):
    survey_type: str


class ShowSurveyButton(MenuButton, prefix="show_survey"):
    survey_id: int


class StartSurveyButton(MenuButton, prefix="start_survey"):
    survey_id: int


class QuestionTypeSelector(MenuButton, prefix="start_survey"):
    qestion_type: Literal["options", "free_response"]


class QuestionAnswer(MenuButton, prefix="answer"):
    answer: int