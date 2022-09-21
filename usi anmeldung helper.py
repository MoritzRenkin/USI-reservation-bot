from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import configparser
import sys
import time


def get_config_kwargs() -> dict:
    config = configparser.ConfigParser()
    config.read('conf.ini', encoding='UTF-8')

    kwargs = dict(config['main'])

    kwargs['kurse'] = kwargs['kurse'].split(',')
    assert len(kwargs['kurse']) != 0

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

    def __init__(self, browser:str):
        """
        :param browser: 'firefox' or 'chrome'.
            Geckodriver or Chromedriver need to be installed for the respective option to work
        """
        if browser == 'firefox':
            self.driver = webdriver.Firefox()
        elif browser == 'chrome':
            self.driver = webdriver.Chrome()
        else:
            raise RuntimeError("Invalid browser")

        self.driver.implicitly_wait(5)

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

    def reserve_course(self, course_id):

        while True:
            search_box = self.driver.find_element_by_id('searchPattern')
            search_box.clear()
            search_box.send_keys(course_id)
            search_box.submit()

            try:
                reservieren_link = self.driver.find_element_by_link_text('Reservieren')
                reservieren_link.click()
            except Exception as e:
                print('Link mit \'Reservieren\' nicht gefunden', file=sys.stderr, flush=True)
                if user_input_continue() is False:
                    break



def main():
    kwargs = get_config_kwargs()

    usi_driver = UsiDriver(browser=kwargs['browser'])

    try:
        usi_driver.login(username=kwargs['username'], password=kwargs['passwort'], institution=kwargs['institution'])

    finally:
        input("Press enter to exit and close the browser.")
        usi_driver.driver.quit()


if __name__ == '__main__':
    main()