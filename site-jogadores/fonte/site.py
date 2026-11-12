# Gera as páginas do site dos jogadores (../docs/) a partir de paginas/ e de posicoes.json.
# Uso: python -I site.py        (sem argumentos; os caminhos são relativos a esta pasta)
# SÓ material para jogadores: nada de segredos aqui.
# estilo.css, site.js e img/ ficam em ../docs/ e não são gerados aqui.
import sys, os, json, re, html
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "paginas")
pos_json = os.path.join(HERE, "posicoes.json")
guia_html = os.path.join(SRC, "guia-personagem.html")
OUT = os.path.normpath(os.path.join(HERE, "..", "docs"))

MENU = [("index.html", "Início"), ("mapa.html", "Mapa"), ("regras.html", "Regras"),
        ("personagem.html", "Personagem"), ("lendas.html", "Lendas"), ("mesa.html", "À mesa")]

def page(fname, title, desc, body, wide=False):
    cur = ' aria-current="page"'
    nav = "".join('<li><a href="%s"%s>%s</a></li>' % (h, cur if h == fname else "", t) for h, t in MENU)
    full_title = "Ducado de Portucale" if fname == "index.html" else f"{title} · Ducado de Portucale"
    return f"""<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Uncial+Antiqua&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Alegreya+Sans+SC:wght@500;700&display=swap">
<link rel="stylesheet" href="estilo.css">
</head>
<body>
<header class="site-header">
  <div class="inner">
    <a class="brand" href="index.html">Ducado de Portucale</a>
    <nav class="site-nav" aria-label="Menu principal"><ul>{nav}</ul></nav>
  </div>
</header>
<main class="wrap{' wide' if wide else ''}">
{body}
</main>
<footer class="site-footer">
  <div class="inner">
    <p>Ducado de Portucale: uma campanha Daggerheart™ Compatible para a nossa mesa. Não é um produto oficial da Darrington Press nem da Critical Role.</p>
    <p><strong>Copyright/Attribution:</strong> This product includes materials from the Daggerheart System Reference Document 2.0, © Critical Role, LLC. under the terms of the Darrington Press Community Gaming (DPCGL) License. More information can be found at <a href="https://www.daggerheart.com">https://www.daggerheart.com</a>. There are no previous modifications by others.</p>
    <p>O SRD 2.0 está em <a href="https://www.daggerheart.com/srd">daggerheart.com/srd</a> e é licenciado nos termos da <a href="https://darringtonpress.com/license">Darrington Press Community Gaming License</a>. As regras foram resumidas e traduzidas para português por nós.</p>
  </div>
</footer>
<script src="site.js" defer></script>
</body>
</html>
"""

def read(n):
    return open(os.path.join(SRC, n), encoding="utf-8").read()

# ---------- lugares (texto para jogadores) ----------
CAT = {"cidade": ("Cidades", "Cidade"), "vila": ("Vilas", "Vila"), "aldeia": ("Aldeias", "Aldeia"), "outro": ("Outros lugares", "Castelo, mosteiro ou ruína")}
L = {
 "Portucale": ("Porto", "A capital do Ducado e o porto que lhe deu o nome, na foz do Douro, com um burgo em cada margem. Marinheiros, mercadores, pescadores e almocreves que sobem o rio. Manda a gente do Grande Duque. Normandos na costa, ondinas no Douro e barcos que não voltam."),
 "Braga": ("Braga", "A velha Bracara Augusta romana, cidade do bispo Gundisalvo e a mais eclesiástica do Ducado. Clérigos, peregrinos a caminho de Santiago e ladrões de relíquias. Na Fonte do Ídolo, um santuário antigo escavado na rocha, ainda há quem deixe oferendas."),
 "Lamego": ("Lamego", "Cidade do bispo Ornato, a sul do Douro, entre vinhas e a serra de Montemuro. Almocreves do rio, contrabandistas e viajantes vindos de Viseu. Diz-se que há mouras nos penedos sobre o Douro."),
 "Viseu": ("Viseu", "Cidade do interior, perto da fronteira, que sofre com os raides. Governa-a Ufo Ufes, velho e farto. A filha, Santa Senhorinha, faz milagres; o filho, Gervásio, anda a monte. Perto fica a Cava de Viriato, um enorme recinto de terra que se diz do herói lusitano."),
 "Eminio": ("Coimbra", "A cidade do Mondego, sede do Condado de Coimbra e do conde Mônio Guterres. É a última grande cidade antes da fronteira sul: moçárabes, mercadores de Córdoba e espiões dos dois lados."),
 "Chaves": ("Chaves", "A romana Aquae Flaviae, com a sua ponte e as termas, no limite nordeste do Ducado. Daqui partem e aqui chegam os raides da Galiza e de Leão."),
 "Vimaranes": ("Guimarães", "A corte da Duquesa Mumadona, que manda construir um mosteiro no vale do Ave. Canteiros, nobres a pedir audiência, e no monte por cima da vila um castro com a Fonte da Moura."),
 "Maia": ("Maia", "Terra senhorial a norte de Portucale, de Lovesendo Ramires, que se prepara para casar com Zayra, prima do Califa. Há gente de Córdoba na Maia, e quem não queira o casamento."),
 "Vieira do Minho": ("Vieira do Minho", "Terra de serra entre o Gerês e a Cabreira, onde Ufo Ufes é capitão-general. Pastores e caçadores, lobos e peeiras, olharapos nas penedias e corredores do fado nas noites de lua."),
 "Terra de Santa Maria": ("Santa Maria da Feira", "Terras entre o Douro e o Vouga, com um castelo que guarda a estrada para sul, governadas por Gonçalo Moniz, filho do conde de Eminio. Salteadores na estrada de Portucale a Eminio e soldados de passagem."),
 "Anégia": ("perto de Penafiel", "Sede de território junto ao Tâmega. Os senhores locais andam em guerra uns com os outros, e há salteadores no rio."),
 "Seia": ("Seia", "Sede de território na Serra da Estrela, no limite do domínio cristão. Lobos, frio e olharapos; um castelo de fronteira."),
 "Montemor-o-Velho": ("Montemor-o-Velho", "Castelo sobre o Mondego, tomado aos mouros há cerca de um século. Conta-se que mortos sem cabeça guardam as muralhas."),
 "Trancoso": ("Trancoso", "Um dos castelos da família da Duquesa na fronteira leste, com uma torre moçárabe."),
 "Cale": ("Vila Nova de Gaia", "O burgo antigo na margem sul do Douro, em frente a Portucale. Contrabando entre as duas margens e normandos que sobem o rio."),
 "Quinta de Azevedo": ("perto de Baião", "Senhorio de Ero Baião, vassalo de Portucale, junto ao Douro."),
 "Lourosa": ("Oliveira do Hospital", "Aldeia com uma igreja moçárabe que tem a data de 912 gravada numa pedra sobre a porta. Moçárabes da fronteira e pastores da Estrela."),
 "S. Pedro do Sul": ("S. Pedro do Sul", "Aldeia moçárabe com termas romanas, nas terras de Lafões."),
 "Soure": ("Soure", "Aldeia moçárabe a sul do Mondego: a fronteira mais exposta, quase terra de ninguém."),
 "Dume": ("Dume, junto a Braga", "Mosteiro antigo fundado por S. Martinho de Dume e sede do bispo Rosendo, famoso por libertar escravos. Monges, libertos, pobres e doentes."),
 "Citânia de Briteiros": ("Guimarães", "Um grande castro antigo perto de Vimaranes, cheio de pedras gravadas e de histórias de mouras."),
 "Cête": ("Paredes", "Mosteiro de S. Pedro, a leste de Portucale. Há monges aqui pelo menos desde 924."),
 "Arouca": ("Arouca", "Mosteiro aos pés da serra da Freita, terra de lobos e das \"pedras parideiras\", penedos que largam pedras como quem dá à luz."),
 "Lorvão": ("Penacova", "Mosteiro nas serras junto a Coimbra. Diz-se que um abade de Lorvão ajudou a tomar Montemor aos mouros, e que os monges ainda sabem pegar em armas."),
 "Vacariça": ("Mealhada", "Mosteiro com abades desde o início do século, nos caminhos da Bairrada. Ladrões de relíquias rondam por perto."),
 "Conímbriga": ("Condeixa", "As ruínas de uma grande cidade romana, perto de Eminio. Muralhas, termas e canos antigos."),
 "Moreira de Rei": ("Moreira de Rei", "Castelo da fronteira leste, com uma necrópole de sepulturas escavadas na rocha."),
 "Penedono": ("Penedono", "Castelo da fronteira leste, no alto de um penedo."),
 "Sernancelhe": ("Sernancelhe", "Castelo da fronteira leste, com restos de construções mais antigas."),
 "Longroiva": ("Longroiva", "Castelo da fronteira leste, entre o Douro e o Côa."),
 "Numão": ("Numão", "Castelo da fronteira leste, perto do Douro."),
 "Souto dos Magos": ("Penha (Guimarães)", "Um souto de castanheiros na serra a leste de Vimaranes, perto da Penha. Ali vivem os magos de Vimara, o Ruivo."),
 "Alavário": ("Aveiro", "Aldeia de salineiros e pescadores na margem da laguna, junto à foz do Vouga. As salinas são da Duquesa Mumadona. Daqui para sul, pelas dunas, vive a gente das salinas; nas rochas da barra há hirãs, e nas noites de maré viva os afogados saem da água."),
 "Casconha": ("Vale do Alva, perto de Arganil", "Senhorio de fronteira no vale do Alva, a leste de Eminio, vassalo do conde. Mandam Egas Moniz e a mulher, Doria, fartos dos raides que vêm do sul."),
}

DIST = [
    ('Portucale → Maia', 12, 'meio dia', 'estrada romana'),
    ('Portucale → Terra de Santa Maria', 30, '1 dia', 'estrada romana'),
    ('Portucale → Braga', 55, '2 dias', 'estrada romana'),
    ('Portucale → Vimaranes', 55, '2 dias', 'caminho'),
    ('Braga → Vimaranes', 25, '1 dia', 'caminho'),
    ('Braga → Vieira do Minho', 35, '1–2 dias', 'estrada romana, pela serra'),
    ('Braga → Chaves', 85, '3–4 dias', 'estrada romana, pela serra'),
    ('Portucale → Lamego', 100, '4 dias', 'caminho, ao longo do Douro'),
    ('Lamego → Viseu', 65, '2–3 dias', 'caminho incerto, pela serra'),
    ('Viseu → Eminio', 90, '3–4 dias', 'caminho incerto, pela fronteira'),
    ('Portucale → Eminio', 120, '5 dias', 'estrada romana'),
    ('Vimaranes → Souto dos Magos', 10, 'meio dia', 'caminho de serra'),
    ('Eminio → Casconha', 40, '1½–2 dias', 'caminho, pelo Mondego e pelo Alva'),
    ('Terra de Santa Maria → Alavário', 40, '1½–2 dias', 'caminho, pela laguna'),
]


def slug(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

pos = json.load(open(pos_json, encoding="utf-8"))
places = pos["lugares"]
missing = [p["nome"] for p in places if p["nome"] not in L]
assert not missing, missing


def vizinhos(nome):
    out = []
    for a, k, d, c in DIST:
        x, y = [t.strip() for t in a.split("→")]
        if nome in (x, y):
            out.append(f"{y if nome == x else x}: {d} ({c})")
    if not out:
        return ""
    return "        <p class=\"dist\"><span>Distâncias</span>" + " · ".join(html.escape(o) for o in out) + "</p>" + chr(10)

pins = []
for p in places:
    sid = "lugar-" + slug(p["nome"])
    pins.append(f'<button class="pin" type="button" data-lugar="{sid}" data-cat="{p["cat"]}" style="left:{p["x"]}%;top:{p["y"]}%" aria-label="{html.escape(p["nome"])}"></button>')

groups = []
for cat in ["cidade", "vila", "aldeia", "outro"]:
    cards = []
    for p in places:
        if p["cat"] != cat:
            continue
        hoje, txt = L[p["nome"]]
        sid = "lugar-" + slug(p["nome"])
        nome = "Eminio (Coimbra)" if p["nome"] == "Eminio" else p["nome"]
        cards.append(f'''      <article class="card place" id="{sid}" data-cat="{cat}">
        <div class="card-top"><strong>{html.escape(nome)}</strong><span class="chip">{CAT[cat][1]}</span></div>
        <p class="today">Hoje: {html.escape(hoje)}</p>
        <p>{html.escape(txt)}</p>
{vizinhos(p["nome"])}        <p><a href="#mapa" class="ver-no-mapa" data-lugar="{sid}">Ver no mapa</a></p>
      </article>''')
    groups.append(f'''    <h3>{CAT[cat][0]}</h3>
    <div class="place-list">
{chr(10).join(cards)}
    </div>''')

dist_rows = chr(10).join(f'          <tr><td>{a}</td><td class="num">{k}</td><td>{d}</td><td>{c}</td></tr>' for a, k, d, c in DIST)

mapa_body = f'''  <header class="page-head">
    <p class="eyebrow">O condado em 950 · do Lima ao Mondego</p>
    <h1>O mapa do Ducado</h1>
    <p class="lead">Toca num lugar do mapa para ler o que se sabe dele. As localizações são aproximadas.</p>
    <nav class="steps plain-links" aria-label="Nesta página">
      <a href="#mapa">Mapa</a><a href="#lugares">Lugares</a><a href="#distancias">Distâncias</a><a href="#fora">Fora do Ducado</a>
    </nav>
  </header>

  <section id="mapa">
    <div class="filters" role="group" aria-label="Mostrar no mapa">
      <button type="button" class="filter" data-filtro="todos" aria-pressed="true">Todos</button>
      <button type="button" class="filter" data-filtro="cidade" aria-pressed="false">Cidades</button>
      <button type="button" class="filter" data-filtro="vila" aria-pressed="false">Vilas</button>
      <button type="button" class="filter" data-filtro="aldeia" aria-pressed="false">Aldeias</button>
      <button type="button" class="filter" data-filtro="outro" aria-pressed="false">Castelos, mosteiros e ruínas</button>
    </div>
    <figure class="map-figure">
      <div class="map">
        <img src="img/mapa-ducado.png" width="{pos["largura"]}" height="{pos["altura"]}" alt="Mapa do Ducado de Portucale por volta de 950, do rio Lima ao Mondego, com as cidades, vilas, aldeias, castelos e mosteiros.">
        {"".join(pins)}
      </div>
      <figcaption class="legend"><span>■ Cidade</span><span>● Vila</span><span>• Aldeia</span><span>▲ Castelo, mosteiro ou ruína</span><span>– – Estrada romana</span><span>· · Caminho incerto</span><span>Portucale é a capital</span></figcaption>
    </figure>
    <div class="box place-panel" id="painel" aria-live="polite" hidden></div>
  </section>

  <section id="lugares">
    <h2 class="section-head">Lugares</h2>
{chr(10).join(groups)}
  </section>

  <section id="distancias">
    <h2 class="section-head">Distâncias</h2>
    <p>A pé fazem-se cerca de 25 km por dia; a cavalo, 40 a 50. Valores aproximados, só para orientar. As estradas romanas (tracejado no mapa) são o caminho mais seguro.</p>
    <div class="table-scroll">
      <table class="compact">
        <thead><tr><th>De → para</th><th class="num">~km</th><th>A pé</th><th>Caminho</th></tr></thead>
        <tbody>
{dist_rows}
        </tbody>
      </table>
    </div>
  </section>

  <section id="fora">
    <h2 class="section-head">Fora do Ducado (mas importa)</h2>
    <div class="table-scroll">
      <table class="compact">
        <thead><tr><th>Lugar</th><th>Porquê</th></tr></thead>
        <tbody>
          <tr><td>Santiago de Compostela</td><td>Destino dos peregrinos que atravessam o Ducado</td></tr>
          <tr><td>Celanova</td><td>Mosteiro na Galiza, ligado ao bispo Rosendo</td></tr>
          <tr><td>Tui</td><td>Bispado logo a norte do Minho</td></tr>
          <tr><td>León</td><td>A corte do rei Ramiro II e de Ordonho III</td></tr>
          <tr><td>Salamanca</td><td>Onde se estuda</td></tr>
          <tr><td>Córdoba</td><td>Capital do Califado; a melhor escola da Península</td></tr>
          <tr><td>Tortosa</td><td>Terra da Ordem da Machadinha</td></tr>
        </tbody>
      </table>
    </div>
  </section>'''

# ---------- personagem: o corpo do guia publicado ----------
g = open(guia_html, encoding="utf-8").read()
body = g[g.index('<div class="wrap">') + len('<div class="wrap">'): g.index("<footer>")].rstrip()
body = body.replace("<header>", '<header class="page-head">', 1).replace('<div class="diffs">', '<div class="box diffs">')

pages = [
    ("index.html", "Início", "Campanha Daggerheart™ Compatible no Portugal lendário do ano 950: o pitch, o mundo e as regras da mesa.", read("index.body.html"), False),
    ("mapa.html", "Mapa", "Mapa clicável do Ducado de Portucale por volta de 950, com os lugares e as distâncias.", mapa_body, True),
    ("regras.html", "Regras", "Resumo das regras do SRD 2.0 (Daggerheart™ Compatible) para os jogadores do Ducado de Portucale.", read("regras.body.html"), False),
    ("personagem.html", "Personagem", "Guia para criar personagens no Ducado de Portucale (Daggerheart™ Compatible).", body, False),
    ("lendas.html", "Lendas", "O que o povo do Ducado conta sobre as criaturas das lendas.", read("lendas.body.html"), False),
    ("mesa.html", "À mesa", "Princípios de jogador, notas de mesa, sessão zero e segurança.", read("mesa.body.html"), False),
]
os.makedirs(OUT, exist_ok=True)
for fname, title, desc, b, wide in pages:
    open(os.path.join(OUT, fname), "w", encoding="utf-8", newline="\n").write(page(fname, title, desc, b, wide))
    print("escrito", fname)
