from netqasm.logging.output import get_new_app_logger

def log(message, role, app_config):
    # Put your code here
    log_config = app_config.log_config
    app_logger = get_new_app_logger(app_name=role, log_config=log_config)
    app_logger.log(message)
    return
