def force_browser_source_refresh(ws, source_name, input_settings):
    """
    Força o refresh visual da fonte browser do OBS:
    - Atualiza a URL com parâmetro fictício alternado
    - Alterna visibilidade (hide/show)
    """
    url = input_settings.get("url", "")
    if "__mainrefresh__=1" in url:
        url_refresh = url.replace("__mainrefresh__=1", "__mainrefresh__=2")
    elif "__mainrefresh__=2" in url:
        url_refresh = url.replace("__mainrefresh__=2", "__mainrefresh__=1")
    elif "?" in url:
        url_refresh = url + "&__mainrefresh__=1"
    else:
        url_refresh = url + "?__mainrefresh__=1"
    input_settings["url"] = url_refresh
    ws.set_input_settings(source_name, input_settings, overlay=True)
    # Alterna visibilidade para garantir refresh visual
    try:
        ws.set_input_settings(source_name, {**input_settings, "visible": False}, overlay=True)
        ws.set_input_settings(source_name, {**input_settings, "visible": True}, overlay=True)
    except Exception:
        pass

def limpar_pesquisa_api(motivo=None):
    import shutil
    from log_config import log_terminal
    shutil.rmtree('pesquisa_api', ignore_errors=True)
    msg = 'Pasta pesquisa_api/ limpa automaticamente para nova pesquisa do dia.' if not motivo else motivo
    log_terminal(msg, cor='red')
