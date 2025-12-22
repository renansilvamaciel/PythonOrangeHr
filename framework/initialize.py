from framework.logger import setup_logger, setup_botcity_log
from webdriver_manager.chrome import ChromeDriverManager
from botcity.web import WebBot, Browser
from framework.finalize import cleanup
from botcity.core import DesktopBot
from framework.state import STATE
from pathlib import Path
import logging
import shutil
import sys

logger = logging.getLogger(__name__)

'''
initialize.py
    Starts the automation process by setting up the logger, cleaning the output directory, and opening the browser.

'''


def run_once():
    """
    Steps that will be performed once the automation starts, such as setting up the logger and cleaning the output directory.
    """
    execution = STATE.execution
    logger.info(f"Automation {STATE.task_info().activity_name} started. ")
    setup_temp_folders()
    setup_logger()
    setup_botcity_log()
    print(f"Task ID is: {execution.task_id}")
    if execution.parameters:
        print(f"Task Parameters are: {execution.parameters}")


def initialize(restart: bool = False):
    """
    Initializes the automation process by setting up the logger, cleaning the output directory, and opening the browser. 
    """
    try:
        STATE.raise_for_interrupt_requested()
        if restart:
            cleanup()
        else:
            run_once()

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        raise ValueError(e, exc_traceback.tb_lineno, exc_traceback.tb_frame.f_code.co_name)




def init_webbot():
    """
    Instantiates BotCity's WebBot, installs the DriverManager and opens the browser.
    """
    STATE.webbot = WebBot()
    bot = STATE.webbot
    bot.headless = False
    bot.browser = Browser.CHROME
    bot.driver_path = ChromeDriverManager().install()


def init_desktopbot():
    """
    Instantiates BotCity's DesktopBot.
    """
    STATE.desktopbot = DesktopBot()


def setup_temp_folders():
    shutil.rmtree("./output", ignore_errors=True)
    Path("./output").mkdir(parents=True, exist_ok=True)
    # if Path("./temp").is_dir():
    shutil.rmtree("./temp", ignore_errors=True)
    Path("./temp").mkdir(parents=True, exist_ok=True)
