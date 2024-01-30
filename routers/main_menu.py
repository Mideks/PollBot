import json

from aiogram import types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from aiogram import Router
from aiogram.utils.deep_linking import create_deep_link
from pysondb import db

import helpers
import markups
from callback_data import NavigateButton, BackButton, SelectSurveyTypeButton, ShowSurveyButton, StartSurveyButton, \
    QuestionTypeSelector
from entities import Survey, Question
from texts import texts
from states import CreateSurvey, CreateQuestion

router = Router()
surveys_db = db.getDb("db/surveys.json")
BOT_USERNAME= "cool_poll_test_bot"



@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await message.answer(text=texts['main'], reply_markup=markups.get_menu_keyboard())
    await state.clear()


async def send_error_message(callback_query: types.CallbackQuery, item_name: str) -> None:
    text = texts["messages.error"]
    # всегда в главное меню вернет
    await callback_query.answer(f"{item_name}\n\n{text}")


async def send_item_message(message: Message, state: FSMContext, item_name: str, **text_args) -> None:
    full_key = f"menu.{item_name}"
    # print(full_key)
    if full_key not in texts:
        print(f"Unknown location: {full_key}")
        # await send_error_message(message, item_name)
        return

    text = texts[full_key].format(**text_args)
    markup = await markups.get_item_markup(item_name, message, state, **text_args)
    #await message.edit_text(f"{text}", reply_markup=markup)
    await message.edit_text(f"{item_name}\n\n{text}", reply_markup=markup)


@router.inline_query()
async def inline_handler(inline_query: InlineQuery):
    text = ("С вами поделились ссылкой на опрос, пройдите его скорее!\n"
            f"{inline_query.query}")

    r = InlineQueryResultArticle(
            id=inline_query.query,  # ссылки у нас уникальные, потому проблем не будет
            title="Отправить ссылку",
            description=inline_query.query,
            input_message_content=InputTextMessageContent(message_text=text)
            )
    await inline_query.answer([r], is_personal=True)


@router.callback_query(QuestionTypeSelector.filter())
async def question_type_selector_handler(callback_query: CallbackQuery, callback_data: QuestionTypeSelector, state: FSMContext):
    question_type = callback_data.qestion_type

    await send_item_message(callback_query.message, state, "questions_edit.add_question.entering_title")

    await state.set_state(CreateQuestion.entering_title)
    await state.update_data(question_type=question_type)
    await state.update_data(message=callback_query.message)


async def add_question_to_survey(question, survey_id):
    survey_raw = surveys_db.getById(survey_id)
    survey = helpers.survey_load(survey_raw)
    survey.questions.append(question)
    helpers.survey_update(survey, surveys_db)


@router.message(CreateQuestion.entering_title)
async def entering_survey_title_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    question_title = message.text
    question_type = data["question_type"]

    await message.delete()
    await state.update_data(question_title=question_title)

    if question_type == "free_response":
        survey_id = data["survey_id"]

        await send_item_message(
            data["message"], state,
            "questions_edit.add_question.ready",
            survey_id = survey_id
        )
        question = Question(title=question_title)


        await add_question_to_survey(question, survey_id)

        await state.set_state(state=None)

    elif question_type == "options":
        await send_item_message(
            data["message"], state,
            "questions_edit.add_question.entering_options",
            question_title=question_title)
        await state.set_state(CreateQuestion.entering_options)


@router.message(CreateQuestion.entering_options)
async def entering_survey_title_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    question_options = message.text
    survey_id = data.get("survey_id")
    question_title = data.get("question_title")

    await message.delete()
    # await state.update_data(question_options=question_options)

    await send_item_message(
        data["message"], state,
        "questions_edit.add_question.ready",
        survey_id=survey_id
    )

    question = Question(title=question_title,
                        options=question_options.split("\n"))

    await add_question_to_survey(question, survey_id)

    await state.set_state(state=None)


@router.callback_query(NavigateButton.filter(F.go_to == "survey.share"))
async def show_survey_callback_handler(callback_query: CallbackQuery, callback_data: NavigateButton,
                                       state: FSMContext):
    location = callback_data.go_to
    data = await state.get_data()
    survey_id = data.get("survey_id")
    link=create_deep_link(BOT_USERNAME, "start", f"{survey_id}")
    await send_item_message(callback_query.message, state, location, link=link, survey_id=survey_id)


@router.callback_query(NavigateButton.filter(F.go_to == "survey.delete"))
async def show_survey_callback_handler(callback_query: CallbackQuery, callback_data: NavigateButton,
                                       state: FSMContext):
    location = callback_data.go_to
    data = await state.get_data()
    survey_id = data['survey_id']
    surveys_db.deleteById(survey_id)
    await send_item_message(callback_query.message, state, location)


@router.callback_query(ShowSurveyButton.filter())
async def show_survey_callback_handler(callback_query: CallbackQuery, callback_data: ShowSurveyButton,
                                       state: FSMContext):
    survey_id = callback_data.survey_id
    survey_raw = surveys_db.getById(survey_id)
    survey = helpers.survey_load(survey_raw)

    await send_item_message(callback_query.message, state, "survey", survey_type=survey.survey_type,
                            survey_title=survey.title)

    await state.update_data(survey_id=survey_id)


@router.callback_query(NavigateButton.filter(F.go_to == "create_survey.step-1"))
async def category_callback_handler(callback_query: CallbackQuery, callback_data: NavigateButton, state: FSMContext):
    item_name = callback_data.go_to
    await send_item_message(callback_query.message, state, item_name)
    await state.set_state(CreateSurvey.entering_title)
    await state.update_data(message=callback_query.message)


@router.message(CreateSurvey.entering_title)
async def entering_survey_title_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    survey_title = message.text
    await send_item_message(data["message"], state, "create_survey.step-2", survey_title=survey_title)

    await message.delete()
    await state.set_state(CreateSurvey.selecting_type)
    await state.update_data(survey_title=survey_title)


@router.callback_query(SelectSurveyTypeButton.filter())
async def selecting_survey_type_handler(
        callback_query: CallbackQuery, callback_data: SelectSurveyTypeButton, state: FSMContext):
    data = await state.get_data()
    survey_type = callback_data.survey_type
    survey_title = data["survey_title"]

    await state.update_data(survey_type=survey_type)
    await send_item_message(
        callback_query.message, state, "create_survey.step-3",
        survey_type=survey_type, survey_title=survey_title)

    owner = callback_query.message.chat.id
    survey = Survey(survey_type=survey_type, title=survey_title, owner=owner)
    survey_id = helpers.survey_save(survey, surveys_db)

    await state.update_data(survey_id=survey_id)
    await state.set_state(None)
    # await  state.set_state()


@router.callback_query(NavigateButton.filter())
async def category_callback_handler(callback_query: CallbackQuery, callback_data: NavigateButton, state: FSMContext):
    item_name = callback_data.go_to

    if callback_data.is_locked:
        await send_error_message(callback_query, item_name)
        return

    await send_item_message(callback_query.message, state, item_name)
    await callback_query.answer()


@router.callback_query(BackButton.filter())
async def back_callback_handler(callback_query: types.CallbackQuery, callback_data: BackButton, state: FSMContext):
    item_name = callback_data.back_location
    await send_item_message(callback_query.message, state, item_name)
    await callback_query.answer()
    await state.clear()
