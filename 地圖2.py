import requests
from bs4 import BeautifulSoup


def get_location(keywords):
    response = requests.get("https://www.google.com/maps/place?q="+keywords)
    soup = BeautifulSoup(response.text, "html.parser")
    location=soup.find_all("meta")
    location_set={"ini"}    #初始值建立set
    for i in location:
        for unit in list(i["content"]):
        #print(unit)
            if "%" in unit:
                print(i["content"])
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
#test
#target="  台北小巨蛋"
#a,b=get_location(target)

#print(a,b)
