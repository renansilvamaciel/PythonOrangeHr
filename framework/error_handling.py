from botcity.maestro.model import AlertType
from framework.state import STATE
import datetime
import logging


logger = logging.getLogger(__name__)
maestro = STATE.maestro
execution = STATE.execution


def handle_business_exception(exception: Exception):
    STATE.register_error()
    maestro.alert(task_id=STATE.task_id,
                  title="Business Exception ocurred.",
                  message=f"Item: {STATE.item}.", alert_type=AlertType.ERROR)

    screenshot_error_report(exception)


def handle_system_exception(exception: Exception):
    STATE.register_error()
    maestro.alert(task_id=STATE.task_id,
                  title="System Exception ocurred.",
                  message="Check the logs for more information.", alert_type=AlertType.ERROR)

    screenshot_error_report(exception)


def handle_interrupt_requested():
    STATE.register_error()
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
    screenshot_filepath = fr".\temp\error-{date}.png"
    STATE.webbot.save_screenshot(screenshot_filepath)



def register_sucess(message):
    logger.info(f"Item processing successfull: {message}")
    STATE.register_success()

    
