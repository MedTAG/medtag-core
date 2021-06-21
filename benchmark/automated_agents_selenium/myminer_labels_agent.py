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

def my_miner_labels(driver,absolute_path_for_collection):
    # absolute_path_for_collection = ""
    driver.get('https://myminer.armi.monash.edu.au/')

    driver.get('https://myminer.armi.monash.edu.au/curator.php')






    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="filepath"]'))
    ).send_keys(absolute_path_for_collection)
    time.sleep(0.1)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@src="pics/upload.jpg"]'))).click()
    time.sleep(0.1)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="input_1"]'))).send_keys('Cancer')
    time.sleep(0.1)

    driver.find_element_by_xpath('//a[text()="Add new label"]').click()
    time.sleep(0.1)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="input_2"]'))).send_keys('Adenomatous polyp - high grade dysplasia')
    time.sleep(0.1)

    driver.find_element_by_xpath('//a[text()="Add new label"]').click()
    time.sleep(0.1)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="input_3"]'))).send_keys('Adenomatous polyp - low grade dysplasia')
    time.sleep(0.1)

    driver.find_element_by_xpath('//a[text()="Add new label"]').click()
    time.sleep(0.1)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="input_4"]'))).send_keys('Hyperplastic polyp')
    time.sleep(0.1)
    driver.find_element_by_xpath('//a[text()="Add new label"]').click()
    time.sleep(0.1)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="input_5"]'))).send_keys('Non-informative')
    time.sleep(0.1)

    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@src="pics/go.jpg"]')))
    elem.click()
    time.sleep(0.1)

    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@src="pics/go.jpg"]')))
    elem.click()
    time.sleep(0.1)
    # elems = driver.find_elements_by_xpath('//div[@id="free_text_uploader"]/input')
    # elem = elems[2]
    # elem.click()
    f = open('../datasets/labels/labels.json','r')
    reports = json.load(f)
    # print(str(len(reports)))
    st = time.time()
    testo_or = ''
    count = 1
    clicks = 0
    for key in reports.keys():
        label = reports[key][0]
        # print(label)

        doc = 'documento_'+str(count)
        testo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'//div[text()="'+doc+'"]')))

        # testo = testo.text
        # print(testo)
        # equal = False
        # while equal:
        #     if testo != testo_or:
        #         equal = False
        # if equal == False:
        #     testo_or = testo
        driver.find_element_by_xpath('//button[text()="'+label+'"]').click()
        # driver.find_element_by_xpath('//button[text()="Exported tagged files"]').click()
        # clicks = clicks+1
        # WebDriverWait(driver, 10).until(
        # EC.presence_of_element_located((By.XPATH, '//button[text()="'+label+'"]'))).click()
        #time.sleep(0.2)
        count = count +1
    tot = time.time() - st
    print('tot: '+str(tot))
    # print('clicks: '+str(clicks))
    return tot

if __name__ == '__main__':
    exec_path = "" # INSERT HERE THE ABSOLUTE PATH TO THE DRIVER
    driver = webdriver.Chrome(executable_path=exec_path)
    absolute_path_for_collection = "" # INSERT HERE THE ABSOLUTE PATH TO THE FILE collection.txt
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