# 🌸 Cycle Tracker – Home Assistant Integration

Integrare completă pentru monitorizarea ciclului menstrual, instalabilă din **HACS**.

---

## ⚡ Instalare

### Pasul 1 – Adaugă repository-ul în HACS

1. HACS → ⋮ → **Custom repositories**
2. URL: `https://github.com/simabogdan1519-sketch/cycle-tracker-ha`
3. Categoria: **Integration**
4. Click **Add** → caută **Cycle Tracker** → instalează

### Pasul 2 – Configurare

1. **Settings → Devices & Services → + Add Integration**
2. Caută **Cycle Tracker**
3. Completează: Nume, Data start, Durata ciclului, Durata perioadei

### Pasul 3 – Adaugă cardul vizual

1. Copiază `www/cycle-tracker-card.js` în `config/www/`
2. **Settings → Dashboards → Resources → Add Resource**:
   - URL: `/local/cycle-tracker-card.js`
   - Type: JavaScript Module
3. Adaugă cardul în dashboard:
```yaml
type: custom:cycle-tracker-card
```

---

## 📊 Senzori creați automat

| Entitate | Descriere |
|---|---|
| `sensor.{nume}_cycle_day` | Ziua curentă din ciclu |
| `sensor.{nume}_phase` | Faza: menstruatie / foliculara / ovulatie / luteala |
| `sensor.{nume}_fertility` | Nivel fertilitate |
| `sensor.{nume}_days_until_period` | Zile până la menstruație |
| `sensor.{nume}_next_period_date` | Data estimată a următoarei menstruații |
| `sensor.{nume}_ovulation_date` | Data estimată a ovulației |
| `sensor.{nume}_cycle_progress` | Progres ciclu (%) |

---

## ⚙️ Actualizare date din card

Cardul are un panou ⚙️ de unde se poate înregistra un ciclu nou direct din Lovelace, fără token, fără config extra.

---

## 🔒 Confidențialitate

- Toate datele sunt stocate local în HA
- Entitățile sunt prefixate cu numele utilizatoarei
- Notificările merg exclusiv pe telefonul ei
