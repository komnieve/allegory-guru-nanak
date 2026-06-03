#!/usr/bin/env python3
"""Build the public Allegory page (index.html) from the markdown in ./data.
Usage:  python3 build.py   (writes ./index.html)
A study companion to Amardeep Singh & Vininder Kaur's Allegory docuseries."""
import re, html, os, json, math

BASE    = os.environ.get("ALLEGORY_BASE", ".")
DATA    = os.environ.get("ALLEGORY_DATA", f"{BASE}/data")
OUTDIR  = os.environ.get("ALLEGORY_OUT", BASE)
GEOJSON = os.environ.get("ALLEGORY_GEO", f"{DATA}/countries.geo.json")
PUBLIC  = True
SCRIPTS = f"{DATA}/allegory-english-scripts.md"
YT      = f"{DATA}/allegory-english-youtube-transcripts.md"
OUT     = f"{OUTDIR}/{'index.html' if PUBLIC else 'amardeep-singh-overview.html'}"

def esc(s): return html.escape(s, quote=False)

# episode -> (youtube_id, duration_seconds, translit, english)
META = {
 1 :("5qt5uIkKUgY",2623,"Noor-e-Tawheed","Light of Oneness"),
 2 :("8SBC42GzrI8",2551,"Shafaf Khayal","Clear Thought"),
 3 :("Q0nvITWhqlc",2461,"Ruhani Rawangi","Spiritual Departure"),
 4 :("e-0Hry-nlks",2235,"Paschimi Surya Uday","Sunrise in the West"),
 5 :("p5cE1ELzre0",2294,"Tatvagyan","Essence of Knowledge"),
 6 :("tvs__M8AshQ",2131,"Paheli","Veiled Message"),
 7 :("xJ1mjrqnZ-A",2048,"Agochar","Seeing the Unseen"),
 8 :("jq1n7eVbnV4",1952,"Adhikaar","Entitlement"),
 9 :("NOANKetZ4Xw",2575,"Sampajanna","Clear Comprehension"),
 10:("2kzpICVxghs",2890,"Gabhira","Depth"),
 11:("NyfEwb8ecFU",2340,"Aham Tvam","I am You"),
 12:("XRa8puUqJQs",1951,"Shrishti","Cosmos"),
 13:("Y_eWBIeGXXE",2194,"Villipunarvn","Call for Awareness"),
 14:("ZrpLHpSztRU",2978,"Setu Bandh","Bridge of Transition"),
 15:("Us1RQqWAvuo",2819,"Sudh Uddesham","Seed of Intent"),
 16:("nuvzoliv0qM",3073,"Gyan Bohit","Boat of Wisdom"),
 17:("1JLfr50OvVE",3331,"Parvaas","Sojourn"),
 18:("D6XybTtvuKo",4030,"Sumeru","Consciousness"),
 19:("AcREtYemdWk",2809,"Nimrit Prabhav","Impression of Humility"),
 20:("CpJOiAgIW78",3693,"Rangeen Guldasta","Colourful Bouquet"),
 21:("LbzSbaxNSTw",2996,"Wahdat-al-Wajud","Unity of Existence"),
 22:("fatBiRe_TTc",4037,"Lihaaze Insaniyat","Respect for Humanity"),
 23:("bsOqrpnzXNQ",2807,"Guru Chela","Mentor and Seeker"),
 24:("0u99WSuTj54",3383,"Baam-e-Nanak","Light of Nanak"),
}
STARRED = {11,18,21}
SYNOPSIS = {
 1:"Guru Nanak's birth at Nankana Sahib and the tender years of the gentle valiant who ignited the spirit of Oneness.",
 2:"His youthful years and the clarity of unity within diversity.",
 3:"The onset of the first odyssey to spread Tawheed — Oneness.",
 4:"Evoking rationality, “to awaken the mind from the slumber of ignorance.”",
 5:"Dialogues with the ascetics at Gorakhmatta.",
 6:"Inducing critical thinking through exemplary, riddle-like cues.",
 7:"At the confluence of seen and unseen waters — the invisible flow within.",
 8:"Along the Ganga, raising his voice against inequalities.",
 9:"Addressing the agnostics in Magadh.",
 10:"In Dhakeshwari, Bangladesh — foresight for impactful action.",
 11:"“Seeing no strangers, Guru Nanak befriends the Nagas” (Assam / Northeast). The cleanest encapsulation of the non-othering ethic.",
 12:"Composing a cosmic anthem at Utkal (Puri).",
 13:"In the Tamil land of the five-element temples (Panch Bhoota Sthalam).",
 14:"Metaphoric expositions for a transition from negativity to positivity (Rameswaram / the Sri Lanka crossing).",
 15:"In Malabar — the magnanimity of sharing with pure intentions.",
 16:"Paradigms for dealing with unfavourable situations, set on a sea voyage.",
 17:"The altruistic traveller returns to his native land of five rivers after twelve years.",
 18:"The longest episode. On the roof of the world (Mount Kailash / Sumeru) — the debate with the Siddhas, engaged life over ascetic retreat.",
 19:"Philosophical words at Taxila.",
 20:"Along the banks of the Sindhu, infusing harmony.",
 21:"The Sufi doctrine of Wahdat-al-Wajud — the Oneness of Being — in the Islamic world. The most explicit cross-tradition non-dual episode.",
 22:"At Khorasan, Guru Nanak spreads the scent of humanity (Iran / Afghanistan).",
 23:"Guru Nanak and Mardana, the Muslim rabab-player who accompanied him everywhere.",
 24:"Rooted in the spirit of benevolence for all — the close.",
}

# --------- journey map: episode -> (lat, lon, place) + geo projection ---------
EPLOC = {
 1:(31.60,73.45,"Nankana Sahib — his birth"),
 2:(30.75,75.65,"Sultanpur Lodhi — the youthful years"),
 3:(29.95,78.16,"Haridwar — the first odyssey begins"),
 4:(28.90,77.20,"the northern plains"),
 5:(26.76,83.37,"Gorakhmatta — the ascetics"),
 6:(26.40,84.60,"the eastern plains"),
 7:(25.43,81.85,"Prayag — the confluence of waters"),
 8:(25.32,83.01,"Banaras — along the Ganga"),
 9:(24.79,85.00,"Magadh — the agnostics"),
 10:(23.72,90.41,"Dhaka — Dhakeshwari"),
 11:(26.18,91.75,"Assam — befriending the Nagas"),
 12:(19.81,85.83,"Puri (Utkal) — the cosmic anthem"),
 13:(10.96,79.38,"the Tamil temple land"),
 14:(9.10,79.80,"Rameswaram → the Sri Lanka crossing"),
 15:(11.25,75.78,"Malabar"),
 16:(12.50,71.50,"the Arabian Sea — the boat of wisdom"),
 17:(31.50,75.00,"the return home, after twelve years"),
 18:(31.07,81.31,"Mount Kailash / Sumeru — the Siddhas"),
 19:(33.74,72.82,"Taxila"),
 20:(27.70,68.85,"the banks of the Sindhu (Indus)"),
 21:(21.42,39.83,"Mecca — the Unity of Being"),
 22:(35.00,61.00,"Khorasan — the scent of humanity"),
 23:(33.31,44.36,"Baghdad — Nanak and Mardana"),
 24:(32.06,75.00,"Kartarpur — the close"),
}
JOURNEY_COUNTRIES={"Pakistan","India","Bangladesh","Afghanistan","Iran","Iraq","Saudi Arabia","China","Sri Lanka"}
CONTEXT_COUNTRIES={"Nepal","Bhutan","Myanmar","Oman","Yemen","United Arab Emirates","Syria","Jordan",
 "Turkey","Turkmenistan","Uzbekistan","Tajikistan","Kuwait","Egypt","Kazakhstan","Mongolia","Thailand"}
CLABELS=[("IRAN",32.0,54.5),("SAUDI ARABIA",23.8,44.0),("IRAQ",32.6,43.2),("AFGHANISTAN",34.4,66.2),
 ("PAKISTAN",27.6,66.6),("INDIA",22.5,79.0),("TIBET",32.8,87.0),("BANGLADESH",24.2,90.7),("SRI LANKA",7.2,80.8)]
GEO_LON0,GEO_LON1,GEO_LAT0,GEO_LAT1 = 37.0,96.0,5.0,39.0
MAP_W=1120.0; SCALE=MAP_W/(GEO_LON1-GEO_LON0); MAP_H=(GEO_LAT1-GEO_LAT0)*SCALE
def prj(lon,lat): return ((lon-GEO_LON0)*SCALE, (GEO_LAT1-lat)*SCALE)
def _ring(r): return "M"+"L".join(f"{prj(lo,la)[0]:.1f},{prj(lo,la)[1]:.1f}" for lo,la in r)+"Z"
def _geom(g):
    polys=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
    return "".join(_ring(ring) for poly in polys for ring in poly)

def map_svg():
    d=json.load(open(GEOJSON))
    land=[]
    for f in d["features"]:
        nm=f["properties"].get("name")
        if nm in JOURNEY_COUNTRIES:
            land.append(f'<path class="ctry j" d="{_geom(f["geometry"])}"><title>{esc(nm)}</title></path>')
        elif nm in CONTEXT_COUNTRIES:
            land.append(f'<path class="ctry" d="{_geom(f["geometry"])}"/>')
    labels="".join(f'<text class="clbl" x="{prj(lo,la)[0]:.0f}" y="{prj(lo,la)[1]:.0f}">{esc(t)}</text>'
                   for t,la,lo in CLABELS)
    pts=[prj(EPLOC[n][1],EPLOC[n][0]) for n in range(1,25)]
    seg=[]
    for i in range(len(pts)-1):
        (x1,y1),(x2,y2)=pts[i],pts[i+1]
        dx,dy=x2-x1,y2-y1; L=math.hypot(dx,dy) or 1; off=0.16*L
        cx,cy=(x1+x2)/2-dy/L*off,(y1+y2)/2+dx/L*off
        seg.append(f"M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}")
    pins=[]
    for n in range(1,25):
        x,y=pts[n-1]; tr=META[n][2]; place=EPLOC[n][2]
        cls="pin star" if n in STARRED else "pin"
        pins.append(f'<g class="{cls}" data-ep="{n}" transform="translate({x:.1f},{y:.1f})" tabindex="0" '
                    f'role="button" aria-label="Episode {n}: {esc(tr)}, {esc(place)}" '
                    f'data-title="{n}. {esc(tr)}" data-place="{esc(place)}">'
                    f'<circle class="pin-c" r="13"/><text class="pin-t" dy="4.6">{n}</text></g>')
    return (f'<svg class="jmap" viewBox="0 0 {MAP_W:.0f} {MAP_H:.0f}" preserveAspectRatio="xMidYMid meet" '
            f'role="img" aria-label="Map of Guru Nanak’s travels across nine countries, with all 24 episode locations">'
            f'<defs><radialGradient id="seaG" cx="48%" cy="38%" r="80%">'
            f'<stop offset="0%" stop-color="#dde4e7"/><stop offset="100%" stop-color="#cdd7da"/></radialGradient></defs>'
            f'<rect class="sea" width="{MAP_W:.0f}" height="{MAP_H:.0f}" fill="url(#seaG)"/>'
            f'<g class="land">{"".join(land)}</g>{labels}'
            f'<path class="route" d="{" ".join(seg)}"/><g class="pins">{"".join(pins)}</g></svg>')

def mmss(s): s=int(s); return f"{s//60}:{s%60:02d}"
def hms_to_sec(t):
    p=[int(x) for x in t.split(':')]
    while len(p)<3: p=[0]+p
    return p[0]*3600+p[1]*60+p[2]

# ----------------------- parse the two markdown docs --------------------------
def parse_scripts():
    eps={}; cur=None; buf=[]
    for line in open(SCRIPTS,encoding='utf-8'):
        line=line.rstrip('\n')
        m=re.match(r'^## Episode (\d+):', line)
        if m:
            if cur is not None: eps[cur]='\n'.join(buf).strip()
            cur=int(m.group(1)); buf=[]; continue
        if cur is None: continue
        if line.strip()=='---' or line.startswith('<a id') or re.match(r'^\*Runtime',line):
            continue
        buf.append(line)
    if cur is not None: eps[cur]='\n'.join(buf).strip()
    return eps

def parse_yt():
    yt={}; cur=None; cues=[]
    for line in open(YT,encoding='utf-8'):
        m=re.match(r'^## Episode (\d+):', line)
        if m:
            if cur is not None: yt[cur]=cues
            cur=int(m.group(1)); cues=[]; continue
        if cur is None: continue
        mm=re.match(r'^\*\*\[([0-9:]+)\]\*\*\s*(.*)$', line.rstrip('\n'))
        if mm: cues.append((mm.group(1), mm.group(2)))
    if cur is not None: yt[cur]=cues
    return yt

CITE_KEYS=('Raag','Guru Nanak','Farid','Kabir','Ravidas','Mardana','Moolmantar',
           'Mool Mantar','Jap','Slok','Var','Trilochan','Bhagat','Sri Raag','Pauri','Japji')
def render_verse_line(text):
    cite=''; body=text
    m=re.search(r'\(([^()]*)\)\s*$', text)
    if m and any(k in m.group(1) for k in CITE_KEYS):
        cite=m.group(1); body=text[:m.start()].strip()
    cls='vt' if '||' in body else 'vtr'
    out=f'<p class="{cls}">{esc(body)}</p>'
    if cite: out+=f'<cite>{esc(cite)}</cite>'
    return out

SPEAKER=re.compile(r"^((?:Dr\.|Prof\.|Mr\.|Mrs\.|Ms\.|Mahant|Bhai|Baba|Giani|Sant|Granthi|Pandit|Maulvi|Sardar)?\s?"
                   r"[A-Z][\w’'.\-]+(?:\s+[A-Z][\w’'.\-]+){0,4}):\s+(.+)$")
def render_para(b):
    m=SPEAKER.match(b)
    if m:
        name=m.group(1).strip()
        if (' ' in name) or name.endswith('.'):
            return f'<p><span class="spk">{esc(name)}</span> {esc(m.group(2))}</p>'
    return f'<p>{esc(b)}</p>'

def render_script_body(body):
    blocks=[b.strip() for b in re.split(r'\n\s*\n', body) if b.strip()]
    out=[]; in_pointers=False; vrun=[]
    def flush():
        if vrun:
            out.append('<div class="verse">'+''.join(vrun)+'</div>'); vrun.clear()
    for b in blocks:
        if b.startswith('> '):
            vrun.append(render_verse_line(b[2:].strip())); continue
        flush()
        if b.startswith('#### '):
            if in_pointers: out.append('</div>')
            in_pointers=True
            out.append('<div class="pointers"><div class="pointers-tag">For the conversation</div>'
                       f'<h4 class="pointers-h">{esc(b[5:])}</h4>'); continue
        if b.startswith('##### '):
            out.append(f'<h5 class="subh">{esc(b[6:])}</h5>'); continue
        out.append(render_para(b))
    flush()
    if in_pointers: out.append('</div>')
    return '\n'.join(out)

def render_transcript(cues, vid):
    rows=[]
    for ts,text in cues:
        sec=hms_to_sec(ts)
        url=f"https://www.youtube.com/watch?v={vid}&t={sec}s"
        rows.append(f'<p class="cue"><a class="ts" href="{url}" target="_blank" rel="noopener">{ts}</a>'
                    f'<span>{esc(text)}</span></p>')
    return '\n'.join(rows)

def build_episodes(scripts, yt):
    cards=[]
    for n in range(1,25):
        vid,dur,tr,en=META[n]
        star = '<span class="star" title="Richest for the conversation">✦</span>' if n in STARRED else ''
        watch=f"https://www.youtube.com/watch?v={vid}"
        pdf=f"https://thegurunanak.com/wp-content/uploads/2025/12/Episode-{n}.pdf"
        script_html=render_script_body(scripts.get(n,''))
        trans_html=render_transcript(yt.get(n,[]), vid)
        cards.append(f'''
<details class="ep" id="ep-{n}" data-ep="{n}">
  <summary>
    <span class="ep-num">{n:02d}</span>
    <span class="ep-titles">
      <span class="ep-tr">{esc(tr)} {star}</span>
      <span class="ep-en">{esc(en)}</span>
      <span class="ep-syn">{esc(SYNOPSIS[n])}</span>
    </span>
    <span class="ep-meta"><span class="ep-dur">{mmss(dur)}</span><span class="chev">›</span></span>
  </summary>
  <div class="ep-body">
    <div class="ep-toolbar">
      <div class="tabs" role="tablist">
        <button class="tab on" data-tab="script" onclick="setTab(this,{n},'script')">Verbatim script</button>
        <button class="tab" data-tab="transcript" onclick="setTab(this,{n},'transcript')">Video transcript</button>
      </div>
      <div class="ep-links">
        <a href="{watch}" target="_blank" rel="noopener">▶ Watch</a>
        <a href="{pdf}" target="_blank" rel="noopener">↓ Script PDF</a>
      </div>
    </div>
    <div class="panel panel-script" data-panel="script">{script_html}</div>
    <div class="panel panel-transcript hidden" data-panel="transcript">
      <p class="trans-note">YouTube captions — spoken narration only (no speaker labels or on-screen verses). Click a timestamp to open the video at that point.</p>
      {trans_html}
    </div>
  </div>
</details>''')
    return '\n'.join(cards)

# ------------------------------ static content --------------------------------
THEMES=[
 ("Oneness beneath identity",
  "Identity — national, religious, caste — is a construct that hides an underlying Oneness, and the whole job is to dissolve the construct. Amardeep insists this is “not just about Guru Nanak’s philosophy on Sikhism, but humanity.”",
  "Guru Nanak was an embodiment of Oneness."),
 ("Allegory over literalism",
  "The travels and the Janam Sakhi miracle-stories are read as metaphor, not literal history. He strips the later myths that “overshadow his core philosophy” and treats each place as the carrier of a teaching, not a pin on a verified map.",
  "Allegory is a revelation of a hidden meaning within a narrative."),
 ("The unseen, all-pervading awareness",
  "His signature interpretive move: he translates every name of God — Raam, Khuda, Allah, Lord — the same way, as “the unseen, all-pervading awareness.” That single editorial choice is the whole worldview in four words. It is a metaphysics, not a translation.",
  "Experience the entirety of creation as One comprehensive phenomenon."),
 ("The dissolution of otherness",
  "He re-reads nirbhau not as “without fear of God” but as the fearlessness that comes from recognising the one awareness in all; and nirvair not as “without enmity” but as the entity that “sees no stranger.” Devotion becomes non-othering.",
  "This entity sees no stranger."),
 ("Release, not relic",
  "He went to the Muzaffarabad bridge intending to carry home a sealed bottle of grave-soil, and chose to leave it. A man turning toward inherited trauma rather than away — closure, not grievance.",
  "The closure I had been seeking happened with the acceptance that things have changed and I need to move on."),
 ("Heritage beyond religion",
  "His refrain: heritage has been wrongly “reduced to a realm of religion.” The deeper recovery is of a trans-religious, pan-Punjabi shared culture that 1947 fractured — a Sufi’s verses sitting inside the Sikh scripture, recited daily.",
  "Guru Nanak’s narrative of coexistence is to put humanity first and to not get divided by faith."),
]

TIMELINE=[
 ("1966","Born in Gorakhpur to a goldsmith father. The family came from Muzaffarabad, Kashmir; his father had left for Gorakhpur in 1945 to set up a jewellery business — which is why this branch survived."),
 ("Oct 1947","Pashtun tribal militias sweep the Muzaffarabad valley. Over 300 Sikh men are shot at the Ranbir Singh / Dumel bridge — among them his relatives, and his wife Vininder Kaur’s grandparents."),
 ("School → career","Doon School, Electronics Engineering at Manipal, then an MBA from the University of Chicago. Twenty-five years in financial services — twenty-one at American Express, rising to Head of Revenue Management, Asia Pacific. India → Hong Kong → Singapore (2001; citizen 2005)."),
 ("2013","Resigns following what he calls a “spiritual calling.”"),
 ("Dec 2014","A single ~30-day pilgrimage to Pakistan to see his ancestral ground. On 26 December the thought of a book first occurs. At the bridge, he leaves the bottle of soil."),
 ("2016 & 2017","Publishes the two Lost Heritage books, documenting ~126–132 Sikh sites across Pakistan before they vanish."),
 ("2021–22","Releases Allegory: A Tapestry of Guru Nanak’s Travels — the 24-episode docuseries across nine countries."),
 ("2022","Wins the Guru Nanak Interfaith Prize (Hofstra University, $50,000), chosen unanimously from ~18 nominees."),
 ("2023–2027","Builds Oneness in Diversity — a multilingual audio-visual reading of ~1,656 verses by 17 spiritual mentors in the Guru Granth Sahib (Phase 2 runs to 2032)."),
 ("Ongoing","LearnWithNanak — a 12-module experiential course on Guru Nanak’s Jap. The body of work made teachable."),
]

WORKS=[
 ("Lost Heritage","Two books · 2016 & 2017",
  "Lost Heritage: The Sikh Legacy in Pakistan and The Quest Continues — visual-ethnography travelogues documenting ~126–132 abandoned and still-living Sikh sites across Pakistan before they vanish.",
  "The personal one. It begins at his own family’s wound and ends in a recovered memory of a trans-religious, pan-Punjabi shared culture that 1947 fractured."),
 ("Allegory","24-ep docuseries · 2021–22",
  "Retraces Guru Nanak’s two decades of udasis across 150+ multi-faith sites in nine countries, filmed in active conflict zones — gunfire in Afghanistan, the Iraqi desert, a boat across the Sindh.",
  "It scales the books’ move from one country to nine, and from buildings to a person. The title is the thesis: the travels are metaphor."),
 ("Oneness in Diversity","Repository · 2023–2027",
  "A multilingual audio-visual reading of ~1,656 verses by 17 mentors in the Guru Granth Sahib — Guru Nanak, Hindu Bhakti saints across caste lines, and the Sufi Sheikh Farid — each given a metaphoric interpretation plus a sung rendition in its prescribed raag.",
  "The Allegory lens turned from the biography onto the scripture itself. His complaint: existing translations “remain largely literal.”"),
 ("LearnWithNanak","Course · 12 modules",
  "An experiential course on Guru Nanak’s Jap — the pedagogical front-door to the same teaching.",
  "The body of work made teachable — a man arranging for the work to outlive the worker."),
]

QUOTES=[
 ("Allegory is a revelation of a hidden meaning within a narrative.","Allegory, Episode 1 — the series’ opening definition"),
 ("It is important to understand that Guru Nanak was an embodiment of Oneness.","Associated Press of Pakistan"),
 ("Guru Nanak’s narrative of coexistence is to put humanity first and to not get divided by faith.","Associated Press of Pakistan"),
 ("Our physical journey in the footsteps of Guru Nanak enabled us to experience the entirety of creation as One comprehensive phenomenon which can be comprehended through truthful intentions.","Hofstra Interfaith Prize statement, 2022"),
 ("The process of learning also feeds the Ego, creating a mist around our subtle faculties that perceive the world. Indeed, the more I learn, the less I know!","Essay: The More I Learn, The Less I Know"),
 ("Pursuits of life need to be spent towards creating berms around the Mind, so that its natural tendency to gravitate thoughts towards the path of least resistance of sense gratification become restricted.","Essay: Berm the Mind"),
 ("Fear arises from one’s mind trap. My passion for exploration far outweighed ambiguous thoughts.","Chronicler of a lost legacy, interview"),
 ("The closure I had been seeking in my mind happened with the acceptance that things have changed and I need to move on in life.","On leaving the grave-soil at the Muzaffarabad bridge"),
 ("Oneness is not a mere experience but an immaculate state of existence.","His Mool Mantar essence, Oneness in Diversity"),
 ("I LOST MY EVERYTHING.","Chalk graffiti he found in an abandoned gurdwara at Mangat — his most-cited found-text"),
]

THREADS=[
 ("The allegory move","Episode 1 defines allegory as “a revelation of a hidden meaning within a narrative,” and the series deliberately strips the miracles to reach the philosophy. Does reading the sites as metaphor ever thin the devotion of those who hold the stories as literally true — and how is that tension held on the ground?"),
 ("The unseen awareness","Across Nanak, Kabir, Ravidas, and the Sufi Farid alike, every name of God is translated the same way — “the unseen, all-pervading awareness.” That is less a translation than a metaphysics. Where does that reading come from?"),
 ("The Siddha debate","In Sumeru, Guru Nanak argues with the Siddhas for engaged life over ascetic retreat. After two decades of walking the udasis, where does the series land on it — is the householder’s road the harder practice?"),
 ("The bottle of soil","Amardeep travelled to the Muzaffarabad bridge intending to carry home grave-soil, and chose to leave it — calling it closure. How does one tell the difference between healthy letting-go and bypassing a real wound?"),
 ("Particular vs. universal","The message is “do not get divided by faith” — and the life’s work is the recovery of a specifically Sikh heritage. When does honouring one tradition deepen Oneness, and when does it quietly redraw the boundary it means to dissolve?"),
 ("Oneness meets emptiness","The Wahdat-al-Wajud episode sits with the Sufi “Unity of Being.” How close does that run to the Buddhist anatta — and how differently do they arrive: all is the One Being, versus no separate self to begin with?"),
 ("The ego of the chronicler","His essays say “the process of learning feeds the Ego” and “the more I learn, the less I know” — and yet the work builds a public identity, a production house, a prize. How does one keep practising that ego-restraint while the work necessarily builds a self?"),
 ("What gets handed forward","The work has moved from books to film to a scripture project to a course — each more teachable than the last. What does it most want a stranger fifty years from now to be able to do — not know, but do — because this exists?"),
]

# ----------------------------------- CSS --------------------------------------
CSS = r"""
*{box-sizing:border-box}
:root{
 --paper:#f3eada; --paper-2:#ece1c9; --card:#fbf7ec;
 --ink:#2b251c; --ink-2:#5a5140; --ink-3:#8a7e66;
 --gold:#a3761c; --gold-soft:#d4ad57; --gold-deep:#7c5810;
 --indigo:#27406a; --indigo-soft:#4d6894;
 --saffron:#b1521e;
 --line:rgba(43,37,28,.14);
 --verse-bg:#ebdfc0; --verse-rule:#bd9a44;
 --maxw:1120px; --read:760px;
}
html{scroll-behavior:smooth}
body{
 margin:0; background:var(--paper); color:var(--ink);
 font-family:'Spectral',Georgia,'Times New Roman',serif; font-weight:400;
 font-size:18px; line-height:1.72; -webkit-font-smoothing:antialiased;
 text-rendering:optimizeLegibility;
}
body::before{ /* paper grain */
 content:""; position:fixed; inset:0; z-index:0; pointer-events:none; opacity:.05;
 background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
body::after{ /* warm light from above */
 content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
 background:radial-gradient(120% 70% at 50% -10%, rgba(212,173,87,.22), transparent 60%);
}
.gu{font-family:'Noto Serif Gurmukhi','Spectral',serif}
a{color:var(--indigo); text-decoration:none}
a:hover{color:var(--gold-deep)}
.wrap{position:relative; z-index:1}

/* progress + nav */
#prog{position:fixed; top:0; left:0; height:3px; width:0; z-index:60;
 background:linear-gradient(90deg,var(--gold),var(--saffron))}
nav{position:sticky; top:0; z-index:50; backdrop-filter:blur(9px);
 background:rgba(243,234,218,.82); border-bottom:1px solid var(--line)}
nav .ninner{max-width:var(--maxw); margin:0 auto; display:flex; align-items:center;
 gap:18px; padding:11px 26px}
nav .brand{font-family:'Cormorant Garamond',serif; font-weight:700; font-size:20px;
 letter-spacing:.01em; white-space:nowrap}
nav .brand .gu{color:var(--gold-deep); margin-right:6px}
nav .links{display:flex; gap:16px; margin-left:6px; flex-wrap:wrap}
nav .links a{font-size:11.5px; letter-spacing:.16em; text-transform:uppercase;
 color:var(--ink-2); font-weight:500}
nav .links a:hover{color:var(--gold-deep)}
.search{margin-left:auto; display:flex; align-items:center; gap:8px; position:relative}
.search input{font-family:'Spectral',serif; font-size:14px; color:var(--ink);
 background:var(--card); border:1px solid var(--line); border-radius:2px;
 padding:7px 11px 7px 30px; width:210px; outline:none; transition:width .25s,border-color .2s}
.search input:focus{width:260px; border-color:var(--gold-soft)}
.search .mag{position:absolute; left:9px; top:50%; transform:translateY(-50%);
 color:var(--ink-3); font-size:13px; pointer-events:none}
.search .cnt{font-size:11px; letter-spacing:.08em; color:var(--ink-3); min-width:74px}
@media(max-width:860px){nav .links{display:none} .search input{width:150px}}

/* hero */
header.hero{position:relative; text-align:center; padding:108px 26px 70px; overflow:hidden}
header.hero .ek{position:absolute; top:46%; left:50%; transform:translate(-50%,-50%);
 font-size:min(58vw,640px); line-height:1; color:var(--gold-deep); opacity:.06; z-index:-1;
 user-select:none}
.hero .eyebrow{font-size:12.5px; letter-spacing:.42em; text-transform:uppercase;
 color:var(--saffron); font-weight:500; margin-bottom:20px}
.hero h1{font-family:'Cormorant Garamond',serif; font-weight:600; letter-spacing:.005em;
 font-size:clamp(48px,8.5vw,104px); line-height:.96; margin:0 0 6px}
.hero h1 em{font-style:italic; color:var(--gold-deep)}
.hero .who{font-family:'Cormorant Garamond',serif; font-size:clamp(20px,3vw,28px);
 color:var(--ink-2); font-weight:500; margin:8px 0 22px; letter-spacing:.02em}
.hero .lede{max-width:660px; margin:0 auto; font-size:20px; color:var(--ink-2);
 font-style:italic; line-height:1.6}
.hero .stats{display:flex; flex-wrap:wrap; justify-content:center; gap:0;
 margin:38px auto 0; max-width:780px}
.hero .stat{padding:6px 22px; border-right:1px solid var(--line)}
.hero .stat:last-child{border-right:0}
.hero .stat b{display:block; font-family:'Cormorant Garamond',serif; font-weight:600;
 font-size:30px; color:var(--gold-deep); line-height:1}
.hero .stat span{font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--ink-3)}
.hero .anim{opacity:0; transform:translateY(16px); animation:rise .9s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes rise{to{opacity:1; transform:none}}
.d1{animation-delay:.05s}.d2{animation-delay:.18s}.d3{animation-delay:.32s}
.d4{animation-delay:.46s}.d5{animation-delay:.6s}

main{max-width:var(--maxw); margin:0 auto; padding:0 26px}
section{padding:64px 0; border-top:1px solid var(--line)}
.sec-head{margin-bottom:34px}
.sec-kicker{font-size:12px; letter-spacing:.34em; text-transform:uppercase;
 color:var(--saffron); font-weight:500; margin-bottom:10px}
.sec-head h2{font-family:'Cormorant Garamond',serif; font-weight:600;
 font-size:clamp(32px,5vw,52px); line-height:1.02; margin:0; max-width:18ch}
.sec-head p{max-width:var(--read); color:var(--ink-2); margin:14px 0 0; font-size:18px}
.reveal{opacity:0; transform:translateY(22px); transition:opacity .7s ease, transform .7s ease}
.reveal.in{opacity:1; transform:none}

.lead{max-width:var(--read); font-size:20px; line-height:1.78}
.lead .dropcap{float:left; font-family:'Cormorant Garamond',serif; font-weight:700;
 font-size:84px; line-height:.72; padding:8px 12px 0 0; color:var(--gold-deep)}

/* themes */
.themes{display:grid; grid-template-columns:1fr 1fr; gap:26px}
.theme{background:var(--card); border:1px solid var(--line); border-radius:3px;
 padding:30px 30px 26px; position:relative; transition:transform .3s, box-shadow .3s}
.theme:hover{transform:translateY(-4px); box-shadow:0 18px 40px -24px rgba(43,37,28,.5)}
.theme .tn{font-family:'Cormorant Garamond',serif; font-size:19px; color:var(--gold-soft);
 font-weight:600; border:1px solid var(--gold-soft); border-radius:50%; width:38px; height:38px;
 display:flex; align-items:center; justify-content:center; margin-bottom:16px}
.theme h3{font-family:'Cormorant Garamond',serif; font-weight:600; font-size:27px;
 margin:0 0 10px; line-height:1.08}
.theme p{margin:0; color:var(--ink-2); font-size:16.5px}
.theme .pq{margin:16px 0 0; padding-left:16px; border-left:2px solid var(--verse-rule);
 font-style:italic; color:var(--ink); font-size:16px}
@media(max-width:760px){.themes{grid-template-columns:1fr}}

/* timeline */
.tl{position:relative; max-width:var(--read); margin-left:6px;
 border-left:2px solid var(--line); padding-left:30px}
.tl .ev{position:relative; padding:0 0 30px}
.tl .ev:last-child{padding-bottom:0}
.tl .ev::before{content:""; position:absolute; left:-37px; top:6px; width:11px; height:11px;
 border-radius:50%; background:var(--gold); box-shadow:0 0 0 4px var(--paper)}
.tl .yr{font-family:'Cormorant Garamond',serif; font-weight:600; font-size:21px;
 color:var(--gold-deep); margin-bottom:3px}
.tl .ev p{margin:0; color:var(--ink-2); font-size:16.5px}

/* works */
.works{display:grid; grid-template-columns:1fr 1fr; gap:24px}
.work{background:var(--card); border:1px solid var(--line); border-radius:3px; padding:28px}
.work .kick{font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:var(--ink-3)}
.work h3{font-family:'Cormorant Garamond',serif; font-weight:600; font-size:30px; margin:4px 0 12px}
.work p{margin:0 0 12px; color:var(--ink-2); font-size:16.5px}
.work .why{font-style:italic; color:var(--ink); border-top:1px solid var(--line); padding-top:12px; font-size:16px}
@media(max-width:760px){.works{grid-template-columns:1fr}}

/* quotes */
.quotes{column-count:2; column-gap:38px; max-width:var(--maxw)}
.q{break-inside:avoid; margin:0 0 30px; padding-left:20px; border-left:3px solid var(--gold-soft)}
.q blockquote{margin:0; font-family:'Cormorant Garamond',serif; font-style:italic;
 font-weight:500; font-size:25px; line-height:1.32; color:var(--ink)}
.q cite{display:block; margin-top:9px; font-style:normal; font-size:11.5px;
 letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3)}
@media(max-width:760px){.quotes{column-count:1}}

/* start-here callout */
.callout{background:linear-gradient(180deg,#26406a,#1d3354); color:#f0e9d8;
 border-radius:4px; padding:34px 36px; margin-top:8px}
.callout .tag{font-size:11px; letter-spacing:.3em; text-transform:uppercase; color:var(--gold-soft)}
.callout h3{font-family:'Cormorant Garamond',serif; font-weight:600; font-size:30px; margin:8px 0 10px; color:#fff}
.callout p{margin:0 0 16px; color:#dcd3bf; max-width:64ch}
.callout a.btn{display:inline-block; background:var(--gold-soft); color:#241a06; font-weight:600;
 padding:10px 20px; border-radius:3px; font-size:14px; letter-spacing:.04em; margin-right:10px}
.callout a.btn:hover{background:#e6c879}
.callout a.alt{color:#cdb978; font-size:14px}
.callout .small{font-size:14px; color:#b9ad93; margin-top:16px; font-style:italic}

/* episodes */
.epctl{display:flex; align-items:center; gap:16px; margin-bottom:18px; flex-wrap:wrap}
.epctl button{background:none; border:1px solid var(--line); color:var(--ink-2);
 font-family:'Spectral',serif; font-size:12px; letter-spacing:.12em; text-transform:uppercase;
 padding:7px 14px; border-radius:2px; cursor:pointer; transition:.2s}
.epctl button:hover{border-color:var(--gold-soft); color:var(--gold-deep)}
details.ep{border-bottom:1px solid var(--line); scroll-margin-top:70px}
details.ep summary{display:flex; align-items:flex-start; gap:20px; padding:22px 6px; cursor:pointer;
 list-style:none; transition:background .25s}
details.ep summary::-webkit-details-marker{display:none}
details.ep summary:hover{background:rgba(212,173,87,.09)}
.ep-num{font-family:'Cormorant Garamond',serif; font-weight:600; font-size:34px; color:var(--gold-soft);
 line-height:1; min-width:54px; padding-top:2px}
.ep-titles{flex:1}
.ep-tr{display:block; font-family:'Cormorant Garamond',serif; font-weight:600; font-size:25px; line-height:1.1}
.ep-tr .star{color:var(--saffron); font-size:16px; vertical-align:super}
.ep-en{display:block; color:var(--ink-3); font-style:italic; font-size:16px; margin:1px 0 5px}
.ep-syn{display:block; color:var(--ink-2); font-size:15.5px; max-width:74ch}
.ep-meta{display:flex; align-items:center; gap:14px; padding-top:6px}
.ep-dur{font-size:12px; letter-spacing:.12em; color:var(--ink-3); white-space:nowrap}
.chev{font-size:24px; color:var(--gold-soft); transition:transform .3s; line-height:1}
details.ep[open] .chev{transform:rotate(90deg)}
.ep-body{padding:4px 6px 36px 78px}
@media(max-width:680px){.ep-body{padding-left:8px} .ep-syn{display:none}}
.ep-toolbar{display:flex; justify-content:space-between; align-items:center; gap:14px;
 margin:6px 0 20px; flex-wrap:wrap; border-bottom:1px solid var(--line); padding-bottom:12px}
.tabs{display:flex; gap:4px}
.tab{background:none; border:1px solid var(--line); border-radius:2px; cursor:pointer;
 font-family:'Spectral',serif; font-size:13px; padding:6px 14px; color:var(--ink-2); transition:.2s}
.tab.on{background:var(--ink); color:var(--paper); border-color:var(--ink)}
.ep-links a{font-size:13px; margin-left:14px; letter-spacing:.02em}
.panel.hidden{display:none}
.panel-script p{max-width:var(--read); margin:0 0 15px}
.spk{font-variant:small-caps; letter-spacing:.04em; font-weight:600; color:var(--indigo)}
.subh{font-family:'Cormorant Garamond',serif; font-weight:600; font-size:20px;
 color:var(--gold-deep); margin:22px 0 8px; letter-spacing:.01em}
.verse{background:var(--verse-bg); border-left:3px solid var(--verse-rule); border-radius:0 3px 3px 0;
 padding:16px 22px; margin:18px 0; max-width:var(--read)}
.verse .vt{font-style:italic; color:var(--ink); margin:0 0 4px; font-size:17px}
.verse .vtr{color:var(--ink-2); margin:0 0 4px; font-size:16.5px}
.verse cite{display:block; font-style:normal; font-size:11px; letter-spacing:.12em;
 text-transform:uppercase; color:var(--gold-deep); margin:4px 0 10px}
.verse cite:last-child{margin-bottom:0}
.verse p:last-of-type{margin-bottom:0}
.pointers{background:rgba(39,64,106,.055); border:1px solid rgba(39,64,106,.16);
 border-radius:4px; padding:8px 26px 22px; margin:26px 0 0; max-width:var(--read)}
.pointers-tag{font-size:10.5px; letter-spacing:.26em; text-transform:uppercase; color:var(--indigo-soft);
 margin:16px 0 0}
.pointers-h{font-family:'Cormorant Garamond',serif; font-weight:600; font-size:24px;
 margin:4px 0 8px; color:var(--indigo)}
.pointers p{font-size:16px; color:var(--ink-2)}
.panel-transcript .trans-note{font-size:14px; font-style:italic; color:var(--ink-3);
 border-bottom:1px solid var(--line); padding-bottom:12px; max-width:var(--read)}
.cue{display:flex; gap:14px; max-width:var(--read); margin:0 0 11px; font-size:16px}
.cue .ts{flex:0 0 64px; font-family:'Cormorant Garamond',serif; font-weight:600; color:var(--gold-deep);
 font-size:15px; padding-top:1px}
.cue .ts:hover{color:var(--saffron)}

/* prep threads */
details.prep{background:var(--card); border:1px solid var(--line); border-radius:4px; padding:6px 26px}
details.prep summary{cursor:pointer; list-style:none; padding:18px 0; font-family:'Cormorant Garamond',serif;
 font-weight:600; font-size:24px; display:flex; align-items:center; gap:12px}
details.prep summary::-webkit-details-marker{display:none}
details.prep summary .pen{color:var(--saffron); font-size:18px}
.thread{border-top:1px solid var(--line); padding:18px 0}
.thread h4{font-family:'Cormorant Garamond',serif; font-weight:600; font-size:20px; margin:0 0 6px; color:var(--indigo)}
.thread p{margin:0; color:var(--ink-2); font-size:16.5px; max-width:78ch; font-style:italic}

footer{max-width:var(--maxw); margin:0 auto; padding:48px 26px 70px; border-top:1px solid var(--line);
 color:var(--ink-3); font-size:14px}
footer .gu{color:var(--gold-deep); font-size:22px}
mark.hit{background:var(--gold-soft); color:#241a06; border-radius:2px; padding:0 1px}
mark.hit.cur{background:var(--saffron); color:#fff}
#top{position:fixed; right:24px; bottom:24px; z-index:40; width:44px; height:44px; border-radius:50%;
 background:var(--ink); color:var(--paper); border:none; cursor:pointer; font-size:18px;
 opacity:0; pointer-events:none; transition:opacity .3s}
#top.show{opacity:.85; pointer-events:auto}
#top:hover{opacity:1}

/* journey map */
.mapwrap{position:relative; background:var(--card); border:1px solid var(--line); border-radius:5px;
 padding:16px; box-shadow:0 22px 56px -34px rgba(43,37,28,.55)}
.jmap{width:100%; height:auto; display:block; border-radius:3px; overflow:hidden}
.ctry{fill:#e3d9c1; stroke:#cabf9c; stroke-width:.5; stroke-linejoin:round}
.ctry.j{fill:#ecdcb0; stroke:var(--gold); stroke-width:.8; stroke-linejoin:round}
.clbl{fill:#9a8961; font-family:'Spectral',serif; font-size:11px; letter-spacing:.2em; text-anchor:middle; pointer-events:none}
.route{fill:none; stroke:var(--gold-deep); stroke-width:1.7; stroke-dasharray:1.5 5.5; stroke-linecap:round; opacity:.6}
.pin{cursor:pointer}
.pin-c{fill:var(--gold); stroke:#fff8ea; stroke-width:1.6; transition:r .15s ease, fill .15s ease}
.pin.star .pin-c{fill:var(--saffron)}
.pin-t{fill:#fff; font-family:'Cormorant Garamond',serif; font-weight:700; font-size:14px; text-anchor:middle; pointer-events:none}
.pin:hover .pin-c,.pin:focus .pin-c{r:17; fill:var(--gold-deep)}
.pin:focus{outline:none}
.pin:focus .pin-c{stroke:var(--ink); stroke-width:2.4}
.maptip{position:absolute; pointer-events:none; background:var(--ink); color:var(--paper); font-size:13.5px;
 padding:7px 12px; border-radius:3px; opacity:0; transform:translate(-50%,-138%); transition:opacity .12s;
 white-space:nowrap; z-index:6; box-shadow:0 6px 18px -8px rgba(0,0,0,.5)}
.maptip.show{opacity:1}
.maplegend{display:flex; gap:24px; flex-wrap:wrap; margin:16px 2px 0; font-size:13.5px; color:var(--ink-2); align-items:center}
.maplegend .dot{display:inline-block; width:11px; height:11px; border-radius:50%; background:var(--gold);
 vertical-align:middle; margin-right:7px; box-shadow:0 0 0 1.5px #fff8ea}
.maplegend .dot.s{background:var(--saffron)}
.maplegend .ln{display:inline-block; width:26px; border-top:2px dotted var(--gold-deep); vertical-align:middle; margin-right:7px}
.mapnote{font-style:italic; color:var(--ink-3); font-size:14px; margin:8px 2px 0; max-width:78ch}

/* resources */
.reslinks{display:grid; grid-template-columns:1fr 1fr; gap:14px; max-width:var(--maxw)}
.res{display:block; background:var(--card); border:1px solid var(--line); border-radius:3px; padding:18px 22px; transition:transform .25s, border-color .25s}
.res:hover{transform:translateY(-3px); border-color:var(--gold-soft)}
.res .rt{font-family:'Cormorant Garamond',serif; font-weight:600; font-size:22px; color:var(--ink); display:flex; align-items:center; gap:8px}
.res .rt .arr{color:var(--gold-soft); font-size:18px}
.res p{margin:5px 0 0; font-size:15px; color:var(--ink-2)}
.sheetlink{display:inline-flex; align-items:center; gap:8px; margin-top:18px; background:var(--ink); color:var(--paper);
 padding:11px 20px; border-radius:3px; font-size:14px; letter-spacing:.03em}
.sheetlink:hover{background:var(--indigo); color:#fff}
@media(max-width:760px){.reslinks{grid-template-columns:1fr}}

@media (prefers-reduced-motion: reduce){
 *,*::before,*::after{animation:none!important; transition:none!important; scroll-behavior:auto!important}
 .anim,.reveal{opacity:1!important; transform:none!important}
}
@media print{
 nav,#prog,#top,.search,.epctl,.ep-toolbar{display:none!important}
 body{font-size:11pt} body::before,body::after{display:none}
 details.ep,details.prep{open:true} details>summary{list-style:none}
 .panel-transcript{display:none!important} .panel.hidden{display:block!important}
 a{color:var(--ink)} section{padding:18px 0; border-color:#ccc}
 .ep-body{padding-left:0}
}
"""

# ----------------------------------- JS ---------------------------------------
JS = r"""
function setTab(btn,n,which){
  var ep=document.getElementById('ep-'+n);
  ep.querySelectorAll('.tab').forEach(function(b){b.classList.toggle('on', b.dataset.tab===which)});
  ep.querySelectorAll('.panel').forEach(function(p){p.classList.toggle('hidden', p.dataset.panel!==which)});
}
function expandAll(v){document.querySelectorAll('details.ep').forEach(function(d){d.open=v})}
// progress + back-to-top
var prog=document.getElementById('prog'), topBtn=document.getElementById('top');
window.addEventListener('scroll',function(){
  var h=document.documentElement, sc=h.scrollTop, mx=h.scrollHeight-h.clientHeight;
  prog.style.width=(mx>0?(sc/mx*100):0)+'%';
  topBtn.classList.toggle('show', sc>700);
},{passive:true});
// reveal on scroll
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.12});
document.querySelectorAll('.reveal').forEach(function(el){io.observe(el)});
// ---- full-text search ----
var doc=document.getElementById('doc'), box=document.getElementById('q'), cnt=document.getElementById('cnt'), tmr;
function clearMarks(){
  doc.querySelectorAll('mark.hit').forEach(function(m){var t=document.createTextNode(m.textContent); m.parentNode.replaceChild(t,m); });
  doc.normalize();
}
function run(q){
  clearMarks();
  q=q.trim().toLowerCase();
  if(q.length<2){cnt.textContent=''; return;}
  var rx=new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi');
  var walker=document.createTreeWalker(doc, NodeFilter.SHOW_TEXT, {acceptNode:function(node){
    if(!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
    var p=node.parentNode.nodeName; if(p==='SCRIPT'||p==='STYLE'||p==='MARK') return NodeFilter.FILTER_REJECT;
    return node.nodeValue.toLowerCase().indexOf(q)>=0?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT;
  }});
  var nodes=[],n; while(n=walker.nextNode()) nodes.push(n);
  var total=0, eps=new Set();
  nodes.forEach(function(node){
    var frag=document.createDocumentFragment(), last=0, s=node.nodeValue; rx.lastIndex=0; var m;
    while(m=rx.exec(s)){
      frag.appendChild(document.createTextNode(s.slice(last,m.index)));
      var mk=document.createElement('mark'); mk.className='hit'; mk.textContent=m[0]; frag.appendChild(mk);
      last=m.index+m[0].length; total++;
    }
    frag.appendChild(document.createTextNode(s.slice(last)));
    node.parentNode.replaceChild(frag,node);
  });
  // open episodes containing a hit
  doc.querySelectorAll('details.ep').forEach(function(d){
    if(d.querySelector('mark.hit')){d.open=true; eps.add(d);}
  });
  cnt.textContent = total? (total+' hit'+(total>1?'s':'')+(eps.size?' · '+eps.size+' ep':'')) : 'no matches';
  var first=doc.querySelector('mark.hit'); if(first){first.classList.add('cur'); first.scrollIntoView({block:'center',behavior:'smooth'});}
}
box.addEventListener('input',function(){clearTimeout(tmr); tmr=setTimeout(function(){run(box.value)},230)});
box.addEventListener('keydown',function(e){if(e.key==='Escape'){box.value='';clearMarks();cnt.textContent='';box.blur();}});
// ---- journey map ----
function jumpEp(n){
  var d=document.getElementById('ep-'+n); if(!d) return;
  d.open=true; var y=d.getBoundingClientRect().top+window.scrollY-64;
  window.scrollTo({top:y,behavior:'smooth'});
  var s=d.querySelector('summary'); if(s) s.focus({preventScroll:true});
}
(function(){
  var jmap=document.querySelector('.jmap'); if(!jmap) return;
  var tip=document.createElement('div'); tip.className='maptip'; jmap.parentNode.appendChild(tip);
  function show(p){ var r=p.getBoundingClientRect(), pr=jmap.parentNode.getBoundingClientRect();
    tip.textContent=p.dataset.title+' · '+p.dataset.place;
    tip.style.left=(r.left+r.width/2-pr.left)+'px'; tip.style.top=(r.top-pr.top)+'px'; tip.classList.add('show'); }
  function hide(){ tip.classList.remove('show'); }
  jmap.querySelectorAll('.pin').forEach(function(p){
    p.addEventListener('mouseenter',function(){show(p)});
    p.addEventListener('mouseleave',hide);
    p.addEventListener('focus',function(){show(p)});
    p.addEventListener('blur',hide);
    p.addEventListener('click',function(){hide(); jumpEp(p.dataset.ep);});
    p.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault(); jumpEp(p.dataset.ep);}});
  });
})();
"""

# ----------------------------- assemble overview ------------------------------
def overview_html():
    themes=''.join(
        f'<div class="theme reveal"><div class="tn">{i+1}</div><h3>{esc(t)}</h3>'
        f'<p>{esc(body)}</p><p class="pq">“{esc(q)}”</p></div>'
        for i,(t,body,q) in enumerate(THEMES))
    tl=''.join(f'<div class="ev"><div class="yr">{esc(y)}</div><p>{esc(p)}</p></div>' for y,p in TIMELINE)
    works=''.join(
        f'<div class="work reveal"><div class="kick">{esc(k)}</div><h3>{esc(t)}</h3>'
        f'<p>{esc(d)}</p><div class="why">{esc(w)}</div></div>'
        for t,k,d,w in WORKS)
    quotes=''.join(f'<div class="q"><blockquote>“{esc(text)}”</blockquote><cite>{esc(src)}</cite></div>'
                   for text,src in QUOTES)
    threads=''.join(f'<div class="thread"><h4>{i+1}. {esc(t)}</h4><p>“{esc(body)}”</p></div>'
                    for i,(t,body) in enumerate(THREADS))
    journey_map=map_svg()
    res=[("Watch Allegory — all 24, in 5 languages","https://thegurunanak.com/english/","The full docuseries on the project site."),
         ("Peering Soul (2020)","https://www.youtube.com/watch?v=Ko7P-6B8irg","The 48-min film he points to: “my mindset and the pursuit.”"),
         ("Peering Warrior (2020)","https://www.youtube.com/watch?v=phbMR9Gy0Fo","The companion film — the forts and martial history."),
         ("Oneness in Diversity — the channel","https://www.youtube.com/@OnenessInDiversity","Allegory, the scripture renditions, and more."),
         ("Lost Heritage Productions","https://www.amardeepphotography.com/","Amardeep &amp; Vininder’s home for the books and photography."),
         ("TheGuruNanak.com","https://thegurunanak.com/","The project home — episodes, scripts, and the team.")]
    reslinks=''.join(
        f'<a class="res" href="{u}" target="_blank" rel="noopener"><span class="rt">{esc(t)}'
        f'<span class="arr">→</span></span><p>{d}</p></a>' for t,u,d in res)
    if PUBLIC:
        start_section=('<section id="start">'
          '<div class="sec-head reveal"><div class="sec-kicker">Where to start</div>'
          '<h2>If you watch one thing.</h2></div>'
          '<div class="callout reveal"><div class="tag">The 48-minute on-ramp</div>'
          '<h3>Peering Soul (2020)</h3>'
          '<p>The short film Amardeep points to as the way into his mindset and his pursuit. He travels to '
          'remote, abandoned Sikh and Hindu spiritual sites across Pakistan — framed as a personal quest '
          'rather than a history lecture. His guardrail on the whole endeavour: '
          '<em>“It is never about politics.”</em></p>'
          '<a class="btn" href="https://www.youtube.com/watch?v=Ko7P-6B8irg" target="_blank" rel="noopener">▶ Watch Peering Soul</a>'
          '<a class="alt" href="https://www.youtube.com/watch?v=phbMR9Gy0Fo" target="_blank" rel="noopener">The companion film, Peering Warrior →</a>'
          '<div class="small">Peering Soul (47:49) is the introspective film; its companion Peering Warrior '
          '(34:46) follows the forts and martial history.</div></div></section>')
        prep_section=('<section id="prep">'
          '<div class="sec-head reveal"><div class="sec-kicker">Going deeper</div>'
          '<h2>Questions the work raises.</h2>'
          '<p>Eight threads the series opens up — for study, for teaching, or for conversation.</p></div>'
          '<details class="prep reveal" open><summary><span class="pen">✎</span> Eight questions (click to toggle)</summary>'
          f'{threads}</details></section>')
    return f"""
<section id="intro">
  <div class="sec-head reveal"><div class="sec-kicker">Orientation</div>
    <h2>One project, in four media — the dissolution of identity into Oneness.</h2></div>
  <p class="lead reveal"><span class="dropcap">A</span>mardeep Singh (b. 1966, Gorakhpur) is a Singapore-based ex-American Express
  revenue-management executive who walked away from a 25-year finance career in 2013–14 to become a
  visual ethnographer of Sikh heritage and the journeys of Guru Nanak. He works as a husband-and-wife
  unit with Vininder Kaur, under Lost Heritage Productions. His throughline is unusually consistent
  across everything he touches: identity — national, religious, caste — is a construct that hides an
  underlying Oneness, and the whole job is to dissolve it. He does this physically, crossing the
  India–Pakistan border to film erased sites, and textually, reading scripture as non-dual awareness
  rather than sectarian devotion.</p>
</section>

<section id="themes">
  <div class="sec-head reveal"><div class="sec-kicker">The throughline</div>
    <h2>Six ideas that carry the whole body of work.</h2></div>
  <div class="themes">{themes}</div>
</section>

<section id="life">
  <div class="sec-head reveal"><div class="sec-kicker">The man</div>
    <h2>A life that turned toward the wound, not away.</h2>
    <p>His family fled Muzaffarabad before Partition; over 300 Sikhs — his relatives, and his wife’s
    grandparents — were massacred at the Dumel bridge in October 1947. The work is a man turning toward
    inherited trauma rather than away. Closure, not grievance.</p></div>
  <div class="tl reveal">{tl}</div>
</section>

<section id="work">
  <div class="sec-head reveal"><div class="sec-kicker">Body of work</div>
    <h2>Not four projects. One project, scaling outward.</h2>
    <p>From one country to nine; from buildings to a person; from biography to scripture; from a film
    to a teachable course.</p></div>
  <div class="works">{works}</div>
</section>

<section id="words">
  <div class="sec-head reveal"><div class="sec-kicker">In his own words</div>
    <h2>The worldview, compressed.</h2></div>
  <div class="quotes reveal">{quotes}</div>
</section>

{start_section}

<section id="journey">
  <div class="sec-head reveal"><div class="sec-kicker">The journey</div>
    <h2>Two decades of udasis, across nine countries.</h2>
    <p>Guru Nanak’s travels fanned east, south, west and north — 150+ multi-faith sites in nine modern
    countries, filmed in active conflict zones. Each pin is an episode: hover to see it, click to jump
    straight to its script below.</p></div>
  <div class="mapwrap reveal">{journey_map}
    <div class="maplegend">
      <span><span class="dot"></span>Episode</span>
      <span><span class="dot s"></span>Key episode &nbsp;(11 · 18 · 21)</span>
      <span><span class="ln"></span>the arc of the travels, in order</span>
    </div>
    <p class="mapnote">Locations are indicative, not surveyed — Amardeep himself reads these places as
    metaphor, “a revelation of a hidden meaning,” not pins on a verified map. The line traces the arc of
    the journey in episode order, including the returns home between odysseys.</p>
  </div>
</section>

<section id="episodes">
  <div class="sec-head reveal"><div class="sec-kicker">The raw text</div>
    <h2>Allegory — all 24 episodes, in full.</h2>
    <p>The complete verbatim narration scripts (with speaker labels, the scripture verses, and the
    series’ own discussion pointers), plus the timestamped video transcript for each. ✦ marks the three
    richest for discussion: <em>Aham Tvam</em>, <em>Sumeru</em>, and <em>Wahdat-al-Wajud</em>.
    Use the search box above to find anything across all of it.</p></div>
  <div class="epctl reveal">
    <button onclick="expandAll(true)">＋ Expand all</button>
    <button onclick="expandAll(false)">－ Collapse all</button>
  </div>
  __EPISODES__
</section>

{prep_section}

<section id="explore">
  <div class="sec-head reveal"><div class="sec-kicker">Explore the work</div>
    <h2>Go to the source.</h2></div>
  <div class="reslinks reveal">{reslinks}</div>
</section>
"""

# ------------------------------- assemble page --------------------------------
def main():
    scripts=parse_scripts(); yt=parse_yt()
    episodes=build_episodes(scripts, yt)
    body=overview_html().replace('__EPISODES__', episodes)
    nav=("""<div id="prog"></div>
<nav><div class="ninner">
  <div class="brand"><span class="gu">ੴ</span>Allegory</div>
  <div class="links">
    <a href="#themes">Themes</a><a href="#life">The Man</a><a href="#work">Body of Work</a>
    <a href="#words">His Words</a><a href="#start">Start Here</a><a href="#journey">Journey</a><a href="#episodes">24 Episodes</a>
  </div>
  <div class="search"><span class="mag">⌕</span>
    <input id="q" type="search" placeholder="Search all 24 scripts…" autocomplete="off" spellcheck="false">
    <span class="cnt" id="cnt"></span>
  </div>
</div></nav>""")
    hero=("""<header class="hero">
  <div class="ek gu">ੴ</div>
  <div class="eyebrow anim d1">Amardeep Singh &amp; Vininder Kaur · Lost Heritage Productions</div>
  <h1 class="anim d2">A Tapestry of <em>Guru Nanak’s</em> Travels</h1>
  <div class="who anim d3">The life, the themes, and the complete work of a chronicler of Oneness</div>
  <p class="lede anim d4">“Allegory is a revelation of a hidden meaning within a narrative.” — a visual ethnographer
  reading the journeys of Guru Nanak as metaphor, and every name of God as the unseen, all-pervading awareness.</p>
  <div class="stats anim d5">
    <div class="stat"><b>9</b><span>countries</span></div>
    <div class="stat"><b>150+</b><span>multi-faith sites</span></div>
    <div class="stat"><b>24</b><span>episodes</span></div>
    <div class="stat"><b>18h 23m</b><span>total runtime</span></div>
    <div class="stat"><b>1,656</b><span>verses annotated</span></div>
  </div>
</header>""")
    if PUBLIC:
        footer=("""<footer>
  <span class="gu">ੴ</span> &nbsp;A study companion to the work of Amardeep Singh &amp; Vininder Kaur
  (Lost Heritage Productions), offered with gratitude — all words are theirs. Sources: the official
  “Script &amp; Discussion Pointers” PDFs and the (English) Allegory YouTube playlist, both at
  TheGuruNanak.com (channel @OnenessInDiversity). Verbatim scripts + timestamped captions, unedited.
  &nbsp;·&nbsp; Press <b>Esc</b> to clear search.
</footer>""")
    page=("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
          "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
          "<title>Amardeep Singh — Allegory & the Work of Oneness</title>"
          "<link rel=\"icon\" href=\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%23f3eada'/%3E%3Ctext x='32' y='49' font-size='44' text-anchor='middle' fill='%23a3761c'%3E%E0%A8%B4%3C/text%3E%3C/svg%3E\">"
          "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">"
          "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>"
          "<link href=\"https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Spectral:ital,wght@0,300;0,400;0,500;0,600;1,400;1,500&family=Noto+Serif+Gurmukhi:wght@400;600;700&display=swap\" rel=\"stylesheet\">"
          f"<style>{CSS}</style></head><body>"
          f"<div class=\"wrap\">{nav}{hero}<main id=\"doc\">{body}</main>{footer}</div>"
          "<button id=\"top\" onclick=\"window.scrollTo({top:0,behavior:'smooth'})\">↑</button>"
          f"<script>{JS}</script></body></html>")
    with open(OUT,'w',encoding='utf-8') as f: f.write(page)
    print(f"[{'PUBLIC' if PUBLIC else 'private'}] wrote {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")
    print(f"episodes parsed: {len(scripts)} scripts, {len(yt)} transcripts")

if __name__=="__main__":
    main()
