from obsws_python import ReqClient
import json
import http.client as client
from datetime import datetime as dt, timezone
from canal_obs import CanalOBS
import yaml

class YouTubeOBSManager:
    def __init__(self):
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.youtube_key = config.get("youtube_api_key")
        self.obs_host = config.get("obs_host", "localhost")
        self.obs_port = config.get("obs_port", 4455)
        self.obs_password = config["obs_password"]
        self.browser_width = 1050
        self.browser_height = 600
        # Criação dos canais sem horários de verificação
        self.canais = [
            CanalOBS(c["channel_id"], c["nome"])
            for c in config["canais"]
        ]

    def get_obs_client(self):
        return ReqClient(host=self.obs_host, port=self.obs_port, password=self.obs_password)

    def buscar_eventos_api(self, canal):
        """
        Busca eventos ao vivo e agendados do canal no YouTube.
        Retorna lista de eventos com detalhes de horário.
        """
        if not canal.channel_id:
            return []
        eventos = []
        try:
            endpoint_live = f"/youtube/v3/search?part=snippet&channelId={canal.channel_id}&key={self.youtube_key}&eventType=live&type=video&maxResults=10"
            eventos += self._eventos_da_api(endpoint_live)
            endpoint_upcoming = f"/youtube/v3/search?part=snippet&channelId={canal.channel_id}&key={self.youtube_key}&eventType=upcoming&type=video&maxResults=10"
            eventos += self._eventos_da_api(endpoint_upcoming)
            # Buscar detalhes dos vídeos para pegar os horários
            video_ids = [ev['videoId'] for ev in eventos]
            if video_ids:
                detalhes = self._detalhes_videos(video_ids)
                for ev in eventos:
                    det = detalhes.get(ev['videoId'], {})
                    ev['actualStartTime'] = det.get('actualStartTime')
                    ev['scheduledStartTime'] = det.get('scheduledStartTime')
                    ev['actualEndTime'] = det.get('actualEndTime')
            # FILTRAR eventos já encerrados
            agora = dt.now(timezone.utc)
            eventos_filtrados = []
            for evento in eventos:
                if evento.get("actualEndTime"):
                    continue
                sched = evento.get("scheduledStartTime")
                # Não remover eventos agendados para hoje ou futuro
                if sched:
                    try:
                        sched_dt = dt.fromisoformat(sched.replace("Z", "+00:00"))
                        # Só remove se agendado para antes de hoje (não apenas antes de agora)
                        if sched_dt.date() < agora.date():
                            continue
                    except Exception:
                        pass
                eventos_filtrados.append(evento)
            eventos = eventos_filtrados
        except Exception as e:
            print(f"[buscar_eventos_api] Erro: {e}")
        return eventos

    def _detalhes_videos(self, video_ids):
        detalhes = {}
        try:
            endpoint = f"/youtube/v3/videos?part=liveStreamingDetails&id={','.join(video_ids)}&key={self.youtube_key}"
            conn = client.HTTPSConnection("www.googleapis.com", timeout=10)
            conn.request("GET", endpoint)
            res = conn.getresponse()
            if res.status != 200:
                print(f"[_detalhes_videos] HTTP status: {res.status}")
                return detalhes
            data = json.loads(res.read().decode("utf-8"))
            for item in data.get("items", []):
                vid = item["id"]
                live_details = item.get("liveStreamingDetails", {})
                detalhes[vid] = live_details
        except Exception as e:
            print(f"[_detalhes_videos] Erro: {e}")
        return detalhes

    def _eventos_da_api(self, endpoint):
        try:
            conn = client.HTTPSConnection("www.googleapis.com", timeout=10)
            conn.request("GET", endpoint)
            res = conn.getresponse()
            if res.status != 200:
                print(f"[_eventos_da_api] HTTP status: {res.status}")
                return []
            data = json.loads(res.read().decode("utf-8"))
            items = data.get("items", [])
            eventos = []
            for item in items:
                try:
                    video_id = item["id"]["videoId"]
                    title = item["snippet"]["title"]
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    live_details = item.get("liveStreamingDetails", {})
                    actualStartTime = live_details.get("actualStartTime")
                    scheduledStartTime = live_details.get("scheduledStartTime")
                    eventos.append({
                        "videoId": video_id,
                        "title": title,
                        "url": url,
                        "actualStartTime": actualStartTime,
                        "scheduledStartTime": scheduledStartTime,
                    })
                except Exception as e:
                    print(f"[_eventos_da_api] Erro ao processar item: {e}")
                    continue
            return eventos
        except Exception as e:
            print(f"[_eventos_da_api] Erro: {e}")
            return []

    def selecionar_stream(self, eventos, canal):
        agora = dt.now(timezone.utc)
        # Filtrar eventos já encerrados e agendados para datas passadas
        eventos_filtrados = []
        for evento in eventos:
            # Ignorar eventos já encerrados
            if evento.get("actualEndTime"):
                continue
            sched = evento.get("scheduledStartTime")
            # Não remover eventos agendados para hoje ou futuro
            if sched:
                try:
                    sched_dt = dt.fromisoformat(sched.replace("Z", "+00:00"))
                    if sched_dt.date() < agora.date():
                        continue
                except Exception:
                    pass
            eventos_filtrados.append(evento)
        eventos = eventos_filtrados
        melhor_evento = None
        menor_delta = None
        # 1. Priorizar evento ao vivo (actualEndTime null e scheduledStartTime já passou OU actualStartTime preenchido)
        for evento in eventos:
            is_live = False
            if evento.get("actualStartTime") and not evento.get("actualEndTime"):
                is_live = True
                try:
                    inicio = dt.fromisoformat(evento["actualStartTime"].replace("Z", "+00:00"))
                except Exception:
                    inicio = agora
            elif evento.get("scheduledStartTime") and not evento.get("actualEndTime"):
                try:
                    sched_dt = dt.fromisoformat(evento["scheduledStartTime"].replace("Z", "+00:00"))
                    if sched_dt <= agora:
                        is_live = True
                        inicio = sched_dt
                except Exception:
                    pass
            if is_live:
                delta = abs((agora - inicio).total_seconds())
                if menor_delta is None or delta < menor_delta:
                    melhor_evento = evento
                    menor_delta = delta
        # 2. Se não há ao vivo, pegar agendado mais próximo no futuro
        if not melhor_evento:
            menor_delta = None
            for evento in eventos:
                sched = evento.get("scheduledStartTime")
                if sched:
                    try:
                        inicio = dt.fromisoformat(sched.replace("Z", "+00:00"))
                        if inicio > agora:
                            delta = (inicio - agora).total_seconds()
                            if menor_delta is None or delta < menor_delta:
                                melhor_evento = evento
                                menor_delta = delta
                    except Exception as e:
                        print(f"[selecionar_stream] Erro ao converter scheduledStartTime: {e}")
                        continue
        if melhor_evento:
            return melhor_evento["url"]
        return None

    def atualizar_fontes_obs(self, ws, canal):
        from obs_utils import force_browser_source_refresh
        largura = 1280 if canal.browser_source_name == "CanaisMassa" else self.browser_width
        try:
            resp = ws.get_input_settings(canal.browser_source_name)
            input_settings = getattr(resp, "inputSettings", {})
            input_settings.update({
                "url": canal.proxima_stream_url or "",
                "width": largura,
                "height": self.browser_height,
                "reloadWhenSceneBecomesActive": True,
            })
            if canal.browser_source_name != "CanaisMassa":
                force_browser_source_refresh(ws, canal.browser_source_name, input_settings)
            else:
                ws.set_input_settings(canal.browser_source_name, input_settings, overlay=True)
        except Exception as e:
            print(f"[atualizar_fontes_obs] Erro: {e}")
