from webdriver_manager.chrome import ChromeDriverManager
from botcity.web.browsers.chrome import default_options
from botcity.web import WebBot, By
import pandas as pd
import config
import tools
import sys


def login(bot: WebBot) -> None:
    """
    This function will login to Orange HRM
    :param bot: Object on browser to the website
    :return: None
    """
    try:
        # Set the driver on browser
        bot.driver_path = ChromeDriverManager().install()

        # Select the folder to download the file
        bot.download_folder_path = config.resources_folder
        def_options = default_options(download_folder_path=config.resources_folder)
        bot.options = def_options

        # navigate do OrangeHRM portal
        bot.navigate_to(url='https://opensource-demo.orangehrmlive.com/web/index.php/auth/login')

        bot.maximize_window()

        # Set Username
        bot.find_element(selector='//input[@name="username"]', by=By.XPATH, ensure_visible=True, ensure_clickable=True).send_keys('Admin')

        # Set password
        bot.find_element(selector='//input[@name="password"]', by=By.XPATH, ensure_visible=True).send_keys('admin123')

        # Press button to login
        bot.find_element(selector='//button[@type="submit"]', by=By.XPATH, ensure_visible=True, ensure_clickable=True).click()

        # Find any hook to confirm login
        if not bot.find_element(selector='//span[text()="Recruitment"]', by=By.XPATH, ensure_visible=True):
            raise Exception('Failed to login to OrangeHRM')

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        raise ValueError(error, exc_traceback.tb_lineno, exc_traceback.tb_frame.f_code.co_name)


def access_add_candidate(bot: WebBot) -> None:
    """
    Access recruitment page on OrangeHRM
    :param bot:
    :return: None
    """
    try:
        # oprn to add candidadtes
        bot.navigate_to(url='https://opensource-demo.orangehrmlive.com/web/index.php/recruitment/addCandidate')

        # find any hook to confirm access recruitment menu
        if not bot.find_element(selector='//button[@type="submit"]', by=By.XPATH, ensure_visible=True):
            raise Exception('Failed to access recruitment page')

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        raise ValueError(error, exc_traceback.tb_lineno, exc_traceback.tb_frame.f_code.co_name)


def download_csv(bot: WebBot, link_download: str) -> str:
    """
    Download csv file from OrangeHRM
    :param bot: Object on browser to the website
    :param link_download: url to download file
    :return: File path to download file
    """
    try:

        # Download file csv
        bot.navigate_to(url=link_download)

        # Waiting for download csv file
        file_path = tools.waiting_download(bot, file_extension='.csv')

        return file_path

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        raise ValueError(error, exc_traceback.tb_lineno, exc_traceback.tb_frame.f_code.co_name)


def read_csv(file_path: str) -> pd.DataFrame:
    """
    Read csv file and return a list of data
    :param file_path:
    :return: list of data
    """
    try:

        df_employes = pd.read_csv(file_path)
        return df_employes

    except Exception as error:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        raise ValueError(error, exc_traceback.tb_lineno, exc_traceback.tb_frame.f_code.co_name)


def register_candidate(bot: WebBot, full_name: str, vacancy: str, email: str, contact_number: str, keywords: str):
    """
    Register candidate to OrangeHRM
    :param keywords: keywords to search
    :param contact_number: contact number to candidate
    :param email: e-mail to candidate
    :param vacancy: vacancy to candidate
    :param full_name: full name to candidate
    :param bot: object on browser to the website
    :return:
    """
    try:
        # Create a file resume to candidate
        with open(f'{config.resources_folder}/resume.txt', 'w') as arquivo:
            arquivo.write(f"{full_name}\n{vacancy}\n{email}\n{contact_number}\n{keywords}")

        name = full_name.split(' ')

        # Set first Name
        bot.find_element(selector='//input[@name="firstName"]', by=By.XPATH, ensure_visible=True).send_keys(name[0])
        # Set middlw Name
        bot.find_element(selector='//input[@name="middleName"]', by=By.XPATH, ensure_visible=True).send_keys(name[1])
        # Set last Name
        bot.find_element(selector='//input[@name="lastName"]', by=By.XPATH, ensure_visible=True).send_keys(name[2])
        # click for open dropbox
        bot.find_element("//div[div[label[text()='Vacancy']]]//div[text()='-- Select --']", By.XPATH).click()
        # Select vacancy on list
        bot.find_element(f"//div[@role='listbox']//*[contains(text(),'{vacancy}')]", By.XPATH).click()
        # set e-mail
        bot.find_element(selector="//div[div[label[text()='Email']]]//input", by=By.XPATH, ensure_visible=True).send_keys(email)
        # set contact number
        bot.find_element(selector="//div[div[label[text()='Contact Number']]]//input", by=By.XPATH, ensure_visible=True).send_keys(contact_number)
        # set keywords
        bot.find_element(selector="//div[div[label[text()='Keywords']]]//input", by=By.XPATH, ensure_visible=True).send_keys(keywords)
        # upload resume file
        tools.upload_file_background(bot, selector_upload="//input[@type='file']", file_path=f'{config.resources_folder}/resume.txt')

        # add candidate
        bot.find_element(selector='//button[@type="submit"]', by=By.XPATH, ensure_visible=True).click()

        # validate if candidate add on OrangeHRM
        if not bot.find_element(selector=f"//form[h6[text()='Application Stage']]//p[text()='{full_name}']", by=By.XPATH, ensure_visible=True):
            raise Exception('Failed to register candidate')

    except Exception as error:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        raise ValueError(error, exc_traceback.tb_lineno, exc_traceback.tb_frame.f_code.co_name)

