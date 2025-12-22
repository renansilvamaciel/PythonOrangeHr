from framework.exceptions import SystemException, BusinessException, InterruptException
from framework.error_handling import (handle_interrupt_requested,
                                      handle_business_exception,
                                      handle_system_exception)
from framework.initialize import initialize, init_webbot
from framework.finalize import finalize, cleanup
from framework.state import STATE
import logging
from framework import orange, tools, config

logger = logging.getLogger(__name__)

def action():
    try:
        initialize()

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

        except BusinessException as ex:
            handle_business_exception(ex)

        except (SystemException, Exception) as ex:
            handle_system_exception(ex)
            initialize(restart=True)


    except InterruptException:
        handle_interrupt_requested()

    except BusinessException as ex:
        handle_business_exception(ex)

    except (SystemException, Exception) as ex:
        handle_system_exception(ex)

    finally:
        cleanup()
        finalize()


if __name__ == "__main__":
    action()
