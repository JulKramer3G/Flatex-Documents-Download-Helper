import argparse

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import logging

import time
import os
import requests
import configparser

download_folder =  os.path.dirname(os.path.realpath(__file__)) + '/downloads'

config_file = os.path.dirname(os.path.realpath(__file__)) + '/credentials.ini'
config = configparser.ConfigParser()
config.read(config_file)

login_id = config['CONFIGURATION']['kundennummer']
login_pass = config['CONFIGURATION']['passwort']
account_ending = config['CONFIGURATION']['kontonummer_letzte_drei_zeichen']

def wait_for_url_with(driver, keyword, timeout_sec):
    timeout = time.time() + timeout_sec   # seconds
    while (not keyword in driver.current_url):
        time.sleep(0.1)
        if time.time() > timeout:
            raise TimeoutError("Timeout waiting for page load with keyword{}".format(keyword))

def download(url: str, session_id: str, dest_folder: str):
    cookie = {'JSESSIONID': session_id}
    print(cookie)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True, cookies=cookie)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:
        raise RuntimeError("Download failed: status code {}\n{}".format(r.status_code, r.text))

def wait_for_element(driver, x_path, timeout_sec = 5):
    return WebDriverWait(driver, timeout_sec).until(EC.presence_of_element_located((By.XPATH, x_path)))

class FlatexBrowser:
    def __init__(self):
        self.logger = self.get_logger()
        self.driver = webdriver.Chrome()
        
        # input("Enter your login details and press Enter to continue once you are logged in...")
        # time.sleep(3)

        # Get all available cookies
        # print("All cookies:")
        # print(self.driver.get_cookies())
        # print("JSESSIONID cookie:")
        # print(self.driver.get_cookie("JSESSIONID"))

    def authenticate(self, id: str, password: str):
        self.driver.get('https://konto.flatex.de')
        field_id = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm_userId"]')))
        field_id.send_keys(id)
        field_pass = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm_pin"]')))
        field_pass.send_keys(password)
        btn_login =  WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm_loginButton"]')))
        ActionChains(self.driver).move_to_element(btn_login).perform()
        btn_login.click()
        wait_for_url_with(self.driver, 'banking-flatex', 5)
        time.sleep(5)

    def get_logger(self):
        log_format = (
            '[%(asctime)s] %(levelname)s\t%(name)s\t%(message)s')
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.StreamHandler()]
        )
        logger = logging.getLogger('flatex')
        return logger

    def select_docreadstate_all(self):
        btn_readstate = wait_for_element(self.driver, '//*[@id="documentArchiveListForm_readState"]/div[1]/div[1]/div')
        ActionChains(self.driver).move_to_element(btn_readstate).perform()
        btn_readstate.click()
        btn_readstate_all = wait_for_element(self.driver, '//*[@id="documentArchiveListForm_readState_item_0"]')
        ActionChains(self.driver).move_to_element(btn_readstate_all).perform()
        btn_readstate_all.click()
        
    def select_timespan_today(self):
        btn_timespan = wait_for_element(self.driver, '//*[@id="documentArchiveListForm_dateRangeComponent_retrievalPeriodSelection"]/div[1]/div[1]/div')
        ActionChains(self.driver).move_to_element(btn_timespan).perform()
        btn_timespan.click()
        btn_timespan_today = wait_for_element(self.driver, '//*[@id="documentArchiveListForm_dateRangeComponent_retrievalPeriodSelection_item_0"]')
        ActionChains(self.driver).move_to_element(btn_timespan_today).perform()
        btn_timespan_today.click()
        time.sleep(3)

    def select_account_with_ending(self, account_end: str):
        btn_account = wait_for_element(self.driver, '//*[@id="documentArchiveListForm_accountSelection_account"]/div[1]/div[1]/div')
        btn_account.click()
        accounts = self.driver.find_elements_by_xpath('//div[starts-with(@id, "documentArchiveListForm_accountSelection_account_item_")]')
        btn_acc = accounts[0]
        for acc in accounts:
            if(account_end in acc.get_attribute('innerHTML')):
                btn_acc = acc
        print('Verwendetes Konto: {}'.format(btn_acc.get_attribute('innerHTML')))
        ActionChains(self.driver).move_to_element(btn_acc).perform()
        btn_acc.click()
        time.sleep(3)

    def apply_filter(self):
        btn_apply = wait_for_element(self.driver, '//*[@id="documentArchiveListForm_applyFilterButton"]')
        ActionChains(self.driver).move_to_element(btn_apply).perform()
        btn_apply.click()
        time.sleep(5)
    
    def select_from_first_of_month(self, go_back_months: int = 0):
        # time selector: FROM
        btn_from_calendar = wait_for_element(self.driver, '//*[@id="documentArchiveListForm_dateRangeComponent_startDateSelection"]/div[1]')
        ActionChains(self.driver).move_to_element(btn_from_calendar).perform()
        btn_from_calendar.click()
        for i in range(go_back_months):
            btn_go_back_month = wait_for_element(self.driver, '//*[@id="documentArchiveListForm_dateRangeComponent_startDateInstance_prevMonthButton"]/div[2]')
            ActionChains(self.driver).move_to_element(btn_go_back_month).perform()
            btn_go_back_month.click()

        btn_first = wait_for_element(self.driver, '//*[@id="day1"]/span')
        ActionChains(self.driver).move_to_element(btn_first).perform()
        btn_first.click()
        time.sleep(1)

    def select_to_last_of_month(self, go_back_months: int = 0):
        # time selector: TO
        btn_to_calendar = wait_for_element(self.driver, '//*[@id="documentArchiveListForm_dateRangeComponent_endDateSelection"]/div[1]')
        ActionChains(self.driver).move_to_element(btn_to_calendar).perform()
        btn_to_calendar.click()
        for i in range(go_back_months):
            btn_go_back_month = wait_for_element(self.driver, '//*[@id="documentArchiveListForm_dateRangeComponent_endDateInstance_prevMonthButton"]/div[2]')
            ActionChains(self.driver).move_to_element(btn_go_back_month).perform()
            btn_go_back_month.click()
        days = self.driver.find_elements_by_xpath('//a[starts-with(@id, "day")]')
        last_day = 0
        highest_day_btn = 0
        ignore_first_elements = bool(len(days) > 31)
        for day in days:
            id = (day.get_property('id'))
            current_day = int(''.join(filter(str.isdigit, id)))
            # print('current id: {}'.format(id))
            if(last_day < current_day):
                last_day = current_day
                highest_day_btn = day
            else:
                if(ignore_first_elements is True):
                    ignore_first_elements = False
                    last_day = 0
        # print(last_day)
        ActionChains(self.driver).move_to_element(highest_day_btn).perform()
        highest_day_btn.click()
        time.sleep(1)

    def open_documents_page(self):
        self.driver.get('https://konto.flatex.de/banking-flatex/documentArchiveListFormAction.do')
        time.sleep(2)

    def download_all_docs_in_table(self, dest_folder: str):
        document_rows = self.driver.find_elements_by_xpath('//tr[starts-with(@id, "TID")]')
        self.logger.info(f"{len(document_rows)} Dokumente in der Liste gefunden. Starte Download ...")

        document_ids = []
        for document_row in document_rows:
            document_ids.append(document_row.get_property('id'))

        document_counter = 0
        for document_id in document_ids:
            document_counter += 1
            document_row = self.driver.find_element_by_xpath(f'//tr[@id="{document_id}"]')
            document_title = self.driver.find_element_by_xpath(f'//tr[@id="{document_id}"]//td[@class="C3 "]').text
            ActionChains(self.driver).move_to_element(document_row).perform()
            document_row.click()
            self.driver.switch_to.window(self.driver.window_handles[-1])
            wait_for_url_with(self.driver, 'downloadData', 5)
            # FILE ready
            download_url = self.driver.current_url
            session_id = self.driver.get_cookie("JSESSIONID")['value']
            download(url=download_url, session_id=session_id, dest_folder=dest_folder)
            # FILE downloaded
            self.logger.info(f"DOWNLOADED [{document_counter}/{len(document_ids)}]\t{document_title} - {self.driver.title}")
            self.driver.switch_to.window(self.driver.window_handles[0])

    def download_documents(self, months: int):
        # @param months the number of full months to download, this month included
        
        # login
        self.authenticate(id=login_id, password=login_pass)

        # go to documents page
        self.open_documents_page()
        
        # select the current account
        self.select_account_with_ending(account_end=account_ending)

        # Prepare the time to be at the current month, init state
        self.select_docreadstate_all()
        self.select_timespan_today()
        time.sleep(3)
        
        # Ready to download documents
        for i in range(months):
            # select current month
            self.select_from_first_of_month(go_back_months=int(i > 0))
            self.select_to_last_of_month(go_back_months=int(i > 0))
            self.apply_filter()
            time.sleep(3)
            self.download_all_docs_in_table(dest_folder=download_folder)
            time.sleep(3)

        print('FERTIG!, Dokumente liegen in:', download_folder)
        

if __name__ == '__main__':
    my_parser = argparse.ArgumentParser(prog='flatex_documents_download_helper',
                                        description='Das Skript erlaubt es mittels per Selenium gesteuerten '
                                                    'Chrome-Browser PDF-Dokumente aus dem Dokumentenarchiv von '
                                                    'Flatex herunterzuladen.')

    my_parser.add_argument('Months',
                           metavar='months',
                           type=int,
                           help='Die Anzahl der herunterzuladenden letzten Monate, der aktuelle Monat inbegriffen. Um also nur diesen Monat herunterzuladen, diesen Parameter auf 1 setzen. Für diesen und den letzten Monat den Parameter auf 2 setzen, und so weiter.')

    args = my_parser.parse_args()

    flatex_browser = FlatexBrowser()
    flatex_browser.download_documents(months=args.Months)