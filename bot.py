from botcity.maestro import AutomationTaskFinishStatus, ErrorType, AlertType
from botcity.web import WebBot
import config
import orange


def main():

    bot = WebBot()

    bot.headless = False

    execution = config.maestro.get_execution("13588300")

    # Inicializar variáveis
    qt_total_itens = qt_itens_sucesso = 0
    item = None

    try:

        # Access the Orange HRM website
        orange.login(bot)

        # Obtendo a referência do Datapool
        candidatos = config.maestro.get_datapool(label="test_find_item")

        while candidatos.has_next():

            try:

                # Verifica se a task foi interrompida via Control Room
                if execution.task_id and config.maestro.get_task(task_id=execution.task_id).is_interrupted():
                    config.maestro.finish_task(task_id=execution.task_id,
                                               status=AutomationTaskFinishStatus.PARTIALLY_COMPLETED,
                                               message="Execução interrompida via Control Room!")
                    return

                # Retorna o próximo item disponível do Datapool
                item = candidatos.next(task_id=execution.task_id)

                if item is None:
                    # Se o item for nulo, encerra o loop
                    break

                full_name = item.get_value("full_name")
                vacancy = item.get_value("vacancy")
                email = item.get_value("email")
                contact_number = item.get_value("contact_number")
                keywords = item.get_value("keywords")


                # Navigate from de recruitment menu
                orange.access_add_candidate(bot)

                # Register all candidates on Orange HRM
                orange.register_candidate(bot, full_name, vacancy, email, contact_number, keywords)

                # Registrar como item processado com sucesso
                item.report_done()

                qt_total_itens += 1

            except Exception as error:

                error_message, error_line, task_name = eval(str(error))

                item.report_error(error_type=ErrorType.SYSTEM, finish_message=f"{error_message}")

                print(fr'Error Message: {error_message} \n Error line number:{error_line} \n Task Name: {task_name}')

                config.maestro.maestro.alert(task_id=execution.task_id,title="Warning alert",
                                             message=fr'Error Message: {error_message} | Error line number:{error_line} | Task Name: {task_name}',
                                             alert_type=AlertType.INFO)


        # Envia status = 'Sucesso' para a BotMaestro
        config.maestro.finish_task(task_id=execution.task_id,
                            status=AutomationTaskFinishStatus.SUCCESS,
                            message="Execução finalizada com sucesso!",
                            total_items=qt_total_itens,
                            processed_items=qt_itens_sucesso)


    except Exception as error:

        bot.screenshot('error.png')
        config.maestro.error(task_id=int(execution.task_id), exception=error, screenshot='error.png')

        print('Error Message: ', error)
        error_message, error_line, task_name = eval(str(error))

        # Envia status = 'Falha' para a Control Room
        config.maestro.finish_task(task_id=execution.task_id,
                                   status=AutomationTaskFinishStatus.FAILED,
                                   message=f"{error_message} | Error line number:{error_line} | Task Name: {task_name}",
                                   total_items=qt_total_itens,
                                   processed_items=qt_itens_sucesso)

    finally:
        # Fecha o navegador
        bot.stop_browser()


if __name__ == '__main__':
    main()
