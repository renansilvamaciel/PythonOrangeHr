from framework.state import STATE
from pathlib import Path
import logging
import glob



logger = logging.getLogger(__name__)


'''
finalize.py
    Gracefully ends the automation process using Cleanup and Finalize steps.
'''


def cleanup():
    """
    Perform steps to gracefully clean up the environment, log out of systems, close apps, connections, sessions etc.
    """
    try:
        # Logs out of systems
        # logger.info(f"Logging out of system/apps")
        ...

        # Close apps, connections, sessions etc
        if STATE.webbot:
            STATE.webbot.stop_browser()
            logger.info(f"Browser closed.")
    except Exception as ex:
        logger.error(f"Error during cleanup: {ex}")
        raise ex


def finalize():
    """
    Performs steps to finalize the automation process gracefully in the BotCity Orchestrator.
    Returns: None
    """
    try:
        logger.info(f"The automation process has finished. Task ID: {STATE.task_id}. Sending results to BotCity Orchestrator...")
        
        # generate_report_file()

        # Send emails/Alerts
        # logger.info(f"Sending emails/alerts")
        ...

        try:
            STATE.maestro.new_log_entry(STATE.task_info().activity_name, {
                "message": finish_status_message()})
        except Exception as ex:
            logger.error(f"Error while trying to create a new log entry in the BotCity Orchestrator: {ex}")

        # Upload output folder to BotCity Orchestrator as Result Files
        upload_output_orchestrator()
        
        
    except Exception as ex:
        logger.error(f"Error during finalize: {ex}")
        raise ex
    finally:
        finish_task_orchestrator()


# def generate_report_file():
#     """
#     Generates a report file with the summary of the automation process and stores it in the output folder.
#     """
#     try:
#         with open('./output/report.html', 'w') as f:
#             f.write(generate_jinja_report())
#         logger.info(f"Report summary created at ./output/report.html")
#     except Exception as ex:
#         logger.error(f"Error generating report file: {ex}")
#         # raise ex


def upload_output_orchestrator():
    """
    Uploads the whole output folder to the BotCity Orchestrator.
    """
    try:
        for f in glob.iglob("./output/*"):
            fp = Path(f)
            STATE.maestro.post_artifact(
                task_id=STATE.task_id,
                artifact_name=fp.name,
                filepath=fp
            )
        logger.info(f"Output uploaded to BotCity Orchestrator.")

    except Exception as ex:
        print(f"Error uploading output to BotCity Orchestrator: {ex}")
        raise ex


def finish_task_orchestrator():
    """
    Finish task accordingly in the BotCity Orchestrator.
    Returns: None
    """
    try:
        STATE.maestro.finish_task(
            task_id=STATE.task_id,
            status=STATE.compute_finish_status(),
            message=finish_status_message(),
            total_items=STATE.total_items,
            processed_items=STATE.success_count,
            failed_items=STATE.error_count
        )

    except Exception as ex:
        print(f"Error finishing task in the BotCity Orchestrator: {ex}")
        raise ex


def finish_status_message() -> str:
    """
    Formats and outputs a simplified finish message.
    Returns: str: Message
    """
    msg = f''' Task Completed - Process: {STATE.task_info().activity_name}. 
    In our run for task {STATE.task_id} we processed {STATE.total_items} items, from which {STATE.success_count} were with success. 
    Check the Result Files for more details.
    '''
    return msg
