from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from multiprocessing import Process
import sys
import time

desired_courses = [819, 1836 ,818, 1978, 834, 835, 1930]


def main():
    processes = []
    for course in desired_courses:
        p = Process(target=reserve_course, args=(course,))
        p.start()

    for p in processes:
        p.join()



def reserve_course(course_id):
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    try:

        driver.get('https://www.usi-wien.at/anmeldung/')

        uni_dropdown = Select(driver.find_element_by_id('idpSelectSelector'))
        uni_dropdown.select_by_visible_text('Universität Wien')
        driver.find_element_by_id('idpSelectListButton').click()

        # auth:
        username_field = driver.find_element_by_id('userid')
        username_field.send_keys(username)

        password_field = driver.find_element_by_id('password')
        password_field.send_keys(password)

        driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div/div[2]/form/div[3]/div/button').click()

        while True:
            search_box = driver.find_element_by_id('searchPattern')
            search_box.clear()
            search_box.send_keys(course_id)
            search_box.submit()

            try:
                reservieren_link = driver.find_element_by_link_text('Reservieren')
                reservieren_link.click()
            except Exception as e:
                print('Link mit \'Reservieren\' nicht gefunden', file=sys.stderr, flush=True)
                if user_input_continue() is False:
                    break

    finally:
        driver.quit()



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


if __name__ == '__main__':
    main()
