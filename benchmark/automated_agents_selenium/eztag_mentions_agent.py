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

def define_json(driver,num,mentions_list):
    new_json = {}
    new_json['mentions_list'] = []
    count = 0
    url_def = "https://eztag.bioqrator.org/documents/" + str(num)

    while count < 100:
        print(str(count))
        url = "https://eztag.bioqrator.org/documents/" + str(num)
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@class="ui button small doc-info-btn"]'))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="ui modal doc-info transition visible active"]'))
        )
        elems = driver.find_elements_by_xpath('//div[@class="header"]')
        id = ''
        for el in elems:
            if 'Document - ' in el.text:
                testo = el.text
                id = testo.split(' - ')[1]
                print(id)
                break

        for el in mentions_list:
            if el['id_report'] == id:
                new_json['mentions_list'].append(el)
                break
        num = num -1
        count = count +1
    driver.get(url_def)
    print(new_json)
    return new_json


def login(driver,my_url,name_coll):


    driver.get(my_url)
    # driver.get("https://eztag.bioqrator.org/sessions/37047115-f6ca-48a5-8175-c175508113d0")

    f = open('../datasets/mentions/mentions.json')
    mentions_json = json.load(f)
    mentions_list = mentions_json['mentions_list']
    id_ref = mentions_list[0]['id_report']
    driver.find_element_by_xpath("//a[text()='Collections']").click()
    time.sleep(1)
    ele = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[text()="' + name_coll + '"]'))
    )
    ele.click()
    time.sleep(1)
    url1 = driver.current_url

    # driver.find_element_by_xpath('//a[contains(@href,"/documents/208633")]').click()
    driver.find_element_by_xpath('//a[text()="' + str(id_ref) + '"]').click()
    time.sleep(0.5)
    url = driver.current_url
    num = int(url.split('https://eztag.bioqrator.org/documents/')[1])
    return num,mentions_list,url1



def find_mentions(driver,num,mentions_list_1,current_x,current_y):
    #
    # current_x = 0
    # current_y = 0
    # driver.execute_script(
    #     "function printMousePos(event){console.log('CLICK X',event.pageX);console.log('CLICK Y',event.pageY);}"
    #     "document.addEventListener('click', printMousePos);")



        # print(ele2.size)

    # count = 208633

    count = num
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="text diagnosis"]'))
    )

    st = time.time()
    clicks = 1
    # for i in range(70,71):
    doc = 0
    ment = mentions_list_1['mentions_list']
    for i in range(100):
        # print(str(i))
        # print(str(i))
        # time.sleep(0.5)
        elem = ment[i]
        # print(elem['id_report'])
        mentions = elem['mentions']
        # print(mentions)
        for mention in mentions:
            # time.sleep(0.5)
            clientRect = driver.execute_script(
                "function printMousePos(event){console.log('CLICK X',event.offsetX);console.log('CLICK Y',event.offsetY);}"
                "document.addEventListener('click', printMousePos);"
                "var elements = document.getElementsByClassName('phrase  ');"
                "var element = elements[elements.length -1];"
                # "var element = document.getElementsByClassName('phrase  ')[0];"
                "var testo = element.innerHTML;"
                "var textNode = element.childNodes[0];"
                "var ind = testo.indexOf(arguments[0]);"
                # "var ind = testo.indexOf('assente espressione');"

                # "ind = testo.indexOf(menntion_text)" #qua andrà il mention text tra parentesi
                # "range.setStart(textNode, ind);"
                # "range.setEnd(textNode, (ind+mention_text.length));"

                "var range = document.createRange();"
                "range.setStart(textNode, ind);"
                "range.setEnd(textNode, (ind + (arguments[0]).length));"
                "const clientRect = range.getBoundingClientRect();"
                "if(clientRect['height'] > 17){window.getSelection().addRange(range);}"

                "return clientRect", mention

            )

            body1 = driver.find_element_by_xpath('//body')
            action = ActionChains(driver)
            # print(body.location)
            # print(clientRect)

            # current_x = 518
            # current_y = 337
            to_ins_x = int(clientRect['x'] - int(current_x))
            to_ins_y = int(clientRect['y'] - current_y)
            to_ins_y_1 = int(clientRect['bottom'] - current_y)

            # to_ins_x1 = int(clientRect['x'] + clientRect['width'])
            # to_ins_y1 = int(clientRect['height'] - clientRect['y'])
            # print(to_ins_x1)
            # print(to_ins_y1)
            # print(to_ins_x)
            # print(to_ins_y)
            if clientRect['height'] > 17:  # new line!
                # print('')
                action.move_to_element(body1).move_by_offset(to_ins_x, to_ins_y_1).click().perform()
                clicks = clicks + 1
            else:
                action.move_to_element(body1).move_by_offset(to_ins_x, to_ins_y).click_and_hold().move_by_offset(
                    clientRect['right'] - clientRect['x'], 0).release().perform()
                clicks = clicks + 1
            time.sleep(0.3)
        # driver.find_element_by_xpath('//label[text()="Done"]').click()
        # clicks = clicks +1
        doc = doc + 1
        # print('doc: ' + str(doc))
        count = count - 1
        if count >= num - 99:
            # if count >= 208534:
            url = "https://eztag.bioqrator.org/documents/" + str(count)
            clicks = clicks + 1
            driver.get(url)
    tot = time.time() - st
    print('tot: ' + str(tot))

    return clicks, tot


if __name__ == '__main__':
    my_url = "" # INSERT HERE THE URL GIVEN BY EZTAG WHEN YOU SIGNED IN
    name_coll = "MedTAG Collection"
    exec_path = "" # INSERT HERE THE PATH TO THE DRIVER
    driver = webdriver.Chrome(executable_path=exec_path)

    c = 0
    timer = 0
    data = []
    mentions_list_1 = {}
    while c < 40:
        time.sleep(1)
        print('count: ' + str(c))
        num,mentions_list,url1 = login(driver,my_url,name_coll)
        # mentions_list_1 = {}
        if c == 0:
            # element1 = driver.execute_script("""
            # return document.elementFromPoint(518, 337);
            # """)
            #
            # print(element1.get_attribute('class'))
            # print(element1.get_attribute('src'))
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//img[@src="/assets/demo-83ede5c705c395bd49e1d9a9554985edb668154d22710241055b4843300aab22.gif"]'))
            )

            # print(element.is_displayed())
            # print(element.location)
            # print(element.size)
            ele2 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="ui red deny button"]'))
            )
            # print(ele2.location)
            # print(ele2.size)
            loc = element.location
            siz = element.size
            current_x = loc['x'] + (siz['width'] / 2)
            current_y = loc['y'] + (siz['height'] / 2)
            # print(current_x)
            # print(current_y)
            ele2.click()
            mentions_list_1 = define_json(driver, num, mentions_list)



        click, tot = find_mentions(driver, num, mentions_list_1,current_x,current_y)

        timer = timer + tot
        data.append(tot)
        print('clicks: ' + str(click))
        # print('tot: '+str(tot))
        c = c + 1
        driver.get(url1)
        elem1 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//i[@class="settings icon"]'))
        )
        elem1.click()
        time.sleep(0.5)
        # driver.find_element_by_xpath('//i[@class="settings icon"]').click()
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[text()="Delete All Annotations"]'))
        )
        elem.click()
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
    print('totale: ' + timer)
    print('std: ' + str(statistics.stdev(data)))

    # if log_in:
    #     timer = exatag_lab_test(driver)
    #     print(timer)