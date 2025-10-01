from botcity.maestro import BotMaestroSDK, AutomationTaskFinishStatus
from botcity.web import WebBot
import config
import orange
import tools


def main():

    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Disable errors if we are not connected to Maestro
    BotMaestroSDK.RAISE_NOT_CONNECTED = True

    # Conecta com a BotMaestro
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    # Inicializar variáveis
    qt_total_itens = qt_itens_sucesso = 0

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

            # Verifica se a task foi interrompida via Control Room
            if execution.task_id and maestro.get_task(task_id=execution.task_id).is_interrupted():
                maestro.finish_task(task_id=execution.task_id,
                                    status=AutomationTaskFinishStatus.PARTIALLY_COMPLETED,
                                    message="Execução interrompida via Control Room!")
                return

            try:
                full_name = candidates.iloc[index, 0]
                vacancy = candidates.iloc[index, 1]
                email = candidates.iloc[index, 2]
                contact_number = candidates.iloc[index, 3]
                keywords = candidates.iloc[index, 4]
                qt_total_itens += 1

                # Navigate from de recruitment menu
                orange.access_add_candidate(bot)

                # Register all candidates on Orange HRM
                orange.register_candidate(bot, full_name, vacancy, email, contact_number, keywords)

                qt_itens_sucesso += 1

            except Exception as error:

                error_message, error_line, task_name = eval(str(error))

                print(fr'Error Message: {error_message} /n Error line number:{error_line} /n Task Name: {task_name}')

                bot.screenshot('error.png')

                maestro.error(task_id=execution.task_id, exception=error, screenshot='error.png')

                maestro.error(task_id=execution.task_id, exception=error)


        # Envia status = 'Sucesso' para a BotMaestro
        maestro.finish_task(task_id=execution.task_id,
                            status=AutomationTaskFinishStatus.PARTIALLY_COMPLETED,
                            message="Execução finalizada Parcialmente completa!",
                            total_items=qt_total_itens,
                            processed_items=qt_itens_sucesso)


    except Exception as error:
        maestro.error(task_id=execution.task_id, exception=error)

        print('Error Message: ', error)
        error_message, error_line, task_name = eval(str(error))

        # Envia status = 'Falha' para a Control Room
        maestro.finish_task(task_id=execution.task_id,
                            status=AutomationTaskFinishStatus.FAILED,
                            message=f"{error_message} | Error line number:{error_line} | Task Name: {task_name}",
                            processed_items=qt_itens_sucesso)

    finally:
        # Fecha o navegador
        bot.stop_browser()


if __name__ == '__main__':
    main()
