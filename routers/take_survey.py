from aiogram import types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from aiogram import Router
from pysondb import db

import callback_data
import helpers
import markups
from callback_data import StartSurveyButton, NavigateButton
from entities import Question
from states import TakeSurvey
from texts import texts

router = Router()
surveys_db = db.getDb("db/surveys.json")


@router.message(CommandStart(deep_link=True))
async def deeplink_handler(message: Message, command: CommandObject, state: FSMContext) -> None:
    await state.clear()
    survey_id = int(command.args)
    survey_raw = surveys_db.getById(survey_id)

    survey = helpers.survey_load(survey_raw)
    location = "take_survey.welcome"
    text = texts[f"menu.{location}"].format(survey_title=survey.title)
    markup = await markups.get_item_markup(location, message, state, survey_id=survey_id)
    await message.answer(text, reply_markup=markup)


@router.callback_query(StartSurveyButton.filter())
async def start_survey_handler(callback_query: CallbackQuery, callback_data: StartSurveyButton,
                               state: FSMContext):
    survey_id = callback_data.survey_id
    survey = helpers.get_survey(surveys_db, survey_id)

    await state.set_state(TakeSurvey.in_survey)
    await state.update_data(survey_id=survey_id)
    await state.update_data(message=callback_query.message)
    await send_next_question_message(state)

    # await callback_query.answer("Ошибка")


@router.message(TakeSurvey.in_survey)
async def question_answer_message_handler(message: Message, state: FSMContext):
    # todo: save user answers
    data = await state.get_data()
    question_number = data.get("question_number")
    survey_id = data.get("survey_id")
    answer = message.text

    # just for test
    await message.answer(
        f"Опрос №{survey_id}\n"
        f"Получен ответ на {question_number + 1} вопрос:\n"
        f"Ответ: {answer}")

    await send_next_question_message(state)


@router.callback_query(callback_data.QuestionAnswer.filter())
async def question_answer_callback_handler(callback_query: CallbackQuery, callback_data: callback_data.QuestionAnswer,
                                           state: FSMContext):
    # todo: save user answers
    data = await state.get_data()
    question_number = data.get("question_number")
    survey_id = data.get("survey_id")
    survey = helpers.get_survey(surveys_db, survey_id)
    answer = callback_data.answer

    # just for test
    await callback_query.message.answer(
        f"Опрос №{survey_id}\n"
        f"Получен ответ на {question_number + 1} вопрос:\n"
        f"Ответ: {survey.questions[question_number].options[answer]}")

    await send_next_question_message(state)


async def send_next_question_message(state: FSMContext) -> None:
    data = await state.get_data()
    message: Message = data.get("message")

    survey_id = data.get("survey_id")
    survey = helpers.get_survey(surveys_db, survey_id)

    question_number = data.get("question_number", -1) + 1
    await state.update_data(question_number=question_number)

    if question_number >= len(survey.questions):
        await message.edit_text("Спасибо за участие в опросе!\n"
                                "Вы можете создать свой тест, просто напишите /start")
        await state.set_state(None)
        return

    question = survey.questions[question_number]

    markup = markups.get_question_markup(question)
    text = f"Вопрос {question_number + 1}/{len(survey.questions)}\n"
    # todo: заменить на проверку типа вопроса
    if len(question.options) == 0:
        text += (f"Напишите ответ на следующий вопрос:\n\n"
                 f"{question.title}")
    else:
        text += (f"Выберите ответ на следующий вопрос:\n\n"
                 f"{question.title}")

    await message.edit_text(text, reply_markup=markup)
