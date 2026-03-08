update_cycle:
  name: Update Cycle
  description: Înregistrează sau actualizează ciclul curent.
  fields:
    entry_id:
      name: Entry ID
      description: ID-ul config entry (se găsește automat din card).
      required: true
      selector:
        text:
    cycle_start_date:
      name: Data start ciclu
      description: Prima zi a menstruației (format YYYY-MM-DD).
      required: true
      selector:
        date:
    period_length:
      name: Durata menstruației (zile)
      description: Câte zile durează sângerarea. Default 5.
      required: false
      default: 5
      selector:
        number:
          min: 1
          max: 10
          mode: slider
    flow_intensity:
      name: Intensitate flux
      description: "Intensitatea fluxului: ușor, mediu, abundent."
      required: false
      default: mediu
      selector:
        select:
          options:
            - ușor
            - mediu
            - abundent

add_past_cycle:
  name: Add Past Cycle
  description: Adaugă un ciclu din trecut pentru a îmbunătăți predicțiile.
  fields:
    entry_id:
      name: Entry ID
      description: ID-ul config entry.
      required: true
      selector:
        text:
    date:
      name: Data start
      description: Prima zi a menstruației din trecut (format YYYY-MM-DD).
      required: true
      selector:
        date:
    period_length:
      name: Durata menstruației (zile)
      description: Câte zile a durat sângerarea. Default 5.
      required: false
      default: 5
      selector:
        number:
          min: 1
          max: 10
          mode: slider
    flow_intensity:
      name: Intensitate flux
      description: "Intensitatea fluxului: ușor, mediu, abundent."
      required: false
      default: mediu
      selector:
        select:
          options:
            - ușor
            - mediu
            - abundent

delete_cycle:
  name: Delete Cycle
  description: Șterge un ciclu din istoric după dată.
  fields:
    entry_id:
      name: Entry ID
      description: ID-ul config entry.
      required: true
      selector:
        text:
    date:
      name: Data
      description: Data ciclului de șters (format YYYY-MM-DD).
      required: true
      selector:
        date:
