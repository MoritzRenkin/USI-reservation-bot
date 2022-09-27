import configparser
import sys
import os
from datetime import datetime
import logging
import time
import pause
from collections import OrderedDict
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


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', stream=sys.stdout)


def get_config_kwargs() -> dict:

    config = configparser.ConfigParser()
    config.read('conf.ini', encoding='UTF-8')

    kwargs = dict(config['main'])

    kwargs['kurse_semesterbetrieb'] = kwargs['kurse_semesterbetrieb'].split(',')
    while '' in kwargs['kurse_semesterbetrieb']: kwargs['kurse_semesterbetrieb'].remove('')

    kwargs['kurse_jahresbetrieb'] = kwargs['kurse_jahresbetrieb'].split(',')
    while '' in kwargs['kurse_jahresbetrieb']: kwargs['kurse_jahresbetrieb'].remove('')

    assert len(kwargs['kurse_semesterbetrieb']) + len(kwargs['kurse_jahresbetrieb']) != 0

    start_str = kwargs['start']
    start_obj = datetime.strptime(start_str, '%d/%m/%Y %H:%M')
    kwargs['start'] = start_obj

    kwargs['browser'] = str(kwargs['browser']).lower()

    return kwargs


class UsiDriver:

    _implicit_wait = 7

    def __init__(self, browser:str):

        os.environ['WDM_LOCAL'] = '1'
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

        if institution == 'Universität Wien':
            uni_dropdown = Select(self.driver.find_element(By.ID, ('idpSelectSelector')))
            uni_dropdown.select_by_visible_text('Universität Wien')
            self.driver.find_element(By.ID, 'idpSelectListButton').click()

            # auth:
            username_field = self.driver.find_element(By.ID, 'userid')
            username_field.send_keys(username)

            password_field = self.driver.find_element(By.ID, 'password')
            password_field.send_keys(password)

            self.driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div/div/div[2]/form/div[3]/div/button').click()

        else:
            raise RuntimeError(f'Institution {institution} not supported.')

    def reserve_course(self, course_id:str, jahresbetrieb:bool, wait_for_unlock:bool=False):

        while True:
            if wait_for_unlock:
                time.sleep(1)  # prevent too many queries and potentially triggering Anti-DOS measures

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
                    continue

                logging.warning(f'Kein \'Reservieren\' Link für Kurs {course_id} gefunden!')
                return False


def main():

    kwargs = get_config_kwargs()

    courses_is_year = OrderedDict()

    for course in kwargs['kurse_semesterbetrieb']:
        courses_is_year[course] = False

    for course in kwargs['kurse_jahresbetrieb']:
        courses_is_year[course] = True

    start_time = kwargs['start']
    n_successes = 0
    n_total = len(courses_is_year)

    logging.info(f'{n_total} Kurse werden ab {start_time} in folgender Reihenfolge reserviert: {[k for k,_ in courses_is_year.items()]}')

    if start_time > datetime.now():
        logging.info(f"Pausiert bis {start_time}")
        pause.until(start_time)

    logging.info("Webdriver wird gestartet...")
    usi_driver = UsiDriver(browser=kwargs['browser'])

    try:
        usi_driver.login(username=kwargs['username'], password=kwargs['passwort'], institution=kwargs['institution'])

        is_first_course = True
        for course, is_year in courses_is_year.items():
            course = str(course).strip()
            try:
                is_success = usi_driver.reserve_course(course, jahresbetrieb=is_year, wait_for_unlock=is_first_course)
                if is_success:
                    n_successes += 1
                is_first_course = False

            except WebDriverException:
                logging.error(f"Webdriver Exception für Kurs {course}. Existiert der Kurs?")

            time.sleep(.5)


        logging.info(f'{n_successes}/{n_total} Kursen wurden erfolgreich reserviert. Der Bezahlvorgang muss nun manuell im Browser abgeschlossen werden!!!')
        if n_successes != 0:
            usi_driver.driver.find_element(By.LINK_TEXT, 'bezahlen').click()

    except Exception as e:
        logging.exception("Uncaught exception")
        raise e

    finally:
        answer = str()
        while answer != 'q':
            answer = input("Tippe \'q\' und enter, NACHDEM der Kaufvorgang abschlossen ist um das Skript zu beenden. ").strip()

        usi_driver.driver.quit()


if __name__ == '__main__':
    main()