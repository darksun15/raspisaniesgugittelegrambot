# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor, types
from config import api_key
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import requests
from bs4 import BeautifulSoup as bs
import json
import os
import datetime


bot = Bot(api_key)

dp = Dispatcher(bot, storage=MemoryStorage())

class get_url_state(StatesGroup):
    inst = State()
    fos = State()
    course = State()
    group = State()


@dp.message_handler(commands='reg', state=None)
async def start_get_url_isnt(message: types.message):
    url_rasp = json.load(open("url.json"))
    id_tg = str(message.chat.id)
    if id_tg in url_rasp:
        await bot.send_message(message.chat.id, 'Твои группа и id уже связаны, если хочешь изменить это, воспользуйся справкой /help')
    else:
        await bot.send_message(message.chat.id, 'Привет. Помоги мне узнать в какой группе ты учишься')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
        }
        url = "https://rasp.sgugit.ru/?ii=1&fi=1&c=1&"
        r = requests.get(url=url, headers=headers)
        soup = bs(r.text, "lxml")
        inst = soup.find_all("a", class_="name_inst")
        inst_sel = {}
        inst_id = 0
        res_list = ""
        res_list += ("Отправь номер иститута: \n\n")
        for link_all_inst in inst:
            link_inst = f'https://rasp.sgugit.ru/{link_all_inst.get("href")}'
            name_of_institut = link_all_inst.find("div", class_="name_of_institut").text.strip()
            inst_id += 1
            res_list +=(f"{inst_id} - {name_of_institut} \n")
            inst_sel[inst_id] = {
                "link_inst": link_inst,
                "name_of_institut": name_of_institut
            }
        await bot.send_message(message.chat.id, res_list)
        await get_url_state.inst.set()

@dp.message_handler(state=get_url_state.inst)
async def get_url_inst(message: types.message, state: FSMContext):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
    }
    url = "https://rasp.sgugit.ru/?ii=1&fi=1&c=1&"
    r = requests.get(url=url, headers=headers)
    soup = bs(r.text, "lxml")
    inst = soup.find_all("a", class_="name_inst")
    inst_sel = {}
    inst_id = 0
    for link_all_inst in inst:
        link_inst = f'https://rasp.sgugit.ru/{link_all_inst.get("href")}'
        name_of_institut = link_all_inst.find("div", class_="name_of_institut").text.strip()
        inst_id += 1
        inst_sel[inst_id] = {
            "link_inst": link_inst,
            "name_of_institut": name_of_institut
        }
    if message.text in ["/reg", "/start", "/link", "/help", "/day", "/week"]:
        await state.reset_state()
    else:
        try:
            answer = int(message.text)
            url = inst_sel[answer].get("link_inst")
            await state.update_data(url=url)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
            }
            r = requests.get(url=url, headers=headers)
            soup = bs(r.text, "lxml")
            fos_sel = {}
            inst_id = 0
            res_list = ""
            res_list += ("Отправь номер формы обучения: \n\n")
            inst = soup.find("div", class_="for_list_inst_selected").find("div", class_="for_list_inst_selected").find(
                "ul").find_all("a")
            for form_of_study in inst:
                fos_url = f'https://rasp.sgugit.ru/{form_of_study.get("href")}'
                fos_name = form_of_study.text.strip()
                inst_id += 1
                res_list += (f"{inst_id} - {fos_name} \n")
                fos_sel[inst_id] = {
                    "fos_url": fos_url,
                    "fos_name": fos_name
                }
            await bot.send_message(message.chat.id, res_list)
            await get_url_state.fos.set()
        except:
            await bot.send_message(message.chat.id, "Ошибка. Проверь правильность")


@dp.message_handler(state=get_url_state.fos)
async def get_url_fos(message: types.message, state: FSMContext):
    data = await state.get_data()
    url = data.get("url")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
    }
    r = requests.get(url=url, headers=headers)
    soup = bs(r.text, "lxml")
    fos_sel = {}
    inst_id = 0
    inst = soup.find("div", class_="for_list_inst_selected").find("div", class_="for_list_inst_selected").find(
        "ul").find_all("a")
    for form_of_study in inst:
        fos_url = f'https://rasp.sgugit.ru/{form_of_study.get("href")}'
        fos_name = form_of_study.text.strip()
        inst_id += 1
        fos_sel[inst_id] = {
            "fos_url": fos_url,
            "fos_name": fos_name
        }
    if message.text in ["/reg", "/start", "/link", "/help", "/day", "/week"]:
        await state.reset_state()
    else:
        try:
            answer = int(message.text)
            url = fos_sel[answer].get("fos_url")
            await state.update_data(url=url)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
            }
            r = requests.get(url=url, headers=headers)
            soup = bs(r.text, "lxml")
            course_sel = {}
            inst_id = 0
            res_list = ""
            res_list += ("Отправь номер курса, где 1 - первый курс, 5 - пятый: \n")
            inst = soup.find("form", class_="table-filter").find_previous("ul").find_all("a")
            for course in inst:
                course_url = f'https://rasp.sgugit.ru/{course.get("href")}'
                course_num = course.text.strip()
                inst_id += 1
                course_sel[inst_id] = {
                    "course_url": course_url,
                    "course_num": course_num
                }
            await bot.send_message(message.chat.id, res_list)
            await get_url_state.course.set()
        except:
            await bot.send_message(message.chat.id, "Ошибка. Проверь правильность ввода")

@dp.message_handler(state=get_url_state.course)
async def get_url_course(message: types.message, state: FSMContext):
    data = await state.get_data()
    url = data.get("url")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
    }
    r = requests.get(url=url, headers=headers)
    soup = bs(r.text, "lxml")
    course_sel = {}
    inst_id = 0
    inst = soup.find("form", class_="table-filter").find_previous("ul").find_all("a")
    for course in inst:
        course_url = f'https://rasp.sgugit.ru/{course.get("href")}'
        course_num = course.text.strip()
        inst_id += 1
        course_sel[inst_id] = {
            "course_url": course_url,
            "course_num": course_num
        }
    if message.text in ["/reg", "/start", "/link", "/help", "/day", "/week"]:
        await state.reset_state()
    else:
        try:
            answer = int(message.text)
            url = course_sel[answer].get("course_url")
            await state.update_data(url=url)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
            }
            r = requests.get(url=url, headers=headers)
            soup = bs(r.text, "lxml")
            group_sel = {}
            inst_id = 0
            res_list = ""
            res_list += ("Отправь цифру, соответствующую твоей группе \n")
            inst = soup.find("form", class_="table-filter").find_all("a")
            for group in inst:
                group_name = group.text.strip()
                group_url = f'https://rasp.sgugit.ru/{group.get("href")}'
                inst_id += 1
                res_list += (f"{inst_id} - {group_name}   \n")
                group_sel[inst_id] = {
                    "group_url": group_url,
                    "group_name": group_name
                }
            await bot.send_message(message.chat.id, res_list)
            await get_url_state.group.set()
        except:
            await bot.send_message(message.chat.id, "Ошибка. Проверь правильность ввода")

@dp.message_handler(state=get_url_state.group)
async def get_url_group(message: types.message, state: FSMContext):
    data = await state.get_data()
    url = data.get("url")
    url_rasp = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
    }
    r = requests.get(url=url, headers=headers)
    soup = bs(r.text, "lxml")
    group_sel = {}
    inst_id = 0
    inst = soup.find("form", class_="table-filter").find_all("a")
    for group in inst:
        group_name = group.text.strip()
        group_url = f'https://rasp.sgugit.ru/{group.get("href")}'
        inst_id += 1
        group_sel[inst_id] = {
            "group_url": group_url,
            "group_name": group_name
        }
    if message.text in ["/reg", "/start", "/link", "/help", "/day", "/week"]:
        await state.reset_state()
    else:
        try:
            answer = int(message.text)
            url = group_sel[answer].get("group_url")
            await state.finish()
            if os.stat("url.json").st_size != 0:
                url_rasp = json.load(open("url.json"))
                id_tg = str(message.chat.id)
                if id_tg not in url_rasp:
                    url_rasp[message.chat.id] = url
                    with open("url.json", "w") as file:
                        json.dump(url_rasp, file, indent=4, ensure_ascii=False)
                    await bot.send_message(message.chat.id, "Готово")

                    r = requests.get(url=url, headers=headers)
                    soup = bs(r.text, "lxml")
                    name_group = soup.find("div", class_="general_title_page no-print").text.strip()
                    rasp_all = soup.find_all("div", class_="one_day-wrap")
                    inst_id = 1
                    dict_less = {}
                    for rasp in rasp_all:
                        everD = rasp.find("div", class_="everD").text.strip()
                        day = rasp.find("div", class_="day").text.strip()
                        one_lesson = rasp.find_all("div", class_="one_lesson")
                        if one_lesson is not None:
                            for less in one_lesson:
                                starting_less = less.find("div", class_="starting_less").text.strip()
                                finished_less = less.find("div", class_="finished_less").text.strip()
                                less_name = less.find("div", class_="names_of_less")
                                # inst_id += 1
                                if less_name is not None:
                                    less_name = less.find("div", class_="names_of_less").text.strip()
                                    kabinet_of_less = less.find("a", class_="kabinet_of_less").text
                                    name_of_teacher = less.find("a", class_="name_of_teacher").text
                                    if name_of_teacher == ",":
                                        name_of_teacher = less.find("a", class_="name_of_teacher").next_element.next_element.text.strip()
                                    type_less = less.find("div", class_="type_less").text.strip()

                                    dict_less[inst_id] = {
                                        "everD": everD,
                                        "day": day,
                                        "starting_less": starting_less,
                                        "finished_less": finished_less,
                                        "names_of_less": less_name,
                                        "kabinet_of_less": kabinet_of_less,
                                        "name_of_teacher": name_of_teacher,
                                        "type_less": type_less
                                    }
                                    inst_id += 1
                    if not os.path.exists(f"{name_group}.json"):
                        with open(f"{name_group}.json", "w") as file:
                            json.dump(dict_less, file, indent=4, ensure_ascii=False)

                else:
                    await bot.send_message(message.chat.id, "Ваш id уже есть в системе")
            else:
                url_rasp[message.chat.id] = url
                with open("url.json", "w") as file:
                    json.dump(url_rasp, file, indent=4, ensure_ascii=False)
        except:
            await bot.send_message(message.chat.id, "Ошибка. Проверь правильность ввода")


@dp.message_handler(commands="start")
async def start(message: types.message):
    await bot.send_message(message.chat.id, "Для регистрации введи /reg \n "
                                            "Или пройди быструю регистрацию, отправив ссылку на расписание в подобном виде: \n"
                                            "(https://rasp.sgugit.ru/?ii=1&fi=1&c=1&gn=1&) \n"
                                            "Чтобы узнать все команды, введи /help \n"
                                            ""
                                            "Примечание: Для выхода из режима регистрации/добавления, введи любую команду из /help (включая /help)")



@dp.message_handler(commands="help")
async def start(message: types.message):
    await bot.send_message(message.chat.id, "Список команд: \n\n"
                                            "/help - получение дополнительной информации \n\n"
                                            "/reg - регистрация в системе\n\n"
                                            "Альтернативный способ регистрации - отправить ссылку на расписание в подобном виде: \n"
                                            "(https://rasp.sgugit.ru/?ii=1&fi=1&c=1&gn=1&) \n\n"
                                            "/delete_link - удаление id из системы\n\n"
                                            "/day - расписание на день\n\n"
                                            "/week - расписание на неделю\n\n"
                                            "/start - начало работы с ботом\n\n"
                                            "\n"
                                            "Для смены информации о группе удалите предыдущую запись и пройдите регистрацию заново одним из двух способов")



@dp.message_handler(commands="delete_link")
async def delete_link(message: types.message):
    if os.stat("url.json").st_size != 0:
        url_rasp = json.load(open("url.json"))
        id_tg = str(message.chat.id)
        if id_tg in url_rasp:
            del url_rasp[id_tg]
            with open("url.json", "w") as file:
                json.dump(url_rasp, file, indent=4, ensure_ascii=False)
            await bot.send_message(message.chat.id, "запись успешно удалена")
        else:
            await bot.send_message(message.chat.id, "Записи с вашим id нет")


@dp.message_handler(regexp="https://")
async def get_link(message: types.message):
    url_rasp = {}
    check_url = message.text
    try:
        if check_url.split("/")[2] == "rasp.sgugit.ru":
            if os.stat("url.json").st_size != 0:
                url_rasp = json.load(open("url.json"))
                id_tg = str(message.chat.id)
                if id_tg not in url_rasp:
                    url_rasp[message.chat.id] = check_url
                    with open("url.json", "w") as file:
                        json.dump(url_rasp, file, indent=4, ensure_ascii=False)
                    await bot.send_message(message.chat.id, "Готово")

                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
                    }
                    r = requests.get(url=check_url, headers=headers)
                    soup = bs(r.text, "lxml")
                    name_group = soup.find("div", class_="general_title_page no-print").text.strip()
                    rasp_all = soup.find_all("div", class_="one_day-wrap")
                    inst_id = 1
                    dict_less = {}
                    for rasp in rasp_all:
                        everD = rasp.find("div", class_="everD").text.strip()
                        day = rasp.find("div", class_="day").text.strip()
                        one_lesson = rasp.find_all("div", class_="one_lesson")
                        if one_lesson is not None:
                            for less in one_lesson:
                                starting_less = less.find("div", class_="starting_less").text.strip()
                                finished_less = less.find("div", class_="finished_less").text.strip()
                                less_name = less.find("div", class_="names_of_less")
                                # inst_id += 1
                                if less_name is not None:
                                    less_name = less.find("div", class_="names_of_less").text.strip()
                                    kabinet_of_less = less.find("a", class_="kabinet_of_less").text
                                    name_of_teacher = less.find("a", class_="name_of_teacher").text.strip()  #!!!!!!
                                    if name_of_teacher == ",":
                                        name_of_teacher = less.find("a", class_="name_of_teacher").next_element.next_element.text.strip()
                                    type_less = less.find("div", class_="type_less").text.strip()

                                    dict_less[inst_id] = {
                                        "everD": everD,
                                        "day": day,
                                        "starting_less": starting_less,
                                        "finished_less": finished_less,
                                        "names_of_less": less_name,
                                        "kabinet_of_less": kabinet_of_less,
                                        "name_of_teacher": name_of_teacher,
                                        "type_less": type_less
                                    }
                                    inst_id += 1
                    if not os.path.exists(f"{name_group}.json"):
                        with open(f"{name_group}.json", "w") as file:
                            json.dump(dict_less, file, indent=4, ensure_ascii=False)

                else:
                    await bot.send_message(message.chat.id, "Ваш id уже есть в системе")
            else:
                url_rasp[message.chat.id] = check_url
                with open("url.json", "w") as file:
                    json.dump(url_rasp, file, indent=4, ensure_ascii=False)
    except:
        await bot.send_message(message.chat.id, "Ошибка, повторите ввод")



@dp.message_handler(commands="day")
async def day(message: types.message):
    if os.stat("url.json").st_size != 0:
        url_rasp = json.load(open("url.json"))
        id_tg = str(message.chat.id)
        flag = False
        if id_tg in url_rasp:
            url = url_rasp[id_tg]
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
            }
            r = requests.get(url=url, headers=headers)
            soup = bs(r.text, "lxml")
            name_group = soup.find("div", class_="general_title_page no-print").text.strip()
            try:
                with open(f"{name_group}.json") as file:
                    all_rasp = json.load(file)
            except:
                await bot.send_message(message.chat.id, f"Непредвиденная ошибка. Пожалуйста удалите id и пройдите регистрацию заново. \n"
                                                        f"Удалить id: /delete_link \n"
                                                        f"Ваша ссылка для альтернативного варианта регистрации: \n "
                                                        f"{url} \n")
            # day_rasp = {}
            rasp = f"{name_group} \n\n"
            today_date = datetime.date.today()
            if int(today_date.strftime("%w")) != 0:
                rasp += f"{today_date} \n\n"
                for k, v in all_rasp.items():
                    if today_date.strftime('%d.%m') == v["everD"]:
                        if v["names_of_less"] != '':
                            rasp += f"{v['starting_less']} - {v['finished_less']} \n" \
                                   f"{v['names_of_less']} - {v['kabinet_of_less']} ({v['type_less']}) \n" \
                                   f"{v['name_of_teacher']} \n\n"
                            flag = True

            else:
                rasp = "ты сегодня не учишься, выходной"
            if not flag:
                rasp += "Сегодня пар нет"
            await bot.send_message(message.chat.id, rasp)
        else:
            await bot.send_message(message.chat.id, "Вашего id нет в системе. Пройдите регистрацию одним из двух способов. Подробнее в /help")


@dp.message_handler(commands="week")
async def week(message: types.message):
    if os.stat("url.json").st_size != 0:
        url_rasp = json.load(open("url.json"))
        id_tg = str(message.chat.id)
        if id_tg in url_rasp:
            url = url_rasp[id_tg]
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
            }
            r = requests.get(url=url, headers=headers)
            soup = bs(r.text, "lxml")
            name_group = soup.find("div", class_="general_title_page no-print").text.strip()
            try:
                with open(f"{name_group}.json") as file:
                    all_rasp = json.load(file)
            except:
                await bot.send_message(message.chat.id, f"Непредвиденная ошибка. Пожалуйста удалите id и пройдите регистрацию заново. \n"
                                                        f"Удалить id: /delete_link \n"
                                                        f"Ваша ссылка для альтернативного варианта регистрации: \n "
                                                        f"{url} \n")
            # week_rasp = {}
            rasp = f"{name_group}\n\n"
            today_date = datetime.date.today()
            diff_of_days = int(datetime.date.today().strftime("%w"))
            # rasp += f"{today_date} \n\n"
            if diff_of_days == 0:
                diff_of_days = 6
            else:
                diff_of_days = diff_of_days - 1
            monday_date = (today_date - datetime.timedelta(days=diff_of_days))
            sunday_date = (monday_date + datetime.timedelta(days=6))
            used_date = monday_date
            rasp += f"\n\n------------{used_date}------------ \n"
            for k, v in all_rasp.items():
                if used_date.strftime('%d.%m') == v["everD"]:
                    if v["names_of_less"] != '':
                        rasp += f"{v['starting_less']} - {v['finished_less']} \n" \
                                f"{v['names_of_less']} - {v['kabinet_of_less']} ({v['type_less']}) \n" \
                                f"{v['name_of_teacher']} \n"
                else:
                    if used_date < sunday_date:
                        used_date = (used_date + datetime.timedelta(days=1))
                        if used_date < sunday_date:
                            if used_date.strftime('%d.%m') == v["everD"]:
                                rasp += f"\n\n------------{used_date} ------------ \n"
                                rasp += f"{v['starting_less']} - {v['finished_less']} \n" \
                                        f"{v['names_of_less']} - {v['kabinet_of_less']} ({v['type_less']}) \n" \
                                        f"{v['name_of_teacher']} \n"
            await bot.send_message(message.chat.id, rasp)
        else:
            await bot.send_message(message.chat.id, "Вашего id нет в системе. Пройдите регистрацию одним из двух способов. Подробнее в /help")



@dp.message_handler()
async def text_check(message: types.message):
    if message.text not in ["/reg", "/start", "/link", "/help", "/day", "/week"]:
        await bot.send_message(message.chat.id, "Я таких команд не знаю, давай ещё раз.")

if __name__ == '__main__':
    executor.start_polling(dp)