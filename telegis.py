from requests import Session, get, post
from bs4 import BeautifulSoup
from time import strptime, strftime, localtime, sleep
from datetime import timedelta, datetime

session = Session()
header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
              'q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Cookie': 'rewlon=1; '
              'b=I0gBAIC4tnQArbFPwwkAABAA; '
              'c=+lwbXwEAAHsTAAAUAAAACQAQ; '
              'tmr_detect=0%7C1595628839054; '
              'tmr_reqNum=715',
    'DNT': '1',
    'pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
}
months = [0, 'january', 'february', 'march', 'april', 'may', 'june',
          'july', 'august', 'september', 'october', 'november', 'december']


# def get_whether(date='27-july'):
#     url = f'https://pogoda.mail.ru/prognoz/yaroslavl/{date}/'
#     print('test1', url)
#     respdata = session.get(url, headers=header, proxies='', allow_redirects=False)
#
#     html = respdata.content.decode('utf-8')
#     soup = BeautifulSoup(html, 'lxml')
#
#     arr_whether = []
#     for per in soup.select('.block_selected .cols__column__inner .day_period'):
#         dic_whether = {'day_date': per.select_one('.day__date').text, 'temp': per.select_one('.day__temperature ').text,
#                        'desc': per.select_one('.day__description').select_one('span').text, 'addit': []}
#         print(per.select_one('.day__date').text)
#         for addit in per.select('.day__additional'):
#             dic_whether['addit'].append(addit.select_one('span')['title'].split(': ')[1])
#         arr_whether.append(dic_whether)
#     return arr_whether
#
#
# def range_date():
#     now = datetime.now()
#     prev30 = now - timedelta(days=30)
#     next30 = now + timedelta(days=13)
#     return [prev30, next30]  # .strftime("%d.%m.%Y")
#
#
# def valid_date(date):
#     try:
#         sel_date = datetime.strptime(date + '.' + str(datetime.now().timetuple()[0]), "%d.%m.%Y")
#     except ValueError as e:
#         return False
#     rd = range_date()
#     if rd[0] < sel_date < rd[1]:
#         return sel_date.strftime("%d.%m.%Y")
#     else:
#         return False
#
#
# def trans_date(date):
#     if date.split('.')[0][0] == '0':
#         transdate = date.split('.')[0][1] + '-' + months[int(date.split('.')[1])]
#     else:
#         transdate = date.split('.')[0] + '-' + months[int(date.split('.')[1])]
#     return transdate
#
#
# def text_whether(date):
#     vd = valid_date(date)
#     if vd:
#         td = trans_date(vd)
#         fulltext = f'<b>Сводка за {vd}:</b>\n' \
#                    '<b>------------------------------------</b>\n'
#         for gw in get_whether(td):
#             text = f'<b>{gw["day_date"]}</b>\n' \
#                    f'\t\t\t\t<i>Температура: </i> <b>{gw["temp"]}</b> | <b>{gw["desc"]}</b>\n' \
#                    f'\t\t\t\t<i>Давление: </i> <b><i>{gw["addit"][0]}</i></b>\n' \
#                    f'\t\t\t\t<i>Влажность: </i> <b><i>{gw["addit"][1]}</i></b>\n' \
#                    f'\t\t\t\t<i>Ветер: </i> <b><i>{gw["addit"][2]}</i></b>\n' \
#                    f'\t\t\t\t<i>Вероятность осадков: </i> <b><i>{gw["addit"][3]}</i></b>\n\n'
#             fulltext += text
#         return fulltext
#     else:
#         rd = range_date()
#         fulltext = '<i>Введите дату в формате\n' \
#                    '<b>ДД.ММ</b> Например: <b>30.07</b>\n' \
#                    f'в диапазоне от <b>{rd[0].strftime("%d.%m.%Y")}</b> до <b>{rd[1].strftime("%d.%m.%Y")}</b></i>'
#         return fulltext


class BotHandler:
    def __init__(self, token, proxi):
        self.whether = []
        self.token = token
        self.proxi = proxi
        self.api_url = f'https://api.telegram.org/bot{token}/'
        now = datetime.now()
        self.min_date = now - timedelta(days=30)
        self.max_date = now + timedelta(days=13)

    def get_updates(self, offset, timeout=60):
        method = 'getUpdates'
        if offset is None:
            params = {'timeout': timeout}
        else:
            params = {'offset': offset, 'timeout': timeout}
        resp = get(self.api_url + method, params, proxies=self.proxi)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        resp = post(self.api_url + method, params, proxies=self.proxi)
        return resp

    def get_last_update(self, offset):
        while 1:
            get_result = self.get_updates(offset)
            if len(get_result) > 0:
                return get_result[-1]
            else:
                sleep(2)

    def get_whether(self, date):
        self.whether = []
        url = f'https://pogoda.mail.ru/prognoz/yaroslavl/{date}/'
        respdata = session.get(url, headers=header, proxies='', allow_redirects=False)

        html = respdata.content.decode('utf-8')
        soup = BeautifulSoup(html, 'lxml')

        for per in soup.select('.block_selected .cols__column__inner .day_period'):
            dic_whether = {'day_date': per.select_one('.day__date').text,
                           'temp': per.select_one('.day__temperature ').text,
                           'desc': per.select_one('.day__description').select_one('span').text, 'addit': []}
            print(per.select_one('.day__date').text)
            for addit in per.select('.day__additional'):
                dic_whether['addit'].append(addit.select_one('span')['title'].split(': ')[1])
            self.whether.append(dic_whether)

    def valid_date(self, date):
        try:
            sel_date = datetime.strptime(date + '.' + str(datetime.now().timetuple()[0]), "%d.%m.%Y")
        except ValueError as e:
            return False
        if self.min_date < sel_date < self.max_date:
            return sel_date.strftime("%d.%m.%Y")
        else:
            return False

    def min_max_str(self):
        return [self.min_date.strftime("%d.%m.%Y"),
                self.max_date.strftime("%d.%m.%Y")]

    @staticmethod
    def trans_date(date):
        if date.split('.')[0][0] == '0':
            transdate = date.split('.')[0][1] + '-' + months[int(date.split('.')[1])]
        else:
            transdate = date.split('.')[0] + '-' + months[int(date.split('.')[1])]
        return transdate

    def text_whether(self, date):
        vd = self.valid_date(date)
        if vd:
            td = self.trans_date(vd)
            self.get_whether(td)
            fulltext = f'<b>Сводка за {vd}:</b>\n' \
                       '<b>------------------------------------</b>\n'

            for gw in self.whether:
                text = f'<b>{gw["day_date"]}</b>\n' \
                       f'\t\t\t\t<i>Температура: </i> <b>{gw["temp"]}</b> | <b>{gw["desc"]}</b>\n' \
                       f'\t\t\t\t<i>Давление: </i> <b><i>{gw["addit"][0]}</i></b>\n' \
                       f'\t\t\t\t<i>Влажность: </i> <b><i>{gw["addit"][1]}</i></b>\n' \
                       f'\t\t\t\t<i>Ветер: </i> <b><i>{gw["addit"][2]}</i></b>\n' \
                       f'\t\t\t\t<i>Вероятность осадков: </i> <b><i>{gw["addit"][3]}</i></b>\n\n'
                fulltext += text
            return fulltext
        else:
            mnd = self.min_max_str()[0]
            mxd = self.min_max_str()[1]
            fulltext = '<i>Введите дату в формате\n' \
                       '<b>ДД.ММ</b> Например: <b>30.07</b>\n' \
                       f'в диапазоне от <b>{mnd}</b> до <b>{mxd}</b></i>'
            return fulltext


tproxi = {}
ttoken = '1251679759:AAENsxOC8KTpkRgdo1_TMspWMvSDVE_CleI'
teleBot = BotHandler(ttoken, tproxi)


def main():
    new_offset = None
    while 1:
        last_update = teleBot.get_last_update(new_offset)
        last_update_id = last_update['update_id']
        last_chat_text = ''

        if 'message' in last_update:
            if 'text' in last_update['message']:
                last_chat_text = last_update['message']['text']
            if 'chat' in last_update['message']:
                last_chat_id = last_update['message']['chat']['id']

        if last_chat_text == '/start':
            mms = teleBot.min_max_str()
            text = '<i>Чтобы получить сводку погоды\n' \
                   'введите дату в формате\n' \
                   '<b>ДД.ММ</b> Например: <b>30.07</b>\n' \
                   f'в диапазоне от <b>{mms[0]}</b> до <b>{mms[1]}</b></i>'
            teleBot.send_message(last_chat_id, text)
        else:
            text = teleBot.text_whether(last_chat_text.lower())
            teleBot.send_message(last_chat_id, text)

        print('\nMessage:\n\t' + last_chat_text.lower())
        new_offset = last_update_id + 1
        print('\nla:', last_update_id, '\nno:', new_offset, '\n----------------------\n')


if __name__ == '__main__':
    main()
