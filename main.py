import os
import re
import json
import time
import shutil
import subprocess
import datetime as dt

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

CHROME_DRIVER = os.environ.get("CHROMEDRIVER")
Download_path = r"C:\Users\dalla\.wdm\drivers\chromedriver\win32"
SPEEDTEST_SITE = r"https://www.speedtest.net/"
TWITTER_SITE = r"https://twitter.com/"
subprocess.Popen(r"chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\WebDriver\bin\localhost", shell=True, stderr=False)

try:
    service = Service(executable_path=CHROME_DRIVER)
except Exception as r:
    print(r)
    CHROM_VERSION = ChromeDriverManager().driver.get_version()
    service = Service(executable_path=ChromeDriverManager().install())
    shutil.move(os.path.join(Download_path, CHROM_VERSION, "chromedriver.exe"), r"C:\WebDriver\bin")

chrome_option = Options()
chrome_option.add_experimental_option("debuggerAddress", "localhost:9222")
driver = webdriver.Chrome(options=chrome_option)
driver.delete_all_cookies()


def open_internet_speed():
    wait = WebDriverWait(driver, 15)
    driver.get(SPEEDTEST_SITE)
    start_btn = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "start-text")))
    start_btn.click()


def get_download_upload():
    wait = WebDriverWait(driver, 1000)
    url_is_change = wait.until(ec.url_matches(re.compile(r'(https://www.speedtest.net/result/\d*)')))
    if url_is_change:

        ping_speed = driver.find_element(By.CSS_SELECTOR, '.ping-speed').text
        download_speed = driver.find_element(By.CSS_SELECTOR, '.download-speed').text
        upload_spead = driver.find_element(By.CSS_SELECTOR, '.upload-speed').text
        wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "js-data-sponsor")))
        internet_provider = driver.find_element(By.CLASS_NAME, "js-data-sponsor").text
        internet_provider_short_name = driver.find_element(By.CSS_SELECTOR, ".js-data-isp").text
        speeds_types = ["internet_provider", "Ping", "Download", "Upload"]
        speeds = [internet_provider, ping_speed, download_speed, upload_spead]
        unites = [unite.text for unite in driver.find_elements(By.CLASS_NAME, "result-data-unit")]
        unites.insert(0, "")
        speeds_data = list(zip(speeds_types, speeds, unites))
        log_time = dt.datetime.now().strftime("D:%d/%m/%Y-T:%H:%M")
        speed_report = {log_time: {}}
        for i in speeds_data:
            speed_report[log_time].update({i[0]: "".join([str(i) for i in i[1:]])})
        # You can remove this part if you don't want to track your speed log
        if os.path.isfile(f"internets_speeds_logs/{internet_provider_short_name}.json"):
            with open(f"internets_speeds_logs/{internet_provider_short_name}.json", "r") as file:
                data_file = json.load(file)
                data_file.update(speed_report)
            with open(f"internets_speeds_logs/{internet_provider_short_name}.json", "w") as file:
                json.dump(data_file, file, indent=4)
        else:
            with open(f"internets_speeds_logs/{internet_provider_short_name}.json", "w") as file:
                json.dump(speed_report, file, indent=4)

        return speed_report


def tweet_speed(report):
    driver.execute_script("window.open('https://twitter.com/?lang=ar','new window')")
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[1])
    driver.implicitly_wait(10)
    select_text_box = driver.find_element(By.XPATH,
                                          '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/label/div[1]/div/div/div/div/div[2]/div/div/div/div')
    driver.implicitly_wait(10)
    select_text_box.clear()
    driver.implicitly_wait(10)
    select_text_box.click()
    driver.implicitly_wait(10)
    report_datetime = list(report.keys())[0]
    report_data = list(report.values())[0]
    internet_provider = report_data['internet_provider']
    ping = report_data['Ping']
    download = report_data['Download']
    upload = report_data["Upload"]
    select_text_box.send_keys(
        f" Hello on {report_datetime}, I checked my internet speed with speedtest.com and this was"
        f"the result as I'm using {internet_provider} internet provider, the ping speed {ping}"
        f",the download speed {download}, the upload speed {upload}. ")
    driver.implicitly_wait(10)
    tweet = driver.find_element(By.XPATH,
                                '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/span/span')
    driver.implicitly_wait(10)
    tweet.click()


def main():
    open_internet_speed()
    speed_report = get_download_upload()
    tweet_speed(speed_report)


if __name__ == '__main__':
    main()
