import fun
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time


#Otwarcie Strony
WEB = "https://licytacje.komornik.pl/Notice/Search"
PATH = "D:\ChromeDriver\chrome-win64\chrome.exe"
service = Service(PATH)
driver = webdriver.Chrome(service=service)


list_of_auctions=[]

przedzial_cenowy = [0,20_000,50_000,100_000 , 150_000,200_000,300_000,500_000]

for i in range(1,len(przedzial_cenowy)):
    driver.get(WEB)
    fun.wyszukiwanie_podstawowe(driver,przedzial_cenowy[i-1],przedzial_cenowy[i])
    print(str(przedzial_cenowy[i-1]) ," - " ,str(przedzial_cenowy[i]))
    fun.zliczanie_wynikow(driver,list_of_auctions)
driver.close()
driver.quit()


fun.odswiezenie_bazy(list_of_auctions)


time.sleep(10)
