from browserActions import BrowserCore
from selenium.common.exceptions import NoSuchElementException
import time

XPATH_POPUP_LOGIN_BUTTON = "//button[@id='install_allow']"
XPATH_POPUP_LOGIN_FORM = "//input[@name='email']"
XPATH_POPUP_PASSWORD_FORM = "//input[@name='pass']"

ID_DIRECT_LOGIN_LOGIN_FORM = "index_email"
ID_DIRECT_LOGIN_PASSWORD_FORM = "index_pass"
ID_DIRECT_LOGIN_BUTTON = "index_login_button"

XPATH_ADD_FRIEND_BUTTON = "//button[@class='flat_button button_wide']"

XPATH_LIKE_BUTTON = "//div[@class='like_button_icon']"

CSS_LIKED = ".like_btn.like.active"
XPATH_LIKED = "//a[@class='like_btn like _like active']"

XPATH_GROUP_MEMBERSHIP = "//span/text()[contains(.,'Вы участник')]"
XPATH_JOIN_GROUP_BUTTON = "//*[@id='join_button']"
XPATH_SUBSCRIBE_BUTTON = "//*[@id='public_subscribe']"
XPATH_SHARE_BUTTON = "//a[@title='Поделиться']"
ID_SHARE_WALL_RADIOBUTTON = "like_share_my"
ID_SHARE_SEND = "like_share_send"


class VkActions(BrowserCore):

    def popup_login(self, login, password):
        try:
            self.waiting(xpath=XPATH_POPUP_LOGIN_FORM, delay=5)
            self.fill_form(login, xpath=XPATH_POPUP_LOGIN_FORM)
            self.fill_form(password, xpath=XPATH_POPUP_PASSWORD_FORM)
            self.find_element(xpath=XPATH_POPUP_LOGIN_BUTTON).click()
        except AttributeError:
            pass

    def login(self, login, password):
        self.fill_form(login, form_id=ID_DIRECT_LOGIN_LOGIN_FORM)
        self.fill_form(password, form_id=ID_DIRECT_LOGIN_PASSWORD_FORM)
        self.find_element(id=ID_DIRECT_LOGIN_BUTTON).click()
        self.waiting(xpath="//span[@class='left_label inl_bl']", type="element_to_be_clickable")

    def add_friend(self):
        self.find_element(xpath=XPATH_ADD_FRIEND_BUTTON).click()

    def add_like(self, element=None):
        if element:
            element.find_element_by_xpath(self, xpath=XPATH_LIKE_BUTTON).click()
        elif not element:
            self.scroll_down()
            self.find_element(xpath=XPATH_LIKE_BUTTON).click()

    def check_liked(self, elem=None):
        try:
            if elem:
                elem.find_element_by_css_selector(CSS_LIKED)
                return True
            else:
                self.find_element(xpath=XPATH_LIKED)
        except NoSuchElementException:
            return False

    def check_group_membership(self):
        try:
            self.find_element(xpath=XPATH_GROUP_MEMBERSHIP)
            return True
        except NoSuchElementException:
            return False

    def join_group(self):
        try:
            self.find_element(xpath=XPATH_JOIN_GROUP_BUTTON).click()
        except NoSuchElementException:
            self.find_element(xpath=XPATH_SUBSCRIBE_BUTTON).click()

    def share(self):
        self.find_element(xpath=XPATH_SHARE_BUTTON).click()
        self.waiting(id=ID_SHARE_WALL_RADIOBUTTON)
        self.find_element(id=ID_SHARE_WALL_RADIOBUTTON).click()
        time.sleep(1)
        self.find_element(id=ID_SHARE_SEND).click()
        time.sleep(1)

    def not_found(self):
        try:
            self.find_element(xpath="//*[contains(text(),'Запись не найдена')]")
            return True
        except NoSuchElementException:
            return False
