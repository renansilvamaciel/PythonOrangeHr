from framework.state import STATE
import logging

import orange


logger = logging.getLogger(__name__)


'''
process.py
    Add the steps to your automation process here.
'''


def process_item():
    """
    Runs the steps of the automation process for each item.
    """
    STATE.raise_for_interrupt_requested()
    
    logger.info(f"Item processing has started: hi.")
    bot = STATE.webbot

    orange.login(bot)









    
    
