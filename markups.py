import json

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from pysondb import db
from aiogram.types import Message

from entities import Survey, Question
# from texts import buttons
from texts import texts
from callback_data import NavigateButton, BackButton, SelectSurveyTypeButton, ShowSurveyButton, StartSurveyButton, \
    QuestionTypeSelector, QuestionAnswer


async def get_item_markup(item_name: str, message: Message, state: FSMContext, **args) -> InlineKeyboardMarkup:
    if item_name == "main":
        return get_menu_keyboard()
    elif item_name == "surveys_menu":
        return get_surveys_menu_markup(message.chat.id)
    elif item_name == "create_survey.step-1":
        return get_back_markup("surveys_menu")
    elif item_name == "create_survey.step-2":
        return get_survey_types_markup()
    elif item_name == "create_survey.step-3":
        return get_survey_create_confirm_markup()
    elif item_name == "questions_edit.main":
        return await get_survey_questions_edit_markup(state)
    elif item_name == "survey":
        return get_survey_markup()
    elif item_name == "survey.share":
        return get_survey_share_markup(**args)
    elif item_name == "survey.edit":
        return get_survey_edit_markup()
    elif item_name == "survey.stats":
        pass
    elif item_name == "survey.delete":
        return get_back_markup("surveys_menu")
    elif item_name == "take_survey.welcome":
        return get_take_survey_welcome_markup(**args)
    elif item_name == "questions_edit.add_question":
        return get_questions_edit_markup()
    elif item_name == "questions_edit.delete_question":
        pass
    elif item_name == "questions_edit.list_questions":
        pass
    elif item_name == "questions_edit.add_question.ready":
        return get_new_question_or_end_markup(**args)
    else:
        print(f"{item_name} не найдена клавиатура")


def get_new_question_or_end_markup(survey_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Да, добавить ещё вопрос", callback_data=NavigateButton(go_to="questions_edit.add_question"))
    builder.button(text="❌ Нет, хватит", callback_data=ShowSurveyButton(survey_id=survey_id))
    builder.adjust(1, 1)
    return builder.as_markup()


def get_questions_edit_markup() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎯 С выбором ответа", callback_data=QuestionTypeSelector(qestion_type="options"))
    builder.button(text="✍️ Свободный ответ", callback_data=QuestionTypeSelector(qestion_type="free_response"))
    builder.add(get_back_button("surveys_menu"))
    builder.adjust(2, 1)
    return builder.as_markup()

def get_take_survey_welcome_markup(survey_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Готов", callback_data=StartSurveyButton(survey_id=survey_id))
    return builder.as_markup()


def get_survey_edit_markup() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔐 Изменить название", callback_data=NavigateButton(is_locked=True))
    builder.button(text="❓ Редактировать вопросы", callback_data=NavigateButton(go_to="questions_edit.main"))
    builder.add(get_back_button("surveys_menu"))
    builder.adjust(1)
    return builder.as_markup()


def get_survey_share_markup(link: str, survey_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 Поделиться", switch_inline_query=link)
    builder.button(text="🔙 Меню", callback_data=ShowSurveyButton(survey_id=survey_id))

    builder.adjust(1)
    return builder.as_markup()


def get_survey_markup() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔗 Поделиться тесотм", callback_data=NavigateButton(go_to="survey.share"))
    builder.button(text="📊 Статистика", callback_data=NavigateButton(go_to="survey.stats", is_locked=True))
    builder.button(text="✏️ Редактирование", callback_data=NavigateButton(go_to="survey.edit"))
    builder.button(text="❌ Удалить", callback_data=NavigateButton(go_to="survey.delete"))
    builder.add(get_back_button("surveys_menu"))
    builder.adjust(1)
    return builder.as_markup()


async def get_survey_questions_edit_markup(state: FSMContext) -> InlineKeyboardMarkup:
    data = await state.get_data()
    survey_id = data.get("survey_id")

    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить вопрос", callback_data=NavigateButton(go_to="questions_edit.add_question"))
    builder.button(text="🗑 Удалить вопрос", callback_data=NavigateButton(go_to="questions_edit.delete_question"))
    builder.button(text="📋 Список вопросов", callback_data=NavigateButton(go_to="questions_edit.list_questions"))
    builder.button(text="🔙 Меню", callback_data=ShowSurveyButton(survey_id=survey_id))

    builder.adjust(1)
    return builder.as_markup()


def get_survey_create_confirm_markup() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, всё верно", callback_data=NavigateButton(go_to="questions_edit.main"))
    builder.adjust(1)
    return builder.as_markup()


def get_user_surveys(user_id: int):
    surveys_db = db.getDb("db/surveys.json")
    surveys_raw = surveys_db.reSearch("owner", rf"{user_id}")
    surveys = (Survey.Schema().loads(json.dumps(i)) for i in surveys_raw)

    return surveys


def get_survey_types_markup() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="Тест", callback_data=SelectSurveyTypeButton(survey_type="Тест"))
    builder.button(text="Опрос", callback_data=SelectSurveyTypeButton(survey_type="Опрос"))

    builder.adjust(1, 2)

    return builder.as_markup()


def get_surveys_menu_markup(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="📊 Создать опрос", callback_data=NavigateButton(go_to="create_survey.step-1"))

    existing_surveys = get_user_surveys(user_id)
    for survey in existing_surveys:
        id_ = survey.id
        id_ = survey.id
        text = survey.title
        builder.button(text=text, callback_data=ShowSurveyButton(survey_id=id_))

    builder.adjust(1, 2)
    # builder.add(get_back_button("main"))

    return builder.as_markup()


def get_menu_keyboard() -> InlineKeyboardMarkup:
    builder = \
        (InlineKeyboardBuilder()
         .button(text="〽️ Пройти опрос", callback_data=NavigateButton(go_to="take_survey", is_locked=True))
         .button(text="🧑‍💻 Мои опрос", callback_data=NavigateButton(go_to="surveys_menu"))
         .button(text="❔ Помощь", callback_data=NavigateButton(go_to="help", is_locked=True))

         .adjust(2, 1))

    return builder.as_markup()


def get_back_markup(location: str) -> InlineKeyboardMarkup:
    builder = \
        (InlineKeyboardBuilder()
         .add(get_back_button(location))
         .adjust(1))

    return builder.as_markup()


def get_back_button(location: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=f"🔙  Назад", callback_data=BackButton(back_location=location).pack())
    # return InlineKeyboardButton(text=f"🔙  Назад ({location})", callback_data=BackButton(back_location=location).pack())


def get_question_markup(question: Question) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if len(question.options) == 0:
        return builder.as_markup()


    for i in range(len(question.options)):
        option = question.options[i]
        answer = i

        builder.button(text=option, callback_data=QuestionAnswer(answer=answer))

    builder.adjust(1)
    return builder.as_markup()