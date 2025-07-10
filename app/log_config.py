import logging
from colorama import Fore, Style
import datetime

def setup_logger(log_file='app.log'):
    import os
    os.makedirs('logs', exist_ok=True)
    log_path = os.path.join('logs', log_file)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8')
        ]
    )
    return logging.getLogger()

def log_terminal(msg, level='info', cor=None):
    hora_str = datetime.datetime.now().strftime("%H:%M:%S")
    cor_map = {
        'green': Fore.LIGHTGREEN_EX,
        'red': Fore.LIGHTRED_EX,
        'magenta': Fore.LIGHTMAGENTA_EX,
        'yellow': Fore.LIGHTYELLOW_EX,
        'black': Fore.LIGHTBLACK_EX,
        'cyan': Fore.LIGHTCYAN_EX,
        'white': Fore.LIGHTWHITE_EX,
    }
    cor_prefix = cor_map.get(cor, '')
    print(f"{cor_prefix}[{hora_str}] {msg}" + Style.RESET_ALL)
    logger = logging.getLogger()
    if level == 'info':
        logger.info(msg)
    elif level == 'warning':
        logger.warning(msg)
    elif level == 'error':
        logger.error(msg)
    else:
        logger.info(msg)
