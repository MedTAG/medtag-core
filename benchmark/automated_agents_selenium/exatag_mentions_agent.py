from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2
import time
import json
import statistics
def login(driver):
    username = "selenium_test"
    password = "selenium"

    driver.get("http://examode.dei.unipd.it/exatag/")
    driver.find_element_by_id("inputUsername").send_keys(username)
    driver.find_element_by_id("inputPassword").send_keys(password)
    driver.find_element_by_xpath('//button[text()="Log In"]').click()
    try:
        ele = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Start"]'))
        )

        all_spans = driver.find_elements_by_xpath("//div[@class='selection css-2b097c-container']")
        for element in all_spans:
            element.click()
            if all_spans.index(element) == 0:
                driver.find_element_by_xpath('//div[text()="English"]').click()
            elif all_spans.index(element) == 1:
                driver.find_element_by_xpath('//div[text()="Colon"]').click()
            else:
                driver.find_element_by_xpath('//div[text()="AOEC"]').click()
        ele.click()
        ele1 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Mentions"]'))
        )
        ele1.click()

    except Exception as e:
        print('ERROR')
        print(e)
        return False

    else:
        print('ok')
        return True


def exatag_mentions_test(driver):


    try:
        count = 0
        f = open('../datasets/mentions/mentions.json')
        mentions_json = json.load(f)
        mentions_list = mentions_json['mentions_list']
        clicks = 1

        ele2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="mentions_list"]'))
        )
        report_ = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="report_sel"]'))
        )
        start_time = time.time()
        for i in range(len(mentions_list)):
            # print(str(i))
            elem = mentions_list[i]
            texts = elem['mentions']
            starts = elem['start']
            for s in range(len(starts)):
                mention = texts[s]
                # print(mention)
                ele2 = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="mentions_list"]'))
                )
                report_ = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="report_sel"]'))
                )
                if (ele2.is_displayed() and report_.is_displayed()):
                    driver.find_element_by_xpath('//button[@id=' +str(starts[s]) +']').click()
                    mention_len = len(mention.split(' '))
                    cou = 1
                    while cou < mention_len:
                        driver.find_element_by_xpath('//button[@class="token-adj-dx"]').click()
                        clicks = clicks + 1
                        cou = cou+1
                    driver.find_element_by_xpath('//button[text()="Add"]').click()
                    clicks = clicks + 1
                    time.sleep(0.3)
            driver.find_element_by_xpath('//button[@id="but_sx"]').click()

        tot = time.time() - start_time
        print(tot)

        for i in range(100):
            driver.find_element_by_xpath('//button[@id="but_dx"]').click()
            time.sleep(0.3)

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="Clear"]'))
            ).click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[text()="Yes"]'))
            ).click()
            time.sleep(0.3)




    except Exception as e:
        print('ERROR')
        print(e)
        return False

    else:
        # print('ok')
        #driver.quit()
        print(str(clicks))
        return tot




if __name__ == '__main__':
        exec_path = "" #INSERT HERE THE PATH TO THE DRIVER
        driver = webdriver.Chrome(executable_path=exec_path)
        data = []
        # data.append(164.54318714141846)
        # data.append(158.71419215202332)
        timer = 0
        try:
            c = 0
            log_in = login(driver)
            if log_in:
                while c < 40:
                    time.sleep(1)
                    print(str(c))
                    # connection = psycopg2.connect(dbname="groundtruthdb", user="ims", password="grace.period",
                    #                               host="localhost",
                    #                               port="5444")
                    #
                    # cursor = connection.cursor()
                    # cursor.execute('SELECT COUNT(*) FROM annotate where username = %s;', ['selenium_test'])
                    # ans = cursor.fetchone()[0]
                    # if (ans <=207):
                    #     cursor.execute('DELETE FROM annotate where username = %s;', ['selenium_test'])
                    #     connection.commit()
                    #
                    # cursor.execute('SELECT COUNT(*) FROM ground_truth_log_file where username = %s AND gt_type = %s;',
                    #                ['selenium_test', 'mentions'])
                    # ans = cursor.fetchone()[0]
                    # if (ans <= 100):
                    #     cursor.execute('DELETE FROM ground_truth_log_file where username = %s and gt_type = %s;',
                    #                    ['selenium_test', 'mentions'])
                    #     connection.commit()

                    if c > 0:
                        driver.refresh()
                        ele1 = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//button[text()="Mentions"]'))
                        )
                        ele1.click()

                    timer_1 = exatag_mentions_test(driver)
                    data.append(timer_1)
                    # print(str(timer_1))
                    if (type(timer_1) == 'str'):
                        break
                    else:
                        timer = timer + timer_1
                    c = c + 1

        except (Exception, psycopg2.Error) as e:
            print(e)


        finally:
            # closing database connection.
            # if (connection):
            #     cursor.close()
            #     connection.close()
                print(timer)
                std = statistics.stdev(data)
                print(str(std))

