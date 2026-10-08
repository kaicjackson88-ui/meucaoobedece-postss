"""Mostra quais permissões a chave da Meta tem (sem mostrar a chave)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from postar import chamar, conta_instagram
r = chamar('GET', 'me/permissions', {})
ok = sorted(p['permission'] for p in r['data'] if p['status'] == 'granted')
nao = sorted(p['permission'] for p in r['data'] if p['status'] != 'granted')
print('Permissões concedidas:', ', '.join(ok)); print('Negadas/pendentes:', ', '.join(nao) or '-')
precisa = {'instagram_content_publish': 'postar', 'instagram_manage_insights': 'métricas (aprendizado)', 'instagram_manage_comments': 'ler/responder comentários XIXI', 'pages_messaging': 'mandar o teste no direct', 'pages_show_list': 'achar a página', 'pages_read_engagement': 'ler a página'}
for p, para in precisa.items():
    print(('✅' if p in ok else '❌'), p, '→', para)
ig = conta_instagram()
print('Limite de publicação:', chamar('GET', f'{ig}/content_publishing_limit', {'fields': 'quota_usage,config'}))
