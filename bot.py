from framework.exceptions import SystemException, BusinessException, InterruptException
from framework.error_handling import (handle_interrupt_requested,
                                      handle_business_exception,
                                      handle_system_exception)
from framework.initialize import initialize, init_webbot
from framework.finalize import finalize, cleanup
from framework.state import STATE
import logging
import config
import orange
import tools


logger = logging.getLogger(__name__)

'''
TODO: report error AND register error at the same time 
'''
def action():
    try:
        initialize()

        '''
           Add the steps to your automation process here.
        '''

        logger.info("Item processing has started")

        init_webbot()

        bot = STATE.webbot

        # Login Orange HRM
        orange.login(bot)

        # replace a resources folder
        tools.new_folder(config.resources_folder, True)

        # Download to CSV file
        path_csv = orange.download_csv(bot, 'https://workshop.botcity.dev/assets/candidatos.csv')

        # Read csv file
        candidates = orange.read_csv(path_csv)
        try:
            for index, row in candidates.iterrows():

                STATE.raise_for_interrupt_requested()

                full_name = str(candidates.iloc[index, 0])
                vacancy = str(candidates.iloc[index, 1])
                email = str(candidates.iloc[index, 2])
                contact_number = str(candidates.iloc[index, 3])
                keywords = str(candidates.iloc[index, 4])

                # Navigate from de recruitment menu
                orange.access_add_candidate(bot)

                # Register all candidates on Orange HRM
                orange.register_candidate(bot, full_name, vacancy, email, contact_number, keywords)

                # Process finalize with success
                STATE.register_success()

        except InterruptException as ex:
            handle_interrupt_requested(ex)

        except BusinessException as ex:
            handle_business_exception(ex)

        except (SystemException, Exception) as ex:
            logger.error(f"systemexception/generic") #arrumar
            handle_system_exception(ex)
            initialize(restart=True)

    except Exception as ex: 
        logger.error(f"Error during initialize: {ex}")
          
    finally:
        cleanup()
        finalize()

if __name__ == "__main__":
    action()
