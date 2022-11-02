import configparser
import sys
import os
from datetime import datetime
import logging
import time
import pause
from collections import OrderedDict
import getpass
from wakepy import keepawake
from playsound import playsound
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


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s ', stream=sys.stdout)
logging.getLogger('playsound').setLevel(logging.WARNING)
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
    for cred_field in ['username', 'passwort']:
        if not kwargs[cred_field]:
            if cred_field == 'passwort':
                kwargs[cred_field] = getpass.getpass(f"{cred_field}: ") # hide password input
            else:
                kwargs[cred_field] = input(f'{cred_field}: ').strip() # no need to hide other input
            assert kwargs[cred_field], f"{cred_field} nicht angegeben!"

    return kwargs

def pause_until_start(start_time: datetime, prevent_screenlock: bool):

    if start_time > datetime.now():
        logging.info(f"Pausiert bis {start_time}")

        if prevent_screenlock:
            logging.info("Standby des Betriebssystems wird verhindert.")
            with keepawake(keep_screen_awake=True):
                pause.until(start_time)

        else:
            pause.until(start_time)


class UsiDriver:

    _implicit_wait = 7

    def __init__(self, browser:str):

        os.environ['WDM_LOCAL'] = '1' # save drivers in locally in project directory instead of ~/.wdm
        if browser == 'firefox':
            self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        elif browser == 'chrome':
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        elif browser == 'edge':
            self.driver =webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
        else:
            raise RuntimeError("Invalid browser")

        self.driver.implicitly_wait(self._implicit_wait)


    def login(self, username, password, institution):

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

        elif institution == 'OpenIdP (alle Anderen)':
            self.driver.find_element(By.ID, 'username').send_keys(username)
            self.driver.find_element(By.ID, 'password').send_keys(password)
            self.driver.find_element(By.ID, 'regularsubmit').click()

        # TODO add elif, support more institutions

        else:
            raise RuntimeError(f'Institution {institution} nicht unterstützt.')

        try:
            self.driver.find_element(By.ID, 'searchPattern')
        except WebDriverException as e:
            logging.error(f"Unerwartetes Verhalten nach Login. Stimmen die Login-Daten?")
            raise RuntimeError("Searchbox with id searchPattern could not be found after login.")


    def reserve_course(self, course_id:str, jahresbetrieb:bool, wait_for_unlock:bool=False):

        while True:
            try:
                search_box = self.driver.find_element(By.ID, 'searchPattern')
            except NoSuchElementException or StaleElementReferenceException:
                self.driver.implicitly_wait(self._implicit_wait)
                self.driver.get('https://www.usi-wien.at/anmeldung/?lang=de')
                search_box = self.driver.find_element(By.ID, 'searchPattern')

            self.driver.implicitly_wait(1)
            search_box.clear()
            search_box.send_keys(course_id)
            search_box.submit()
            time.sleep(1)

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
                    logging.warning(f"Link für Jahresbetrieb wurde bei Kurs {course_id} nicht gefunden. Link für Semesterbetrieb wird als Backup gesucht.")


            try:
                reservieren_link = course_table.find_element(By.LINK_TEXT, 'Reservieren')
                reservieren_link.click()
                logging.info(f'Kurs {course_id} im Semesterbetrieb reserviert.')
                return True

            except NoSuchElementException:
                if wait_for_unlock:
                    time.sleep(2)  # prevent too many queries and potentially triggering Anti-DOS measures
                    continue

                logging.warning(f'Kein \'Reservieren\' Link für Kurs {course_id} gefunden!')
                return False


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

    logging.info(f'{n_total} Kurse werden ab {start_time} in folgender Reihenfolge reserviert: {[k for k,_ in courses_is_year.items()]}')
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
                logging.error(f"Webdriver Exception ({e}) bei Kurs {course}. Exisitiert der Kurs?")

            time.sleep(.5)

        logging.info(f'{n_successes}/{n_total} Kursen wurden erfolgreich reserviert. Der Bezahlvorgang muss nun manuell im Browser abgeschlossen werden!!!')
        if n_successes != 0:
            pay_link = usi_driver.driver.find_element(By.LINK_TEXT, 'bezahlen')
            pay_link.click()

    except Exception as e:
        logging.exception("Uncaught exception")
        raise e

    finally:
        if kwargs['alarm']:
            for _ in range(2): # alarm is played twice
                wav_path = os.path.join(project_directory, "sounds/alarm.wav")
                playsound(wav_path)

        answer = str()
        while answer != 'q':
            answer = input("Tippe \'q\' und enter, NACHDEM der Kaufvorgang abschlossen ist um das Skript zu beenden. Schließe dieses Fenseter NICHT!")
            answer = answer.strip()

        usi_driver.driver.quit()


if __name__ == '__main__':
    main()
