import os
import time
import datetime
from youtube_obs_manager import YouTubeOBSManager
from colorama import init
import msvcrt
from log_config import setup_logger, log_terminal
from datetime import timezone
from obs_utils import limpar_pesquisa_api

init(autoreset=True)
logger = setup_logger()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def processar_canal(canal, manager, ws, canais):
    try:
        if canal.browser_source_name == "CanaisMassa":
            canal.proxima_stream_url = "https://massa.com.br/canais/"
            manager.atualizar_fontes_obs(ws, canal)
            log_terminal(f"[{canal.browser_source_name}] Fonte OBS atualizada (fixa): {canal.proxima_stream_url}", cor='green')
            return
        if canal.browser_source_name == "FonteIguacu24x7":
            iguacu = next((c for c in canais if c.browser_source_name == "FonteIguacu"), None)
            eventos = iguacu.carregar_ultima_pesquisa() if iguacu else []
            eventos = [ev for ev in eventos if ev.get('title') == "Rede Massa SBT AO VIVO 24h"]
        else:
            agora = datetime.datetime.now(timezone.utc)
            eventos = canal.carregar_ultima_pesquisa()
            eventos = [ev for ev in eventos if ev.get('title') != "Rede Massa SBT AO VIVO 24h"]
            # Forçar busca se houver evento agendado para os próximos 2 minutos
            for ev in eventos:
                sched = ev.get('scheduledStartTime')
                if sched:
                    try:
                        sched_dt = datetime.datetime.fromisoformat(sched.replace("Z", "+00:00"))
                        if 0 <= (sched_dt - agora).total_seconds() <= 120:
                            log_terminal(f"[{canal.browser_source_name}] Evento agendado prestes a começar, forçando busca na API...", level='warning', cor='yellow')
                            eventos_api = manager.buscar_eventos_api(canal)
                            if eventos_api:
                                canal.salvar_pesquisa(eventos_api)
                                eventos = [ev for ev in eventos_api if ev.get('title') != "Rede Massa SBT AO VIVO 24h"]
                                log_terminal(f"[{canal.browser_source_name}] Pesquisa API realizada.", cor='magenta')
                            break
                    except Exception:
                        pass
            if not eventos:
                log_terminal(f"[{canal.browser_source_name}] Forçando busca na API...", level='warning', cor='yellow')
                eventos_api = manager.buscar_eventos_api(canal)
                if eventos_api:
                    canal.salvar_pesquisa(eventos_api)
                    eventos = [ev for ev in eventos_api if ev.get('title') != "Rede Massa SBT AO VIVO 24h"]
                    log_terminal(f"[{canal.browser_source_name}] Pesquisa API realizada.", cor='magenta')
        url = manager.selecionar_stream(eventos, canal)
        titulo_stream = None
        if url:
            for ev in eventos:
                if ev.get('url') == url:
                    titulo_stream = ev.get('title')
                    break
        if not url:
            log_terminal(f"[{canal.browser_source_name}] Nenhum evento válido encontrado.", level='warning', cor='red')
        elif canal.proxima_stream_url != url:
            canal.proxima_stream_url = url
            manager.atualizar_fontes_obs(ws, canal)
            if titulo_stream:
                log_terminal(f"[{canal.browser_source_name}] Fonte OBS atualizada: {titulo_stream} | {url}", cor='green')
            else:
                log_terminal(f"[{canal.browser_source_name}] Fonte OBS atualizada: {url}", cor='green')
        else:
            if titulo_stream:
                log_terminal(f"[{canal.browser_source_name}] URL não mudou: {titulo_stream} | {url}", cor='black')
            else:
                log_terminal(f"[{canal.browser_source_name}] URL não mudou: {url}", cor='black')
    except Exception as e:
        log_terminal(f"[{canal.browser_source_name}] Erro: {e}", level='error', cor='red')

def precisa_limpar_pesquisa_api():
    import os
    import glob
    from datetime import datetime, timezone
    hoje_str = datetime.now(timezone.utc).strftime("%d-%m-%Y")
    arquivos_hoje = glob.glob(f"pesquisa_api/*/{hoje_str}_*.json")
    return len(arquivos_hoje) == 0

def main_loop(intervalo=60):
    manager = YouTubeOBSManager()
    iteracao = 0
    canais = manager.canais
    ws = manager.get_obs_client()  # Novo método utilitário para obter o client OBS
    # Limpeza automática da pasta pesquisa_api apenas se não houver pesquisa do dia
    if precisa_limpar_pesquisa_api():
        limpar_pesquisa_api()
    try:
        while True:
            clear_terminal()
            iteracao += 1
            log_terminal(f"YouTube/OBS Monitor - Iteração: {iteracao}", cor='cyan')
            log_terminal("[R] Rodar manualmente | [F] Forçar atualização | [Ctrl+C] Sair\n", cor='yellow')
            log_terminal("Streams enviadas ao OBS nesta iteração:\n", cor='white')
            logger.info(f"--- Iteração {iteracao} ---")
            for canal in canais:
                processar_canal(canal, manager, ws, canais)
            for _ in range(intervalo):
                if msvcrt.kbhit():
                    tecla = msvcrt.getch()
                    if tecla in [b'r', b'R']:
                        log_terminal("Execução manual disparada.", cor='yellow')
                        break
                    elif tecla in [b'f', b'F']:
                        try:
                            limpar_pesquisa_api("Pasta pesquisa_api/ removida. Atualizando todas as pesquisas agora...")
                            for canal in canais:
                                processar_canal(canal, manager, ws, canais)
                            log_terminal("Atualização forçada concluída.", cor='green')
                        except Exception as e:
                            log_terminal(f"Erro ao remover pasta pesquisa_api/: {e}", level='error', cor='red')
                        break
                time.sleep(1)
    finally:
        ws.disconnect()

if __name__ == "__main__":
    try:
        main_loop(intervalo=120)
    except KeyboardInterrupt:
        log_terminal("Encerrando monitoramento.", cor='yellow')
