import fnmatch
import logging
import os
import sys
import selenium
import urllib3
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, \
    ElementNotInteractableException, ElementClickInterceptedException, UnexpectedAlertPresentException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import requests
import statistics


def delete_reports(docs_ids):
    counter = 0  # Success delete operation counter
    for doc_id in docs_ids:
        time.sleep(0.5)
        while True:
            try:
                if delete_report(doc_id) == 200:
                    counter += 1
                    break
            except (urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectionError) as e:
                time.sleep(1)
                pass

    if counter == len(docs_ids):
        return True # All the documents successfully deleted

    return False # Some documents not deleted


def delete_report(doc_id):
    tagtogAPIUrl = "https://www.tagtog.net/-api/documents/v1"
    username = ""  # Put here the username of your tagtog account
    password = ""  # Put here the password of your tagtog account
    tagtog_project_name = ""  # Put here the name of your tagtog project

    auth = requests.auth.HTTPBasicAuth(username=username, password=password)
    params = {"owner": username, "project": tagtog_project_name, 'idType': 'tagtogID', "ids": doc_id}
    response = requests.delete(tagtogAPIUrl, params=params, auth=auth)
    return response.status_code


def upload_reports():
    username = ""  # Put here the username of your tagtog account
    password = ""  # Put here the password of your tagtog account
    tagtog_project_name = ""  # Put here the name of your tagtog project
    medtag_core_project_root = ""  # Put here your project root
    documents_path = medtag_core_project_root + "benchmark/datasets/documents/"
    files = os.listdir(documents_path)
    reports = []
    pattern = "*.txt"
    for filename in files:
        if fnmatch.fnmatch(filename, pattern):
            reports.append(filename)
    for report in reports:
        time.sleep(0.2)
        os.system(
            f"python3 tagtog.py upload {documents_path + report} -u {username} -w {password} -o {username} -p {tagtog_project_name}")


def delete_and_upload_reports(docs_id):
    delete_reports(docs_id)
    upload_reports()


def annotate_labels(driver):
    username = ""  # Put here the username of your tagtog account
    docID = ""  # Put here the id of the first document by which starting the annotation process
    medtag_core_project_root = ""  # Put here your project root
    labels_path = medtag_core_project_root + "benchmark/datasets/labels/"
    login(driver)  # log into tagtog

    driver.get(
        f"https://www.tagtog.net/{username}/test/pool/{docID}")

    with open(labels_path + "labels.json", "r") as f_read:

        reports = json.load(f_read)

    start = time.time()  # Init time stopwatch
    n_clicks = 0  # Number of clicks used to annotate 100 reports

    for report in reports.keys():
        labels = reports[report]
        print(report, labels)

        for label in labels:

            label_txt = label
            select_id = None

            if label_txt == "Adenomatous polyp - high grade dysplasia":
                select_id = 6
                menu_option_to_click = 1
            elif label_txt == "Adenomatous polyp - low grade dysplasia":
                select_id = 7
                menu_option_to_click = 2
            elif label_txt == "Cancer":
                select_id = 5
                menu_option_to_click = 3
            elif label_txt == "Hyperplastic polyp":
                select_id = 8
                menu_option_to_click = 4
            elif label_txt == "Non-informative":
                select_id = 9
                menu_option_to_click = 5

            # option_to_click = 0 # ?
            option_to_click = 1  # true
            # option_to_click = 2 # false

            time.sleep(0.2)

            menu_id_to_open = "bs-select-" + str(menu_option_to_click) + "-" + str(option_to_click)

            while (True):
                try:
                    menu = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//button[@data-id="select-m_' + str(select_id) + '"]'))
                        # menu
                    )
                    menu.click()
                    n_clicks += 1
                    break
                except (TimeoutException, ElementNotInteractableException, ElementClickInterceptedException) as e:
                    driver.refresh()
                    time.sleep(0.5)
                    pass
                except UnexpectedAlertPresentException as e:
                    driver.refresh()
                    time.sleep(0.5)
                    pass

            time.sleep(0.2)

            while (True):
                try:
                    menu_options = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//a[@id="' + menu_id_to_open + '"]'))
                        # menu_options
                    )
                    menu_options.click()
                    n_clicks += 1
                    break
                except (TimeoutException, ElementNotInteractableException, ElementClickInterceptedException) as e:
                    driver.refresh()
                    time.sleep(0.5)
                    menu = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//button[@data-id="select-m_' + str(select_id) + '"]'))
                        # menu
                    )
                    menu.click()
                    pass
                except UnexpectedAlertPresentException as e:
                    driver.refresh()
                    time.sleep(0.5)
                    menu = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//button[@data-id="select-m_' + str(select_id) + '"]'))
                        # menu
                    )
                    menu.click()
                    pass

            time.sleep(0.2)

            while (True):
                try:
                    save_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//button[@id="save-doc"]'))
                        # button save doc
                    )
                    save_button.click()
                    n_clicks += 1
                    break
                except (TimeoutException, ElementNotInteractableException, ElementClickInterceptedException) as e:
                    x1 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[@data-reactid=".2.2.1.0.1.0.1.$m_6.1.1.$remove-m_6.0"]')))
                    x1.click()
                    time.sleep(0.5)
                    pass
                except UnexpectedAlertPresentException as e:
                    driver.refresh()
                    time.sleep(0.5)
                    x1 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[@data-reactid=".2.2.1.0.1.0.1.$m_6.1.1.$remove-m_6.0"]')))
                    x1.click()
                    pass

            # webdriver.ActionChains(driver).send_keys("s").perform() # save report

            time.sleep(0.2)

            # webdriver.ActionChains(driver).send_keys("]").perform() # next report

            while (True):
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//a[@title="next item"]'))
                        # button next_button
                    )

                    next_button.click()
                    n_clicks += 1
                    break
                except (TimeoutException, ElementNotInteractableException, ElementClickInterceptedException) as e:
                    driver.refresh()
                    time.sleep(0.5)
                    pass
                except UnexpectedAlertPresentException as e:
                    driver.refresh()
                    time.sleep(0.5)
                    pass

    end = time.time()  # Stopwatch end time
    time_elapsed = end - start  # time elapsed
    print(f"Time elapsed: {time_elapsed}")
    print(f"Number of clicks {n_clicks}")

    return time_elapsed, n_clicks


def get_documents_id(driver):
    username = ""  # Put here the username of your tagtog account

    login(driver)
    docs_id = []

    driver.get(
        f"https://www.tagtog.net/{username}/test/pool")  # First page of documents

    time.sleep(0.5)
    elems = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[@href]'))
    )
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        href = elem.get_attribute("href")
        if f"https://www.tagtog.net/{username}/test/pool/" in href and ".txt" in href:
            doc_id = href.replace(f"https://www.tagtog.net/{username}/test/pool/", "").replace(
                f"https://www.tagtog.net/{username}/test/pool/", "")
            pos = doc_id.find("?p=")
            doc_id = doc_id[0:pos]

            if doc_id not in docs_id:
                docs_id.append(doc_id)

    driver.get(f"https://www.tagtog.net/{username}/test/pool?p=1")  # Second page of documents
    time.sleep(0.5)
    elems = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[@href]'))
    )
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        href = elem.get_attribute("href")
        if f"https://www.tagtog.net/{username}/test/pool/" in href and ".txt" in href:
            doc_id = href.replace(f"https://www.tagtog.net/{username}/test/pool/", "").replace(
                f"https://www.tagtog.net/{username}/test/pool/", "")
            pos = doc_id.find("?p=")
            doc_id = doc_id[0:pos]

            # print(doc_id)
            if doc_id not in docs_id:
                docs_id.append(doc_id)
    return docs_id


def login(driver):
    username = ""  # put here your tagtog username
    password = ""  # put here your tagtog pasword
    driver.get("https://www.tagtog.net/-login")
    session_id = driver.session_id
    executor_url = driver.command_executor._url

    element = driver.find_element_by_id("loginid")
    element.send_keys(username)
    element = driver.find_element_by_id("password")
    element.send_keys(password)

    submits = driver.find_elements_by_class_name("btn-warning")

    for submit in submits:
        submit.click()


def initFireFoxDriver():
    # Initialize the selenium driver. NOTE: you need to set the correct path to the Firefox "geckodriver"
    driver = webdriver.Firefox()
    return driver


def annotate_mentions(driver, docs):
    medtag_core_project_root = ""  # Put here your project root
    mentions_folder = medtag_core_project_root + "/datasets/mentions/"
    username = ""  # put here your tagtog username
    docID = ""  # Put here the id of the first document by which starting the annotation process
    reports_mentions = {}
    with open(mentions_folder + "mentions.json", "r") as f_in:
        reports_mentions = json.load(f_in)

    driver.get(
        f"https://www.tagtog.net/{username}/test/pool/{docID}")

    start = time.time()  # Init time stopwatch
    n_clicks = 0  # Number of clicks used to annotate 100 reports

    print(reports_mentions)
    for doc in docs:
        mentions = []
        doc_id = doc[doc.find("-") + 1:].replace(".txt", "")
        for report in reports_mentions["mentions_list"]:
            if report['id_report'] == doc_id:
                mentions = report["mentions"]
                break

        time.sleep(0.2)

        diagnosis_text_item = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//pre[@id="s1v1"]'))
        )

        diagnosis_text = diagnosis_text_item.get_attribute('innerHTML')
        print(diagnosis_text)

        for index, mention in enumerate(mentions):
            print(f"mention: {mention}")

            diagnosis_text = diagnosis_text.replace(mention, f"<span class='mention'>{mention}</span>", 1)
            print(diagnosis_text)
            time.sleep(0.2)
            driver.execute_script("var ele = document.getElementById('s1v1'); ele.innerHTML=arguments[0];",
                                  diagnosis_text)

        mentions_processed = []

        for m_i in range(len(mentions)):
            men_i = mentions[m_i]
            mentions_sem = driver.find_elements_by_class_name("mention")

            for m_i_j in mentions_sem:
                if m_i_j.text == men_i:
                    webdriver.ActionChains(driver).move_to_element(m_i_j).move_by_offset(-m_i_j.size['width'] / 2,
                                                                                         0).click_and_hold().move_by_offset(
                        m_i_j.size['width'], 0).release().perform()
                    n_clicks += 1
                    mentions_processed.append(men_i)
                    break

            diagnosis_text_item = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//pre[@id="s1v1"]'))
            )
            if m_i + 1 < len(mentions):
                diagnosis_text = diagnosis_text_item.get_attribute('innerHTML')
                diagnosis_text = diagnosis_text.replace(mentions[m_i + 1],
                                                        f"<span class='mention'>{mentions[m_i + 1]}</span>", 1)
                print(diagnosis_text)
                driver.execute_script("var ele = document.getElementById('s1v1'); ele.innerHTML=arguments[0];",
                                      diagnosis_text)

        webdriver.ActionChains(driver).send_keys("s").perform()
        n_clicks += 1

        time.sleep(0.2)

        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@title="next item"]'))
            # button next_button
        )

        next_button.click()
        n_clicks += 1

    end = time.time()  # Stopwatch end time
    time_elapsed = end - start
    print(f"Time elapsed: {time_elapsed}")
    print(f"Number of clicks: {n_clicks}")

    return time_elapsed


def remove_annotations(driver):
    username = ""  # Put here your tagtog username
    docID = ""  # Put here the id of the first document in your tagtog collection
    login(driver)
    driver.get(
        f"https://www.tagtog.net/{username}/test/pool/{docID}")

    for i in range(100):
        try:
            time.sleep(0.2)

            while (True):
                try:
                    x1 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[@data-reactid=".2.2.1.0.1.0.1.$m_5.1.1.$remove-m_5.0"]')))
                    break
                except selenium.common.exceptions.TimeoutException:
                    webdriver.ActionChains(driver).send_keys("[").perform()
                    time.sleep(0.5)
                    webdriver.ActionChains(driver).send_keys("]").perform()
                    pass
            x1.click()

            time.sleep(0.2)

            while (True):
                try:
                    x2 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[@data-reactid=".2.2.1.0.1.0.1.$m_6.1.1.$remove-m_6.0"]')))
                    break
                except selenium.common.exceptions.TimeoutException:
                    webdriver.ActionChains(driver).send_keys("[").perform()
                    time.sleep(0.5)
                    webdriver.ActionChains(driver).send_keys("]").perform()
                    pass

            x2.click()

            time.sleep(0.2)

            while (True):
                try:
                    x3 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[@data-reactid=".2.2.1.0.1.0.1.$m_7.1.1.$remove-m_7.0"]')))
                    break
                except selenium.common.exceptions.TimeoutException:
                    webdriver.ActionChains(driver).send_keys("[").perform()
                    time.sleep(0.5)
                    webdriver.ActionChains(driver).send_keys("]").perform()
                    pass

            x3.click()

            time.sleep(0.2)

            while (True):
                try:
                    x4 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[@data-reactid=".2.2.1.0.1.0.1.$m_8.1.1.$remove-m_8.0"]')))
                    break
                except selenium.common.exceptions.TimeoutException:
                    webdriver.ActionChains(driver).send_keys("[").perform()
                    time.sleep(0.5)
                    webdriver.ActionChains(driver).send_keys("]").perform()
                    pass

            x4.click()

            time.sleep(0.2)

            while (True):
                try:
                    x5 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//span[@data-reactid=".2.2.1.0.1.0.1.$m_9.1.1.$remove-m_9.0"]')))
                    break
                except selenium.common.exceptions.TimeoutException:
                    webdriver.ActionChains(driver).send_keys("[").perform()
                    time.sleep(0.5)
                    webdriver.ActionChains(driver).send_keys("]").perform()
                    pass

            x5.click()

        except selenium.common.exceptions.UnexpectedAlertPresentException:
            # Switch the control to the Alert window and accept
            obj = driver.switch_to.alert.accept()

        time.sleep(0.2)

        trash_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@id="dropdownDelActions"]')))
        trash_button.click()

        time.sleep(0.2)

        remove_annotations_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Remove annotations']")))
        remove_annotations_button.click()

        time.sleep(0.2)

        # Switch the control to the Alert window and accept
        obj = driver.switch_to.alert.accept()

        webdriver.ActionChains(driver).send_keys("s").perform()

        time.sleep(0.2)

        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@title="next item"]'))
            # button next_button
        )

        next_button.click()

        time.sleep(0.2)


# program entry point
if __name__ == '__main__':
    driver = initFireFoxDriver()
    if len(sys.argv) == 2:
        action = sys.argv[1]
        if action == "annotate_labels":
            exec_times_array_labels = []
            for i in range(40):
                docs = get_documents_id(driver)
                delete_and_upload_reports(docs)
                t = annotate_labels(driver)
                exec_times_array_labels.append(t)
                print(f"exec_times_array_labels: {exec_times_array_labels}")
            exec_times_array_labels_str = [str(t_i) for t_i in exec_times_array_labels]
            mean_labels = statistics.mean(exec_times_array_labels)
            stdev_labels = statistics.stdev(exec_times_array_labels)
            print(f"Mean (labels): {mean_labels} ; Stdev (labels): {stdev_labels}")
            with open('out_elapsed_times_labels.txt', "w") as f_out_et:
                f_out_et.write("\n".join(exec_times_array_labels_str))
        elif action == "annotate_mentions":
            exec_times_array = []
            for i in range(40):
                docs = get_documents_id(driver)
                if len(docs) == 100:
                    t = annotate_mentions(driver, docs)
                    exec_times_array.append(str(t))
                else:
                    logging.error("Number of documents passed less (<) than 100!")
            mean = statistics.mean(exec_times_array)
            stdev = statistics.stdev(exec_times_array)
            exec_times_array_mentions_str = [str(t_i) for t_i in exec_times_array]
            print(f"Mean (mentions): {mean} ; Stdev (mentions): {stdev}")
            with open('out_elapsed_times_mentions.txt', "w") as f_out_et:
                f_out_et.write("\n".join(exec_times_array_mentions_str))
        elif action == "delete_reports":
            docs = get_documents_id(driver)
            delete_reports(docs)
        elif action == "upload_reports":  # Delete all the present reports and then uploads the new ones
            docs = get_documents_id(driver)
            delete_reports(docs)
            upload_reports()
        elif action == "remove_annotations":
            remove_annotations(driver)
        else:
            logging.error(
                "Action not recognised! choose betweeen ('annotate_labels', 'annotate_mentions', 'delete_reports'):")
    else:
        logging.error(
            "Action not provided! choose betweeen ('annotate_labels', 'annotate_mentions', 'delete_reports'):")
