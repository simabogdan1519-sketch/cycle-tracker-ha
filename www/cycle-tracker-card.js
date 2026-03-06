// cycle-tracker-card.js
// Lovelace Custom Card – Cycle Tracker Smart
// Instalare: copiază în config/www/cycle-tracker-card.js
// Adaugă în dashboard: type: custom:cycle-tracker-card

const HIST_KEY = 'cycle_tracker_history_v1';

// ── Storage ──────────────────────────────────────────────
function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HIST_KEY) || '[]'); } catch { return []; }
}
function saveHistory(h) {
  try { localStorage.setItem(HIST_KEY, JSON.stringify(h)); } catch {}
}

// ── Smart engine ─────────────────────────────────────────
function smartLen(history, haLen) {
  if (history.length < 2) return haLen || 28;
  const s = [...history].sort((a, b) => new Date(a) - new Date(b));
  const lens = [];
  for (let i = 1; i < s.length; i++) {
    const d = Math.round((new Date(s[i]) - new Date(s[i - 1])) / 86400000);
    if (d >= 15 && d <= 50) lens.push(d);
  }
  return lens.length ? Math.round(lens.reduce((a, b) => a + b) / lens.length) : haLen || 28;
}

function isIrregular(h) {
  if (h.length < 3) return false;
  const s = [...h].sort((a, b) => new Date(a) - new Date(b));
  const lens = [];
  for (let i = 1; i < s.length; i++) {
    const d = Math.round((new Date(s[i]) - new Date(s[i - 1])) / 86400000);
    if (d >= 15 && d <= 50) lens.push(d);
  }
  if (lens.length < 2) return false;
  const avg = lens.reduce((a, b) => a + b) / lens.length;
  return Math.sqrt(lens.reduce((a, b) => a + Math.pow(b - avg, 2) / lens.length, 0)) > 4;
}

function trendDir(h) {
  if (h.length < 4) return null;
  const s = [...h].sort((a, b) => new Date(a) - new Date(b));
  const lens = [];
  for (let i = 1; i < s.length; i++) {
    const d = Math.round((new Date(s[i]) - new Date(s[i - 1])) / 86400000);
    if (d >= 15 && d <= 50) lens.push(d);
  }
  if (lens.length < 3) return null;
  const hh = Math.floor(lens.length / 2);
  const a1 = lens.slice(0, hh).reduce((a, b) => a + b) / hh;
  const a2 = lens.slice(-hh).reduce((a, b) => a + b) / hh;
  if (a2 - a1 > 2) return 'longer';
  if (a1 - a2 > 2) return 'shorter';
  return 'stable';
}

// ── Phase content ────────────────────────────────────────
const FERT_PCT = { maxim: 98, foarte_inalt: 80, inalt: 55, moderat: 25, scazut: 5 };
const FERT_LBL = { maxim: 'Maxim', foarte_inalt: 'Foarte înalt', inalt: 'Înalt', moderat: 'Moderat', scazut: 'Scăzut' };

const PHASES = {
  menstruatie: {
    name: 'Menstruație 🌹',
    bg: 'linear-gradient(135deg,rgba(232,96,122,0.18),rgba(155,77,110,0.10))',
    br: 'rgba(232,96,122,0.26)',
    desc: 'Corpul se regenerează. Odihnă, căldură și hidratare sunt esențiale.',
    recs: [
      { i: '🛁', t: '<strong>Odihnă & căldură:</strong> Pernă termică, ceai de ghimbir sau mușețel pentru crampe.' },
      { i: '🥗', t: '<strong>Alimentație:</strong> Alimente bogate în fier – spanac, linte, carne roșie slabă.' },
      { i: '🧘', t: '<strong>Mișcare blândă:</strong> Yoga yin sau stretching. Evită antrenamentele intense.' },
      { i: '💊', t: '<strong>Suplimente:</strong> Magneziu și omega-3 reduc crampele și inflamația.' },
    ],
  },
  foliculara: {
    name: 'Foliculară 🌱',
    bg: 'linear-gradient(135deg,rgba(196,168,224,0.14),rgba(91,200,184,0.07))',
    br: 'rgba(196,168,224,0.22)',
    desc: 'Energia revine. Ideal pentru activitate fizică și planuri noi.',
    recs: [
      { i: '🏃', t: '<strong>Energie crescută:</strong> Moment ideal pentru antrenamente de forță sau cardio.' },
      { i: '🥦', t: '<strong>Alimentație:</strong> Proteine slabe și legume crucifere susțin estrogenul.' },
      { i: '🎯', t: '<strong>Productivitate:</strong> Creierul e mai creativ – ideal pentru brainstorming.' },
      { i: '🌿', t: '<strong>Suplimente:</strong> Vitamina D și zinc susțin maturarea foliculilor.' },
    ],
  },
  ovulatie: {
    name: 'Ovulație ✨',
    bg: 'linear-gradient(135deg,rgba(240,192,96,0.16),rgba(232,96,122,0.08))',
    br: 'rgba(240,192,96,0.28)',
    desc: 'Vârf de fertilitate. Energie și comunicare la cote maxime.',
    recs: [
      { i: '🥚', t: '<strong>Fertilitate maximă:</strong> Fereastra optimă dacă îți dorești o sarcină (±2–3 zile).' },
      { i: '🍓', t: '<strong>Alimentație:</strong> Antioxidanți (fructe de pădure, roșii) și fibre.' },
      { i: '💪', t: '<strong>Mișcare:</strong> Performanță fizică maximă – HIIT, dans, sporturi de echipă.' },
      { i: '💬', t: '<strong>Social:</strong> Prezentări, discuții importante – ești la cel mai bun al tău.' },
    ],
  },
  luteala: {
    name: 'Luteală 🍂',
    bg: 'linear-gradient(135deg,rgba(155,77,110,0.16),rgba(91,200,184,0.07))',
    br: 'rgba(155,77,110,0.24)',
    desc: 'Pregătire pentru un nou ciclu. Introspecție și confort.',
    recs: [
      { i: '🍫', t: '<strong>Pofte & PMS:</strong> Ciocolată neagră (>70%), nuci și magneziu reduc PMS-ul.' },
      { i: '🌙', t: '<strong>Somn:</strong> Prioritizează somnul – temperatura corpului crește ușor.' },
      { i: '🧴', t: '<strong>Îngrijire:</strong> Pielea mai sensibilă – hidratare intensă și protecție solară.' },
      { i: '📓', t: '<strong>Emoții:</strong> Jurnal, meditație sau plimbări în natură.' },
    ],
  },
};

const MS = ['Ian','Feb','Mar','Apr','Mai','Iun','Iul','Aug','Sep','Oct','Nov','Dec'];
const ML = ['Ianuarie','Februarie','Martie','Aprilie','Mai','Iunie','Iulie','August','Septembrie','Octombrie','Noiembrie','Decembrie'];
function fmtDate(d) { return (!d || isNaN(d)) ? '—' : `${d.getDate()} ${MS[d.getMonth()]}`; }
function fmtDateL(d) { return (!d || isNaN(d)) ? '—' : `${d.getDate()} ${ML[d.getMonth()]} ${d.getFullYear()}`; }

// ════════════════════════════════════════════════════════════
// CUSTOM ELEMENT
// ════════════════════════════════════════════════════════════
class CycleTrackerCard extends HTMLElement {

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._hass = null;
    this._entryId = null;
    this._prefix = null;
    this._histOpen = false;
    this._inpOpen = false;
  }

  // Lovelace apelează setConfig la inițializare
  setConfig(config) {
    this._config = config || {};
  }

  // Lovelace apelează set hass() la fiecare update de stare
  set hass(hass) {
    this._hass = hass;
    if (!this.shadowRoot.innerHTML) {
      this._build();
    }
    this._updateFromHass();
  }

  // Lovelace cere înălțimea cardului (unități de 50px)
  getCardSize() { return 12; }

  // ── Build shadow DOM ──────────────────────────────────
  _build() {
    this.shadowRoot.innerHTML = `
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;1,400&family=Nunito:wght@300;400;500;600&display=swap');
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
        :host{display:block;font-family:'Nunito',sans-serif}
        :root{}

        .card{
          background:linear-gradient(170deg,#1c0e20 0%,#110c18 50%,#180e1f 100%);
          border-radius:24px;
          border:1px solid rgba(232,96,122,0.15);
          overflow:hidden;
          color:#fff;
          position:relative;
          box-shadow:0 0 0 1px rgba(255,255,255,0.03) inset;
        }
        .g1,.g2{position:absolute;border-radius:50%;pointer-events:none}
        .g1{width:280px;height:280px;top:-70px;right:-50px;background:radial-gradient(circle,rgba(232,96,122,0.10) 0%,transparent 70%)}
        .g2{width:220px;height:220px;bottom:-50px;left:-50px;background:radial-gradient(circle,rgba(91,200,184,0.07) 0%,transparent 70%)}

        /* status */
        .sbar{display:flex;align-items:center;justify-content:space-between;padding:14px 20px 0;position:relative;z-index:2}
        .sl{display:flex;align-items:center;gap:6px}
        .dot{width:6px;height:6px;border-radius:50%;background:#5BC8B8;box-shadow:0 0 8px #5BC8B8;animation:bl 2.5s ease-in-out infinite}
        .dot.err{background:#E8607A;box-shadow:0 0 8px #E8607A}
        @keyframes bl{0%,100%{opacity:1}50%{opacity:.4}}
        .stxt{font-size:10px;color:rgba(255,255,255,0.30)}
        .spill{display:flex;align-items:center;gap:4px;background:rgba(91,200,184,0.10);border:1px solid rgba(91,200,184,0.20);border-radius:99px;padding:3px 9px;font-size:9px;color:#5BC8B8}

        /* topbar */
        .topbar{padding:10px 20px 0;position:relative;z-index:2}
        .brand{font-family:'Playfair Display',serif;font-size:19px}
        .brand em{color:#E8607A;font-style:italic}
        .sub{font-size:10px;color:rgba(255,255,255,0.25);letter-spacing:.6px;text-transform:uppercase;margin-top:2px}

        /* phase hero */
        .ph{margin:14px 16px 0;border-radius:20px;padding:16px 18px;position:relative;z-index:2;transition:background .5s,border-color .5s;border:1px solid transparent}
        .ph-tag{font-size:9px;letter-spacing:1.4px;text-transform:uppercase;color:rgba(255,255,255,0.35);margin-bottom:4px}
        .ph-name{font-family:'Playfair Display',serif;font-size:26px;line-height:1.05;color:#fff}
        .ph-desc{font-size:12px;color:rgba(255,255,255,0.50);line-height:1.6;margin-top:5px;max-width:210px}
        .day-orb{position:absolute;top:14px;right:14px;width:54px;height:54px;border-radius:50%;background:rgba(0,0,0,0.28);border:1px solid rgba(255,255,255,0.10);display:flex;flex-direction:column;align-items:center;justify-content:center}
        .dn{font-family:'Playfair Display',serif;font-size:21px;line-height:1;color:#fff}
        .dl{font-size:8px;color:rgba(255,255,255,0.28);text-transform:uppercase;letter-spacing:.5px}

        /* alert */
        .az{padding:8px 16px 0;position:relative;z-index:2}
        .ab{display:flex;align-items:center;gap:10px;border-radius:13px;padding:9px 13px;font-size:11.5px;line-height:1.5}
        .ab.h{display:none}
        .ab.warn{background:rgba(232,96,122,0.10);border:1px solid rgba(232,96,122,0.22);color:rgba(255,255,255,.70)}
        .ab.info{background:rgba(91,200,184,0.10);border:1px solid rgba(91,200,184,0.22);color:rgba(255,255,255,.70)}
        .ab strong{color:#fff}

        /* ring + stats */
        .mr{display:flex;align-items:center;gap:12px;padding:12px 16px 0;position:relative;z-index:2}
        .rbg{fill:none;stroke:rgba(255,255,255,0.05);stroke-width:8}
        .rtr{fill:none;stroke-width:8;stroke-linecap:round;transform:rotate(-90deg);transform-origin:50% 50%;stroke:url(#rg);transition:stroke-dashoffset 1.3s cubic-bezier(.4,0,.2,1)}
        .rct{text-anchor:middle;dominant-baseline:middle}
        .msc{flex:1;display:flex;flex-direction:column;gap:6px}
        .ms{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:8px 11px;display:flex;align-items:center;gap:8px}
        .mi{font-size:13px;flex-shrink:0}
        .mv{font-size:13px;font-weight:600;color:#fff;line-height:1}
        .ml{font-size:9px;color:rgba(255,255,255,0.28);margin-top:1px}

        /* fertility */
        .frt{padding:12px 16px 0;position:relative;z-index:2}
        .sl2{font-size:9px;letter-spacing:1.2px;text-transform:uppercase;color:rgba(255,255,255,0.25);margin-bottom:7px}
        .fb{height:7px;background:rgba(255,255,255,0.05);border-radius:99px;overflow:hidden;margin-bottom:4px}
        .ff{height:100%;border-radius:99px;background:linear-gradient(90deg,#5BC8B8,#F0C060);transition:width 1.4s cubic-bezier(.4,0,.2,1)}
        .fl{display:flex;justify-content:space-between;font-size:9px;color:rgba(255,255,255,0.22)}

        /* calendar */
        .cal{padding:12px 16px 0;position:relative;z-index:2}
        .cg{display:grid;grid-template-columns:repeat(7,1fr);gap:3px}
        .ch{font-size:8px;color:rgba(255,255,255,0.18);text-align:center;text-transform:uppercase;padding-bottom:2px}
        .cd{aspect-ratio:1;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:9.5px;cursor:default;transition:transform .15s}
        .cd:hover{transform:scale(1.15)}
        .cd.n{background:rgba(255,255,255,0.03);color:rgba(255,255,255,0.30)}
        .cd.p{background:rgba(232,96,122,0.22);color:#F4A0B0;font-weight:600}
        .cd.f{background:rgba(91,200,184,0.18);color:#5BC8B8}
        .cd.ov{background:rgba(240,192,96,0.24);color:#F0C060;font-weight:700;border:1px solid rgba(240,192,96,.32)}
        .cd.td{box-shadow:0 0 0 2px #E8607A}
        .cd.em{background:transparent}
        .cd.hp{background:rgba(232,96,122,0.09);color:rgba(255,255,255,0.22)}

        .leg{display:flex;gap:9px;flex-wrap:wrap;padding:7px 16px 0;position:relative;z-index:2}
        .li{display:flex;align-items:center;gap:3px;font-size:9px;color:rgba(255,255,255,0.35)}
        .ld{width:6px;height:6px;border-radius:50%}

        /* recs */
        .rcs{padding:12px 16px;position:relative;z-index:2}
        .rc{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:10px 12px;margin-bottom:6px;display:flex;gap:9px;align-items:flex-start}
        .rc:last-child{margin-bottom:0}
        .ri{font-size:15px;flex-shrink:0}
        .rt{font-size:11px;color:rgba(255,255,255,0.55);line-height:1.55}
        .rt strong{color:rgba(255,255,255,0.85);font-weight:600}

        /* insights */
        .ins{padding:0 16px 14px;position:relative;z-index:2}
        .ins-hd{font-size:9px;letter-spacing:1.2px;text-transform:uppercase;color:rgba(91,200,184,0.6);margin-bottom:7px}
        .ib{background:rgba(91,200,184,0.06);border:1px solid rgba(91,200,184,0.14);border-radius:12px;padding:10px 12px;margin-bottom:6px;font-size:11px;color:rgba(255,255,255,0.58);line-height:1.55}
        .ib:last-child{margin-bottom:0}
        .ib strong{color:rgba(91,200,184,0.9);font-weight:600}
        .ib.wi{background:rgba(240,192,96,0.06);border-color:rgba(240,192,96,0.16)}
        .ib.wi strong{color:rgba(240,192,96,0.9)}
        .ie{font-size:11px;color:rgba(255,255,255,0.22);text-align:center;padding:6px 0}

        /* history */
        .htog{width:100%;background:none;border:none;padding:10px 16px;display:flex;justify-content:space-between;align-items:center;color:rgba(255,255,255,0.38);font-size:11px;font-family:'Nunito',sans-serif;cursor:pointer;transition:color .2s;position:relative;z-index:2}
        .htog:hover{color:rgba(255,255,255,.65)}
        .ha{transition:transform .3s;display:inline-block}
        .ha.open{transform:rotate(180deg)}
        .hbody{display:none;padding:0 16px 12px;position:relative;z-index:2}
        .hbody.open{display:block}
        .hr{display:flex;align-items:center;justify-content:space-between;padding:7px 11px;border-radius:10px;margin-bottom:4px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);font-size:11px}
        .hrd{color:rgba(255,255,255,0.55)}
        .hrl{padding:2px 7px;border-radius:99px;font-size:9.5px;font-weight:600;background:rgba(232,96,122,0.15);color:#F4A0B0}
        .hrl.ok{background:rgba(91,200,184,0.15);color:#5BC8B8}
        .hdl{width:18px;height:18px;border-radius:50%;background:rgba(255,255,255,0.05);border:none;color:rgba(255,255,255,0.25);cursor:pointer;font-size:9px;display:flex;align-items:center;justify-content:center;transition:all .2s}
        .hdl:hover{background:rgba(232,96,122,0.20);color:#E8607A}
        .nh{font-size:11px;color:rgba(255,255,255,0.22);text-align:center;padding:6px 0}

        /* input panel */
        .ip{margin:0 16px 20px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:16px;overflow:hidden;position:relative;z-index:2}
        .iptog{width:100%;background:none;border:none;padding:12px 15px;display:flex;justify-content:space-between;align-items:center;color:rgba(255,255,255,0.48);font-size:11.5px;font-family:'Nunito',sans-serif;cursor:pointer;transition:color .2s}
        .iptog:hover{color:#fff}
        .ia{transition:transform .3s;display:inline-block}
        .ia.open{transform:rotate(180deg)}
        .ipbody{display:none;padding:0 15px 15px}
        .ipbody.open{display:block}
        .lbl{font-size:10px;color:rgba(255,255,255,0.32);margin-bottom:4px;margin-top:9px}
        .inp{width:100%;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.09);border-radius:10px;padding:9px 12px;font-size:13px;color:#fff;font-family:'Nunito',sans-serif;outline:none;transition:border-color .2s}
        .inp:focus{border-color:rgba(232,96,122,.45)}
        .inp::-webkit-calendar-picker-indicator{filter:invert(1) opacity(.3)}
        .r2{display:grid;grid-template-columns:1fr 1fr;gap:7px}
        .sbtn{width:100%;margin-top:11px;background:linear-gradient(135deg,#E8607A,#9B4D6E);border:none;border-radius:11px;padding:10px;color:#fff;font-size:13px;font-weight:600;font-family:'Nunito',sans-serif;cursor:pointer;transition:opacity .2s}
        .sbtn:hover{opacity:.88}
        .sbtn:disabled{opacity:.4;cursor:not-allowed}

        .dv{height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.06),transparent);margin:0 16px 11px}

        /* toast */
        .toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(14px);background:rgba(18,10,22,.96);border:1px solid rgba(91,200,184,.28);border-radius:11px;padding:8px 18px;font-size:12px;color:#fff;opacity:0;transition:all .3s;pointer-events:none;z-index:9999}
        .toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
      </style>

      <div class="card">
        <div class="g1"></div><div class="g2"></div>

        <div class="sbar">
          <div class="sl">
            <div class="dot" id="dot"></div>
            <div class="stxt" id="stxt">Se încarcă…</div>
          </div>
          <div class="spill">✦ Smart</div>
        </div>

        <div class="topbar">
          <div class="brand">Ciclul <em>meu</em></div>
          <div class="sub">Monitorizare · Fertilitate · Recomandări</div>
        </div>

        <div class="ph" id="phHero">
          <div class="ph-tag">Faza curentă</div>
          <div class="ph-name" id="phN">—</div>
          <div class="ph-desc" id="phD">Se caută senzorii integrării…</div>
          <div class="day-orb"><div class="dn" id="dayN">—</div><div class="dl">ziua</div></div>
        </div>

        <div class="az"><div class="ab h" id="alertB"><span id="aIco">🔔</span><span id="aTxt"></span></div></div>

        <div class="mr">
          <svg width="112" height="112" viewBox="0 0 112 112" style="overflow:visible;flex-shrink:0">
            <defs>
              <linearGradient id="rg" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#E8607A"/>
                <stop offset="50%" stop-color="#B84D9E"/>
                <stop offset="100%" stop-color="#5BC8B8"/>
              </linearGradient>
            </defs>
            <circle class="rbg" cx="56" cy="56" r="47"/>
            <circle class="rtr" id="ringC" cx="56" cy="56" r="47" stroke-dasharray="295.3" stroke-dashoffset="295.3"/>
            <text class="rct" x="56" y="47" font-size="9" fill="rgba(255,255,255,0.28)">Progres</text>
            <text class="rct" x="56" y="61" font-family="Playfair Display,serif" font-size="19" fill="#fff" id="rPct">—</text>
            <text class="rct" x="56" y="73" font-size="9" fill="rgba(255,255,255,0.26)" id="rLeft">—</text>
          </svg>
          <div class="msc">
            <div class="ms"><div class="mi">📅</div><div><div class="mv" id="sCLen">—</div><div class="ml">zile/ciclu</div></div></div>
            <div class="ms"><div class="mi">🥚</div><div><div class="mv" id="sOvul">—</div><div class="ml">ziua ovulației</div></div></div>
            <div class="ms"><div class="mi">🔜</div><div><div class="mv" id="sNext">—</div><div class="ml">urm. perioadă</div></div></div>
          </div>
        </div>

        <div class="frt">
          <div class="sl2">Nivelul de fertilitate estimat</div>
          <div class="fb"><div class="ff" id="ffill" style="width:0%"></div></div>
          <div class="fl"><span>Scăzut</span><span id="fLbl">—</span><span>Înalt</span></div>
        </div>

        <div class="cal">
          <div class="sl2">Calendar – luna curentă</div>
          <div class="cg" id="calG"></div>
        </div>

        <div class="leg">
          <div class="li"><div class="ld" style="background:rgba(232,96,122,.75)"></div>Menstruație</div>
          <div class="li"><div class="ld" style="background:rgba(91,200,184,.75)"></div>Fertilă</div>
          <div class="li"><div class="ld" style="background:rgba(240,192,96,.85)"></div>Ovulație</div>
          <div class="li"><div class="ld" style="background:rgba(232,96,122,.4)"></div>Istoric</div>
          <div class="li"><div class="ld" style="background:rgba(232,96,122,.9);box-shadow:0 0 0 2px rgba(232,96,122,.5)"></div>Azi</div>
        </div>

        <div class="dv" style="margin-top:13px"></div>

        <div class="rcs">
          <div class="sl2" style="margin-bottom:7px">Recomandări pentru azi</div>
          <div id="recL"></div>
        </div>

        <div class="dv"></div>

        <div class="ins">
          <div class="ins-hd">✦ Insights inteligente</div>
          <div id="insL"></div>
        </div>

        <div class="dv"></div>

        <button class="htog" id="htog">
          <span>📋 Istoricul ciclurilor (<span id="hCnt">0</span>)</span>
          <span class="ha" id="hArr">▼</span>
        </button>
        <div class="hbody" id="hBody"><div id="hList"></div></div>

        <div class="ip">
          <button class="iptog" id="iptog">
            <span>⚙️ Adaugă / actualizează ciclu</span>
            <span class="ia" id="iArr">▼</span>
          </button>
          <div class="ipbody" id="iBody">
            <div class="lbl">Prima zi a ultimei menstruații</div>
            <input type="date" class="inp" id="inD"/>
            <div class="r2">
              <div><div class="lbl">Ciclu (zile) – opțional</div><input type="number" class="inp" id="inC" min="21" max="40" placeholder="auto"/></div>
              <div><div class="lbl">Perioadă (zile) – opțional</div><input type="number" class="inp" id="inP" min="2" max="10" placeholder="auto"/></div>
            </div>
            <button class="sbtn" id="saveBtn">💾 Salvează în Home Assistant</button>
          </div>
        </div>
      </div>
      <div class="toast" id="toast"></div>
    `;

    // Event listeners
    this.shadowRoot.getElementById('htog').addEventListener('click', () => this._toggleH());
    this.shadowRoot.getElementById('iptog').addEventListener('click', () => this._toggleI());
    this.shadowRoot.getElementById('saveBtn').addEventListener('click', () => this._saveCycle());

    // Pre-fill today
    this.shadowRoot.getElementById('inD').value = new Date().toISOString().split('T')[0];
  }

  // ── Update from hass states ───────────────────────────
  _updateFromHass() {
    if (!this._hass) return;

    // Auto-discover senzori cycle_tracker
    const allStates = this._hass.states;
    const cycleDay = Object.keys(allStates).find(
      k => k.startsWith('sensor.') && k.endsWith('cycle_day')
    );

    if (!cycleDay) {
      this._setStatus(false, 'Integrarea Cycle Tracker nu a fost găsită');
      this._render(null);
      return;
    }

    // Extrage prefix: "sensor.ana_cycle_day" → "ana_"
    this._prefix = cycleDay.replace('sensor.', '').replace('cycle_day', '');

    const get = name => allStates[`sensor.${this._prefix}${name}`];

    const sensors = {
      cycle_day:          get('cycle_day'),
      cycle_phase:        get('cycle_phase'),
      fertility_level:    get('fertility_level'),
      days_until_period:  get('days_until_period'),
      next_period_date:   get('next_period_date'),
      ovulation_date:     get('ovulation_date'),
      cycle_progress:     get('cycle_progress'),
    };

    this._setStatus(true, `HA conectat · sensor.${this._prefix}cycle_day`);
    this._render(sensors);

    // Găsește entry_id pentru serviciu (din config_entries via hass)
    if (!this._entryId) {
      this._findEntryId();
    }
  }

  async _findEntryId() {
    try {
      // Folosim hass.callApi — disponibil nativ în custom cards, fără token!
      const entries = await this._hass.callApi('GET', 'config/config_entries/entry');
      const entry = entries.find(e => e.domain === 'cycle_tracker');
      if (entry) this._entryId = entry.entry_id;
    } catch (e) {
      console.warn('CycleTracker: nu am găsit entry_id', e);
    }
  }

  _setStatus(ok, msg) {
    const dot = this.shadowRoot.getElementById('dot');
    const stxt = this.shadowRoot.getElementById('stxt');
    if (!dot || !stxt) return;
    dot.className = ok ? 'dot' : 'dot err';
    stxt.textContent = msg;
  }

  // ── Render ────────────────────────────────────────────
  _render(sensors) {
    const history  = loadHistory();
    const haPhase  = sensors?.cycle_phase?.state  || 'foliculara';
    const haDay    = parseInt(sensors?.cycle_day?.state   || 1);
    const haFert   = sensors?.fertility_level?.state      || 'scazut';
    const haDL     = parseInt(sensors?.days_until_period?.state ?? 27);
    const haProg   = parseInt(sensors?.cycle_progress?.state    || 0);
    const haCLen   = sensors?.cycle_day?.attributes?.cycle_length  || 28;
    const haPLen   = sensors?.cycle_day?.attributes?.period_length || 5;
    const haOvDay  = sensors?.cycle_day?.attributes?.ovulation_day || 14;
    const haNext   = sensors?.next_period_date?.state;
    const haOvul   = sensors?.ovulation_date?.state;
    const hasData  = !!sensors?.cycle_day;

    const sl = smartLen(history, haCLen);
    const ph = PHASES[haPhase] || PHASES.foliculara;
    const fp = FERT_PCT[haFert] || 5;
    const fl = FERT_LBL[haFert] || 'Scăzut';

    const $ = id => this.shadowRoot.getElementById(id);

    const hero = $('phHero');
    if (hero) {
      hero.style.background  = hasData ? ph.bg : 'rgba(255,255,255,0.04)';
      hero.style.borderColor = hasData ? ph.br : 'rgba(255,255,255,0.08)';
    }
    if ($('phN'))   $('phN').textContent  = hasData ? ph.name : '—';
    if ($('phD'))   $('phD').textContent  = hasData ? ph.desc : 'Adaugă ciclul din panoul ⚙️ de mai jos.';
    if ($('dayN'))  $('dayN').textContent = hasData ? haDay   : '—';

    // Alert
    const ab = $('alertB');
    if (ab) {
      if (hasData && haDL <= 3) {
        ab.className = 'ab warn';
        $('aIco').textContent = '🔔';
        $('aTxt').innerHTML = haDL === 0
          ? '<strong>Menstruația poate începe azi!</strong>'
          : `Menstruația în <strong>${haDL} ${haDL === 1 ? 'zi' : 'zile'}</strong>.`;
      } else if (hasData && haPhase === 'ovulatie') {
        ab.className = 'ab info';
        $('aIco').textContent = '✨';
        $('aTxt').innerHTML = '<strong>Fertilitate maximă azi!</strong> Energie la cote înalte.';
      } else {
        ab.className = 'ab h';
      }
    }

    // Ring
    setTimeout(() => {
      const ring = $('ringC');
      if (ring) ring.style.strokeDashoffset = 295.3 - (haProg / 100) * 295.3;
      if ($('rPct'))  $('rPct').textContent  = hasData ? haProg + '%' : '—';
      if ($('rLeft')) $('rLeft').textContent = hasData ? haDL + ' zile rămase' : '—';
    }, 80);

    if ($('sCLen')) $('sCLen').textContent = sl + (history.length >= 2 ? ' 📊' : '');
    if ($('sOvul')) $('sOvul').textContent = haOvul ? fmtDate(new Date(haOvul)) : '—';
    if ($('sNext')) $('sNext').textContent = haNext  ? fmtDate(new Date(haNext))  : '—';

    setTimeout(() => {
      const ff = $('ffill');
      if (ff) ff.style.width = hasData ? fp + '%' : '0%';
    }, 100);
    if ($('fLbl')) $('fLbl').textContent = hasData ? fl : '—';

    this._buildCal(history, haCLen, haPLen, haOvDay, haDay, hasData);

    if ($('recL')) {
      $('recL').innerHTML = hasData
        ? ph.recs.map(r => `<div class="rc"><div class="ri">${r.i}</div><div class="rt">${r.t}</div></div>`).join('')
        : '<div class="rc"><div class="rt" style="color:rgba(255,255,255,0.28)">Adaugă ciclul din panoul ⚙️ de mai jos.</div></div>';
    }

    this._renderInsights(history, sl, haCLen);
    this._renderHistory(history);
    if ($('hCnt')) $('hCnt').textContent = history.length;
  }

  _buildCal(history, cLen, pLen, ovDay, doc, hasData) {
    const $ = id => this.shadowRoot.getElementById(id);
    const heads = ['Lu','Ma','Mi','Jo','Vi','Sâ','Du'];
    let html = heads.map(d => `<div class="ch">${d}</div>`).join('');
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const fom = new Date(today.getFullYear(), today.getMonth(), 1);
    let sw = fom.getDay(); sw = sw === 0 ? 6 : sw - 1;
    for (let i = 0; i < sw; i++) html += `<div class="cd em"></div>`;
    const dim = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
    const cs = new Date(today); cs.setDate(today.getDate() - doc + 1);
    const hs = new Set();
    [...history].sort((a, b) => new Date(a) - new Date(b)).slice(0, -1).forEach(d => {
      const s = new Date(d);
      for (let i = 0; i < pLen; i++) {
        const dd = new Date(s); dd.setDate(dd.getDate() + i);
        if (dd.getMonth() === today.getMonth() && dd.getFullYear() === today.getFullYear()) hs.add(dd.getDate());
      }
    });
    for (let d = 1; d <= dim; d++) {
      const date = new Date(today.getFullYear(), today.getMonth(), d);
      const diff = Math.floor((date - cs) / 86400000);
      const dic  = ((diff % cLen) + cLen) % cLen + 1;
      const isT  = d === today.getDate();
      let cls = 'n';
      if (hasData) {
        if (dic >= 1 && dic <= pLen)        cls = 'p';
        else if (Math.abs(dic - ovDay) === 0) cls = 'ov';
        else if (Math.abs(dic - ovDay) <= 3)  cls = 'f';
      }
      if (cls === 'n' && hs.has(d)) cls = 'hp';
      if (isT) cls += ' td';
      html += `<div class="cd ${cls}">${d}</div>`;
    }
    if ($('calG')) $('calG').innerHTML = html;
  }

  _renderInsights(history, sl, haLen) {
    const el = this.shadowRoot.getElementById('insL');
    if (!el) return;
    if (!history.length) { el.innerHTML = '<div class="ie">Înregistrează cicluri din ⚙️ pentru insights.</div>'; return; }
    const items = [];
    if (history.length >= 2) {
      const note = sl !== haLen ? ' (ajustat din istoric)' : '';
      items.push({ w: false, t: `<strong>Durata medie:</strong> ${sl} zile${note}, din ${history.length} cicluri.` });
    }
    if (isIrregular(history)) items.push({ w: true, t: `<strong>Ciclu neregulat detectat.</strong> Variațiile depășesc 4 zile.` });
    else if (history.length >= 3) items.push({ w: false, t: `✓ <strong>Ciclu regulat.</strong> Variațiile sunt normale.` });
    const tr = trendDir(history);
    if (tr === 'longer')  items.push({ w: true,  t: `<strong>Tendință:</strong> ciclurile devin mai lungi recent.` });
    if (tr === 'shorter') items.push({ w: true,  t: `<strong>Tendință:</strong> ciclurile devin mai scurte recent.` });
    if (tr === 'stable' && history.length >= 4) items.push({ w: false, t: `✓ <strong>Ciclu stabil</strong> în ultimele luni.` });
    if (history.length >= 5) items.push({ w: false, t: `🏆 <strong>${history.length} cicluri înregistrate!</strong> Predicțiile sunt precise.` });
    el.innerHTML = items.map(x => `<div class="ib ${x.w ? 'wi' : ''}">${x.t}</div>`).join('');
  }

  _renderHistory(history) {
    const el = this.shadowRoot.getElementById('hList');
    if (!el) return;
    if (!history.length) { el.innerHTML = '<div class="nh">Niciun ciclu înregistrat încă.</div>'; return; }
    const sa = [...history].sort((a, b) => new Date(a) - new Date(b));
    el.innerHTML = [...sa].reverse().map(d => {
      const idx = sa.indexOf(d);
      let ls = 'curent', lc = 'ok';
      if (idx < sa.length - 1) {
        const diff = Math.round((new Date(sa[idx + 1]) - new Date(d)) / 86400000);
        ls = diff + ' zile'; lc = (diff >= 21 && diff <= 35) ? 'ok' : '';
      }
      return `<div class="hr"><span class="hrd">${fmtDateL(new Date(d))}</span><span class="hrl ${lc}">${ls}</span><button class="hdl" data-date="${d}">✕</button></div>`;
    }).join('');

    // Event listeners pentru delete
    el.querySelectorAll('.hdl').forEach(btn => {
      btn.addEventListener('click', () => {
        const h = loadHistory().filter(x => x !== btn.dataset.date);
        saveHistory(h);
        this._render(this._lastSensors);
        this._showToast('🗑️ Șters');
      });
    });
  }

  // ── Save cycle ────────────────────────────────────────
  async _saveCycle() {
    const $ = id => this.shadowRoot.getElementById(id);
    const dv = $('inD').value;
    const cv = parseInt($('inC').value) || null;
    const pv = parseInt($('inP').value) || null;
    if (!dv) { this._showToast('⚠️ Selectează o dată'); return; }

    const btn = $('saveBtn');
    btn.disabled = true; btn.textContent = 'Se salvează…';

    // Salvează în istoric local
    const h = loadHistory();
    if (!h.includes(dv)) { h.push(dv); saveHistory(h); }

    const sl = smartLen(h, cv || 28);

    // Trimite la integrarea HA — folosim hass.callService, fără token!
    let saved = false;
    if (this._hass && this._entryId) {
      try {
        await this._hass.callService('cycle_tracker', 'update_cycle', {
          entry_id:         this._entryId,
          cycle_start_date: dv,
          cycle_length:     sl,
          period_length:    pv || 5,
        });
        saved = true;
      } catch (e) {
        console.warn('CycleTracker: callService error', e);
      }
    }

    btn.disabled = false; btn.textContent = '💾 Salvează în Home Assistant';
    this._showToast(saved ? '✅ Salvat în Home Assistant!' : '💾 Salvat local (HA nu a răspuns)');

    // Închide panoul
    $('iBody').classList.remove('open');
    $('iArr').classList.remove('open');
    this._inpOpen = false;
  }

  _toggleH() {
    this._histOpen = !this._histOpen;
    const body = this.shadowRoot.getElementById('hBody');
    const arr  = this.shadowRoot.getElementById('hArr');
    body.classList.toggle('open', this._histOpen);
    arr.classList.toggle('open', this._histOpen);
  }

  _toggleI() {
    this._inpOpen = !this._inpOpen;
    const body = this.shadowRoot.getElementById('iBody');
    const arr  = this.shadowRoot.getElementById('iArr');
    body.classList.toggle('open', this._inpOpen);
    arr.classList.toggle('open', this._inpOpen);
  }

  _showToast(msg) {
    const t = this.shadowRoot.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3200);
  }

  // Stochează ultimii senzori pentru re-render după delete
  _render(sensors) {
    if (sensors) this._lastSensors = sensors;
    this.__render(sensors || this._lastSensors);
  }
}

// Alias intern
CycleTrackerCard.prototype.__render = CycleTrackerCard.prototype._render;
// Fix: __render trebuie să fie funcția care face treaba
Object.defineProperty(CycleTrackerCard.prototype, '__render', {
  value: function(sensors) {
    const history  = loadHistory();
    const haPhase  = sensors?.cycle_phase?.state  || 'foliculara';
    const haDay    = parseInt(sensors?.cycle_day?.state   || 1);
    const haFert   = sensors?.fertility_level?.state      || 'scazut';
    const haDL     = parseInt(sensors?.days_until_period?.state ?? 27);
    const haProg   = parseInt(sensors?.cycle_progress?.state    || 0);
    const haCLen   = sensors?.cycle_day?.attributes?.cycle_length  || 28;
    const haPLen   = sensors?.cycle_day?.attributes?.period_length || 5;
    const haOvDay  = sensors?.cycle_day?.attributes?.ovulation_day || 14;
    const haNext   = sensors?.next_period_date?.state;
    const haOvul   = sensors?.ovulation_date?.state;
    const hasData  = !!sensors?.cycle_day;

    const sl = smartLen(history, haCLen);
    const ph = PHASES[haPhase] || PHASES.foliculara;
    const fp = FERT_PCT[haFert] || 5;
    const fl = FERT_LBL[haFert] || 'Scăzut';

    const $ = id => this.shadowRoot.getElementById(id);
    if (!$('phN')) return;

    const hero = $('phHero');
    if (hero) { hero.style.background = hasData ? ph.bg : 'rgba(255,255,255,0.04)'; hero.style.borderColor = hasData ? ph.br : 'rgba(255,255,255,0.08)'; }
    $('phN').textContent  = hasData ? ph.name : '—';
    $('phD').textContent  = hasData ? ph.desc : 'Adaugă ciclul din panoul ⚙️ de mai jos.';
    $('dayN').textContent = hasData ? haDay   : '—';

    const ab = $('alertB');
    if (ab) {
      if (hasData && haDL <= 3) { ab.className='ab warn'; $('aIco').textContent='🔔'; $('aTxt').innerHTML=haDL===0?'<strong>Menstruația poate începe azi!</strong>':`Menstruația în <strong>${haDL} ${haDL===1?'zi':'zile'}</strong>.`; }
      else if (hasData && haPhase==='ovulatie') { ab.className='ab info'; $('aIco').textContent='✨'; $('aTxt').innerHTML='<strong>Fertilitate maximă azi!</strong>'; }
      else ab.className='ab h';
    }

    setTimeout(() => {
      const ring=$('ringC'); if(ring) ring.style.strokeDashoffset=295.3-(haProg/100)*295.3;
      if($('rPct'))  $('rPct').textContent  = hasData ? haProg+'%' : '—';
      if($('rLeft')) $('rLeft').textContent = hasData ? haDL+' zile rămase' : '—';
    }, 80);

    if($('sCLen')) $('sCLen').textContent = sl+(history.length>=2?' 📊':'');
    if($('sOvul')) $('sOvul').textContent = haOvul ? fmtDate(new Date(haOvul)) : '—';
    if($('sNext')) $('sNext').textContent = haNext  ? fmtDate(new Date(haNext))  : '—';
    setTimeout(()=>{ const ff=$('ffill'); if(ff) ff.style.width=hasData?fp+'%':'0%'; },100);
    if($('fLbl')) $('fLbl').textContent = hasData ? fl : '—';

    this._buildCal(history, haCLen, haPLen, haOvDay, haDay, hasData);
    if($('recL')) $('recL').innerHTML = hasData ? ph.recs.map(r=>`<div class="rc"><div class="ri">${r.i}</div><div class="rt">${r.t}</div></div>`).join('') : '<div class="rc"><div class="rt" style="color:rgba(255,255,255,0.28)">Adaugă ciclul din panoul ⚙️ de mai jos.</div></div>';
    this._renderInsights(history, sl, haCLen);
    this._renderHistory(history);
    if($('hCnt')) $('hCnt').textContent = history.length;
  },
  writable: true, configurable: true
});

// Înregistrează custom element
customElements.define('cycle-tracker-card', CycleTrackerCard);
