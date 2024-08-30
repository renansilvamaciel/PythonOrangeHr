from botcity.web import WebBot
import config
import orange
import tools


def main():

    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = False

    try:
        # replace a resources folder
        tools.new_folder(config.resources_folder, True)

        # Access the Orange HRM website
        orange.login(bot)

        # Download to CSV file
        path_csv = orange.download_csv(bot, 'https://workshop.botcity.dev/assets/candidatos.csv')

        # Read csv file
        candidates = orange.read_csv(path_csv)

        for index, row in candidates.iterrows():

            try:
                full_name = candidates.iloc[index, 0]
                vacancy = candidates.iloc[index, 1]
                email = candidates.iloc[index, 2]
                contact_number = candidates.iloc[index, 3]
                keywords = candidates.iloc[index, 4]

                # Navigate from de recruitment menu
                orange.access_add_candidate(bot)

                # Register all candidates on Orange HRM
                orange.register_candidate(bot, full_name, vacancy, email, contact_number, keywords)

            except Exception as error:
                error_message, error_line, task_name = eval(str(error))
                print(fr'Error Message: {error_message} /n Error line number:{error_line} /n Task Name: {task_name}')

    except Exception as error:
        error_message, error_line, task_name = eval(str(error))
        print(fr'Error Message: {error_message} Error line number:{error_line} Task Name: {task_name}')

    finally:
        # Fecha o navegador
        bot.stop_browser()


if __name__ == '__main__':
    main()
