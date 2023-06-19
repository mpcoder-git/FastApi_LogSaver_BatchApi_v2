from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import json
import base64
import asyncio
import aiomysql
from datetime import datetime


app = FastAPI()


def base64decode(encodedstring):
    """ функция декодирования строки в формате base64 """
    base64_message = encodedstring
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode('ascii')


async def splitcontent(line):
    """функция разбивки текста на параметры"""
    index1s = 0
    index1e = 0
    index2s = 0
    index2e = 0
    par_dataset = ""
    par_sqlquery = ""
    content = line['content']

    content = "\n".join(content)
    print(content)

    # разбивка на переменные
    index1s = content.find("[")
    index1e = content.find("]")
    index2s = content.find("[", index1e)
    index2e = content.find("]", index2s)

    if index1e > 0 and index2s > 0 and index2e > 0:
        par_dataset = content[index1e + 1:index2s - 2].strip()
        par_sqlquery = content[index2e + 1:len(content) - 1]
        #print(f'par_dataset: {par_dataset}  par_sqlquery: {par_sqlquery} ')
        return par_dataset, par_sqlquery
    else:
        par_sqlquery = content
        return par_dataset, par_sqlquery


async def savetomysql(line):
    conn = await aiomysql.connect(host='127.0.0.1', port=3306,
                                  user='root', password='root', db='logsklad',
                                  loop=None)
    cur = await conn.cursor()
    await cur.execute("INSERT INTO logtable (userid, localname, linenum, component, querytext, datetimesave ) VALUES(%s,%s,%s,%s,%s, %s)",line)
    await conn.commit()
    await cur.close()
    conn.close()


async def jobline(oj):
    ''' обработка строки и запись результата в базу '''
    # начальные значения параметров
    par_userid = 0
    par_localname = ""
    par_linenum = 0
    par_dataset = ""
    par_sqlquery = ""
    par_datetimesave = "00.00.0000"
    #получаем список параметров
    if oj['userid']:
        par_userid = oj['userid']
    if oj['localname']:
        par_localname = oj['localname']
    if oj['linenum']:
        par_linenum = oj['linenum']
    if oj['datetimesave']:
        par_datetimesave = oj['datetimesave']
    if oj['content']:
        par_tuple = await splitcontent(oj)
        par_dataset = par_tuple[0]
        par_sqlquery = par_tuple[1]

    date_string = par_datetimesave
    #определяем, что передано: дата или дата с временем
    dt = False
    dtime1 = False
    dtime2 = False
    try:
        date_obj = datetime.strptime(date_string, '%d.%m.%Y')
        dt  =True
    except ValueError:
        dt = False
    try:
        date_obj = datetime.strptime(date_string, '%d.%m.%Y %H:%M')
        dtime1 = True
    except ValueError:
        dtime1 = False
    try:
        date_obj = datetime.strptime(date_string, '%d.%m.%Y %H:%M:%S')
        dtime2 = True
    except ValueError:
        dtime2 = False


    if (dt):
        formatted_date = date_obj.strftime('%Y-%m-%d')
    if ((dtime1) or (dtime2)):
        formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')

    if ((dt == False) and (dtime1 == False) and (dtime2 == False)):
        par_datetimesave = '0000-00-00'
    else:
        par_datetimesave = formatted_date

    #формируем список параметров
    par_list = par_userid, par_localname, par_linenum, par_dataset, par_sqlquery, par_datetimesave

    #обработка списка параметров, формирование нужного списка


    #отправляем список параметров на запись
    #print(par_list)
    await savetomysql(par_list)
    return par_list


@app.get("/")
async def read_root():
    html_content = "<h2>WEB SERVER LOGSAVER</h2>"
    return HTMLResponse(content=html_content)


@app.get("/status")
async def fn_status():
    html_content = "OK"
    return HTMLResponse(content=html_content)


@app.post("/logsave")
async def fn_logsave(inpacket=''):
    '''функция приема данных, обработки и записи в базу данных'''
    if (inpacket == ''):
        message = "Нет данных для обработки!"
        return HTMLResponse(content=message)
    else:

        # если данные переданы, обрабатываем их
        message = ""
        # задаем максимальное количество одновременно выполняемых задач
        max_tasks = 10
        # создаем семафор с максимальным значением max_tasks
        semaphore = asyncio.Semaphore(max_tasks)


        print(inpacket)
        try:
            dictData = json.loads(inpacket, strict=False)
        except:
            message = 'неверный формат данных'
            print(message)
            exit()

        #print(type(dictData))

        tasks = []

        #''' закоментировать этот блок, если надо проверять входящие данные
        for oj in dictData:
            async with semaphore:
                #формирование списка функций
                tasks.append(asyncio.create_task(jobline(oj)))
        results = await asyncio.gather(*tasks)
        print(results)
        #'''

        return HTMLResponse(content='message')


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
