from selenium import webdriver
import time
import pandas as pd

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x935')
browser = webdriver.Chrome(chrome_options=options)

browser.get('https://www.dohod.ru/analytic/bonds/')
browser.find_element_by_xpath('//*[@id="table-bonds_length"]/label/select/option[3]').click()
list = []
time.sleep(20)
k = 1
while k < 174:
    for i in range(16):
        try:
            new_users = browser.find_element_by_xpath(
                '//*[@id="table-bonds"]/tbody/tr[' + str(k) + ']/td[' + str(i) + ']').text
            list.append(new_users)
        except:
            pass
    k += 1

mylist = [x for x in list if x]
splt = lambda lst, sz: [lst[i:i + sz] for i in range(0, len(lst), sz)]
table = splt(mylist, 9)

df = pd.DataFrame(table)
df.columns = ['ID', 'Name', 'DateOff', 'YearsOff', 'Prof', 'Credit', 'Qual', 'Liquidity', 'Risk']
print(df)
df["YearsOff"] = pd.to_numeric(df["YearsOff"], errors='coerce')
df["Prof"] = pd.to_numeric(df["Prof"], errors='coerce')
df["Liquidity"] = pd.to_numeric(df["Liquidity"], errors='coerce')
browser.close()
print((df.dtypes))
