"""Plantão dos vídeos (TikTok + YouTube): fica rodando ~5h30 conferindo a cada 10 min se tem algo pra fazer
(renderizar de madrugada, mandar lote de rascunhos, subir Shorts) e no fim o workflow se religa sozinho.
Não depende do agendador do GitHub, que pula horários.
"""
import importlib, os, sys, time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts'))
import reels  # noqa: E402

LIMITE_MIN = int(os.environ.get('TURNO_MIN', '300'))


def passo():
    fez = False
    if os.environ.get('TIKTOK_CLIENT_SECRET'):
        try:
            import tiktok_rascunho as tt
            tt = importlib.reload(tt)  # pega melhorias enviadas no meio do plantão
            if tt.TOKEN_ARQ.exists() and (tt.noite_pendente() or tt.a_enviar() > 0 or reels.ler_json(tt.FILA, [])):
                print(datetime.now(reels.BRT).strftime('%H:%M'), 'TikTok: trabalhando…', flush=True)
                tt.ciclo(); fez = True
        except Exception as e:
            print('⚠️ TikTok falhou:', e, flush=True)
    if os.environ.get('YT_CLIENT_SECRET'):
        try:
            import youtube as yt
            yt = importlib.reload(yt)
            if yt.TOKEN.exists() and yt.faltam_agora() > 0:
                print(datetime.now(reels.BRT).strftime('%H:%M'), 'YouTube: subindo…', flush=True)
                yt.enviar(); fez = True
        except Exception as e:
            print('⚠️ YouTube falhou:', e, flush=True)
    try:
        fez = relatorio_na_hora() or fez
    except Exception as e:
        print('⚠️ disparo do relatório falhou:', e, flush=True)
    if fez:
        reels.salvar_git('Vídeos: plantão')
    return fez


def relatorio_na_hora():
    """O agendador do GitHub atrasa horas; o plantão dispara o relatório diário no horário certo (23:40)."""
    import subprocess
    agora = datetime.now(reels.BRT); hoje = agora.strftime('%Y-%m-%d')
    marca = RAIZ / 'dados' / 'relatorio_disparo.txt'
    if agora.strftime('%H:%M') < '23:40' or (marca.exists() and marca.read_text().strip() == hoje):
        return False
    repo = os.environ.get('GITHUB_REPOSITORY', 'kaicjackson88-ui/meucaoobedece-postss')
    r = subprocess.run(['gh', 'api', '-X', 'POST', f'repos/{repo}/actions/workflows/metricas.yml/dispatches', '-f', 'ref=main'],
                       capture_output=True, text=True, env={**os.environ, 'GH_TOKEN': os.environ.get('GITHUB_TOKEN', '')})
    print(datetime.now(reels.BRT).strftime('%H:%M'), 'relatório diário disparado', r.returncode, r.stderr[:200], flush=True)
    if r.returncode == 0:
        marca.write_text(hoje); return True
    return False


def main():
    inicio = time.time()
    while (time.time() - inicio) / 60 < LIMITE_MIN:
        subprocess_pull()
        passo()
        time.sleep(600)
    print('Plantão dos vídeos encerrado; o workflow vai religar.')


def subprocess_pull():
    import subprocess
    subprocess.run(['git', 'pull', '-q', '--rebase', '--autostash'], cwd=RAIZ, capture_output=True)


if __name__ == '__main__':
    main()
