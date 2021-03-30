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
import urllib.request

# FIRMWARE FILES
firmware_files = [r"\an810i-v2.0.02.02.bin", r"\an810i-v2.0.02.03.bin"]
# firmware_files = [r"\an510i-v2.1.01.01.bin", r"\an810i-v2.0.02.03.bin"]

# COUNTERS
update_successful_counter = 0
update_failed_counter = 0
upgrade_counter = 0
downgrade_counter = 0
same_firmware_update_counter = 0
default_counter = 0
recovery_counter = 0
cycle_counter = 0

def extract_firmware_version():
    global version_number, version_list_1, version_list_2

    version_number = [files[9:-4] for files in firmware_files]
    # print(version_number)

    version_list_1 = version_number[0]
    version_list_2 = version_number[1]

    return version_number, version_list_1, version_list_2

def list_of_versions():
    extract_firmware_version()

    for i, files in enumerate(version_number, 1):
        print("{}. {}".format(i, files))


output_filename = input("Enter file name to save as: ")
an_810_IP = input("Enter IP address for AP: ")
an_810_username = input("Enter username for AP: ")
an_810_password = input("Enter password for AP: ")
switch_IP = input("Enter IP address for switch: ")
# switch_password = input("Enter password for switch: ")
list_of_versions()
update_version_choice = input("Enter version you would like to update to: ")
number_of_loops = input("Enter number of loops: ")
fault_insertion_time = input("Enter time (seconds) to start fault insertion: ")
user_start = input("Start test (Y/N): ")

# output_filepath = "/Users/Amitabh.Mishra/Documents/AN-810/Script Outputs/{}.txt".format(output_filename)
# chrome_driver = webdriver.Chrome(executable_path = "/Users/Amitabh.Mishra/Documents/AN-810/chromedriver.exe")

output_filepath = "/Users/amAmi/Documents/AN-810/Script Outputs/{}.txt".format(output_filename)
chrome_driver = webdriver.Chrome(executable_path = "/Users/amAmi/Documents/AN-810/chromedriver.exe")

# FUNCTIONS
def default_login():
    # default_counter = default_counter + 1
    WebDriverWait(chrome_driver, 30).until(ec.visibility_of_element_located((By.ID, "user")))
    chrome_driver.find_element_by_id("user").send_keys("araknis")
    chrome_driver.find_element_by_id("pass").send_keys("araknis")
    chrome_driver.find_element_by_css_selector(".btn-primary:nth-child(1)").click()

    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Logged In With Default Credentials\n")
    print(currentDateTime + " - Logged In With Default Credentials\n", file = outputFile)

    time.sleep(5)

    chrome_driver.find_element_by_id("newpass").click()
    chrome_driver.find_element_by_id("newpass").send_keys("snapav704")
    chrome_driver.find_element_by_id("confirmpass").click()
    chrome_driver.find_element_by_id("confirmpass").send_keys("snapav704")
    chrome_driver.find_element_by_css_selector(".btn:nth-child(2)").click()
def an_810_login():
    WebDriverWait(chrome_driver, 30).until(ec.visibility_of_element_located((By.ID, "user")))
    chrome_driver.find_element_by_id("user").send_keys("araknis")
    chrome_driver.find_element_by_id("pass").send_keys(an_810_password)
    chrome_driver.find_element_by_css_selector(".btn-primary:nth-child(1)").click()

    if chrome_driver.find_elements_by_id("login-model"):
        default_login()

        WebDriverWait(chrome_driver, 30).until(ec.visibility_of_element_located((By.ID, "user")))
        chrome_driver.find_element_by_id("user").send_keys("araknis")
        chrome_driver.find_element_by_id("pass").send_keys(an_810_password)
        chrome_driver.find_element_by_css_selector(".btn-primary:nth-child(1)").click()
 
    elif chrome_driver.find_elements_by_id("ctx-title"):
        currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
        print(currentDateTime + " - Successful Login With User Credentials\n")
        print(currentDateTime + " - Successful Login With User Credentials\n", file = outputFile)

    time.sleep(5)
def get_current_firmware_version():
    global current_firmware_version

    tn = telnetlib.Telnet(an_810_IP) 
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
    current_firmware_version = tn.read_very_eager().decode("ascii")[:9]
    tn.close()

    # WebDriverWait(chrome_driver, 30).until(ec.text_to_be_present_in_element((By.ID, "ctx-title"), "SYSTEM STATUS"))
    # chrome_driver.switch_to.frame(0)
    # current_firmware_version = chrome_driver.find_element_by_css_selector("#ap_SysInfo_inText3").text

    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Current Firmware Version: " + current_firmware_version + "\n")
    print(currentDateTime + " - Current Firmware Version: " + current_firmware_version + "\n", file = outputFile)
    time.sleep(5)

    return current_firmware_version
def get_firmware_version_after_update():
    global firmware_version_after_update

    tn = telnetlib.Telnet(an_810_IP) 
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
    firmware_version_after_update = tn.read_very_eager().decode("ascii")[:9]
    tn.close()

    # WebDriverWait(chrome_driver, 30).until(ec.text_to_be_present_in_element((By.ID, "ctx-title"), "SYSTEM STATUS"))
    # chrome_driver.switch_to.frame(0)
    # firmware_version_after_update = chrome_driver.find_element_by_css_selector("#ap_SysInfo_inText3").text
    
    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Firmware Version After Update: " + firmware_version_after_update + "\n")
    print(currentDateTime + " - Firmware Version After Update: " + firmware_version_after_update + "\n", file = outputFile)
    time.sleep(5)

    return firmware_version_after_update
def navigate_to_file_management_page():
    chrome_driver.get("http://{}/cgi-bin/luci/;stok=8922483091bb26a24f346f590bbbe3db/html/index#fun_2_2".format(an_810_IP))
    print("Successful navigation to file management page.\n")
    time.sleep(5)
def upgrade_firmware_file():
    WebDriverWait(chrome_driver, 30).until(ec.text_to_be_present_in_element((By.ID, "ctx-title"), "FILE MANAGEMENT"))
    chrome_driver.switch_to.frame(0)

    if update_version_choice == "1":
        chrome_driver.find_element_by_id("image").send_keys(os.getcwd() + "\Documents\AN-810\Firmware Files" + firmware_files[0])
        currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
        print(currentDateTime + " - Firmware version selected for upload: {}\n".format(version_list_1))
        print(currentDateTime + " - Firmware version selected for upload: {}\n".format(version_list_1), file = outputFile)
    elif update_version_choice == "2":
        chrome_driver.find_element_by_id("image").send_keys(os.getcwd() + "\Documents\AN-810\Firmware Files" + firmware_files[1])
        currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
        print(currentDateTime + " - Firmware version selected for upload: {}\n".format(version_list_2))
        print(currentDateTime + " - Firmware version selected for upload: {}\n".format(version_list_2), file = outputFile)

    time.sleep(5)
    chrome_driver.find_element_by_id("UploadButton").click()

    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.NAME, "Button")))
    chrome_driver.find_element_by_name("Button").send_keys(Keys.ENTER)

    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Upgrade started...\n")
    print(currentDateTime + " - Upgrade started...\n", file = outputFile)

    power_fault_insertion()
    time.sleep(360)

    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Upgrade finished...\n")
    print(currentDateTime + " - Upgrade finished...\n", file = outputFile)

    # chrome_driver.close()
    # chrome_driver.switch_to.frame(0)
    # chrome_driver.find_element(By.CSS_SELECTOR, "a > font").click()
    # time.sleep(10)
def downgrade_firmware_file():
    WebDriverWait(chrome_driver, 30).until(ec.text_to_be_present_in_element((By.ID, "ctx-title"), "FILE MANAGEMENT"))
    chrome_driver.switch_to.frame(0)

    if update_version_choice == "1":
        chrome_driver.find_element_by_id("image").send_keys(os.getcwd() + "\Documents\AN-810\Firmware Files" + firmware_files[1])
        currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
        print(currentDateTime + " - Firmware version selected for upload: {}\n".format(version_list_1))
        print(currentDateTime + " - Firmware version selected for upload: {}\n".format(version_list_1), file = outputFile)
    elif update_version_choice == "2":
        chrome_driver.find_element_by_id("image").send_keys(os.getcwd() + "\Documents\AN-810\Firmware Files" + firmware_files[0])
        currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
        print(currentDateTime + " - Firmware version selected for upload: {}\n".format(version_list_1))
        print(currentDateTime + " - Firmware version selected for upload: {}\n".format(version_list_1), file = outputFile)

    time.sleep(5)
    chrome_driver.find_element_by_id("UploadButton").click()
    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.NAME, "Button")))
    chrome_driver.find_element_by_name("Button").click()

    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Downgrade started...\n")
    print(currentDateTime + " - Downgrade started...\n", file = outputFile)

    power_fault_insertion()
    time.sleep(480-int(fault_insertion_time))

    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Downgrade finished...\n")
    print(currentDateTime + " - Downgrade finished...\n", file = outputFile)

    chrome_driver.switch_to.frame(0)
    chrome_driver.find_element(By.CSS_SELECTOR, "a > font").click()
    time.sleep(10)
def logout_ap():
    chrome_driver.get("http://{}/cgi-bin/luci/;stok=b8dd823851263905d2a1375cd9d5d009/html/index#fun_2_4".format(an_810_IP))
    time.sleep(2)
    chrome_driver.find_element_by_css_selector(".msgbox-button-space").click()
    time.sleep(2)
    chrome_driver.refresh()
    time.sleep(2)
def network_fault_insertion():
    time.sleep(int(fault_insertion_time))
    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Network port shutdown")
    print(currentDateTime + " - Network port shutdown", file = outputFile)

    tn = telnetlib.Telnet(switch_IP) 
    tn.read_until(b"Username: ") 
    tn.write(b"araknis\n") 
    tn.read_until(b"Password: ") 
    tn.write(b"snapav704\n") 
    time.sleep(1)
    tn.write(b"configure\n") 
    time.sleep(1)
    tn.write(b"interface GigabitEthernet 2\n") 
    time.sleep(1)
    tn.write(b"poe state disable\n")
    time.sleep(30)
    tn.write(b"poe state enable\n")
    time.sleep(1)
    tn.write(b"end\n")
    time.sleep(1)
    tn.write(b"exit\n")

    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Network port back up")
    print(currentDateTime + " - Network port back up", file = outputFile)
def power_fault_insertion():
    time.sleep(int(fault_insertion_time))
    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Network port shutdown")
    print(currentDateTime + " - Network port shutdown", file = outputFile)

    with telnetlib.Telnet(wattbox_IP, 23, 100) as session:
        session.write(b"wattbox\n")
        time.sleep(2)
        session.write(b"snapav704\n")
        time.sleep(2)
        session.write(b"!Outlet=12,RESET,30")
def enable_telnet():
    time.sleep(10)
    chrome_driver.get("http://{}/cgi-bin/luci/html/index#fun_1_3".format(an_810_IP))
    time.sleep(5)
    chrome_driver.switch_to.frame(0)
    chrome_driver.find_element_by_id("TelnetEnable").click()
    time.sleep(5)
    keyboard.press_and_release("up")
    keyboard.press_and_release("enter")
    time.sleep(5)
    chrome_driver.find_element(By.CSS_SELECTOR, "#id-cbi-page-actions2 > .button1:nth-child(1)").click()
    time.sleep(5)
    chrome_driver.switch_to.default_content()
    chrome_driver.find_element(By.ID, "fun_4").click()
    time.sleep(5)
    chrome_driver.switch_to.frame(0)
    time.sleep(5)
    chrome_driver.find_element(By.CSS_SELECTOR, ".button1:nth-child(6)").click()
    time.sleep(10)

    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Telnet Enabled")
    print(currentDateTime + " - Telnet Enabled", file = outputFile)
def get_local_ip():
    global ip_address

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    print("Current IP: {}".format(ip_address))
    
    return ip_address
def release_renew_ip():
    os.system("ipconfig/release")
    time.sleep(5)
    os.system("ipconfig/renew")
    time.sleep(10)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def connect(host="http://{}".format(an_810_IP)):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False
def recovery():
    if not connect():
        currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
        print(currentDateTime + " - Recovery Initiated")
        print(currentDateTime + " - Recovery Initiated", file = outputFile)

        subprocess.call('netsh interface ip set address "Ethernet" static 192.168.20.252 255.255.255.0 8.8.8.8')
        
        time.sleep(10)

        chrome_driver.execute_script("window.open('http://192.168.20.253/', 'new_window')")
        chrome_driver.switch_to.window(chrome_driver.window_handles[1])

        # chrome_driver = webdriver.Chrome(executable_path = "/Users/amAmi/Documents/AN-810/chromedriver.exe")
        # chrome_driver.get("http://192.168.20.253/")
        # WebDriverWait(chrome_driver, 30).until(ec.text_to_be_present_in_element((By.CSS_SELECTOR, "b > font"), "Device is Upgrading the Firmware"))

        WebDriverWait(chrome_driver, 120).until(ec.visibility_of_element_located((By.NAME, "userfile")))
        chrome_driver.find_element_by_name("userfile").send_keys(os.getcwd() + "\Documents\AN-810\Firmware Files" + firmware_files[0])
        chrome_driver.find_element_by_css_selector("tr:nth-child(2) input").click()
        
        # WebDriverWait(chrome_driver, 30).until(ec.text_to_be_present_in_element((By.CSS_SELECTOR, "center > font > b"), "Device is Upgrading the Firmware"))
        time.sleep(420)
        # chrome_driver.close()

        currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
        print(currentDateTime + " - Recovery Complete")
        print(currentDateTime + " - Recovery Complete", file = outputFile)
    
        subprocess.call('netsh interface ip set address "Ethernet" dhcp')
        
        time.sleep(10)
        # chrome_driver = webdriver.Chrome(executable_path = "/Users/amAmi/Documents/AN-810/chromedriver.exe")
        chrome_driver.switch_to.window(chrome_driver.window_handles[0])
        chrome_driver.get("http://{}/cgi-bin/luci".format(an_810_IP))
    else:
        chrome_driver.switch_to.frame(0)
        chrome_driver.find_element(By.CSS_SELECTOR, "a > font").click()
        time.sleep(10)
def reboot_ap():
    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print(currentDateTime + " - Rebooting AP")
    print(currentDateTime + " - Rebooting AP", file = outputFile)
    
    chrome_driver.switch_to.default_content()
    time.sleep(2)
    chrome_driver.execute_script("window.scrollTo(0,0)")
    time.sleep(2)
    chrome_driver.find_element(By.ID, "fun_2_3").click()
    time.sleep(2)
    chrome_driver.switch_to.frame(0)
    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.ID, "reboot")))
    chrome_driver.find_element(By.ID, "reboot").click()
    WebDriverWait(chrome_driver, 30).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "#msg-buton > input:nth-child(1)")))
    chrome_driver.find_element(By.CSS_SELECTOR, "#msg-buton > input:nth-child(1)").click()

    time.sleep(180)

if user_start == "Y" or user_start == "y":
    outputFile = open(output_filepath, "a+")

    currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
    print("***** AN-810 FIRMWARE UPGRADE / DOWNGRADE TEST *****\n", file = outputFile)
    print(currentDateTime + " Test Started\n", file = outputFile)
    print("*****************************************************\n", file = outputFile)

    for cycles in range(0, int(number_of_loops)):
        chrome_driver.get("http://{}/cgi-bin/luci".format(an_810_IP))

        an_810_login()
        get_current_firmware_version()
        navigate_to_file_management_page()
        upgrade_firmware_file()
        recovery()
        an_810_login()
        chrome_driver.refresh()
        enable_telnet()
        chrome_driver.refresh()
        reboot_ap()
        an_810_login()
        get_firmware_version_after_update()

        if firmware_version_after_update == current_firmware_version:
            currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
            print(currentDateTime + " - Firmware Successfully Upgraded From {} to {}.\n".format(current_firmware_version, firmware_version_after_update))
            print(currentDateTime + " - Firmware Successfully Upgraded From {} to {}.\n".format(current_firmware_version, firmware_version_after_update), file = outputFile)
            update_successful_counter = update_successful_counter + 1
        else:
            currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
            print(currentDateTime + " - Firmware Did Not Successfully Upgrade from {} to {}\n.".format(current_firmware_version, firmware_version_after_update))
            print(currentDateTime + " - Firmware Did Not Successfully Upgrade from {} to {}\n.".format(current_firmware_version, firmware_version_after_update), file = outputFile)
            update_failed_counter = update_failed_counter + 1
        
        upgrade_counter = upgrade_counter + 1

        navigate_to_file_management_page()
        downgrade_firmware_file()
        recovery()
        an_810_login()
        chrome_driver.refresh()
        enable_telnet()
        chrome_driver.refresh()
        reboot_ap()
        an_810_login()
        get_firmware_version_after_update()

        if firmware_version_after_update == version_list_1:
            currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
            print(currentDateTime + " - Firmware Successfully Downgraded From {} to {}.\n".format(version_list_2, version_list_1))
            print(currentDateTime + " - Firmware Successfully Downgraded From {} to {}.\n".format(version_list_2, version_list_1), file = outputFile)
            update_successful_counter = update_successful_counter + 1
        else:
            currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
            print(currentDateTime + " - Firmware Did Not Successfully Downgrade from {} to {}\n.".format(version_list_2, version_list_1))
            print(currentDateTime + " - Firmware Did Not Successfully Downgrade from {} to {}\n.".format(version_list_2, version_list_1), file = outputFile)
            update_failed_counter = update_failed_counter + 1

        downgrade_counter = downgrade_counter + 1

        logout_ap()
 
        cycle_counter = cycle_counter + 1

        print("Cycle {} of {}.\n".format(cycle_counter, number_of_loops))
        print("Updates: {}".format(upgrade_counter + downgrade_counter))
        print("Upgrades: {}".format(upgrade_counter))
        print("Downgrades: {}".format(downgrade_counter))
        print("Failed: {}".format(update_failed_counter))

        print("Cycle {} of {}.\n".format(cycle_counter, number_of_loops), file = outputFile)
        print("Updates: {}".format(upgrade_counter + downgrade_counter), file = outputFile)
        print("Upgrades: {}".format(upgrade_counter), file = outputFile)
        print("Downgrades: {}".format(downgrade_counter), file = outputFile)
        print("Failed: {}".format(update_failed_counter), file = outputFile)
        
        outputFile.close()

# SUMMARY
total_cycle_counter = upgrade_counter + downgrade_counter
outputFile = open(output_filepath, "a+")

currentDateTime = str(datetime.datetime.now().strftime("%m/%d/%Y | %H:%M:%S"))
print("***** END-OF-TEST SUMMARY *****\n", file = outputFile)
print(currentDateTime + " - Test Ended\n", file = outputFile)
print("*****************************************************\n", file = outputFile)

print("Successful Updates: {}/{}".format(update_successful_counter, total_cycle_counter))
print("Failed Updates: {}/{}".format(update_failed_counter, total_cycle_counter))
print("Total Upgrades: {}/{}".format(upgrade_counter, total_cycle_counter))
print("Total Downgrades: {}/{}".format(downgrade_counter, total_cycle_counter))
print("Defaults: {}/{}".format(default_counter, total_cycle_counter))
print("Recoveries: {}/{}".format(recovery_counter, total_cycle_counter))

outputFile.close()

chrome_driver.close()