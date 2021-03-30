import os, sys, time, keyboard, selenium, requests, pytest, re, datetime, urllib3, telnetlib, glob, socket, ctypes, subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from splinter import Browser as browser
from threading import Timer

update_successful_counter = 0
update_failed_counter = 0
upgrade_counter = 0
downgrade_counter = 0
same_firmware_update_counter = 0
default_counter = 0
recovery_counter = 0
cycle_counter = 0

cloud_server_url_list = ["https://snapav-firmware.s3.amazonaws.com/Network/AN810-AccessPoint/an810i-v2.1.01.03.bin",
                         "https://snapav-firmware.s3.amazonaws.com/Network/AN810-AccessPoint/an810i-v2.1.01.04.bin"]
version_list = []

output_filename = input("Enter name to save file as: ")
# x10_IP = input("Enter IP: ")
# x10_username = input("Enter username: ")
# x10_password = input("Enter password: ")
# x10_lan1_mac = input("Enter LAN 1 MAC: ")
user_cycles = input("Enter number of loop/cycles: ")

output_filepath = "/Users/Amitabh.Mishra/Documents/AN-810/Script Outputs/{}.txt".format(output_filename)

x10_IP = "10.1.20.113"
x10_username = "araknis"
x10_password = "snapav704"
x10_lan1_mac = "D4:6A:91:E5:B7:3B"

def get_cdt():
    global currentDateTime
    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    return currentDateTime

def list_versions():
    global firmware_version

    for urls in range(0, len(cloud_server_url_list)):
        firmware_version = cloud_server_url_list[urls].split("-v")[-1].split(".bin")[0]
        version_list.append(firmware_version)
        print("{}. {}".format(urls + 1, firmware_version))
    
def firmware_bu():
    global firmware_before_update

    tn = telnetlib.Telnet(x10_IP) 
    tn.read_until(b"login as: ") 
    tn.write(b"araknis\n") 
    tn.read_until(b"araknis's password: ") 
    tn.write(b"snapav704\n")
    time.sleep(1)
    tn.write(b"stat\n") 
    time.sleep(1)
    tn.write(b"main\n") 
    time.sleep(1)
    tn.read_until(b"Firmware Version -- ")
    firmware_before_update = tn.read_very_eager().decode("ascii")[:9]
    tn.close()

    get_cdt()
    print(currentDateTime + " - Firmware Version (Before Update): {}".format(firmware_before_update))
    print(currentDateTime + " - Firmware Version (Before Update): {}".format(firmware_before_update), file = outputFile)

    time.sleep(5)

    return firmware_before_update

list_versions() 
upgrade_choice = input("Enter which firmware to upgrade to: ")
downgrade_choice = input("Enter which firmware to downgrade to: ")
user_start = input("Start (Y/N): ")

def login():
    WebDriverWait(chrome_driver, 30).until(ec.visibility_of_element_located((By.ID, "user")))
    chrome_driver.find_element_by_id("user").send_keys(x10_username)
    chrome_driver.find_element_by_id("pass").send_keys(x10_password)
    chrome_driver.find_element_by_css_selector(".btn-primary:nth-child(1)").click()

    get_cdt()
    print(currentDateTime + " - Successful Login")
    print(currentDateTime + " - Successful Login", file = outputFile)

def webservice_page():
    chrome_driver.get("http://{}/webservice.htm".format(x10_IP))
    login()
    WebDriverWait(chrome_driver, 30).until(ec.visibility_of_element_located((By.ID, "tbl_service")))
    chrome_driver.find_element_by_id("basic_Url").clear()
    chrome_driver.find_element_by_id("basic_Url").send_keys("wss://firmware.testing.ovrc.com")
    chrome_driver.find_element_by_id("basic_Port_number").clear()
    chrome_driver.find_element_by_id("basic_Port_number").send_keys("12443")
    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".button1:nth-child(1)")))
    chrome_driver.find_element_by_css_selector(".button1:nth-child(1)").click()
    time.sleep(5)

def firmware_test_page():
    chrome_driver.execute_script("window.open('https://admin:abs01ut3@firmware.testing.ovrc.com/emplus/meshWap.html', 'new_window')")
    chrome_driver.switch_to.window(chrome_driver.window_handles[1])
    chrome_driver.find_element_by_id("tbMacAddress").clear()
    WebDriverWait(chrome_driver, 30).until(ec.visibility_of_element_located((By.ID, "tbMacAddress"))).send_keys(x10_lan1_mac)
    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.ID, "btnConnect"))).click()
    # chrome_driver.find_element_by_id("btnConnect").click()
    time.sleep(10)

def get_online_offline_status():
    global device_status

    device_status = chrome_driver.find_element_by_id("statusText").text
    # WebDriverWait(chrome_driver, 30).until(ec.text_to_be_present_in_element((By.ID, "statusText"), "Device is online"))

    return device_status

def retry_webservice():
    get_cdt()
    print(currentDateTime + " - Retrying Webservice")
    print(currentDateTime + " - Retrying Webservice")

    chrome_driver.switch_to.window(chrome_driver.window_handles[0])
    WebDriverWait(chrome_driver, 30).until(ec.visibility_of_element_located((By.ID, "tbl_service")))
    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".button1:nth-child(1)")))
    chrome_driver.find_element_by_css_selector(".button1:nth-child(1)").click()
    chrome_driver.switch_to.window(chrome_driver.window_handles[1])

    time.sleep(10)

def firmware_au():
    global firmware_after_update

    tn = telnetlib.Telnet(x10_IP) 
    tn.read_until(b"login as: ") 
    tn.write(b"araknis\n") 
    tn.read_until(b"araknis's password: ") 
    tn.write(b"snapav704\n")
    time.sleep(1)
    tn.write(b"stat\n") 
    time.sleep(1)
    tn.write(b"main\n") 
    time.sleep(1)
    tn.read_until(b"Firmware Version -- ")
    firmware_after_update = tn.read_very_eager().decode("ascii")[:9]
    tn.close()

    get_cdt()
    print(currentDateTime + " - Firmware Version (After Update): {}".format(firmware_after_update))
    print(currentDateTime + " - Firmware Version (After Update): {}".format(firmware_after_update), file = outputFile)

    time.sleep(5)

    return firmware_after_update

def firmware_ad():
    global firmware_after_downgrade

    tn = telnetlib.Telnet(x10_IP) 
    tn.read_until(b"login as: ") 
    tn.write(b"araknis\n") 
    tn.read_until(b"araknis's password: ") 
    tn.write(b"snapav704\n")
    time.sleep(1)
    tn.write(b"stat\n") 
    time.sleep(1)
    tn.write(b"main\n") 
    time.sleep(1)
    tn.read_until(b"Firmware Version -- ")
    firmware_after_downgrade = tn.read_very_eager().decode("ascii")[:9]
    tn.close()

    get_cdt()
    print(currentDateTime + " - Firmware Version (After Update): {}".format(firmware_after_downgrade))
    print(currentDateTime + " - Firmware Version (After Update): {}".format(firmware_after_downgrade), file = outputFile)

    time.sleep(5)

    return firmware_after_downgrade

def upgrade_firmware():
    if upgrade_choice == "1":
        chrome_driver.find_element_by_id("tbFirmwareUrl").send_keys(cloud_server_url_list[0])
    elif upgrade_choice == "2":
        chrome_driver.find_element_by_id("tbFirmwareUrl").send_keys(cloud_server_url_list[1])

    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.ID, "btnUpdateFirmware")))
    chrome_driver.find_element_by_id("btnUpdateFirmware").click()
    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.ID, "btnSendJson")))
    chrome_driver.find_element_by_id("btnSendJson").click()

    get_cdt()

    if upgrade_choice == "1":
        print(currentDateTime  + " - Update from {} to {} started.".format(firmware_before_update, version_list[0]))
        print(currentDateTime  + " - Update from {} to {} started.".format(firmware_before_update, version_list[0]), file = outputFile)
    if upgrade_choice == "2":
        print(currentDateTime  + " - Update from {} to {} started.".format(firmware_before_update, version_list[1]))
        print(currentDateTime  + " - Update from {} to {} started.".format(firmware_before_update, version_list[1]), file = outputFile)

    time.sleep(600)

    get_cdt()
    print(currentDateTime + " - Update Complete")
    print(currentDateTime + " - Update Complete", file = outputFile)

def downgrade_firmware():
    if upgrade_choice == "1":
        chrome_driver.find_element_by_id("tbFirmwareUrl").send_keys(cloud_server_url_list[int(downgrade_choice) - 1])
    elif upgrade_choice == "2":
        chrome_driver.find_element_by_id("tbFirmwareUrl").send_keys(cloud_server_url_list[int(downgrade_choice) - 1])

    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.ID, "btnUpdateFirmware")))
    chrome_driver.find_element_by_id("btnUpdateFirmware").click()
    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.ID, "btnSendJson")))
    chrome_driver.find_element_by_id("btnSendJson").click()

    get_cdt()

    if downgrade_choice == "1":
        print(currentDateTime  + " - Update from {} to {} started.".format(firmware_after_update, version_list[0]))
        print(currentDateTime  + " - Update from {} to {} started.".format(firmware_after_update, version_list[0]), file = outputFile)
    elif downgrade_choice == "2":
        print(currentDateTime  + " - Update from {} to {} started.".format(firmware_after_update, version_list[1]))
        print(currentDateTime  + " - Update from {} to {} started.".format(firmware_after_update, version_list[1]), file = outputFile)

    time.sleep(600)

    get_cdt()
    print(currentDateTime + " - Update Complete")
    print(currentDateTime + " - Update Complete", file = outputFile)

if user_start == "Y" or user_start == "y":
    outputFile = open(output_filepath, "a+")
    get_cdt()
    print(currentDateTime + " - API Test Started")
    chrome_driver = webdriver.Chrome(executable_path = "/Users/Amitabh.Mishra/Documents/AN-810/chromedriver.exe")
    webservice_page()
    outputFile.close()
    for cycles in range(0, int(user_cycles)):
        outputFile = open(output_filepath, "a+")

        firmware_test_page()
        get_online_offline_status()

        while device_status == "Device is offline":
            print("Device is offline.")
            retry_webservice()

            if device_status == "Device is online":
                break

        time.sleep(5)

        if device_status == "Device is online":
            firmware_bu()
            upgrade_firmware()
            upgrade_counter += 1
            firmware_au()

            get_cdt()

            if upgrade_choice == "1":
                if firmware_after_update == version_list[0]:
                    print(currentDateTime + " - Update from {} to {} is successful.\n".format(firmware_before_update, firmware_after_update))
                    print(currentDateTime + " - Update from {} to {} is successful.\n".format(firmware_before_update, firmware_after_update), file = outputFile)
                    update_successful_counter += 1
                else:
                    print(currentDateTime + " - Update from {} to {} is not successful.\n".format(firmware_before_update, firmware_after_update))
                    print(currentDateTime + " - Update from {} to {} is not successful.\n".format(firmware_before_update, firmware_after_update), file = outputFile)
                    update_failed_counter += 1
            elif upgrade_choice == "2":
                if firmware_after_update == version_list[1]:
                    print(currentDateTime + " - Update from {} to {} is successful.\n".format(firmware_before_update, firmware_after_update))
                    print(currentDateTime + " - Update from {} to {} is successful.\n".format(firmware_before_update, firmware_after_update), file = outputFile)
                    update_successful_counter += 1
                else:
                    print(currentDateTime + " - Update from {} to {} is not successful.\n".format(firmware_before_update, firmware_after_update))
                    print(currentDateTime + " - Update from {} to {} is not successful.\n".format(firmware_before_update, firmware_after_update), file = outputFile)
                    update_failed_counter += 1

        # chrome_driver.switch_to.window(chrome_driver.window_handles[0])
        # webservice_page()

        chrome_driver.close()
        chrome_driver.switch_to.window(chrome_driver.window_handles[0])
        firmware_test_page()
        get_online_offline_status()

        while device_status == "Device is offline":
            print("Device is offline.")
            retry_webservice()

            if device_status == "Device is online":
                break

        time.sleep(5)

        if device_status == "Device is online":
            downgrade_firmware()
            downgrade_counter += 1
            firmware_ad()

            get_cdt()

            if downgrade_choice == "1":
                if firmware_after_downgrade == version_list[0]:
                    print(currentDateTime + " - Update from {} to {} is successful.\n".format(firmware_after_update, firmware_after_downgrade))
                    print(currentDateTime + " - Update from {} to {} is successful.\n".format(firmware_after_update, firmware_after_downgrade), file = outputFile)
                    update_successful_counter += 1
            elif downgrade_choice == "2":
                if firmware_after_update == version_list[1]:
                    print(currentDateTime + " - Update from {} to {} is not successful.\n".format(firmware_after_update, firmware_after_downgrade))
                    print(currentDateTime + " - Update from {} to {} is not successful.\n".format(firmware_after_update, firmware_after_downgrade), file = outputFile)
                    update_failed_counter += 1

        cycle_counter += 1

        print("Cycle {} of {}.\n".format(cycle_counter, user_cycles))
        print("Upgrades: {}".format(upgrade_counter))
        print("Downgrades: {}".format(downgrade_counter))
        print("Successful Updates: {}".format(update_successful_counter))
        print("Failed Updates: {}".format(update_failed_counter))

        print("Cycle {} of {}.\n".format(cycle_counter, user_cycles), file = outputFile)
        print("Upgrades: {}".format(upgrade_counter), file = outputFile)
        print("Downgrades: {}".format(downgrade_counter), file = outputFile)
        print("Successful Updates: {}".format(update_successful_counter), file = outputFile)
        print("Failed Updates: {}".format(update_failed_counter), file = outputFile)

        chrome_driver.close()
        chrome_driver.switch_to.window(chrome_driver.window_handles[0])
        outputFile.close()
    
chrome_driver.close()

outputFile = open(output_filepath, "a+")
print("*** TEST SUMMARY ***\n")

print("Total Upgrades: {}/{}".format(upgrade_counter, cycle_counter))
print("Total Downgrades: {}/{}".format(downgrade_counter, cycle_counter))
print("Sucessful Updates: {}/{}".format(update_successful_counter, cycle_counter))
print("Failed Updates: {}/{}".format(update_failed_counter, cycle_counter))

print("*** TEST SUMMARY ***\n", file = outputFile)

print("Total Upgrades: {}/{}".format(upgrade_counter, cycle_counter), file = outputFile)
print("Total Downgrades: {}/{}".format(downgrade_counter, cycle_counter), file = outputFile)
print("Sucessful Updates: {}/{}".format(update_successful_counter, cycle_counter), file = outputFile)
print("Failed Updates: {}/{}".format(update_failed_counter, cycle_counter), file = outputFile)

outputFile.close()