import fun
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

#Otwarcie Strony
WEB = "https://licytacje.komornik.pl/Notice/Search"
# Ścieżka do pliku chrome.exe

"""
options = Options()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
"""
#driver = webdriver.Chrome(service=service)
driver = webdriver.Chrome(ChromeDriverManager().install())



list_of_auctions=[]

przedzial_cenowy = [0,20_000,50_000,100_000,300_000,500_000 ]

for i in range(1,len(przedzial_cenowy)):
    driver.get(WEB)
    fun.wyszukiwanie_podstawowe(driver,przedzial_cenowy[i-1],przedzial_cenowy[i])
    print(str(przedzial_cenowy[i-1]) ," - " ,str(przedzial_cenowy[i]))
    fun.zliczanie_wynikow(driver,list_of_auctions)
driver.close()
driver.quit()


fun.odswiezenie_bazy(list_of_auctions)


fun.szukanie_księgi_wieczystej_z_HTML()
#fun.szukanie_linku_do_ksiegi(driver)


fun.zapis_do_pliku_xlsx()


time.sleep(2)
