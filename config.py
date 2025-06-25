from botcity.maestro import BotMaestroSDK
import os

maestro = BotMaestroSDK()


BotMaestroSDK.RAISE_NOT_CONNECTED = False

# Conecta com a BotMaestro
maestro.login(os.getenv("MAESTRO_SERVER"), os.getenv("MAESTRO_LOGIN"), os.getenv("MAESTRO_KEY"))

resources_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')


