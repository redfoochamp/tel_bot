import time
import pandas as pd
import telebot
import config
import dbworker
from tabulate import tabulate
from selenium import webdriver

bot = telebot.TeleBot(config.token)


def stat():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x935')
    browser = webdriver.Chrome(chrome_options=options)
    browser.get('https://www.dohod.ru/analytic/bonds/')
    browser.find_element_by_xpath('//*[@id="table-bonds_length"]/label/select/option[3]').click()

    list_n = []
    time.sleep(20)
    k = 1
    while k < 174:
        for i in range(16):
            try:
                new_users = browser.find_element_by_xpath(
                    '//*[@id="table-bonds"]/tbody/tr[' + str(k) + ']/td[' + str(i) + ']').text
                list_n.append(new_users)
            except:
                pass
        k += 1

    mylist = [x for x in list_n if x]
    splt = lambda lst, sz: [lst[i:i + sz] for i in range(0, len(lst), sz)]
    table = splt(mylist, 9)

    df = pd.DataFrame(table)
    df.columns = ['ID', 'Name', 'DateOff', 'YearsOff', 'Prof', 'Credit', 'Qual', 'Liquidity', 'Risk']
    browser.close()
    df["YearsOff"] = pd.to_numeric(df["YearsOff"], errors='coerce')
    df["Prof"] = pd.to_numeric(df["Prof"], errors='coerce')
    df["Liquidity"] = pd.to_numeric(df["Liquidity"], errors='coerce')
    return df


@bot.message_handler(commands=["start"])
def cmd_start(message):
    dbworker.set_state(message.chat.id, config.States.S_START.value)
    bot.send_message(message.chat.id, "Привет!) \n"
                                      "Этот сервис поможет вам подобрать облигации для ваших инвестиционных портфелей.\n"
                                      "Вы можете выбрать инструменты по множеству предлагаемых критериев.\n"
                                      "Нажмите /commands список доступных команд.\n"
                                      "Нажмите /reset чтобы начать заново\n"
                                      "Нажмите /info чтобы узнать, что я могу сделать.\n"
                                      "Чтобы приступить введите интересующий уровень доходности облигаций от 0 до 9")
    dbworker.set_state(message.chat.id, config.States.S_Prof.value)


@bot.message_handler(commands=["info"])
def cmd_info(message):
    bot.send_message(message.chat.id, "/Info команда, которая покажет, информацию о боте и его возможностях.\n"
                                      "Бот покажет следующую информацию об облигациях:.\n"
                                      "-Название бумаги \n"
                                      "-Эффективная дата погашения - ближайшая дата, в которую облигация может быть погашена или выкуплена эмитентом.\n"
                                      "-Лет до погашения\n"
                                      "-Эффективная доходность - эта доходность в % годовых отражает доходность облигации с учетом ее текущей цены, размера купона, периодичности выплаты купонов.\n"
                                      "-Качество эмитента - показывает устойчивость бизнес-модели эмитента.\n"
                                      "-Кредитное качество - рейтинг бумаги.\n"
                                      "-Ликвидность - чем выше показатель, тем легче купить и продать облигацию.\n"
                                      "-Рыночный риск - как изменится цена облигации при существенном росте рыночных процентных ставок в данной валюте.\n")
    bot.send_message(message.chat.id,
                     "Для получения информации об облигация предлагается ввести 3 показателя отбора бумаг.\n"
                     "Вначале предлагается ввести интересующий уровень доходности в пределах от 0 до 9.\n"
                     "На втором шаге требуется ввести интересующий показатель ликвидности в пределах от 0 до 80.\n"
                     "Финальный показатель количество лет до погашения в пределах от 0 до 23. \n")
    bot.send_message(message.chat.id, "Введите /reset , чтобы начать сначала.\n"
                                      "Вы можете ввести /commands , чтобы посмотреть список доступных команд. \n"
                                      "Или сразу введите уровень доходности.")


@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Начнем сначала.\n"
                                      "Введите интересующий уровен доходности облигаций от 0 до 9\n"
                                      "Нажмите /info или /commands чтобы посмотрить информацию о боте и его командах.")
    dbworker.set_state(message.chat.id, config.States.S_Prof.value)


@bot.message_handler(commands=["property"])
def cmd_property(message):
    x = ['Сколько лет до погашения', 'Эффективная доходность', 'Ликвидность']
    bot.send_message(message.chat.id, "В этом боте используется следущие кретерии отбора обилгаций:\n")
    bot.send_message(message.chat.id, "\n".join(x))
    bot.send_message(message.chat.id, "/start - Запустить бота.\n"
                                      "/info - Посмотреть информацию о боте.\n"
                                      "/commands - Посмотреть список доступных команд.\n")


@bot.message_handler(commands=["commands"])
def cmd_commands(message):
    bot.send_message(message.chat.id, "/reset - Начать сначала.\n"
                                      "/start - Запустить бота.\n"
                                      "/info - Посмотреть информацию о боте.\n"
                                      "/commands - Посмотреть список доступных команд.\n"
                                      "/property - Посмотреть список фильторов.\n")


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_Prof.value
                                          and message.text.strip().lower() not in (
                                                  '/reset', '/info', '/start', '/commands',
                                                  '/property'))
def get_prof(message):
    dbworker.del_state(str(message.chat.id) + 'profit')
    try:
        if (message.text.isdigit()) & (float(message.text) <= 12):
            bot.send_message(message.chat.id,
                             "Ок, теперь введите интересующую ликвидность облигаций в пределах от 0 до 80 \n"
                             "Нажмите /reset чтобы начать заново\n"
                             "Нажмите /info чтобы узнать, что я могу сделать.")
            dbworker.set_state(str(message.chat.id) + 'profit', message.text)  # запишем доходность в базу
            dbworker.set_state(message.chat.id, config.States.S_Liquidity.value)
        else:
            bot.send_message(message.chat.id, "Упс, что-то не так введено. Попробуй снова.\n"
                                              "Введите интересующий уровень доходности облигаций от 0 до 9\n"
                                              "Нажмите /reset чтобы начать заново\n"
                                              "Нажмите /info чтобы узнать, что я могу сделать.")
    except:
        bot.send_message(message.chat.id, "Упс, что-то не так введено. Попробуй снова.\n"
                                          "Введите интересующий уровень доходности облигаций от 0 до 9\n"
                                          "Нажмите /reset чтобы начать заново\n"
                                          "Нажмите /info чтобы узнать, что я могу сделать.")


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_Liquidity.value
                                          and message.text.strip().lower() not in (
                                                  '/reset', '/info', '/start', '/commands',
                                                  '/property'))
def get_liquidity(message):
    dbworker.del_state(str(message.chat.id) + 'liquid')
    try:
        if (message.text.isdigit()) & (float(message.text) <= 93):
            bot.send_message(message.chat.id,
                             "Ок, теперь введите количество лет до погашения облигаций в пределах от 0 до 23 \n"
                             "Нажмите /reset чтобы начать заново\n"
                             "Нажмите /info чтобы узнать, что я могу сделать.")
            dbworker.set_state(str(message.chat.id) + 'liquid', message.text)  # запишем ликвидность в базу
            dbworker.set_state(message.chat.id, config.States.S_YearsOff.value)
        else:
            bot.send_message(message.chat.id, "Упс, что-то не так введено. Попробуй снова.\n"
                                              "Введите интересующую ликвидность облигаций в пределах от 0 до 80\n"
                                              "Нажмите /reset чтобы начать заново\n"
                                              "Нажмите /info чтобы узнать, что я могу сделать.")
    except:
        bot.send_message(message.chat.id, "Упс, что-то не так введено. Попробуй снова.\n"
                                          "Введите интересующую ликвидность облигаций в пределах от 0 до 80\n"
                                          "Нажмите /reset чтобы начать заново\n"
                                          "Нажмите /info чтобы узнать, что я могу сделать.")


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_YearsOff.value
                                          and message.text.strip().lower() not in (
                                                  '/reset', '/info', '/start', '/commands',
                                                  '/property'))
def get_yearsoff(message):
    dbworker.del_state(str(message.chat.id) + 'years')
    try:
        if (message.text.isdigit()) & (float(message.text) <= 33):
            bot.send_message(message.chat.id, 'Постараюсь подобрать подходящиие облигации.\n'
                                              "Это может занять несколько минут. Спасибо за ожидание.")
            dbworker.set_state(str(message.chat.id) + 'years', message.text)  # запишем срок до погашения в базу

        else:
            bot.send_message(message.chat.id, "Упс, что-то не так введено. Попробуй снова.\n"
                                              "Введите количество лет до погашения облигаций в пределах от 0 до 23\n"
                                              "Нажмите /reset чтобы начать заново\n"
                                              "Нажмите /info чтобы узнать, что я могу сделать.")
    except:
        bot.send_message(message.chat.id, "Упс, что-то не так введено. Попробуй снова.\n"
                                          "Введите количество лет до погашения облигаций в пределах от 0 до 23\n"
                                          "Нажмите /reset чтобы начать заново\n"
                                          "Нажмите /info чтобы узнать, что я могу сделать.")
    df = stat()
    first = dbworker.get_current_state(str(message.chat.id) + 'profit')
    second = dbworker.get_current_state(str(message.chat.id) + 'liquid')
    third = dbworker.get_current_state(str(message.chat.id) + 'years')
    for_sending = df.loc[
        (df['Prof'] >= float(first)) & (df['Liquidity'] >= float(second)) & (df['YearsOff'] <= float(third))]
    if for_sending.empty:
        bot.send_message(message.chat.id, "Упс, ничего подходящего не нашли.\n"
                                          "Попробуйте снова /reset \n")
    else:
        bot.send_message(message.chat.id, tabulate(for_sending.head(2), headers=for_sending.columns, tablefmt="pipe"))
        bot.send_message(message.chat.id, "Спасибо, что воспользовались ботом.\n"
                                          "Попробуйте снова /reset \n")


bot.infinity_polling()
