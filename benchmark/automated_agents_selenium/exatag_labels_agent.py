from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2
import time
import statistics
from selenium.webdriver.support.select import Select

import json
def wait_until_unchecked(driver,nums_3):
        inp = driver.find_elements_by_xpath('//input[@name="labels"]')
        count = 0
        for el in nums_3:
            if inp[el].is_selected() == False:
                count = count +1
        if count == len(nums_3):
            return inp
        else:
            return False




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
            EC.presence_of_element_located((By.XPATH, '//button[text()="Labels"]'))
        )
        ele1.click()

    except Exception as e:
        print('ERROR')
        print(e)
        return False

    else:
        # print('ok')
        return True


def exatag_lab_test(driver):


        f = open('../datasets/labels/labels.json','r')
        reports1 = json.load(f)
        reports = []
        for key in reports1.keys():
            label = reports1[key]
            reports.append(label)

        try:

            count = 0
            nums = []
            while count < 100:
                labs = reports[count]
                nums_1 = []

                for cop in labs:
                    if cop == 'Cancer':
                        nums_1.append(0)
                    elif cop == 'Adenomatous polyp - high grade dysplasia':
                        nums_1.append(1)
                    elif cop == 'Adenomatous polyp - low grade dysplasia':
                        nums_1.append(2)
                    elif cop == 'Hyperplastic polyp':
                        nums_1.append(3)
                    elif cop == 'Non-informative':
                        nums_1.append(4)
                nums.append(nums_1)
                count = count+1
                # print(str(count))
                # print(str(labs))
                # print('\n')
            count = 0
            testo = ''
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="container_list"]'))
            )
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="report_sel"]'))
            )
            inp = driver.find_elements_by_xpath('//input[@name="labels"]')

            start = time.time()
            click = 0
            while count < 100:
                # time.sleep(0.02)

                # if count > 0:
                # selected_option = select.first_selected_option
                # if (selected_option.get_attribute('value') == str(count)):
                time.sleep(0.02)
                testo_rep = driver.find_element_by_xpath('//div[@id="report_sel"]')
                if (testo != testo_rep.text):
                    testo = testo_rep.text
                    nums_3 = []
                    nums_2 = nums[count]
                    # if count>0:
                    #     nums_3 = nums[count-1]




                    sel = False
                    while sel == False:
                        ss = 0
                        for el in range(len(inp)):
                            if inp[el].is_selected() == False:
                                ss = ss + 1
                            else:
                                break
                        if ss == len(inp):
                            sel = True
                    if sel:
                        for el in nums_2:
                            inp[el].click()
                            click = click+1
                        # time.sleep(0.02)
                        driver.find_element_by_xpath('//button[@id="but_sx"]').click()
                        click = click+1
                        time.sleep(0.2)
                        # time.sleep(0.02)
                        count = count + 1




            end = time.time()
            tot = end - start
            print('tot: '+str(tot))
            print('click:  '+str(click))
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

            return tot

        except Exception as e:
            print('ERROR')
            print(e)
            return False

        # else:
        #     # print('ok')
        #     # driver.quit()
        #     cursor.execute('SELECT gt_json FROM ground_truth_log_file WHERE username = %s ORDER BY insertion_time ASC',
        #                    ['selenium_test'])
        #     ans = cursor.fetchall()
        #     if len(ans) != len(reports):
        #         st = 'A groundtruth is missing'
        #         return st
        #     count = 0
        #     while count < 100:
        #         # report = json.dump(reports[count])
        #         labs_john = reports[count]['labels']
        #         nums = []
        #         json_el = ans[count][0]
        #
        #
        #         for cop in labs_john:
        #             nums.append(int(cop['seq_number']))
        #
        #         labs_sel = json_el['labels']
        #         for cop in labs_sel:
        #             # print(cop['seq_number'])
        #             # print(nums)
        #             # print('\n')
        #             if cop['seq_number'] not in nums:
        #                 stringa = str(count) + ' : ' + str(cop) + ' is missing.'
        #                 return stringa
        #         # cursor.execute('SELECT gt_json FROM ground_truth_log_file WHERE username = %s ORDER BY insertion_time ASC',['selenium_test'])
        #         # ans = cursor.fetchall()
        #         # for el in ans:
        #         #     json_el = el[0]
        #         #     lab = json_el['labels']
        #         #     for cop in lab:
        #         #         print(cop['seq_number'])
        #         #         print(nums)
        #         #         print('\n')
        #         #         if cop['seq_number'] not in nums:
        #         #             stringa = str(count) + ' : ' + str(cop) + ' is missing.'
        #         #             return stringa
        #         count = count+1
        #     return tot

    # except (Exception, psycopg2.Error) as e:
    #     print(e)
    #
    #
    # finally:
    #     # closing database connection.
    #     if (connection):
    #         cursor.close()
    #         connection.close()



if __name__ == '__main__':
        exec_path = "" # INSERT HERE THE PATH TO THE DRIVER
        driver = webdriver.Chrome(executable_path=exec_path)
        data = []
        timer = 0
        try:
            c = 0
            log_in = login(driver)
            if log_in:
                while c < 40:
                    time.sleep(2)
                    print(str(c))
                    # connection = psycopg2.connect(dbname="groundtruthdb", user="ims", password="grace.period", host="localhost",
                    #                               port="5444")
                    #
                    # cursor = connection.cursor()
                    # cursor.execute('SELECT COUNT(*) FROM associate where username = %s;',['selenium_test'])
                    # ans = cursor.fetchone()[0]
                    # if(ans == 100):
                    #     cursor.execute('DELETE FROM associate where username = %s;',['selenium_test'])
                    #     connection.commit()
                    #
                    # cursor.execute('SELECT COUNT(*) FROM ground_truth_log_file where username = %s AND gt_type = %s;',['selenium_test','labels'])
                    # ans = cursor.fetchone()[0]
                    # if(ans == 100):
                    #     cursor.execute('DELETE FROM ground_truth_log_file where username = %s and gt_type = %s;',['selenium_test','labels'])
                    #     connection.commit()

                    if c > 0:
                        driver.refresh()
                        ele1 = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//button[text()="Labels"]'))
                        )
                        ele1.click()

                    timer_1 = exatag_lab_test(driver)
                    data.append(timer_1)
                    print(str(timer_1))
                    if(type(timer_1) == 'str'):
                        break
                    else:
                        timer = timer + timer_1
                    c = c+1


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

