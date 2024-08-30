from botcity.web.util import element_as_select
from botcity.web import WebBot, By
import shutil as sh
import config
import os


def waiting_download(bot: WebBot, file_extension: str = '.pdf', timeout: int = 30000) -> str:
    """
    Function for waiting download of a file.

    :param bot: Object of browser
    :param file_extension: Extension of file to download
    :param timeout: Timeout in milliseconds
    :return: Path to file
    """
    try:
        qt_files_before = bot.get_file_count(file_extension=file_extension)

        qt_files_after = 0
        for i in range(int(timeout / 500)):
            qt_files_after = bot.get_file_count(file_extension=file_extension)
            if qt_files_after > qt_files_before:
                break
            bot.wait(500)

        if qt_files_after <= qt_files_before:
            raise Exception('Timeout to waiting download file complete')

        file_path = bot.get_last_created_file(path=config.resources_folder)

        return file_path

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        raise ValueError(error, exc_traceback.tb_lineno, exc_traceback.tb_frame.f_code.co_name)


def new_folder(folder_path: str, replace_folder: bool = False) -> None:
    """
    make a new folder in the directory informed by parameter.
    :param folder_path: New folder path
    :param replace_folder: If True, replaces the folder if it exists
    """
    try:
        if replace_folder:
            sh.rmtree(path=folder_path, ignore_errors=True)
        os.makedirs(folder_path, exist_ok=True)

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        raise ValueError(error, exc_traceback.tb_lineno, exc_traceback.tb_frame.f_code.co_name)


def upload_file_background(bot: WebBot,
                           selector_upload: str,
                           file_path: str,
                           confirm_xpath: str = None,
                           timeout: int = 60000) -> bool:
    """
    Uploads a file without relying on the File Explorer window.

    Note: The ensure_visible and ensure_clickable properties were not considered,
    because not all elements of type "file" have them, which could result in
    unwanted errors.

    :param bot: An instance of the WebDriver to interact with the browser.
    :param selector_upload: XPath for the file upload element.
    :param file_path: Full path to the file to be loaded.
    :param confirm_xpath: (Optional) XPath for a verification element.
    :param timeout: Waiting time to report failure.
    :return: True if the file was loaded successfully.
    """

    try:
        # Search for the web element used to upload the file
        bot.find_element(selector_upload, By.XPATH, waiting_time=timeout).send_keys(file_path)

        # Checks whether an upload confirmation element was provided
        if confirm_xpath:
            # Checks if the confirmation element exists. If yes, it means the upload was successful.
            if bot.find_element(confirm_xpath, By.XPATH, waiting_time=timeout, ensure_clickable=True):
                return True

            raise Exception('Upload confirmation not found.')

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        raise ValueError(error, exc_traceback.tb_lineno, exc_traceback.tb_frame.f_code.co_name)

