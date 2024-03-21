from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,LocationSendMessage
from linebot.models import PostbackAction,URIAction, MessageAction, TemplateSendMessage, ButtonsTemplate

import time ,os
from threading import Thread

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import requests
import json

trace_tack=False
app = Flask(__name__)

line_bot_api = LineBotApi('ZujAhff2/bYDyZ3CAE+Na5K9vSRejKpNSzWKH1xT8XfYG1QzYxgIaDFLAFhRbLDC/JJXsIrGcWlNtmILfzT2jjGftW/yoqSo4cPLrR2FzbjF2e6MruVCFk0w3Glooc5Gl9U4l9GO7mIMKSEVhLSQJQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c99d8a1de4737d3c9760fc89a529f553')


#爬取地點座標
def get_location(keywords):
    response = requests.get("https://www.google.com/maps/place?q="+keywords)    #在google搜尋地標
    soup = BeautifulSoup(response.text, "html.parser")
    location=soup.find_all("meta")
    location_set={"ini"}    #初始值建立set
    for i in location:
        for unit in list(i["content"]): #每一項element拆成字元檢查
        #print(unit)
            if "%" in unit:
                #print(i["content"])
                location_set.add(i["content"])   #使用set去除重複
    location_set.remove("ini")  #移除set的初始值
    string_location=(str(location_set)) #使用字串摘取出經緯度
    latitude_position1=string_location.find("=")    #節錄:center=25.04642248%2C121.51334263&
    latitude_position2=string_location.find("%")
    latitude=string_location[latitude_position1+1:latitude_position2:]
    #longitude_position1=string_location.find("c")
    longitude_position2=string_location.find("&")
    logitude=string_location[latitude_position2+3:longitude_position2:]   #latitude的終點+3設為longitude的起點
    return latitude,logitude



def run_app():#追蹤的??? what is this?
    
    # time.sleep(3600)
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 在後台運行，不顯示瀏覽器視窗
    chrome_options.add_argument('--disable-gpu')  # 禁用 GPU
    chrome_service = ChromeService(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)


    url = 'https://tixcraft.com/activity'

    # 發送HTTP請求，獲取網頁內容
    response = requests.get(url)

    # 以下這一個是因為發現印出來是亂碼才改的
    response.encoding = 'utf8'

    targer_web=[]
    with open('line-bot.json', newline='',encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)

    # 檢查是否成功獲取網頁內容
    if response.status_code == 200:
        print('網頁獲取成功！')
        # 使用Beautiful Soup解析網頁內容
        soup = BeautifulSoup(response.text, 'html.parser')

        contain_div = soup.find("div", class_="row display-card display-content")
        rows = contain_div.find_all("div", class_="thumbnails")


        # print(rows)

        for user in data['user']:
            targer_web=[]
            for singer in user['concer']:
                # print(singer)

        # 遍歷每一行
                for row in rows:  # 第一行通常是表頭，跳過
                    t=row.find('div', class_= 'multi_ellipsis')
                    # print(t)
                    # unicode_string = utf8_bytes.decode('utf-8')
                    print(t.text.encode('utf8', 'ignore').decode('utf8'))
                    concer = t.text.encode('utf8', 'ignore').decode('utf8')
                    if singer in concer:
                        print("find11111111")
                        print(concer)
                        t1=row.find("a")
                        print(t1.get('href'))
                        targer_web.append('https://tixcraft.com'+t1.get('href'))
    
    # # 找到class = multi-ellipsis 的元素
    # game_list_div = soup.find_all('div', class_= 'thumbnails')

    # for concer in game_list_div:
    #     title = concer.find('div', class_= 'multi-ellipsis') 
    #     if singer in concer:
    #         print(concer)
    #         targer_web.append(concer)
        #all > div.row.display-card.display-content


        for web in targer_web:
            if trace_tack:
                break
            # 前往目標網頁
            print(web)
            driver.get(web)

            # 點選「立即購票」按鈕，使用 xpath 定位
            buy_button = driver.find_element(By.XPATH, '//li[@class="buy"]/a/div')
            driver.execute_script("arguments[0].click();", buy_button)

            # 使用延遲等待，確保 JavaScript 加載完畢
            wait = WebDriverWait(driver, 5)
            wait.until(EC.presence_of_element_located((By.ID, 'gameList')))
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'grid-view')))


            # 獲取網頁內容
            html = driver.page_source

            # 關閉 WebDriver
            #driver.quit()

            # 使用 BeautifulSoup 解析網頁內容
            soup = BeautifulSoup(html, 'html.parser')

            # 找到表格元素
            game_list_div = soup.find('div', {'id': 'gameList', 'class': 'grid-view'})

            # 檢查是否找到 gameList
            if game_list_div:
                table = game_list_div.find('table')

                # 初始化一個列表，用於存儲表格數據
                table_data = []

                show_list = []

                # 找到表格中的所有行
                rows = table.find_all('tr')

                # 遍歷每一行
                for row in rows[1:]:  # 跳過表頭行
                    # 獲取當前行中的所有儲存格
                    cells = row.find_all('td')

                    # 提取每個儲存格的文本數據
                    show_time = cells[0].text.strip()
                    event_name = cells[1].text.strip()
                    location = cells[2].text.strip()
                    purchase_status = cells[3].text.strip()



                    # 將提取的數據組合成一個字典並添加到列表中
                    show_info = {
                        '演出時間': show_time,
                        '場次名稱': event_name,
                        '場地': location,
                        '購買狀態': purchase_status,
                    }

                    # print(show_info)
                    table_data.append(show_info)


                    array = (cells[3].find('button'))
                    show_list.append(array)


                # 打印抓取到的表格數據
                #for data in table_data:
                    #print(data)

            else:
                print('找不到 id 為 gameList 的 div 元素')
            #print(show_list)

            for i,element in enumerate(show_list):
                button_web = element['data-href']
                driver.get(button_web)
                time.sleep(5)

                # 爬取票價資訊
                price_elements = []

                # 尋找所有的票價元素
                ticket_elements = driver.find_elements(By.XPATH, '//div[@class="zone area-list"]//ul/li')

                ticket_check =False
            # 循環處理每個票價元素
                for  ticket_element in ticket_elements:
                    try:
                        # 使用 WebDriverWait 等待每個票價元素可見
                        ticket_info = ticket_element.text.strip()
                        print(f'{ticket_info}')
                        if "remaining" in ticket_info or "Available" in ticket_info or "熱賣中" in ticket_info or "剩餘" in ticket_info:
                            print("有票")
                            ticket_check = True
                            break


                    except TimeoutException:
                        print(f'無法找到某個票價元素，可能發生了錯誤。')
                print("-"*100)
                if ticket_check:
                    print(type(user['userid']))
                    text = TextSendMessage('演出時間:' + table_data[i]['演出時間'] + '\n' 
                                        + '場次名稱:' + table_data[i]['場次名稱'] + '\n' 
                                        + '場地:' + table_data[i]['場地'] + '\n' 
                                        + '購買狀態:' + '有票' + '\n' 
                                        + button_web)
                    line_bot_api.push_message(user['userid'], text)
                    
                # 返回上一頁
        
                Latitude,Logitude=get_location(str(table_data[i]['場地']))
                # print("#########################")
                # print(Latitude,Logitude)
                # print("tabledata=",table_data[i]['場地'])
                location_msg = LocationSendMessage(
                title=str(table_data[i]['場地']),
                address='spot',
                latitude=float(Latitude),
                longitude=float(Logitude)
                )
                line_bot_api.push_message(user['userid'],location_msg)
                driver.back()
        text = TextSendMessage('finish')
        line_bot_api.push_message(user['userid'], text)
        
    # text = TextSendMessage("搶到了")
    # line_bot_api.push_message("Uc7f392db3e59657b6ce04a370b12b9d0", text)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        # text = TextSendMessage(text="Hello, world")
        # line_bot_api.push_message("Uc7f392db3e59657b6ce04a370b12b9d0", text)
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    body = request.get_data(as_text=True)
    json_data = json.loads(body)
#================    
    print('1324654156165')
    print(type(event.source.user_id))
    # print(trace_tack)
    # line_bot_api.push_message( id, TextSendMessage(text="XD"))
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))
    text=event.message.text+"python"
    print(event.source.user_id)
    text = TextSendMessage(text="收尋中...")
    line_bot_api.push_message(event.source.user_id, text)
 
    with open('line-bot.json', newline='',encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)
    
    trace_tack=False
    

    if data['check']==1:
        line_bot_api.push_message(event.source.user_id, TextSendMessage(text="你好"))
        check=False
        for i in data['user']:
            print("json:::::::::::")
            print(i)
            if i['userid']==str(event.source.user_id):
                i['concer'].append(event.message.text)
                check=True
                break
        if not check:
            data['user'].append({
                "userid": event.source.user_id,
                "concer": [event.message.text]
                })
    
        data['check']=0
        text = TextSendMessage(text="已追蹤")
        line_bot_api.push_message(event.source.user_id, text)
    
        with open('line-bot.json', 'w',encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile,ensure_ascii=False)
        trace_tack = True

    if event.message.text == "追蹤":
        text = TextSendMessage(text="請輸入追蹤的演出者")
        line_bot_api.push_message(event.source.user_id, text)
        data['check']=1
        with open('line-bot.json', 'w',encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile,ensure_ascii=False)
        trace_tack = True
    if event.message.text == "取消追蹤":
        for i in data['user']:
            print("json:::::::::::")
            print(i)
            if i['userid']==str(event.source.user_id):
                i['concer']=[]
                break
        with open('line-bot.json', 'w',encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile,ensure_ascii=False)
        text = TextSendMessage(text="已取消追蹤")
        line_bot_api.push_message(event.source.user_id, text)
        data['check']=0
        trace_tack = True
    if event.message.text == "查看追蹤項目":
        for i in data['user']:
            print("json:::::::::::查看追蹤項目")
            print(i)
            if i['userid']==str(event.source.user_id):
                for j in i['concer']:
                    text = TextSendMessage(text=j)
                    line_bot_api.push_message(event.source.user_id, text)
                print(i['concer'])
                # text = TextSendMessage(text=i['concer'])
                # line_bot_api.push_message(event.source.user_id, text)
                break
        data['check']=0
        trace_tack = True
        
        trace_tack = True
    if event.message.text == "查看追蹤演唱會":
        run_app()
        data['check']=0
        trace_tack = True


    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 在後台運行，不顯示瀏覽器視窗
    # chrome_options.add_argument('--disable-gpu')  # 禁用 GPU
    chrome_service = ChromeService(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)



    url = 'https://tixcraft.com/activity'

    

    targer_web=[]
    
    # 發送HTTP請求，獲取網頁內容
    response = requests.get(url)

# 以下這一個是因為發現印出來是亂碼才改的
    response.encoding = 'utf8'
    # 檢查是否成功獲取網頁內容
    if response.status_code == 200:
        print('網頁獲取成功！')
        # 使用Beautiful Soup解析網頁內容
        soup = BeautifulSoup(response.text, 'html.parser')

        contain_div = soup.find("div", class_="row display-card display-content")
        rows = contain_div.find_all("div", class_="thumbnails")

        singer=event.message.text
        # 遍歷每一行
        for row in rows:  # 第一行通常是表頭，跳過
            t=row.find('div', class_= 'multi_ellipsis')
            # print(t)
            # unicode_string = utf8_bytes.decode('utf-8')
            print(t.text.encode('utf8', 'ignore').decode('utf8'))
            concer = t.text.encode('utf8', 'ignore').decode('utf8')
            if singer in concer:
                print("find11111111")
                print(concer)
                t1=row.find("a")
                print(t1.get('href'))
                targer_web.append('https://tixcraft.com'+t1.get('href'))
    else:
        print('網頁無法正常獲取！')

    print(targer_web)

    for web in targer_web:
        if trace_tack:
            break
        # 前往目標網頁
        print(web)
        driver.get(web)

        # 點選「立即購票」按鈕，使用 xpath 定位
        buy_button = driver.find_element(By.XPATH, '//li[@class="buy"]/a/div')
        driver.execute_script("arguments[0].click();", buy_button)

        # 使用延遲等待，確保 JavaScript 加載完畢
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.ID, 'gameList')))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'grid-view')))


        # 獲取網頁內容
        html = driver.page_source

        # 關閉 WebDriver
        #driver.quit()

        # 使用 BeautifulSoup 解析網頁內容
        soup = BeautifulSoup(html, 'html.parser')

        # 找到表格元素
        game_list_div = soup.find('div', {'id': 'gameList', 'class': 'grid-view'})

        # 檢查是否找到 gameList
        if game_list_div:
            table = game_list_div.find('table')

            # 初始化一個列表，用於存儲表格數據
            table_data = []

            show_list = []

            # 找到表格中的所有行
            rows = table.find_all('tr')

            # 遍歷每一行
            for row in rows[1:]:  # 跳過表頭行
                # 獲取當前行中的所有儲存格
                cells = row.find_all('td')

                # 提取每個儲存格的文本數據
                show_time = cells[0].text.strip()
                event_name = cells[1].text.strip()
                location = cells[2].text.strip()
                purchase_status = cells[3].text.strip()



                # 將提取的數據組合成一個字典並添加到列表中
                show_info = {
                    '演出時間': show_time,
                    '場次名稱': event_name,
                    '場地': location,
                    '購買狀態': purchase_status,
                }

                # print(show_info)
                table_data.append(show_info)


                array = (cells[3].find('button'))
                show_list.append(array)


            # 打印抓取到的表格數據
            #for data in table_data:
                #print(data)

        else:
            print('找不到 id 為 gameList 的 div 元素')
        #print(show_list)
        
        for i,element in enumerate(show_list):
            button_web = element['data-href']
            driver.get(button_web)
            time.sleep(5)

            # 爬取票價資訊
            price_elements = []

            # 尋找所有的票價元素
            ticket_elements = driver.find_elements(By.XPATH, '//div[@class="zone area-list"]//ul/li')

            ticket_check =False
        # 循環處理每個票價元素
            for  ticket_element in ticket_elements:
                try:
                    # 使用 WebDriverWait 等待每個票價元素可見
                    ticket_info = ticket_element.text.strip()
                    print(f'{ticket_info}')
                    if "remaining" in ticket_info or "Available" in ticket_info or "熱賣中" in ticket_info :
                        print("有票")
                        ticket_check = True
                        break


                except TimeoutException:
                    print(f'無法找到某個票價元素，可能發生了錯誤。')
            print("-"*100)
            if ticket_check:
                text = TextSendMessage('演出時間:' + table_data[i]['演出時間'] + '\n' 
                                    + '場次名稱:' + table_data[i]['場次名稱'] + '\n' 
                                    + '場地:' + table_data[i]['場地'] + '\n' 
                                    + '購買狀態:' + '有票' + '\n' 
                                    + button_web)
                
                line_bot_api.push_message(event.source.user_id, text)   
                line_bot_api.push_message(event.source.user_id, TextSendMessage("剩餘座位"+"\n"+ticket_info))


            else:
                text = TextSendMessage('演出時間:' + table_data[i]['演出時間'] + '\n' 
                                    + '場次名稱:' + table_data[i]['場次名稱'] + '\n' 
                                    + '場地:' + table_data[i]['場地'] + '\n' 
                                    + '購買狀態:' + '無票' + '\n' 
                                    + button_web)
                line_bot_api.push_message(event.source.user_id, text)
            # 返回上一頁
        
        
            Latitude,Logitude=get_location(str(table_data[i]['場地']))
            # print("#########################")
            # print(Latitude,Logitude)
            # print("tabledata=",table_data[i]['場地'])
            location_msg = LocationSendMessage(
            title=str(table_data[i]['場地']),
            address='spot',
            latitude=float(Latitude),
            longitude=float(Logitude)
            )
            line_bot_api.push_message(event.source.user_id,location_msg)
           
            driver.back()
            time.sleep(5)

    


    

    text = TextSendMessage('finish')
    line_bot_api.push_message(event.source.user_id, text)
    



if __name__ == "__main__":
    # 在一個單獨的線程中運行 app.run()
    t = Thread(target=run_app)
    t.start()
    trace_tack=False
    app.run(debug=False, port=80)
    print("run\n\n")
    os._exit(0)
    