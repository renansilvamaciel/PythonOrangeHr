from botcity.maestro.model import AutomationTaskFinishStatus, AutomationTask
from botcity.maestro import BotMaestroSDK, dataclass
from framework.exceptions import InterruptException
from dataclasses import field, asdict
from botcity.web import WebBot
from dotenv import load_dotenv
from datetime import timezone
import logging
import os



logger = logging.getLogger(__name__)

'''
state.py
    Implements a state management system that works seamlessly with BotCity Orchestrator features.
    The State class Maintains the execution state of automation tasks, providing features such as:
        - Count successful and failed items
        - Check for interruption request
        - Stores WebBot(), DesktopBot() instances
        - And more
'''


@dataclass
class State:
    maestro: BotMaestroSDK = None
    task_id: str = ""
    item: dict = field(default_factory=dict)
    success_count: int = 0
    error_count: int = 0
    has_error: bool = False
    has_success: bool = False
    webbot: WebBot = None
    BotMaestroSDK.RAISE_NOT_CONNECTED = False
    TIMEZONE: timezone = 'America/Sao_Paulo'
    
    @property
    def total_items(self):
        """
        Sums success and error items.
        Returns: Total items.
        """
        return self.success_count + self.error_count

    def register_success(self):
        """
        Registers item success.
        """
        self.has_success = True
        self.success_count += 1

    def register_error(self):
        """
        Registers item error.
        """
        self.has_error = True
        self.error_count += 1

    def compute_finish_status(self) -> AutomationTaskFinishStatus:
        """
        Calculates the finish status of a task.
        Returns: AutomationTaskFinishStatus
        """
        if self.has_success and self.has_error:
            return AutomationTaskFinishStatus.PARTIALLY_COMPLETED
        elif self.has_error:
            return AutomationTaskFinishStatus.FAILED
        else:
            return AutomationTaskFinishStatus.SUCCESS

    def raise_for_interrupt_requested(self) -> bool:
        """
        Checks whether or not this task received an interrupt request.
        Returns: bool
        """

        if self.task_id and self.maestro.get_task(task_id=self.task_id).is_interrupted():
            raise InterruptException("Interrupt requested via BotCity.")
        return False

    def task_info(self) -> AutomationTask:
        """
        Returns details about a given task.
        Returns: AutomationTask
        """
        return self.maestro.get_task(self.task_id)

    def as_dict(self):
        """
        Returns:
            Dictionary representation of this object.
        """
        return asdict(self)


SIMULATION = True



if SIMULATION:
    # Set your credentials in the .env file order to run your bot locally.
    load_dotenv()
    SERVER = os.getenv('SERVER')
    LOGIN = os.getenv('LOGIN')
    KEY = os.getenv('KEY')
    TASK_ID = os.getenv('TASK_ID')

    if any(var == '' for var in (LOGIN, KEY)):
        print("\n ######### ERROR: You're in simulation mode. "
              "\n ######### Set your credentials in .env in order to run your bot locally.\n")
        exit()
    STATE = State()
    STATE.maestro = BotMaestroSDK.from_sys_args(default_server=SERVER,
                                                default_login=LOGIN, default_key=KEY)

    STATE.task_id = TASK_ID
    STATE.execution = STATE.maestro.get_execution(STATE.task_id)

else:
    STATE = State()
    STATE.maestro = BotMaestroSDK.from_sys_args()
    STATE.task_id = STATE.maestro.task_id
    STATE.execution = STATE.maestro.get_execution(STATE.task_id)

