import streamlit as st
import openai
from datetime import datetime, date, timedelta
import plotly.express as px
import pandas as pd
import json

openai.api_key = st.secrets.get("OPENAI_API_KEY", "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")

SUPPORTED_LANGUAGES = {
    "hu": "Magyar",
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
    "it": "Italiano",
    "pl": "Polski",
    "uk": "Українська",
    "cs": "Čeština",
    "sr": "Српски",
    "ru": "Русский",
    "ja": "日本語",
    "ko": "한국어"
}

if "language" not in st.session_state:
    headers = st.context.headers if hasattr(st, "context") and hasattr(st.context, "headers") else {}
    accept_language = headers.get("Accept-Language", "en")
    if accept_language:
        primary_lang = accept_language.split(",")[0].strip().lower()[:2]
        st.session_state.language = primary_lang if primary_lang in SUPPORTED_LANGUAGES else "en"
    else:
        st.session_state.language = "en"

translations = {
    "hu": {
        "title": "🌼 SoulGarden – Mentális Támogató AI",
        "caption": "Ez nem helyettesíti a szakmai segítséget! Krízisben hívd: 116-123",
        "weekly_summary": "📊 Heti összefoglaló",
        "summary_button": "Heti összefoglaló készítése",
        "daily_journal": "📔 Napi naplód",
        "journal_prompt": "Mi történt ma? Hogy érzed magad emiatt?",
        "journal_save": "Mentés ma",
        "mood_question": "Hogy érzed most magad 1-5 skálán?",
        "chat_placeholder": "Hogy vagy most? Mesélj...",
        "crisis": "Kérlek, hívd azonnal a Lelki Elsősegély Telefonszolgálatot: 116-123 (ingyenes, éjjel-nappal)!",
        "previous_entries": "Korábbi naplóbejegyzések",
        "language": "Nyelv",
        "dream_section": "🌙 Álomnapló",
        "dream_prompt": "Mit álmodtál ma éjjel?",
        "dream_save": "Álom mentése",
        "time_travel": "⏳ Időutazás",
        "music_suggestion": "🎶 Hangulatodhoz illő zene vagy meditáció",
        "garden": "🌿 A Te Lélek Kerted",
        "mantra": "🕉️ Heti Lélek Mantra",
        "mantra_button": "Kérd a heti lélek mantrádat ✨",
        "data_management": "📦 Adatmentés és visszaállítás",
        "export_button": "📥 Adatok exportálása (letöltés)",
        "import_label": "📂 Mentés feltöltése (import)",
    },
    "en": {
        "title": "🌼 SoulGarden – Mental Support AI",
        "caption": "This is not a substitute for professional help! In crisis, contact a local helpline.",
        "weekly_summary": "📊 Weekly Summary",
        "summary_button": "Generate Weekly Summary",
        "daily_journal": "📔 Daily Journal",
        "journal_prompt": "What happened today? How do you feel about it?",
        "journal_save": "Save Today",
        "mood_question": "How are you feeling right now on a scale of 1-5?",
        "chat_placeholder": "How are you feeling? Tell me...",
        "crisis": "Please contact a crisis helpline immediately (e.g., US: 988, UK: 116 123)",
        "previous_entries": "Previous Entries",
        "language": "Language",
        "dream_section": "🌙 Dream Journal",
        "dream_prompt": "What did you dream about tonight?",
        "dream_save": "Save Dream",
        "time_travel": "⏳ Time Travel",
        "music_suggestion": "🎶 Music or meditation for your mood",
        "garden": "🌿 Your Soul Garden",
        "mantra": "🕉️ Weekly Soul Mantra",
        "mantra_button": "Request your weekly soul mantra ✨",
        "data_management": "📦 Data Backup & Restore",
        "export_button": "📥 Export data (download)",
        "import_label": "📂 Upload backup (import)",
    },
    "de": {
        "title": "🌼 SoulGarden – Mentale Unterstützungs-KI",
        "caption": "Dies ersetzt keine professionelle Hilfe! In einer Krise rufe eine lokale Hotline an.",
        "weekly_summary": "📊 Wöchentliche Zusammenfassung",
        "summary_button": "Wöchentliche Zusammenfassung erstellen",
        "daily_journal": "📔 Tägliches Tagebuch",
        "journal_prompt": "Was ist heute passiert? Wie fühlst du dich dabei?",
        "journal_save": "Heute speichern",
        "mood_question": "Wie fühlst du dich gerade auf einer Skala von 1-5?",
        "chat_placeholder": "Wie geht es dir gerade? Erzähl mir...",
        "crisis": "Bitte kontaktiere sofort die Telefonseelsorge: 0800 111 0 111",
        "previous_entries": "Frühere Einträge",
        "language": "Sprache",
        "dream_section": "🌙 Traumtagebuch",
        "dream_prompt": "Was hast du heute Nacht geträumt?",
        "dream_save": "Traum speichern",
        "time_travel": "⏳ Zeitreise",
        "music_suggestion": "🎶 Musik oder Meditation zu deiner Stimmung",
        "garden": "🌿 Dein Seelengarten",
        "mantra": "🕉️ Wöchentliches Seelenmantra",
        "mantra_button": "Bitte dein wöchentliches Seelenmantra ✨",
        "data_management": "📦 Datensicherung & Wiederherstellung",
        "export_button": "📥 Daten exportieren (Download)",
        "import_label": "📂 Backup hochladen (Import)",
    },

}

lang = st.session_state.language
_ = translations.get(lang, translations["en"])  # fallback angol

# === SYSTEM PROMPT (nyelvenként + krízisvonalak) ===
crisis_helplines = {
    "hu": "Kérlek, hívd azonnal a Lelki Elsősegélyt: 116-123",
    "en": "Please call a crisis helpline immediately (US: 988 | UK: 116 123)",
    "de": "Bitte rufe sofort die Telefonseelsorge an: 0800 111 0 111",
    # ... további nyelvek a korábbi üzenetből
}

base_prompts = {
    "hu": "Te egy kedves, empátiás mentális támogató AI vagy. SOHA nem vagy pszichológus vagy orvos – mindig emlékeztess rá!",
    "en": "You are a kind, empathetic mental support AI. You are NEVER a psychologist or doctor – always remind the user of this!",
    "de": "Du bist eine freundliche, empathische KI zur mentalen Unterstützung. Du bist NIEMALS Psychologe oder Arzt – erinnere immer daran!",
}

def get_system_prompt(latest_mood=None):
    mood_text = ""
    if latest_mood:
        mood_emojis = ["nagyon rossz", "rossz", "semleges", "jó", "nagyon jó"]
        mood_text = f"A felhasználó legutóbbi hangulata: {latest_mood}/5 ({mood_emojis[latest_mood-1]})."
    return f"""
    {base_prompts.get(lang, base_prompts["en"])}
    Ha krízishelyzetről van szó, azonnal írd: "{crisis_helplines.get(lang, crisis_helplines["en"])}"
    {mood_text}
    Válaszolj mindig {lang.title()} nyelven.
    Legyél támogató, rövid és melegszívű.
    """

# === SESSION STATE ===
if "messages" not in st.session_state:
    st.session_state.messages = []
if "moods" not in st.session_state:
    st.session_state.moods = []  # (datetime, score)
if "journal" not in st.session_state:
    st.session_state.journal = {}  # date -> text
if "dreams" not in st.session_state:
    st.session_state.dreams = {}  # date -> text

latest_mood = st.session_state.moods[-1][1] if st.session_state.moods else None

if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
    st.session_state.messages = [{"role": "system", "content": get_system_prompt(latest_mood)}]
else:
    st.session_state.messages[0]["content"] = get_system_prompt(latest_mood)

st.set_page_config(page_title="SoulGarden", page_icon="🌼", layout="centered")

st.markdown("""
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/static/icon-192x192.png">
<meta name="theme-color" content="#c4b5fd">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
""", unsafe_allow_html=True)

st.title(_["title"])
st.caption(_["caption"])

today = date.today()

with st.sidebar:
    st.header("⚙️ " + _["language"])
    lang_options = SUPPORTED_LANGUAGES
    current_lang_name = lang_options.get(lang, "English")
    selected_lang_name = st.selectbox(_["language"], options=list(lang_options.values()), index=list(lang_options.values()).index(current_lang_name))
    selected_code = next(code for code, name in lang_options.items() if name == selected_lang_name)
    if selected_code != lang:
        st.session_state.language = selected_code
        st.rerun()

if st.session_state.moods:
    df = pd.DataFrame(st.session_state.moods, columns=["Idő", "Hangulat"])
    df["Idő"] = pd.to_datetime(df["Idő"])
    fig = px.line(df, x="Idő", y="Hangulat", markers=True, range_y=[0.5, 5.5], title="Hangulatod alakulása")
    fig.update_traces(line=dict(width=3), marker=dict(size=10))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### " + _["garden"])

total_entries = len(st.session_state.journal) + len(st.session_state.dreams)
total_moods = len(st.session_state.moods)
avg_mood = sum(score for _, score in st.session_state.moods) / total_moods if total_moods > 0 else 3

if total_entries == 0:
    description = "A kerted még csak várja az első magokat. Kezdj el írni, és hamarosan virágba borul! 🌱"
    garden_emojis = "🌱 🌱 🌱"
elif total_entries < 5:
    description = "Az első hajtások már kinéznek a földből. Folytasd, és szép kerted lesz! 🌿"
    garden_emojis = "🌱 🌿 🌷"
elif avg_mood < 2.5:
    description = "A kerted most pihen, néhány növény lehajtotta a fejét. De a gondoskodásod segít neki újra virágozni. 💜"
    garden_emojis = "🌿 🍂 🌧️"
elif total_entries < 20:
    description = "A kerted szépen fejlődik! Már látni a színes virágokat és zöld leveleket. 🌸"
    garden_emojis = "🌿 🌷 🌹 🦋"
else:
    description = "A Lélek Kerted gyönyörűen virágzik! Tele van élettel, színekkel és békével. Nagyon büszke vagyok rád! ✨"
    garden_emojis = "🌸 🌺 🌼 🌷 🦋 ✨"

st.info(description)

mood_extras = ""
if latest_mood:
    if latest_mood <= 2:
        mood_extras = " 🌧️ 🍂"
    elif latest_mood == 3:
        mood_extras = " ☁️"
    elif latest_mood == 4:
        mood_extras = " 🌸 🐦"
    else:
        mood_extras = " 🌞 🦋 ✨"

st.markdown(f"<h1 style='text-align: center; font-size: 60px;'>{garden_emojis + mood_extras}</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Virágok (bejegyzések)", total_entries)
col2.metric("Öntözések (hangulatok)", total_moods)
col3.metric("Átlagos napfény", f"{avg_mood:.1f}/5 ☀️" if total_moods > 0 else "—")

st.markdown("### " + _["time_travel"])

travel_days = st.slider("Hány nappal ezelőtt szeretnél visszatekinteni?", 1, 730, 365)
target_date = today - timedelta(days=travel_days)


st.markdown("---")
st.caption("Köszönöm, hogy gondozod a lelkedet. A SoulGarden mindig itt van Neked. 💜")
