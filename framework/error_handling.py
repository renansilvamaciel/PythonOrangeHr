from framework.datasources import data_source
from botcity.maestro.model import AlertType
from framework.state import STATE
import datetime
import logging
'''
error_handling.py
    Add steps to handle errors, send alerts and more.

'''

logger = logging.getLogger(__name__)
maestro = STATE.maestro
execution = STATE.execution
bot = STATE.webbot #STATE.desktopbot

# todo unificar funções repetitivas \/

def handle_business_exception(exception: Exception):
    STATE.register_error()  # TODO report error + register error
    data_source.report_error("BUSINESS EXCEPTION", "Business Exception message")
    logger.error(f"Business Exception occurred for item {STATE.item}.")
    maestro.alert(task_id=STATE.task_id,
                  title="Business Exception ocurred.",
                  message=f"Item: {STATE.item}.", alert_type=AlertType.ERROR)

    screenshot_error_report(exception)


def handle_system_exception(exception: Exception):
    STATE.register_error()  # TODO report error + register error
    data_source.report_error("SYSTEM EXCEPTION", exception)
    logger.error(f"System Exception ocurred: {exception}")
    maestro.alert(task_id=STATE.task_id,
                  title="System Exception ocurred.",
                  message="Check the logs for more information.", alert_type=AlertType.ERROR)

    screenshot_error_report(exception)


def handle_interrupt_requested(exception: Exception):
    STATE.register_error()  # TODO report error + register error
    data_source.report_error("INTERRUPTION REQUESTED", Exception)
    logger.warning(f"Interruption requested.")
    maestro.alert(task_id=STATE.task_id,
                  title="Interruption requested.",
                  message="Check the logs for more information.", alert_type=AlertType.ERROR)


def screenshot_error_report(exception):
    """
    Saves a screenshot and registers the error in the BotCity Orchestrator.
    Returns: None
    """
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_filepath = f".\\temp\\error-{date}.png"
    # \/ todo fix "STATE.desktopbot" #definição do 'bot' que está sendo usado (web ou desktop) de forma mais genérica?
    STATE.webbot.save_screenshot(screenshot_filepath)
    maestro.error(task_id=STATE.task_id, exception=exception,
                  screenshot=screenshot_filepath)
    
def register_sucess(message): #TODO realocate(?)
    logger.info(f"Item processing successfull: {message}")
    STATE.register_success()
    data_source.report_success(message)
    
