from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import selenium
import configparser
import sys
import pause
from datetime import datetime
import logging
import time


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', stream=sys.stdout)


def get_config_kwargs() -> dict:
    config = configparser.ConfigParser()
    config.read('conf.ini', encoding='UTF-8')

    kwargs = dict(config['main'])

    kwargs['kurse'] = kwargs['kurse'].split(',')
    assert len(kwargs['kurse']) != 0

    start_str = kwargs['start']
    start_obj = datetime.strptime(start_str, '%d/%m/%Y %H:%M')
    kwargs['start'] = start_obj

    jahresbetrieb = str(kwargs['jahresbetrieb']).lower()
    assert jahresbetrieb == 'ja' or jahresbetrieb == 'nein'
    kwargs['jahresbetrieb'] = True if jahresbetrieb == 'ja' else False

    return kwargs


def user_input_continue(count=0):
    if count > 10:
        return False

    u_input = input('Continue? (\'y\'|\'n\') ')
    if u_input == 'y':
        return True
    elif u_input == 'n':
        return False
    else:
        return user_input_continue(count+1)


class UsiDriver:

    _implicit_wait = 5

    def __init__(self, browser:str):
        """
        :param browser: 'firefox' or 'chrome'.
            Geckodriver or Chromedriver need to be installed for the respective option to work
        """
        if browser == 'firefox':
            self.driver = selenium.webdriver.Firefox()
        elif browser == 'chrome':
            self.driver = selenium.webdriver.Chrome()
        else:
            raise RuntimeError("Invalid browser")

        self.driver.implicitly_wait(self._implicit_wait)

    def login(self, username, password, institution):
        self.driver.get('https://www.usi-wien.at/anmeldung/')

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

    def reserve_course(self, course_id, jahresbetrieb, wait_for_unlock=False):

        while True:
            if wait_for_unlock:
                time.sleep(1)  # prevent too many queries and potentially triggering Anti-DOS measures

            search_box = self.driver.find_element(By.ID, 'searchPattern')
            self.driver.implicitly_wait(1)
            search_box.clear()
            search_box.send_keys(course_id)
            search_box.submit()

            if jahresbetrieb:
                try:
                    jahresbetrieb_link = self.driver.find_element(By.LINK_TEXT, 'Reservieren Jahr')
                    jahresbetrieb_link.click()
                    logging.info(f'Kurs {course_id} im Jahresbetrieb reserviert.')
                    return True
                except NoSuchElementException:
                    logging.warning(f"Link für Jahresbetrieb wurde bei Kurs {course_id} nicht gefunden. Link für Semesterbetrieb wird als Backup gesucht.")


            try:
                reservieren_link = self.driver.find_element(By.LINK_TEXT, 'Reservieren')
                reservieren_link.click()
                logging.info(f'Kurs {course_id} im Semesterbetrieb reserviert.')
                return True

            except NoSuchElementException:
                if wait_for_unlock:
                    if 'Ausgebuct' not in self.driver.page_source:
                        continue
                    else:
                        logging.warning(f'Kurs {course_id} bereits ausgebucht!')

                logging.warning(f'Kein \'Reservieren\' Link für Kurs {course_id} gefunden!')
                return False




def main():
    kwargs = get_config_kwargs()
    courses: list[str] = kwargs['kurse']
    start_time = kwargs['start']

    if start_time > datetime.now():
        logging.info(f"Pausiert bis {start_time}")
        pause.until(start_time)

    usi_driver = UsiDriver(browser=kwargs['browser'])

    try:
        usi_driver.login(username=kwargs['username'], password=kwargs['passwort'], institution=kwargs['institution'])

        for i, course in enumerate(courses):
            wait_for_unlock = True if i==0 else False
            usi_driver.reserve_course(course, jahresbetrieb=kwargs['jahresbetrieb'], wait_for_unlock=wait_for_unlock)

    except Exception as e:
        logging.exception("Uncaught exception")
        raise e

    finally:
        input("Press enter to exit and close the browser.")
        usi_driver.driver.quit()


if __name__ == '__main__':
    main()