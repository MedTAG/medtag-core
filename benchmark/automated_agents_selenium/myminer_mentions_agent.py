import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2
import time
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui
import statistics
import json

def create_collection():
    f = open('./other_files/collection.txt','a')
    raws = []
    count = 0
    for filename in os.listdir('./other_files/to_insert_eztag/'):
        count = count+1
        g = open('./other_files/to_insert_eztag/'+filename)
        line = g.readline()
        print(filename + '   ' + line)
        stringa = str(count) + "\t" + "documento_" + str(count) + "\t" + line + "\n"
        f.write(stringa)
#create_collection()
def my_miner_labels(driver,absolute_path_for_collection):
    # absolute_path_for_collection = ""
    driver.get('https://myminer.armi.monash.edu.au/')

    driver.get('https://myminer.armi.monash.edu.au/entity_modified.php')

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="filepath"]'))
    ).send_keys(absolute_path_for_collection)
    time.sleep(0.1)

    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@src="pics/upload.jpg"]')))
    time.sleep(0.1)
    st = time.time()
    clicks = 0
    loc = element.location
    siz = element.size
    current_x = loc['x'] + (siz['width'] / 2)
    current_y = loc['y'] + (siz['height'] / 2)
    # print(current_x)
    # print(current_y)
    element.click()
    # for i in range(70,71):
    doc = 0
    f = open('./other_files/new_json.json')
    mentions_json = json.load(f)
    mentions_list = mentions_json['mentions_list']

    for i in range(100):
        # print(str(i))
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="abstract_area"]')))
        mention_element = mentions_list[i]
        elem = driver.find_element_by_xpath('//div[@id="abstract_area"]')
        # print(elem.text)
        # print(mention_element['id_report'])
        # print('\n')
        a = False
        while a == False:
            if mention_element['id_report'] in elem.text:
                a = True
        count = 3
        for mention in mention_element['mentions']:
            # print(mention)
            clientRect = driver.execute_script(
                "var element = document.getElementById('abstract_area');"
                "var testo = element.innerHTML;"
                "var textNode = element.childNodes[arguments[1]];"
                "var ind = textNode.wholeText.indexOf(arguments[0]);"
                "console.log('indice',ind);"
                "console.log('count',arguments[1]);"
                "console.log('test',testo);"
                "console.log('txt', textNode);"
                "console.log('len',textNode.length);"
                "var range = document.createRange();"
                "range.setStart(textNode, ind);"
                "range.setEnd(textNode, (ind + (arguments[0]).length));"
                "console.log('range',range);"
                "const clientRect = range.getBoundingClientRect();"
                "window.getSelection().addRange(range);"
        
                "return clientRect", mention,count

            )
            count +=2
            clicks = clicks+1
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//a[@id="protein"]'))
            ).click()
            driver.execute_script(
                "var sel = window.getSelection ? window.getSelection() : document.selection;"
                "if (sel) {"
                "if (sel.removeAllRanges) {"
                "sel.removeAllRanges();"
                "} else if (sel.empty) {"
                "sel.empty();"
                "}"
                "}"
                "if (sel.rangeCount > 1)"
                "{"
                "for (var i = 1; i < s.rangeCount; i++) {"
                    "s.removeRange(s.getRangeAt(i));"
                "}"
            "}"

            )
            time.sleep(0.3)
            clicks = clicks + 1
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//img[@src="pics/next.jpg"]'))).click()
        #time.sleep(0.5)


    tot = time.time() - st
    print('tot: '+str(tot))
    print('clicks: '+str(clicks))
    return tot

if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path='C:/Users/ornel/Examode/medtag/chromedriver.exe')
    absolute_path_for_collection = 'C:\\Users\\ornel\\PycharmProjects\\Selenium_test\\other_files\\collection1.txt'
    c = 0
    data = []
    timer = 0
    while c<40:
        print(str(c))
        log_in = my_miner_labels(driver,absolute_path_for_collection)
        timer = timer + log_in
        data.append(log_in)
        c = c+1
    std = statistics.stdev(data)
    print('tot_time_spent: ' + str(timer))
    print('std: '+ str(std))