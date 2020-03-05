import datetime
import time
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from pytz import timezone
from dateutil import parser


def mmotop_time():
    return datetime.datetime.now(timezone("Europe/Vilnius"))


def can_voted_time(mmotop_timer):
    delta = datetime.timedelta(hours=mmotop_timer.hour, minutes=mmotop_timer.minute,
                               seconds=mmotop_timer.second)
    now = datetime.datetime.now()
    can_time = now + delta

    def helper():
        return datetime.datetime.now() >= can_time
    return helper()


class WrongWorldError(Exception):
    pass


class Browser(webdriver.Chrome):

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
                 " (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"

    def __init__(self):
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument(f'--user-agent={Browser.USER_AGENT}')
        webdriver.Chrome.__init__(self, options=options)

    def login(self, vk_login, vk_password):
        vote_button_xpath = "//a[@class='btn btn-danger icon-thumbs-up']"
        self._waiting(vote_button_xpath, delay=30)
        self.find_element_by_xpath(vote_button_xpath).click()
        vk_login_button_xpath = "//a[@href='/users/auth/vkontakte']"
        time.sleep(2)
        self._waiting(xpath=vk_login_button_xpath, type="element_to_be_clickable")
        self.find_element_by_xpath(vk_login_button_xpath).click()
        self._waiting(xpath="//input[@name='email']")
        self.find_element_by_xpath("//input[@name='email']").send_keys(vk_login)
        self.find_element_by_xpath("//input[@name='pass']").send_keys(vk_password)
        self.find_element_by_xpath("//button[@id='install_allow']").click()

    def _do_slide(self):
        slider = self.find_element_by_xpath("//div[@class='Slider ui-draggable']")
        slider_width = slider.size["width"]
        field_width = self.find_element_by_xpath("//div[@class='bgSlider']").size["width"]
        offset = field_width - slider_width
        actions = ActionChains(self)
        actions.drag_and_drop_by_offset(slider, offset, 0).perform()

    def is_voted(self):
        try:
            self.find_element_by_xpath("//span[@class='countdown_row countdown_amount']")
            return True
        except NoSuchElementException:
            return False

    def vote_success(self):
        try:
            self._waiting(xpath="//div[@class='ui-pnotify-text' and contains(text(), 'Голос принят')]",
                          delay=10)
            return True
        except TimeoutException:
            return False

    def get_timer(self):
        self._waiting(xpath="//span[@class='countdown_row countdown_amount']")
        self._waiting(xpath="//span[@class='countdown_row countdown_amount']",
                      type="element_to_be_clickable")
        return self.find_element_by_xpath("//span[@class='countdown_row countdown_amount']").text

    def _waiting(self, xpath=None, id=None, elem_class=None, link_text=None,
                type="default", delay=None):
        delay = delay or 20

        if type == "default":
            if xpath:
                WebDriverWait(self, delay).until(
                    EC.presence_of_element_located((By.XPATH, xpath)))
            elif id:
                WebDriverWait(self, delay).until(
                    EC.presence_of_element_located((By.ID, id)))
            elif elem_class:
                WebDriverWait(self, delay).until(
                    EC.presence_of_element_located((By.CLASS_NAME, elem_class)))
            elif link_text:
                WebDriverWait(self, delay).until(
                    EC.presence_of_element_located((By.LINK_TEXT, link_text)))

        elif type == "element_to_be_clickable":
            if xpath:
                WebDriverWait(self, delay).until(
                    EC.element_to_be_clickable((By.XPATH, xpath)))
            elif id:
                WebDriverWait(self, delay).until(
                    EC.element_to_be_clickable((By.ID, id)))
            elif elem_class:
                WebDriverWait(self, delay).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, elem_class)))
            elif link_text:
                WebDriverWait(self, delay).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, link_text)))

    def _is_404(self):
        try:
            self.find_element_by_xpath("//div[@class='body error-404']")
            return True
        except NoSuchElementException:
            return False

    def choice_world(self, n):
        time.sleep(2)
        worlds = self.find_elements_by_xpath("//tr[@style='cursor: pointer;']")
        n = n-1
        try:
            worlds[n].click()
        except IndexError:
            raise WrongWorldError

    def input_name(self, name):
        self._waiting(xpath="//input[@type='text']")
        self.execute_script(f"$('#charname input').val('{name}');")

    def confirm_vote(self):
        self.find_element_by_xpath("//input[@id='check_vote_form']").click()

    def get_page_with_timer(self, url):
        self.get(url)
        self.find_element_by_xpath("//a[@class='btn btn-danger icon-thumbs-up']").click()
        return self.get_timer()

    def main(self, vk_login, vk_password, url, name, world_n, log):
        self.get(url)
        log("Перешли на сайт mmotop")
        self.login(vk_login, vk_password)
        log("Залогинились")
        if self.is_voted():
            timer = self.get_timer()
            log(f"Следующий голос через {timer}")
        else:
            self._do_slide()
            self.input_name(name)
            self.choice_world(world_n)
            self.confirm_vote()
            if self.vote_success():
                log("Проголосовали")
            else:
                log("Ошибка!")


def main(vk_login, vk_password, url, name, world_n, once, log):
    while True:
        try:
            browser = Browser()
            browser.main(vk_login=vk_login, vk_password=vk_password, url=url, name=name,
                         world_n=world_n, log=log)
            if once:
                log("Программа завершила работу")
                browser.quit()
                break

            elif not once:
                timer = parser.parse(browser.get_page_with_timer(url))
                is_can_vote = can_voted_time(timer)
                log("Ждем...")
                while not is_can_vote:
                    time.sleep(300)
        except WrongWorldError:
            log("Мир указан неверно!")
            browser.quit()
            return
