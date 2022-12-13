import configparser
import sys
import os
from datetime import datetime
import logging
from time import sleep
from collections import OrderedDict
from getpass import getpass

import pause
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from exceptions import UsiLoginException

project_directory = os.path.dirname(__file__)

console_header = r"""
░█░█░█▀▀░▀█▀░░░░░█▀▄░█▀▀░█▀▀░█▀▀░█▀▄░█░█░█▀█░▀█▀░▀█▀░█▀█░█▀█░░░░░█▀▄░█▀█░▀█▀
░█░█░▀▀█░░█░░▄▄▄░█▀▄░█▀▀░▀▀█░█▀▀░█▀▄░▀▄▀░█▀█░░█░░░█░░█░█░█░█░▄▄▄░█▀▄░█░█░░█░
░▀▀▀░▀▀▀░▀▀▀░░░░░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░░▀░░▀░▀░░▀░░▀▀▀░▀▀▀░▀░▀░░░░░▀▀░░▀▀▀░░▀░
"""


def get_config_kwargs() -> dict:

    config = configparser.ConfigParser()
    config.read(os.path.join(project_directory, 'config.ini'), encoding='UTF-8')

    kwargs = dict(config['main'])
    kwargs = { key:str(value).strip() for key, value in kwargs.items() }

    kwargs['kurse_semesterbetrieb'] = kwargs['kurse_semesterbetrieb'].split(',')
    while '' in kwargs['kurse_semesterbetrieb']: kwargs['kurse_semesterbetrieb'].remove('')

    kwargs['kurse_jahresbetrieb'] = kwargs['kurse_jahresbetrieb'].split(',')
    while '' in kwargs['kurse_jahresbetrieb']: kwargs['kurse_jahresbetrieb'].remove('')

    assert len(kwargs['kurse_semesterbetrieb']) + len(kwargs['kurse_jahresbetrieb']) != 0, "Keine Kurse angegeben!"

    start_format = '%d.%m.%Y %H:%M'
    start_str = kwargs['start']
    start_obj = datetime.strptime(start_str, start_format)
    kwargs['start'] = start_obj

    kwargs['browser'] = str(kwargs['browser']).lower()

    energiesparen_verhindern = str(kwargs['os_standby_verhindern']).lower()
    kwargs['os_standby_verhindern'] = True if energiesparen_verhindern=="ja" or energiesparen_verhindern=="true" else False

    alarm = str(kwargs['alarm']).lower()
    kwargs['alarm'] = True if alarm=="ja" or alarm=="true" else False

    # getting username and password if left empty
    cred_fields = ['username', 'passwort']
    if not all(kwargs[cred_field] for cred_field in cred_fields):
        logging.info(f"Zugangsdaten für {kwargs['login_institution']} fehlen.")

        for cred_field in cred_fields:
            if not kwargs[cred_field]:
                if cred_field == 'passwort':
                    kwargs[cred_field] = getpass(f"{cred_field} (wird nicht angezeigt): ") # hide password input
                else:
                    kwargs[cred_field] = input(f'{cred_field}: ').strip() # no need to hide other input
                assert kwargs[cred_field], f"{cred_field} nicht angegeben!"

    return kwargs


def pause_until_start(start_time: datetime, prevent_screenlock: bool) -> None:

    if start_time > datetime.now():
        logging.info(f"Pausiert bis {start_time.strftime('%d.%m.%Y, %H:%M')}.")

        if prevent_screenlock:
            from wakepy import keepawake
            logging.info("Standby des Betriebssystems wird verhindert.")
            with keepawake(keep_screen_awake=True):
                pause.until(start_time)

        else:
            pause.until(start_time)

class UsiDriver:

    _implicit_wait_default = 10
    _implicit_wait_low = 2
    _implicit_wait_minimal = .2

    wdm_cache_validity = 5 # days
    def __init__(self, browser:str):

        os.environ['WDM_LOCAL'] = '1' # save drivers in locally in project directory instead of ~/.wdm
        if browser == 'firefox':
            firefox_service = FirefoxService(GeckoDriverManager(cache_valid_range=self.wdm_cache_validity).install())
            self.driver = webdriver.Firefox(service=firefox_service)
        elif browser == 'chrome':
            chrome_service = ChromeService(ChromeDriverManager(cache_valid_range=self.wdm_cache_validity).install())
            self.driver = webdriver.Chrome(service=chrome_service)
        elif browser == 'edge':
            edge_service = EdgeService(EdgeChromiumDriverManager(cache_valid_range=self.wdm_cache_validity).install())
            self.driver =webdriver.Edge(service=edge_service)
        else:
            raise RuntimeError("Invalid browser")

        self.driver.implicitly_wait(self._implicit_wait_default)


    def login(self, username: str, password: str, institution: str) -> None:

        self.driver.get('https://www.usi-wien.at/anmeldung/?lang=de')

        uni_dropdown = Select(self.driver.find_element(By.ID, ('idpSelectSelector')))
        uni_dropdown.select_by_visible_text(institution)
        self.driver.find_element(By.ID, 'idpSelectListButton').click()

        if institution == 'Universität Wien':
            self.driver.find_element(By.ID, 'userid').send_keys(username)
            self.driver.find_element(By.ID, 'password').send_keys(password)
            self.driver.find_element(By.CSS_SELECTOR, '.loginform > div:nth-child(4) > div:nth-child(1) > button:nth-child(1)').click()

        elif institution == 'Technische Universität Wien':
            self.driver.find_element(By.ID, 'username').send_keys(username)
            self.driver.find_element(By.ID, 'password').send_keys(password)
            self.driver.find_element(By.ID, 'samlloginbutton').click()

            sleep(1)
            if 'getconsent' in self.driver.current_url: # Zustimmung zur Weitergabe persönlicher Daten
                yes_button = self.driver.find_element(By.ID, 'yesbutton')
                yes_button.click()

        elif institution == 'OpenIdP (alle Anderen)':
            self.driver.find_element(By.ID, 'username').send_keys(username)
            self.driver.find_element(By.ID, 'password').send_keys(password)
            self.driver.find_element(By.ID, 'regularsubmit').click()

        # TODO add elif, support more institutions

        else:
            raise RuntimeError(f'Institution {institution} nicht unterstützt.')

        try:
            self.driver.find_element(By.ID, 'searchPattern')
            logging.info("Login erfolgreich.")
        except WebDriverException as e:
            logging.error(f"Unerwartetes Verhalten nach Login. Stimmen die Login-Daten?")
            raise RuntimeError("Searchbox with id searchPattern could not be found after login.")


    def reserve_course(self, course_id:str, jahresbetrieb:bool, wait_for_unlock:bool=False) -> bool:

        while True:
            try:
                search_box = self.driver.find_element(By.ID, 'searchPattern')
            except NoSuchElementException or StaleElementReferenceException:
                self.driver.implicitly_wait(self._implicit_wait_default)
                self.driver.get('https://www.usi-wien.at/anmeldung/?lang=de')
                search_box = self.driver.find_element(By.ID, 'searchPattern')

            self.driver.implicitly_wait(self._implicit_wait_low)
            search_box.clear()
            search_box.send_keys(course_id)
            search_box.submit()
            sleep(.5)

            course_table = self.driver.find_element(By.CLASS_NAME, "tablewithbottom")
            reservation_cell = course_table.find_element(By.CSS_SELECTOR,"tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(5)")

            if 'Ausgebucht' in reservation_cell.get_attribute('innerHTML').strip():
                logging.warning(f'Kurs {course_id} bereits ausgebucht!')
                return False

            if jahresbetrieb:
                try:
                    jahresbetrieb_link = course_table.find_element(By.LINK_TEXT, 'Reservieren Jahr')
                    jahresbetrieb_link.click()
                    logging.info(f'Kurs {course_id} im Jahresbetrieb reserviert.')
                    return True

                except NoSuchElementException:
                    if not wait_for_unlock: # TODO enable this log message for wait_for_unlock==True in a sensible way
                        logging.warning(f"Link für Jahresbetrieb wurde bei Kurs {course_id} nicht gefunden. Link für Semesterbetrieb wird als Backup gesucht.")
                    self.driver.implicitly_wait(self._implicit_wait_minimal) # page should have already loaded after implicit_wait causing Exception

            try:
                reservieren_link = course_table.find_element(By.LINK_TEXT, 'Reservieren')
                reservieren_link.click()
                logging.info(f'Kurs {course_id} im Semesterbetrieb reserviert.')
                return True

            except NoSuchElementException:
                if wait_for_unlock:
                    sleep(1)  # prevent too many queries and potentially triggering Anti-DOS measures
                    continue

                logging.warning(f'Kein \'Reservieren\' Link für Kurs {course_id} gefunden!')
                return False

            finally:
                self.driver.implicitly_wait(self._implicit_wait_low)

    def proceed_to_payment(self) -> None:

        pay_link = self.driver.find_element(By.LINK_TEXT, 'bezahlen')
        pay_link.click()

def main():
    print(console_header)

    kwargs = get_config_kwargs()

    courses_is_year = OrderedDict()

    for course in kwargs['kurse_semesterbetrieb']:
        courses_is_year[course] = False

    for course in kwargs['kurse_jahresbetrieb']:
        courses_is_year[course] = True

    n_successes = 0
    n_total = len(courses_is_year)
    start_time = kwargs['start']

    logging.info(f"{n_total} Kurse werden ab {start_time} in folgender Reihenfolge reserviert: {[k for k,_ in courses_is_year.items()]}")

    if start_time > datetime.now():
        usi_driver = UsiDriver(browser=kwargs['browser'])
        logging.info("Logindaten werden überprüft.")
        try:
            usi_driver.login(username=kwargs['username'], password=kwargs['passwort'], institution=kwargs['login_institution'])
        except UsiLoginException as e:
            logging.error("Die Logindaten scheinen nicht zu stimmen.")
            raise e

        usi_driver.driver.quit()
        pause_until_start(start_time=start_time, prevent_screenlock=kwargs['os_standby_verhindern'])

    logging.info("Webdriver wird gestartet...")
    usi_driver = UsiDriver(browser=kwargs['browser'])

    try:
        usi_driver.login(username=kwargs['username'], password=kwargs['passwort'], institution=kwargs['login_institution'])

        is_first_course = True
        for course, is_year in courses_is_year.items():
            course = str(course).strip()
            try:
                is_success = usi_driver.reserve_course(course, jahresbetrieb=is_year, wait_for_unlock=is_first_course)
                if is_success:
                    n_successes += 1
                is_first_course = False

            except WebDriverException as e:
                logging.error(f"Webdriver Exception ({e}) bei Kurs {course}. Existiert der Kurs?")

            sleep(.5)

        if n_successes != 0:
            usi_driver.proceed_to_payment()
            logging.info(f'{n_successes}/{n_total} Kursen wurden erfolgreich reserviert. Der Bezahlvorgang muss nun manuell im Browser abgeschlossen werden.')

    except Exception as e:
        logging.exception("Uncaught exception")
        raise e

    finally:
        if kwargs['alarm']:
            from playsound import playsound
            for _ in range(2): # alarm is played twice
                wav_path = os.path.join(project_directory, "sounds/alarm.wav")
                playsound(wav_path)

        answer = str()
        while answer != 'q':
            answer = input("Tippe \'q\' und enter, NACHDEM der Kaufvorgang abschlossen ist um das Skript zu beenden. Schließe dieses Fenseter NICHT! ")
            answer = answer.strip()

        usi_driver.driver.quit()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s ', stream=sys.stdout)
    logging.getLogger('playsound').setLevel(logging.WARNING)
    main()
