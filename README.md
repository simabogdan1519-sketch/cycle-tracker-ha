# 🌸 Cycle Tracker – Home Assistant Integration

Integrare completă pentru monitorizarea ciclului menstrual, instalabilă din **HACS** fără editare YAML.

---

## ⚡ Instalare rapidă (5 pași)

### Pasul 1 – Adaugă repository-ul în HACS
1. Deschide **HACS** din meniul lateral HA
2. Click pe **⋮ (trei puncte)** → **Custom repositories**
3. La URL introdu: `https://github.com/youruser/cycle-tracker-ha`
4. Categoria: **Integration**
5. Click **Add** → caută **Cycle Tracker** și instalează

### Pasul 2 – Configurare prin UI (zero YAML!)
1. Mergi la **Settings → Devices & Services → + Add Integration**
2. Caută **Cycle Tracker**
3. Completează formularul:
   - **Numele** (ex: Ana)
   - **Prima zi a ultimei menstruații**
   - **Durata ciclului** (implicit 28 zile)
   - **Durata perioadei** (implicit 5 zile)
   - **Telefonul pentru notificări** (selectat din listă)
   - Bifează notificările dorite ✅
4. Click **Submit** – gata! Senzorii apar automat.

### Pasul 3 – Copiază cardul HTML
1. Copiază `www/cycle_tracker_card.html` în `config/www/`
2. Deschide fișierul și completează în secțiunea `CONFIG`:
   ```javascript
   const CONFIG = {
     token:   'TOKEN_EI',    // vezi Pasul 4
     entryId: 'ENTRY_ID',    // vezi Pasul 5
     haUrl:   '',
   };
   ```

### Pasul 4 – Generează token (din contul ei)
1. Loghează-te cu **contul ei** în HA
2. Click pe **avatar** (dreapta jos) → **Security**
3. Scroll jos → **Long-Lived Access Tokens** → **Create Token**
4. Copiază token-ul și pune-l în `CONFIG.token`

### Pasul 5 – Găsește Entry ID
1. **Settings → Devices & Services → Cycle Tracker**
2. Click pe **⋮** → **System Information** (sau URL conține entry_id)
3. Alternativ: **Developer Tools → States** și caută `sensor.*_cycle_day`
4. Pune entry_id în `CONFIG.entryId`

### Pasul 6 – Adaugă cardul în dashboard
```yaml
type: iframe
url: /local/cycle_tracker_card.html
aspect_ratio: "130%"
title: Ciclul meu
```

---

## 🔒 Confidențialitate per user

- Toate datele sunt stocate **local în HA**, nu în cloud
- Entitățile sunt prefixate cu numele ei: `sensor.ana_cycle_day`
- Notificările merg **exclusiv pe telefonul ei**
- Cardul folosește **tokenul ei personal** – nimeni altcineva nu poate accesa

---

## 📊 Senzori creați automat

| Entitate | Descriere |
|----------|-----------|
| `sensor.{nume}_cycle_day` | Ziua curentă din ciclu (1–N) |
| `sensor.{nume}_cycle_phase` | Faza: menstruatie / foliculara / ovulatie / luteala |
| `sensor.{nume}_fertility_level` | Nivel fertilitate: scazut → maxim |
| `sensor.{nume}_days_until_period` | Zile rămase până la menstruație |
| `sensor.{nume}_next_period_date` | Data estimată a următoarei menstruații |
| `sensor.{nume}_ovulation_date` | Data estimată a ovulației |
| `sensor.{nume}_cycle_progress` | Progres ciclu (%) |

---

## 🔔 Notificări automate

| Trigger | Mesaj |
|---------|-------|
| Cu 3 zile înainte de menstruație | „Pregătește-te! Menstruația în 3 zile." |
| Ziua 1 a ciclului | „Astăzi ar trebui să înceapă menstruația." |
| Ovulație | „Fertilitate maximă azi! ✨" |
| În fiecare dimineață la 08:00 | Rezumat: faza + zile rămase |
| Ciclu > 35 zile | Reminder să actualizeze data |

---

## ⚙️ Actualizare date

**Din cardul HTML:** click pe ⚙️ → completează data → Salvează  
**Din HA UI:** Settings → Integrations → Cycle Tracker → **Configurare**  
**Din automatizări:**
```yaml
service: cycle_tracker.update_cycle
data:
  entry_id: "abc123"
  cycle_start_date: "2024-03-15"
  cycle_length: 28
  period_length: 5
```

---

## 🗂️ Structura fișierelor

```
custom_components/cycle_tracker/
├── __init__.py          # Setup, coordinator, servicii
├── config_flow.py       # Wizard UI de configurare
├── sensor.py            # 7 senzori auto-creați
├── const.py             # Constante
├── manifest.json        # Metadata HACS
├── services.yaml        # Documentație servicii
├── strings.json         # Texte UI
└── translations/
    ├── ro.json          # Română
    └── en.json          # Engleză

www/
└── cycle_tracker_card.html   # Cardul vizual (copiază în config/www/)
```
