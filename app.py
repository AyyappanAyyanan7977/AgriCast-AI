import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path
from agricast.ml.pipeline import load_dataset, train_and_evaluate, load_model, predict_one
from agricast.rag.retriever import BM25Retriever
from agricast.rag.ingest import ingest_directory
from agricast.services.status import system_status
from agricast.services.data_validation import keep_first_duplicate_columns
from agricast.services.dataset_manager import save_uploaded_dataset
from agricast.services.navigation import PAGE_OPTIONS, PAGE_MAP, resolve_navigation_target
import asyncio
import sys
import base64
import json
import os
import urllib.parse
import urllib.request
import urllib.error

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

st.set_page_config(page_title="AgriCast | Field Intelligence", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
px.defaults.template = "plotly_white"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');
:root{--bg:#F4F8F2;--surface:#FFFFFF;--surface2:#EAF5E8;--line:#DCE9DC;--ink:#102B20;--muted:#61776A;--green:#087F4F;--green2:#13A568;--lime:#C8F169;--blue:#1688E8;--violet:#7B61FF;--orange:#F59E0B;--red:#E05252;--shadow:0 12px 32px rgba(16,59,37,.075)}
html,body,[class*="css"]{font-family:'DM Sans',Manrope,ui-sans-serif,system-ui,sans-serif;color:var(--ink)}
.stApp{background:radial-gradient(ellipse at 92% 0%,rgba(200,241,105,.20),transparent 26%),radial-gradient(ellipse at 0% 22%,rgba(19,165,104,.08),transparent 25%),linear-gradient(180deg,#F8FBF7 0%,#F1F7F0 55%,#EDF5EC 100%);color:var(--ink)}
.block-container{padding-top:1.25rem;padding-bottom:3rem;max-width:1600px}
h1,h2,h3{font-family:Manrope,sans-serif;letter-spacing:-.045em!important;color:var(--ink);font-weight:800}
h1{font-size:clamp(30px,3vw,46px)!important;line-height:1.12}h2{font-size:23px!important}h3{font-size:17px!important}
p,li{line-height:1.68;color:#455F50}
[data-testid="stHeader"]{background:rgba(248,251,247,.78)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0B3927 0%,#0C5135 55%,#073522 100%);border-right:1px solid rgba(255,255,255,.08)}
[data-testid="stSidebar"] .block-container{padding-top:1.3rem}
[data-testid="stSidebar"] [data-testid="stRadio"] label{font-size:13px;color:#EAF8EC}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{color:var(--lime)}
[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(240,249,239,.96));padding:20px;border:1px solid rgba(192,220,195,.85);border-radius:20px;box-shadow:var(--shadow);min-height:118px;transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease;position:relative;overflow:hidden}
[data-testid="stMetric"]:before{content:"";position:absolute;left:0;top:0;width:4px;height:100%;background:linear-gradient(180deg,var(--green2),var(--lime));opacity:.95}
[data-testid="stMetric"]:hover{transform:translateY(-3px);box-shadow:0 18px 38px rgba(16,59,37,.12);border-color:#A9D9B1}
[data-testid="stMetricLabel"]{color:#657C6B;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.09em}
[data-testid="stMetricValue"]{color:#102B20!important;font-family:Manrope,sans-serif;font-weight:800;letter-spacing:-.055em}
[data-testid="stMetricDelta"]{font-size:11px}
div.stButton>button[kind="primary"],button[kind="primaryFormSubmit"]{background:linear-gradient(115deg,#087F4F,#13A568);border:1px solid #087F4F;border-radius:12px;font-weight:800;color:#FFFFFF;min-height:44px;box-shadow:0 7px 16px rgba(8,127,79,.18);transition:transform .2s ease,box-shadow .2s ease,filter .2s ease}
div.stButton>button[kind="primary"]:hover,button[kind="primaryFormSubmit"]:hover{filter:brightness(1.06);transform:translateY(-2px);box-shadow:0 12px 24px rgba(8,127,79,.24)}
div.stButton>button{border-radius:12px;border:1px solid #D5E4D6;background:rgba(255,255,255,.92);color:#17452F;min-height:42px;transition:all .2s ease}
div.stButton>button:hover{border-color:#43B77B;color:#087F4F;transform:translateY(-2px);box-shadow:0 8px 18px rgba(16,59,37,.08)}
.ag-card,.panel{background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(244,250,243,.96));border:1px solid #DCE9DC;border-radius:20px;padding:22px;box-shadow:var(--shadow);transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease}
.ag-card:hover,.panel:hover{transform:translateY(-3px);box-shadow:0 18px 40px rgba(16,59,37,.10);border-color:#B7DDBD}
.eyebrow{color:#07804D;text-transform:uppercase;letter-spacing:.15em;font:700 10px 'Space Mono',monospace}
.note,.small-muted{color:#61776A;font-size:12px;line-height:1.65}
.stAlert{border-radius:15px;border:1px solid #DCE9DC;background:linear-gradient(120deg,#F0F8EA,#F8FBF4);color:var(--ink)}
div[data-testid="stDataFrame"]{border:1px solid #DCE9DC;border-radius:15px;overflow:hidden;box-shadow:0 5px 16px rgba(16,59,37,.04)}
[data-testid="stFileUploader"]{border-radius:15px;background:#FBFEFA;border:1.5px dashed #8DC8A0;padding:8px}
input,textarea,select{border-radius:12px!important}
[data-baseweb="select"]>div,[data-baseweb="input"]>div,textarea{background:#FFFFFF!important;border-color:#D4E4D5!important;color:#102B20!important;border-radius:12px!important}
button:focus-visible,input:focus-visible,textarea:focus-visible,[role="radiogroup"]:focus-visible{outline:3px solid #13A568!important;outline-offset:3px}
/* Horizontal website navigation with a high-contrast active state. */
div[data-testid="stRadio"]>label{display:none}
div[data-testid="stRadio"] div[role="radiogroup"]{display:flex;flex-wrap:wrap;gap:8px;padding:7px;background:rgba(230,241,229,.72);border:1px solid #DCE9DC;border-radius:16px}
div[data-testid="stRadio"] div[role="radiogroup"] label{background:rgba(255,255,255,.88);border:1px solid transparent;border-radius:11px;padding:9px 14px;transition:all .18s ease;box-shadow:0 1px 2px rgba(16,59,37,.025)}
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked){background:linear-gradient(120deg,#087F4F,#13A568);border-color:#087F4F;color:#FFFFFF;box-shadow:0 5px 13px rgba(8,127,79,.19)}
div[data-testid="stRadio"] div[role="radiogroup"] label p{font-size:12px;font-weight:800;color:inherit;margin:0}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover{border-color:#9ED5AE;transform:translateY(-1px)}
hr{border-color:#DCE9DC!important}
div[data-testid="stExpander"]{border:1px solid #DCE9DC;border-radius:15px;background:rgba(255,255,255,.86);overflow:hidden}
div[data-testid="stExpander"] summary{font-weight:700}
[data-testid="stProgressBar"]>div>div{background:linear-gradient(90deg,#087F4F,#C8F169)}
.ag-topbar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px;margin-bottom:24px;background:rgba(255,255,255,.86);border:1px solid #DCE9DC;border-radius:16px;box-shadow:0 5px 18px rgba(16,59,37,.04);backdrop-filter:blur(14px)}
.ag-pill{display:inline-flex;align-items:center;gap:7px;border:1px solid #BCE6C5;background:#E9F8E9;color:#087F4F;padding:8px 12px;border-radius:999px;font:700 10px 'Space Mono',monospace;text-transform:uppercase;letter-spacing:.04em}
.ag-pill-dot{width:7px;height:7px;border-radius:50%;background:#20C879;box-shadow:0 0 0 4px rgba(32,200,121,.13);animation:ag-pulse 2.2s ease-in-out infinite}
.ag-muted{font:400 10px 'Space Mono',monospace;color:#61776A;letter-spacing:.04em}
.hero-panel{padding:30px 32px;border:1px solid rgba(200,241,105,.22);border-radius:24px;background:radial-gradient(ellipse at 90% 20%,rgba(200,241,105,.22),transparent 32%),radial-gradient(ellipse at 70% 120%,rgba(19,165,104,.38),transparent 38%),linear-gradient(115deg,#073B28,#0B6240 60%,#0B3927);position:relative;overflow:hidden;margin:8px 0 20px;color:#F5FFF4;box-shadow:0 18px 42px rgba(7,59,40,.19);animation:ag-rise .55s ease both}
.hero-panel:after{content:'AG / FIELD INTELLIGENCE';position:absolute;right:24px;top:22px;color:#D9F6B0;font:700 10px 'Space Mono',monospace;letter-spacing:.12em}
.hero-panel h1,.hero-panel h2,.hero-panel h3{color:#F5FFF4!important}.hero-panel p,.hero-panel .hero-sub{color:#D8F0DE;font-size:14px;max-width:700px;margin-top:8px}
.section-kicker{color:#07804D;font:700 10px 'Space Mono',monospace;letter-spacing:.15em;text-transform:uppercase;margin-bottom:8px}
.signal-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 0;border-bottom:1px solid #DCE9DC}
.signal-row:last-child{border-bottom:0}
.signal-label{color:#61776A;font-size:12px}.signal-value{color:#102B20;font:700 11px 'Space Mono',monospace}
@keyframes ag-rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes ag-pulse{0%,100%{box-shadow:0 0 0 4px rgba(32,200,121,.13)}50%{box-shadow:0 0 0 7px rgba(32,200,121,.035)}}
@media(max-width:768px){.block-container{padding:1rem .8rem 2rem}h1{font-size:29px!important}[data-testid="stMetric"]{padding:14px;min-height:98px}.hero-panel{padding:23px}.hero-panel:after{display:none}div[data-testid="stRadio"] div[role="radiogroup"]{gap:5px}div[data-testid="stRadio"] div[role="radiogroup"] label{padding:7px 10px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}

/* Premium agricultural visual system */
.ag-brand-mark{width:46px;height:46px;display:grid;place-items:center;border-radius:15px;background:linear-gradient(145deg,#0B9B58,#6FCB55);box-shadow:0 8px 18px rgba(8,127,79,.22);flex:0 0 46px}
.ag-brand-mark svg{width:33px;height:33px}.ag-brand-title{font:800 25px/1.05 Manrope,sans-serif;letter-spacing:-1.1px;color:#102B20}.ag-brand-tag{font:600 10px/1.6 'DM Sans',sans-serif;color:#61776A}
.ag-hero-image{position:relative;overflow:hidden;min-height:300px;border-radius:24px;padding:30px 32px;background-size:cover;background-position:center 55%;box-shadow:0 20px 48px rgba(8,55,35,.18);margin:8px 0 22px;display:flex;align-items:center}
.ag-hero-image:before{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(5,48,31,.90),rgba(5,48,31,.62) 46%,rgba(5,48,31,.12))}.ag-hero-content{position:relative;z-index:1;max-width:720px;color:white}.ag-hero-content h1{color:#fff!important;font-size:clamp(31px,3.2vw,48px)!important;letter-spacing:-.055em!important}.ag-hero-content p{color:#F0F8EF;font-size:15px;max-width:630px;line-height:1.7}
.ag-trust-chip{display:inline-flex;align-items:center;gap:7px;border:1px solid rgba(255,255,255,.28);background:rgba(5,55,34,.35);backdrop-filter:blur(8px);color:#fff;padding:8px 11px;border-radius:999px;font-size:11px;font-weight:700;margin:12px 6px 0 0}
.ag-weather-glass{position:absolute;right:22px;bottom:20px;width:min(330px,34%);z-index:2;border:1px solid rgba(255,255,255,.26);background:rgba(5,55,34,.78);backdrop-filter:blur(15px);color:white;border-radius:19px;padding:18px 20px;box-shadow:0 12px 35px rgba(0,0,0,.16)}.ag-weather-glass strong{color:#fff}.ag-weather-glass .weather-number{font-size:29px;font-weight:800;letter-spacing:-1px;color:white}
.ag-quick-action{display:flex;align-items:center;gap:13px;min-height:95px;padding:14px;border-radius:19px;border:1px solid #E0EBE0;background:linear-gradient(135deg,#fff,#F6FBF4);box-shadow:0 7px 18px rgba(16,59,37,.045);transition:transform .2s ease,box-shadow .2s ease}.ag-quick-action:hover{transform:translateY(-4px);box-shadow:0 15px 28px rgba(16,59,37,.11)}.ag-action-icon{width:46px;height:46px;flex:0 0 46px;border-radius:15px;display:grid;place-items:center;color:white;font-size:22px;box-shadow:0 6px 14px rgba(8,127,79,.18)}.ag-action-title{font-size:13px;font-weight:800;color:#102B20;margin-bottom:4px}.ag-action-sub{font-size:11px;color:#61776A;line-height:1.5}
.ag-page-banner{border-radius:20px;padding:23px 26px;margin:6px 0 20px;background:linear-gradient(115deg,#0B5135,#087F4F 64%,#61A94B);color:white;box-shadow:0 12px 30px rgba(8,90,54,.15);position:relative;overflow:hidden}.ag-page-banner:after{content:'AGRICAST / FIELD INTELLIGENCE';position:absolute;right:20px;top:20px;font:700 9px 'Space Mono',monospace;letter-spacing:.12em;color:#D9F6B0}.ag-page-banner h1{color:#fff!important;margin:4px 0 8px!important}.ag-page-banner p{color:#E5F5E8!important;margin:0;max-width:760px}
@media(max-width:900px){.ag-weather-glass{position:relative;right:auto;bottom:auto;width:100%;margin-top:22px}.ag-hero-image{display:block;padding:24px;min-height:0}}@media(max-width:640px){.ag-brand-title{font-size:22px}.ag-hero-image{padding:20px}.ag-page-banner:after{display:none}}


/* Reference-matched application shell: white sidebar, forest-green active state, shared photo header. */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#FFFFFF 0%,#FBFEFA 72%,#F0F8EE 100%)!important;border-right:1px solid #DDEBDD!important}
[data-testid="stSidebar"]>div:first-child{background:transparent!important}
[data-testid="stSidebar"] .block-container{padding:1rem .8rem 1.2rem!important}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#132D20}
.sidebar-brand{display:flex;align-items:center;gap:9px;padding:8px 4px 23px;border-bottom:1px solid #E4EEE2;margin-bottom:18px}
.sidebar-leaf{width:39px;height:39px;border-radius:13px;display:grid;place-items:center;background:linear-gradient(145deg,#07964F,#73CB4F);color:#fff;font-size:27px;box-shadow:0 5px 13px #0A8B4A24}
.sidebar-title{font:800 19px/1.1 Manrope,sans-serif;color:#102B20;letter-spacing:-.7px;white-space:nowrap}.sidebar-title span{color:#07884D}
.sidebar-tag{font-size:9px;color:#627769;line-height:1.5;margin-top:3px;white-space:nowrap}
.sidebar-section-label{font:700 9px 'Space Mono',monospace;letter-spacing:.15em;color:#84968A;margin:0 0 7px 8px}
[data-testid="stSidebar"] div[data-testid="stRadio"]>label{display:none!important}
[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"]{display:flex!important;flex-direction:column!important;gap:5px!important;padding:0!important;background:transparent!important;border:0!important}
[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label{display:flex!important;align-items:center!important;width:100%!important;min-height:39px!important;padding:9px 11px!important;background:transparent!important;border:1px solid transparent!important;border-radius:11px!important;color:#152C21!important;box-shadow:none!important;transform:none!important}
[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label p{font-size:12px!important;font-weight:650!important;color:inherit!important;margin:0!important}
[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked){background:linear-gradient(110deg,#07874C,#0A9C59)!important;color:#fff!important;box-shadow:0 6px 13px #07874C25!important}
[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label:hover{background:#ECF8EC!important;border-color:#D6EED7!important;color:#087F4F!important}
.sidebar-bottom{margin-top:clamp(22px,12vh,110px);padding:16px 10px 18px;text-align:center;border:1px solid #E0EDE0;border-radius:18px;background:linear-gradient(145deg,#FFFFFF,#F0F9ED);position:relative;overflow:hidden}
.sidebar-bottom:after{content:"";position:absolute;bottom:-25px;left:-12%;width:125%;height:44px;border-radius:50%;background:#B9E8A9;opacity:.45}
.sidebar-bottom-icon{font-size:29px}.sidebar-bottom-title{font-weight:800;color:#087F4F;font-size:13px}.sidebar-bottom-sub{font-weight:800;color:#102B20;font-size:14px}
.utility-icon{height:38px;width:38px;display:grid;place-items:center;border:1px solid #E0EBDF;background:#fff;border-radius:50%;font-size:19px;color:#153B27;box-shadow:0 4px 12px #173D2710}
.profile-chip{display:flex;align-items:center;gap:8px;white-space:nowrap;padding:5px 7px;border:1px solid #E1ECE0;border-radius:13px;background:#fff}
.profile-avatar{height:31px;width:31px;border-radius:50%;display:grid;place-items:center;background:#4A2D16;color:#fff;font-weight:800}
.profile-chip b{display:block;font-size:10px;color:#152B20}.profile-chip small{display:block;font-size:9px;color:#728276}
.shared-hero{min-height:265px!important;margin-top:2px!important;margin-bottom:0!important;padding:28px 30px!important;border-radius:22px 22px 20px 20px!important;background-position:center 54%!important}
.shared-hero:before{background:linear-gradient(90deg,rgba(4,43,27,.88),rgba(4,43,27,.55) 48%,rgba(4,43,27,.10))!important}
.shared-hero .ag-hero-content{max-width:59%;padding-right:12px}
.shared-hero .ag-hero-content h1{font-size:clamp(27px,2.7vw,41px)!important;margin:.1rem 0 .4rem!important}
.hero-eyebrow{font:700 9px 'Space Mono',monospace;letter-spacing:.16em;color:#D7F5A9;margin-bottom:9px}
.shared-hero .ag-weather-glass{width:min(340px,35%);right:18px;bottom:17px;padding:16px 17px;border-radius:18px}
.weather-head{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:12px}
.demo-pill{font:700 8px 'Space Mono',monospace;color:#E0F6A9;background:#FFFFFF17;border:1px solid #FFFFFF38;border-radius:999px;padding:4px 6px}
.weather-main{display:flex;align-items:center;gap:12px;margin:12px 0 10px}
.weather-sun{font-size:35px;color:#FBD34D}.weather-caption{font-size:11px;color:#E2F3E5}
.weather-line{display:flex;justify-content:space-between;gap:10px;padding:6px 0;border-top:1px solid #FFFFFF20;font-size:10px;color:#D5E9D8}
.weather-line b{color:#fff;font-weight:650}.weather-note{font-size:9px;line-height:1.45;color:#D5E9D8;margin-top:7px}
.global-context-strip{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:10px 14px;margin:0 0 19px;border:1px solid #DCE9DC;border-top:0;border-radius:0 0 14px 14px;background:linear-gradient(90deg,#F0F9EB,#FFFFFF 65%);font-size:10px;color:#61776A}
.global-context-strip span:first-child{font-weight:800;color:#087F4F}.global-context-strip i{display:inline-block;width:7px;height:7px;border-radius:50%;background:#20B96B;margin-right:6px;box-shadow:0 0 0 3px #20B96B20}
.ag-page-banner{display:none!important}
/* Decorative crop-row curves persist at the bottom of every page without blocking controls. */
.stApp:after{content:"";position:fixed;z-index:0;pointer-events:none;left:0;right:0;bottom:-1px;height:58px;opacity:.7;background:
radial-gradient(120% 85px at 8% 100%,rgba(95,190,77,.42) 0 35%,transparent 36%),
radial-gradient(105% 95px at 78% 110%,rgba(8,127,79,.30) 0 34%,transparent 35%),
radial-gradient(115% 70px at 40% 125%,rgba(177,226,126,.50) 0 36%,transparent 37%);}
/* Keep app content above decorative curves; respect narrow screens and reduced-motion settings. */
[data-testid="stAppViewContainer"]>.main{position:relative;z-index:1}
@media(max-width:900px){.shared-hero{min-height:0!important;padding:23px!important}.shared-hero .ag-hero-content{max-width:100%;padding-right:0}.shared-hero .ag-weather-glass{position:relative;right:auto;bottom:auto;width:100%;margin-top:18px}.profile-chip small{display:none}}
@media(max-width:600px){.sidebar-title{font-size:17px}.shared-hero .ag-hero-content h1{font-size:28px!important}.ag-trust-chip{font-size:9px;padding:6px 8px}.global-context-strip{font-size:9px}}

</style>
""", unsafe_allow_html=True)

# Supabase authentication and region-aware weather helpers.
REGIONS = {
    "Madurai, Tamil Nadu": {"latitude": 9.9252, "longitude": 78.1198, "demo_temp": 31},
    "Chennai, Tamil Nadu": {"latitude": 13.0827, "longitude": 80.2707, "demo_temp": 32},
    "Coimbatore, Tamil Nadu": {"latitude": 11.0168, "longitude": 76.9558, "demo_temp": 29},
    "Tirunelveli, Tamil Nadu": {"latitude": 8.7139, "longitude": 77.7567, "demo_temp": 31},
    "Thoothukudi, Tamil Nadu": {"latitude": 8.7642, "longitude": 78.1348, "demo_temp": 31},
    "Bengaluru, Karnataka": {"latitude": 12.9716, "longitude": 77.5946, "demo_temp": 27},
    "Hyderabad, Telangana": {"latitude": 17.3850, "longitude": 78.4867, "demo_temp": 30},
    "Pune, Maharashtra": {"latitude": 18.5204, "longitude": 73.8567, "demo_temp": 28},
    "New Delhi, Delhi": {"latitude": 28.6139, "longitude": 77.2090, "demo_temp": 27},
    "Other / enter later": {"latitude": 9.9252, "longitude": 78.1198, "demo_temp": 30},
}


def _env_value(name: str) -> str:
    """Read environment or Streamlit secrets without requiring secrets.toml."""
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def supabase_request(path: str, payload: dict, access_token: str | None = None, method: str = "POST") -> dict:
    """Call Supabase Auth REST endpoints using the public anon key."""
    base = _env_value("SUPABASE_URL").rstrip("/")
    anon = _env_value("SUPABASE_ANON_KEY")
    if not base or not anon:
        raise RuntimeError("Supabase is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY in .env or Streamlit secrets.")
    headers = {"Content-Type": "application/json", "apikey": anon}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    request = urllib.request.Request(base + path, data=json.dumps(payload).encode("utf-8"), headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            return json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
            message = body.get("msg") or body.get("message") or body.get("error_description") or body.get("error") or "Authentication failed"
        except Exception:
            message = "Authentication failed; check your credentials and Supabase Auth settings."
        raise RuntimeError(str(message)) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("Could not reach Supabase. Check your internet connection and SUPABASE_URL.") from exc


def fetch_weather(region: str) -> dict:
    """Fetch current conditions from Open-Meteo; use a clearly labelled demo fallback offline."""
    coords = REGIONS.get(region, REGIONS["Other / enter later"])
    query = urllib.parse.urlencode({
        "latitude": coords["latitude"], "longitude": coords["longitude"],
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "timezone": "auto",
    })
    url = "https://api.open-meteo.com/v1/forecast?" + query
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgriCastAI/1.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            body = json.loads(response.read().decode("utf-8"))
        current = body.get("current", {})
        if "temperature_2m" not in current:
            raise ValueError("Weather provider returned no current temperature")
        return {
            "temperature": round(float(current["temperature_2m"])),
            "humidity": current.get("relative_humidity_2m"),
            "rainfall": current.get("precipitation"),
            "wind": current.get("wind_speed_10m"),
            "source": "Open-Meteo live",
            "updated": current.get("time", "Current observation"),
            "is_live": True,
        }
    except Exception:
        return {
            "temperature": coords["demo_temp"], "humidity": None, "rainfall": None, "wind": None,
            "source": "Demo default (not live)", "updated": "Live provider unavailable", "is_live": False,
        }


def render_auth_gate() -> None:
    """Ask for a user's name and farm region; authenticate with Supabase when configured."""
    st.markdown("<div style='max-width:780px;margin:4vh auto 0'>", unsafe_allow_html=True)
    st.markdown("<div class='ag-hero-image' style='min-height:190px;background-image:linear-gradient(90deg,#063b28dd,#063b2870),url(\"assets/farm_sunrise.png\")'><div class='ag-hero-content'><div class='hero-eyebrow'>FIELD INTELLIGENCE · AGRICAST AI</div><h1>Welcome to a healthier harvest.</h1><p>Sign in to your workspace and choose the region you farm in.</p></div></div>", unsafe_allow_html=True)
    configured = bool(_env_value("SUPABASE_URL") and _env_value("SUPABASE_ANON_KEY"))
    mode = st.radio("Account", ["Sign in", "Create account"], horizontal=True, key="auth_mode")
    with st.form("supabase_auth_form"):
        full_name = st.text_input("Your name", placeholder="e.g. Ayyappan", key="auth_full_name") if mode == "Create account" else st.text_input("Your name (optional)", placeholder="Used if available in your profile", key="auth_login_name")
        email = st.text_input("Email address", placeholder="you@example.com", key="auth_email")
        password = st.text_input("Password", type="password", key="auth_password")
        region = st.selectbox("Farm region / city", list(REGIONS.keys()), index=0, key="auth_region")
        submit = st.form_submit_button("Create account" if mode == "Create account" else "Sign in", type="primary", use_container_width=True)
    if submit:
        if not email.strip() or not password:
            st.error("Enter your email and password to continue.")
        elif mode == "Create account" and not full_name.strip():
            st.error("Enter your name to create an account.")
        elif not configured:
            st.error("Supabase login is not configured yet. Add SUPABASE_URL and SUPABASE_ANON_KEY to your .env file; see .env.example. No password is stored by this app.")
        else:
            try:
                if mode == "Create account":
                    result = supabase_request("/auth/v1/signup", {"email": email.strip(), "password": password, "data": {"full_name": full_name.strip(), "region": region}})
                    if not result.get("access_token"):
                        st.success("Account created. If email confirmation is enabled in Supabase, confirm your email, then sign in.")
                    else:
                        st.session_state["auth_user"] = result.get("user", {})
                        st.session_state["auth_access_token"] = result.get("access_token")
                        st.session_state["profile_name"] = full_name.strip()
                        st.session_state["farm_region"] = region
                        st.rerun()
                else:
                    result = supabase_request("/auth/v1/token?grant_type=password", {"email": email.strip(), "password": password})
                    user = result.get("user", {})
                    metadata = user.get("user_metadata", {}) or {}
                    st.session_state["auth_user"] = user
                    st.session_state["auth_access_token"] = result.get("access_token")
                    st.session_state["profile_name"] = metadata.get("full_name") or full_name.strip() or email.split("@")[0]
                    st.session_state["farm_region"] = metadata.get("region") or region
                    st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
    if not configured:
        st.info("Supabase setup required for real login. Add your project URL and public anon key in .env. Do not use a service-role key here.")
        if st.button("Continue in local demo mode", help="Demo mode does not authenticate or save a real account."):
            st.session_state["demo_mode"] = True
            st.session_state["profile_name"] = full_name.strip() or "Farm Manager"
            st.session_state["farm_region"] = region
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# Keep the dashboard usable locally while enforcing real Supabase auth when configured.
if not st.session_state.get("auth_user") and not st.session_state.get("demo_mode"):
    render_auth_gate()
    st.stop()

# Shared shell: persistent sidebar navigation, top utility bar, and farm-weather hero.
page_options = PAGE_OPTIONS
page_map = PAGE_MAP
nav_target = st.session_state.pop("_nav_target", None)
resolved_target = resolve_navigation_target(nav_target) if nav_target else None
if resolved_target:
    st.session_state["sidebar_nav"] = resolved_target

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <div class="sidebar-leaf">❧</div>
      <div><div class="sidebar-title">AgriCast <span>AI</span></div>
      <div class="sidebar-tag">Smart Predictions. Healthier Farms.</div></div>
    </div>
    <div class="sidebar-section-label">WORKSPACE</div>
    """, unsafe_allow_html=True)
    page_label = st.radio("Workspace navigation", page_options, key="sidebar_nav",
                          label_visibility="collapsed")
    st.markdown("""
    <div class="sidebar-bottom">
      <div class="sidebar-bottom-icon">🌱</div>
      <div class="sidebar-bottom-title">Smarter Decisions</div>
      <div class="sidebar-bottom-sub">Greener Tomorrow</div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("Workspace settings"):
        st.caption("Your profile and farm region")
        st.text_input("Display name", key="profile_name")
        st.selectbox("Farm region", list(REGIONS.keys()), index=list(REGIONS.keys()).index(st.session_state.get("farm_region", "Madurai, Tamil Nadu")) if st.session_state.get("farm_region", "Madurai, Tamil Nadu") in REGIONS else 0, key="farm_region")
        if st.button("Save profile and region", key="save_profile_region"):
            token = st.session_state.get("auth_access_token")
            if token and st.session_state.get("auth_user"):
                try:
                    supabase_request("/auth/v1/user", {"data": {
                        "full_name": st.session_state.get("profile_name", "").strip(),
                        "region": st.session_state.get("farm_region", "Madurai, Tamil Nadu")}}, access_token=token, method="PUT")
                    st.success("Profile and farm region saved to Supabase.")
                except RuntimeError as exc:
                    st.error(f"Could not save profile: {exc}")
            else:
                st.info("This is a local demo profile; changes are not saved to Supabase.")
        if st.button("Refresh weather", key="refresh_weather"):
            st.rerun()
        if st.button("Sign out", key="sign_out"):
            st.session_state.pop("auth_user", None)
            st.session_state.pop("auth_access_token", None)
            st.session_state.pop("demo_mode", None)
            st.rerun()
page = page_map[page_label]

# Resolve paths once; the same shell appears on every page.
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data/raw/crop_yield.csv"
DOC_DIR = PROJECT_ROOT / "data/documents"
INDEX_PATH = PROJECT_ROOT / "data/index/chunks.json"
MODEL_PATH = PROJECT_ROOT / "data/models/crop_yield_pipeline.joblib"
REPORT_PATH = PROJECT_ROOT / "data/reports/evaluation.json"

search_col, notification_col, profile_col = st.columns([5.3, .45, 1.15], vertical_alignment="center")
with search_col:
    global_query = st.text_input("Global search", key="global_search",
        placeholder="⌕  Search crops, climate variables, datasets, evidence…", label_visibility="collapsed")
with notification_col:
    st.markdown("<div class='utility-icon' title='Notifications'>♧</div>", unsafe_allow_html=True)
with profile_col:
    profile_name = st.session_state.get('profile_name', 'Farm Manager')
    profile_region = st.session_state.get('farm_region', 'Region not selected')
    safe_profile_name = __import__('html').escape(str(profile_name))
    safe_profile_region = __import__('html').escape(str(profile_region))
    st.markdown(f"<div class='profile-chip'><span class='profile-avatar'>{safe_profile_name[:1].upper()}</span><span><b>{safe_profile_name}</b><small>{safe_profile_region}</small></span></div>", unsafe_allow_html=True)

hero_titles = {
    "Command overview": ("Good morning, Farmer!", "Make smarter decisions with farm data, yield estimates and climate insights."),
    "Farm overview": ("Farm Overview", "Review the dataset currently connected to this local workspace."),
    "Data configuration": ("Farm Data", "Upload and validate your farm dataset to prepare reliable analysis."),
    "Yield forecast": ("Yield Forecasting", "Explore model-based crop yield estimates with transparent inputs."),
    "Climate signals": ("Climate Analysis", "Understand weather and crop patterns using the data you have connected."),
    "Evidence search": ("Agronomy Guidance", "Search trusted local agronomy notes and inspect the source passages."),
    "Knowledge assistant": ("Knowledge Assistant", "Search the indexed agronomy library and review supporting source passages."),
    "Tool integrations": ("Integrations", "Review API readiness, MCP tools and system integration status."),
    "Model diagnostics": ("Model Performance", "Evaluate model quality before relying on any prediction."),
}
hero_title, hero_subtitle = hero_titles.get(page, ("AgriCast AI", "Agricultural intelligence for clearer decisions."))
hero_path = PROJECT_ROOT / "assets" / "farm_sunrise.png"
hero_b64 = base64.b64encode(hero_path.read_bytes()).decode("ascii") if hero_path.exists() else ""
hero_bg = f"data:image/png;base64,{hero_b64}" if hero_b64 else ""
selected_region = st.session_state.get("farm_region", "Madurai, Tamil Nadu")
weather = fetch_weather(selected_region)
weather_badge = "LIVE" if weather["is_live"] else "DEMO DEFAULT"
weather_caption = "Current conditions" if weather["is_live"] else "Typical placeholder · not live weather"
def weather_value(key, suffix=""):
    value = weather.get(key)
    return f"{value}{suffix}" if value is not None else "—"
st.markdown(f"""
<div class="ag-hero-image shared-hero" style="background-image:url('{hero_bg}')">
  <div class="ag-hero-content">
    <div class="hero-eyebrow">FIELD INTELLIGENCE · AGRICAST AI</div>
    <h1>{hero_title}</h1><p>{hero_subtitle}</p>
    <div class="ag-trust-chip">✦ Data-led insights</div>
    <div class="ag-trust-chip">↗ Yield forecasting</div>
    <div class="ag-trust-chip">✓ Evidence-aware guidance</div>
  </div>
  <div class="ag-weather-glass">
    <div class="weather-head"><strong>Weather snapshot</strong><span class="demo-pill">{weather_badge}</span></div>
    <div class="weather-main"><span class="weather-sun">☀</span><div><div class="weather-number">{weather['temperature']}°C</div><div class="weather-caption">{weather_caption}</div></div></div>
    <div class="weather-line"><span>⌖ Region</span><b>{__import__('html').escape(selected_region)}</b></div>
    <div class="weather-line"><span>💧 Humidity</span><b>{weather_value('humidity', '%')}</b></div>
    <div class="weather-line"><span>☂ Rainfall</span><b>{weather_value('rainfall', ' mm')}</b></div>
    <div class="weather-line"><span>↗ Wind</span><b>{weather_value('wind', ' km/h')}</b></div>
    <div class="weather-note">Source: {weather['source']} · {weather['updated']}</div>
  </div>
</div>
<div class="global-context-strip"><span><i></i> Workspace ready</span><span>Dataset and model status are shown on relevant pages</span></div>
""", unsafe_allow_html=True)

def get_data():
    if DATA_PATH.exists():
        try:
            provenance = PROJECT_ROOT / "data/raw/DATA_PROVENANCE.md"
            label = "Bundled synthetic demo dataset" if provenance.exists() else "Connected dataset"
            return pd.read_csv(DATA_PATH), label
        except Exception:
            pass
    return None, "No dataset connected"


def check_mcp_connection():
    """Launch the local stdio MCP server as a client would and verify its tools."""
    async def _check():
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "agricast.services.mcp_server"],
            env=None,
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.list_tools()
                return [tool.name for tool in response.tools]
    return asyncio.run(_check())


# First-run setup: populate the demo workflow, but label its synthetic provenance.
# A real uploaded dataset can replace this file at any time.
if DATA_PATH.exists() and not MODEL_PATH.exists():
    try:
        initial_df = pd.read_csv(DATA_PATH)
        target_path = PROJECT_ROOT / "data/raw/target_column.txt"
        if target_path.exists():
            train_and_evaluate(initial_df, target_path.read_text(encoding="utf-8").strip(),
                               0.2, "Random Forest", MODEL_PATH, REPORT_PATH)
    except Exception:
        pass

def card(title, body):
    st.markdown(f'<div class="ag-card"><div class="eyebrow">{title}</div><p>{body}</p></div>', unsafe_allow_html=True)

if page == "Command overview":
    data, source = get_data()
    status = system_status()
    model_ready = MODEL_PATH.exists()
    target_path = PROJECT_ROOT / "data/raw/target_column.txt"
    target_ready = target_path.exists()
    if data is not None and "synthetic demo" in source.lower():
        st.warning("Demo mode: the bundled dataset contains synthetic values. Use it to explore the software, not to make real farming decisions.")
    elif data is None:
        st.info("Start here: upload your farm or crop-yield CSV in **Farm data**. The rest of the workspace depends on the columns and quality of that data.")

    st.markdown('<div style="display:flex;justify-content:space-between;align-items:end;gap:12px;margin:20px 0 12px"><div><div class="section-kicker">MOVE WITH PURPOSE</div><h2 style="margin:0">Quick actions</h2></div><div class="small-muted">Your most-used tools, one click away</div></div>', unsafe_allow_html=True)
    action_cols = st.columns(4, gap="medium")
    quick_actions = [("🌱", "Enter farm data", "Add or update your crop dataset", "Farm data", "#0C9B5B"),("▥", "Predict yield", "Estimate with your model", "Yield forecasting", "#2388F4"),("☁", "Explore climate", "Compare climate variables", "Climate analysis", "#F28B35"),("✧", "Find guidance", "Search the agronomy library", "Agronomy guidance", "#8060E8")]
    for ac, item in zip(action_cols, quick_actions):
        icon, title, desc, target, color = item
        with ac:
            st.markdown(f'<div class="ag-quick-action"><div class="ag-action-icon" style="background:linear-gradient(145deg,{color},{color}CC)">{icon}</div><div><div class="ag-action-title">{title}</div><div class="ag-action-sub">{desc}</div></div></div>', unsafe_allow_html=True)
            if st.button(f"Open {title} →", key=f"hero_{target}", width="stretch"):
                st.session_state["_nav_target"] = target
                st.rerun()

    # Simple, action-oriented progress panel.
    steps = [
        ("1", "Add farm data", "Upload a CSV and check its columns.", data is not None, "Farm data", "go_data"),
        ("2", "Review climate", "Explore patterns available in your dataset.", data is not None, "Climate & weather", "go_climate"),
        ("3", "Estimate yield", "Use a compatible trained model.", bool(data is not None and model_ready and target_ready), "Yield forecast", "go_forecast"),
        ("4", "Check evidence", "Search the local agronomy reference library.", status.get("rag_documents", 0) > 0, "Agronomy library", "go_evidence"),
    ]
    st.subheader("Your next steps")
    for row in range(2):
        c1, c2 = st.columns(2, gap="medium")
        for col, item in zip((c1,c2), steps[row*2:row*2+2]):
            n, title, desc, ready, target, key = item
            with col:
                with st.container(border=True):
                    st.markdown(f"### {n}. {title}")
                    st.write(desc)
                    st.caption("Available" if ready else "Needs setup")
                    if st.button(("Open " if ready else "Set up ") + title.lower() + " →", key=key, type="primary" if not ready else "secondary", width="stretch"):
                        st.session_state["_nav_target"] = target
                        st.rerun()

    st.subheader("Workspace status")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Dataset", "Loaded" if data is not None else "Not added")
    m2.metric("Yield model", "Available" if model_ready else "Not trained")
    m3.metric("Knowledge files", str(status.get("rag_documents", 0)))
    m4.metric("MCP tools", str(status.get("mcp_tool_count", 0)))
    if data is not None:
        st.subheader("What your dataset contains")
        q1, q2, q3 = st.columns(3)
        q1.metric("Records", f"{len(data):,}")
        q2.metric("Fields", f"{len(data.columns):,}")
        q3.metric("Missing values", f"{int(data.isna().sum().sum()):,}")
        with st.expander("Preview the first 10 rows"):
            preview = keep_first_duplicate_columns(data)
            if global_query:
                mask = preview.astype(str).apply(lambda col: col.str.contains(global_query, case=False, na=False)).any(axis=1)
                preview = preview[mask]
            st.dataframe(preview.head(10), width="stretch", hide_index=True)
    with st.expander("What do these features mean?"):
        st.markdown("""
        - **Farm data:** upload and validate a CSV. This is the first step for a new dataset.
        - **Yield forecasting:** estimate the target column using a compatible saved model.
        - **Weather & climate:** explore relationships in the data you have uploaded; this is not automatically live weather.
        - **Agronomy guidance:** search indexed text and Markdown documents. Results are source passages, not automatically AI-generated advice.
        - **Forecast quality:** train and evaluate a baseline model and review its metrics.
        - **Advanced integrations:** inspect API/MCP technical health. Most farmers do not need this page.
        """)
    st.caption("Use predictions as exploratory estimates until the model is validated on representative real agricultural data.")

elif page == "Data configuration":
    if st.session_state.get("dataset_upload_notice"):
        st.success(st.session_state.pop("dataset_upload_notice"))
    st.markdown('<div class="eyebrow">CONFIGURATION / DATA</div>', unsafe_allow_html=True)
    st.title("Add and check your farm data")
    st.write("Use this page first. Upload a CSV, review its columns, choose the value you want to predict, and save only after checking the preview.")
    st.info("You need a CSV file with column headers. For yield forecasting, the dataset must contain a numeric yield/target column and the input features used by the saved model.")
    upload = st.file_uploader("Crop-yield dataset (.csv)", type=["csv"])
    if upload:
        try:
            df = pd.read_csv(upload)
            duplicate_count = int(df.columns.duplicated(keep="first").sum())
            if duplicate_count:
                df = keep_first_duplicate_columns(df)
                st.warning(f"Found {duplicate_count} repeated column name(s). Kept the first column for each repeated name so charts and models can use unique headers.")
            st.write(f"Detected **{len(df):,} rows × {len(df.columns)} columns**")
            st.dataframe(df.head(15), width="stretch")
            target = st.selectbox("Target column (yield)", df.columns.tolist(), index=len(df.columns)-1)
            if st.button("Save dataset and target", type="primary"):
                try:
                    provenance = PROJECT_ROOT / "data/raw/DATA_PROVENANCE.md"
                    validated = save_uploaded_dataset(
                        df, target, DATA_PATH, PROJECT_ROOT / "data/raw/target_column.txt",
                        MODEL_PATH, REPORT_PATH, provenance,
                    )
                    st.session_state["dataset_upload_notice"] = f"Saved {len(validated):,} rows and {len(validated.columns):,} columns. Previous model and evaluation were invalidated because they belong to the old dataset. Train and evaluate again before forecasting."
                    st.rerun()
                except (ValueError, TypeError, OSError) as exc:
                    st.error(f"Dataset was not saved: {exc}")
        except Exception as e:
            st.error(f"Could not read this CSV: {e}")
    st.subheader("Document corpus for RAG")
    st.write("Manage the approved knowledge corpus. Supported source formats: Markdown (.md) and plain text (.txt).")
    if st.button("Index local documents"):
        try:
            chunks = ingest_directory(DOC_DIR, index_path=INDEX_PATH)
            st.success(f"Indexed {len(chunks)} text chunks into the local BM25 corpus.")
        except Exception as e:
            st.error(f"Indexing failed: {e}")
    st.caption("For PDFs, extract text in a separate, tested ingestion step and preserve page/section metadata before indexing.")

elif page == "Farm overview":
    st.markdown('<div class="eyebrow">FARM WORKSPACE / OVERVIEW</div>', unsafe_allow_html=True)
    st.title("Your farm data at a glance")
    data, source = get_data()
    if data is None:
        st.info("No dataset is connected yet. Open Farm data to upload and validate a CSV.")
    else:
        data = keep_first_duplicate_columns(data)
        provenance_path = PROJECT_ROOT / "data/raw/DATA_PROVENANCE.md"
        if provenance_path.exists():
            st.warning("Demo dataset: bundled values are synthetic and are not evidence of real-world farm conditions.")
        missing = int(data.isna().sum().sum())
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows / records", f"{len(data):,}")
        c2.metric("Fields", f"{len(data.columns):,}")
        c3.metric("Missing cells", f"{missing:,}")
        c4.metric("Duplicate rows", f"{int(data.duplicated().sum()):,}")
        left, right = st.columns([1.05, 1.5], gap="large")
        with left:
            st.markdown('<div class="ag-card"><div class="eyebrow">CONNECTED DATASET</div><h3>Dataset status</h3></div>', unsafe_allow_html=True)
            st.write(f"**Source:** {source}")
            st.write(f"**Model artifact:** {'Available' if MODEL_PATH.exists() else 'Not trained / not found'}")
            target_path = PROJECT_ROOT / "data/raw/target_column.txt"
            st.write(f"**Target column:** {target_path.read_text(encoding='utf-8').strip() if target_path.exists() else 'Not configured'}")
            if st.button("Manage farm data →", type="primary", width="stretch"):
                st.session_state["_nav_target"] = "Data configuration"
                st.rerun()
        with right:
            st.markdown('<div class="ag-card"><div class="eyebrow">DATA COVERAGE</div><h3>Column types</h3></div>', unsafe_allow_html=True)
            types = data.dtypes.astype(str).value_counts().rename_axis("Data type").reset_index(name="Columns")
            st.plotly_chart(px.bar(types, x="Data type", y="Columns", color="Data type",
                color_discrete_sequence=["#07874F", "#72BE44", "#1688E8", "#F59E0B"]), width="stretch")
        st.subheader("Field details")
        st.dataframe(pd.DataFrame({
            "Column": data.columns.astype(str),
            "Data type": data.dtypes.astype(str).values,
            "Non-empty values": data.notna().sum().values,
            "Missing values": data.isna().sum().values,
            "Unique values": data.nunique(dropna=True).values,
        }), width="stretch", hide_index=True)
        with st.expander("Preview records"):
            st.dataframe(data.head(15), width="stretch", hide_index=True)

elif page == "Yield forecast":
    st.markdown('<div class="eyebrow">WORKSPACE / FORECAST STUDIO</div>', unsafe_allow_html=True)
    st.title("Estimate crop yield")
    st.write("Choose values for the model inputs and run an estimate. The result is a model prediction, not a guarantee of what a farm will produce.")
    with st.expander("How to use this page"):
        st.markdown("1. Check that your dataset and trained model match.\n2. Review each input and its unit/category.\n3. Select **Run prediction**.\n4. Record the result together with its assumptions.")
    data, _ = get_data()
    if not MODEL_PATH.exists():
        st.warning("No trained model found. Go to Model diagnostics and train a baseline before predicting.")
    elif data is None:
        st.warning("Dataset not found. Upload the schema-compatible dataset first.")
    else:
        try:
            target = (PROJECT_ROOT / "data/raw/target_column.txt").read_text().strip()
            model, meta = load_model(MODEL_PATH)
            feature_cols = meta["feature_columns"]
            st.caption(f"Model version: {meta.get('model_version','unknown')} · Target: {target}")
            with st.form("predict_form"):
                inputs = {}
                cols = st.columns(2)
                for i, col in enumerate(feature_cols):
                    series = data[col]
                    if pd.api.types.is_numeric_dtype(series):
                        val = float(series.dropna().median()) if series.notna().any() else 0.0
                        inputs[col] = cols[i % 2].number_input(col, value=val)
                    else:
                        opts = series.dropna().astype(str).value_counts().index.tolist()
                        if not opts: opts = ["Unknown"]
                        inputs[col] = cols[i % 2].selectbox(col, opts)
                run = st.form_submit_button("Estimate yield", type="primary", width="stretch")
            if run:
                pred = predict_one(model, inputs)
                st.metric("Predicted target value", f"{pred:,.3f}")
                st.caption("Value is in the target column's original units. Validate units and applicability before use.")
                with st.expander("Input snapshot"):
                    st.json(inputs)
                st.info("This is a point estimate. Do not imply a confidence interval unless you implement and validate an uncertainty method.")
        except Exception as e:
            st.error(f"Model/input schema issue: {e}")

elif page == "Climate signals":
    st.markdown('<div class="eyebrow">ANALYTICS / CLIMATE EXPLORER</div>', unsafe_allow_html=True)
    st.title("Explore climate and crop patterns")
    st.write("Choose two columns to compare. Use this page to explore associations in your uploaded data; a correlation does not prove that one factor causes another.")
    data, _ = get_data()
    if data is None:
        st.info("Upload a real CSV in Data configuration. Charts are not populated with invented values.")
    else:
        st.write("Choose variables from the connected dataset. Interpret correlations as associations, not causal effects.")
        # Uploaded CSVs can contain repeated header names (for example, rainfall_mm twice).
        # Plotly/Narwhals requires unique dataframe column names, so keep the first occurrence.
        data = keep_first_duplicate_columns(data)
        numeric = data.select_dtypes(include="number").columns.tolist()
        allcols = data.columns.tolist()
        if numeric and len(allcols) >= 2:
            ycol = st.selectbox("Y axis", numeric, index=0, key="climate_y_axis")
            x_options = [c for c in allcols if c != ycol]
            if not x_options:
                st.warning("At least two distinct columns are required to create a scatter plot.")
            else:
                xcol = st.selectbox("X axis", x_options, index=0, key="climate_x_axis")
                group_options = ["None"] + [c for c in allcols if c not in {xcol, ycol}]
                colorcol = st.selectbox("Optional grouping", group_options, key="climate_grouping")
                selected = [xcol, ycol] + ([] if colorcol == "None" else [colorcol])
                # Defensive uniqueness check prevents duplicate selections reaching Plotly.
                selected = list(dict.fromkeys(selected))
                plot_data = data.loc[:, selected].dropna().copy()
                if plot_data.empty:
                    st.warning("No complete rows are available for this variable selection. Choose different columns or upload more data.")
                else:
                    fig = px.scatter(
                        plot_data, x=xcol, y=ycol,
                        color=None if colorcol == "None" else colorcol,
                        title=f"{ycol} vs {xcol}",
                    )
                    # Add an optional least-squares line with NumPy rather than
                    # Plotly's trendline="ols", which requires the extra statsmodels package.
                    if pd.api.types.is_numeric_dtype(plot_data[xcol]) and pd.api.types.is_numeric_dtype(plot_data[ycol]) and len(plot_data) >= 2:
                        x_values = pd.to_numeric(plot_data[xcol], errors="coerce").to_numpy(dtype=float)
                        y_values = pd.to_numeric(plot_data[ycol], errors="coerce").to_numpy(dtype=float)
                        valid = np.isfinite(x_values) & np.isfinite(y_values)
                        if valid.sum() >= 2 and np.unique(x_values[valid]).size >= 2:
                            slope, intercept = np.polyfit(x_values[valid], y_values[valid], 1)
                            line_x = np.linspace(x_values[valid].min(), x_values[valid].max(), 100)
                            fig.add_scatter(x=line_x, y=slope * line_x + intercept, mode="lines", name="Linear trend", line={"dash": "dash", "width": 2})
                    st.plotly_chart(fig, width="stretch")
                    st.caption(f"Rows plotted: {len(plot_data):,}. The dashed line is a descriptive linear trend, not evidence of causation.")
            if len(numeric) >= 2:
                st.subheader("Numerical correlation heatmap")
                method = st.selectbox("Correlation method", ["pearson", "spearman"], key="climate_corr_method")
                corr = data[numeric].corr(method=method)
                heat = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r",
                                 labels={"color": f"{method.title()} correlation"}, title="Feature correlation matrix")
                st.plotly_chart(heat, width="stretch")
        else:
            st.warning("At least two distinct columns and one numeric column are required to plot this dataset.")

elif page in ("Evidence search", "Knowledge assistant"):
    st.markdown('<div class="eyebrow">AI SYSTEMS / RETRIEVAL</div>', unsafe_allow_html=True)
    st.title("Knowledge assistant · evidence search" if page == "Knowledge assistant" else "Find agronomy guidance")
    st.write("Search the local reference library and open the matching passages. This feature retrieves documents; it does not independently verify advice or replace a qualified agricultural advisor.")
    st.info("Try a short question such as “rainfall and rice yield”. Results are useful only when relevant source documents have been added and indexed.")
    query = st.text_input("Search indexed documents", placeholder="e.g. rainfall variability and rice yield")
    top_k = st.slider("Passages to retrieve", 1, 10, 5)
    if st.button("Search the reference library", type="primary"):
        if not query.strip():
            st.warning("Enter a question or a few keywords first.")
            st.stop()
        try:
            retriever = BM25Retriever.from_directory(DOC_DIR, index_path=INDEX_PATH)
            results = retriever.search(query, top_k=top_k)
            if not results:
                st.warning("No indexed passages found. Add .txt or .md documents and index them.")
            for i, r in enumerate(results, 1):
                with st.expander(f"{i}. {r['source']} · rank score {r['score']:.3f}", expanded=(i==1)):
                    st.write(r["text"])
                    st.caption(f"Chunk: {r['chunk_id']} · source path: {r['source']}")
                    st.warning("Verify the source and surrounding context before citing this passage.")
        except Exception as e:
            st.error(f"Retrieval unavailable: {e}")
    st.subheader("RAG quality checks")
    st.markdown("- Does each answer claim have a supporting passage?\n- Are document title, URL/license, and page/section retained?\n- Does the assistant abstain when retrieval is weak?\n- Evaluate context precision/recall and answer faithfulness on a versioned test set.")

elif page == "Tool integrations":
    st.markdown('<div class="eyebrow">AI SYSTEMS / MCP OBSERVABILITY</div>', unsafe_allow_html=True)
    st.title("Advanced integrations and system status")
    st.write("This page is intended for developers and system operators. Farmers can usually ignore it.")
    st.info("A server file being present does not prove a live connection. Use the connection test to verify MCP tool discovery.")
    status = system_status()
    a,b,c = st.columns(3)
    a.metric("Server entrypoint", "Present" if status["mcp_entrypoint_exists"] else "Missing")
    b.metric("Tool handlers", str(status["mcp_tool_count"]))
    c.metric("Document files", str(status["rag_documents"]))
    st.subheader("Live MCP connection")
    if st.button("Test MCP connection", type="primary"):
        try:
            with st.spinner("Starting MCP server and negotiating protocol..."):
                live_tools = check_mcp_connection()
            st.session_state["mcp_live_tools"] = live_tools
            st.session_state["mcp_connection_ok"] = True
        except Exception as e:
            st.session_state["mcp_connection_ok"] = False
            st.session_state["mcp_connection_error"] = str(e)
    if st.session_state.get("mcp_connection_ok"):
        st.success("Connected: MCP initialization and tool discovery succeeded.")
        live_tools = st.session_state.get("mcp_live_tools", [])
        st.write("Tools discovered: " + ", ".join(live_tools))
    elif "mcp_connection_ok" in st.session_state:
        st.error("MCP connection failed. Check the error and install requirements in this virtual environment.")
        st.code(st.session_state.get("mcp_connection_error", "Unknown error"))
    else:
        st.info("Not yet verified in this session. Click **Test MCP connection** to perform a real protocol handshake.")
    st.subheader("Registered tool catalog")
    st.dataframe(pd.DataFrame(status["tools"]), hide_index=True, width="stretch")
    st.caption("The connection test launches the stdio server as an MCP client would, initializes the session, and discovers the actual tool list.")
    st.subheader("Execution trace")
    trace = PROJECT_ROOT / "data/reports/mcp_trace.jsonl"
    if trace.exists():
        rows=[]
        for line in trace.read_text(encoding="utf-8").splitlines()[-100:]:
            try:
                import json
                rows.append(json.loads(line))
            except Exception:
                pass
        if rows: st.dataframe(pd.DataFrame(rows), width="stretch")
    else:
        st.info("No tool calls recorded yet. The trace appears when a tool handler executes.")
    st.warning("Keep tools narrowly scoped. Validate arguments, limit input sizes, set timeouts, avoid arbitrary code execution, and do not return secrets.")

elif page == "Model diagnostics":
    st.markdown('<div class="eyebrow">MODEL QUALITY / EVALUATION</div>', unsafe_allow_html=True)
    st.title("Check forecast quality")
    st.write("Train a baseline and review how it performed on held-out rows. These metrics describe the evaluation sample, not a guarantee for a future farm.")
    with st.expander("Understand the metrics"):
        st.markdown("- **MAE:** average absolute prediction error, in the target's units.\n- **RMSE:** penalizes larger errors more heavily, in the target's units.\n- **R²:** comparison against a simple mean-based reference; it can be negative.\n- **Important:** the split method and data representativeness affect how useful these metrics are.")
    data, _ = get_data()
    if data is None:
        st.info("Upload a CSV and select its target in Data configuration.")
    else:
        if (PROJECT_ROOT / "data/raw/DATA_PROVENANCE.md").exists():
            st.warning("The selected dataset is synthetic demonstration data. These metrics do not establish real-world crop-yield accuracy.")
        target_file = PROJECT_ROOT / "data/raw/target_column.txt"
        if not target_file.exists():
            st.warning("Select and save a target column in Data configuration first.")
        else:
            target = target_file.read_text().strip()
            st.write(f"Target: **{target}**")
            test_size = st.slider("Test-set proportion", 0.1, 0.4, 0.2, 0.05)
            model_choice = st.selectbox("Baseline estimator", ["Random Forest", "Extra Trees", "Ridge Regression"])
            if st.button("Train and evaluate", type="primary"):
                with st.spinner("Training and evaluating on a held-out split..."):
                    try:
                        metrics = train_and_evaluate(data, target, test_size, model_choice, MODEL_PATH, REPORT_PATH)
                        st.success("Baseline training complete.")
                        x1,x2,x3 = st.columns(3)
                        x1.metric("MAE", f"{metrics['mae']:.4f}")
                        x2.metric("RMSE", f"{metrics['rmse']:.4f}")
                        x3.metric("R²", f"{metrics['r2']:.4f}")
                        st.caption(f"Rows: {metrics['n_rows']} · Test rows: {metrics['n_test']} · Split seed: {metrics['random_state']}")
                        st.warning("These metrics are only as valid as the dataset and split. Review leakage risks and use a temporal/geographic split when appropriate.")
                    except Exception as e:
                        st.error(f"Training failed: {e}")
    report = PROJECT_ROOT / "data/reports/evaluation.json"
    if report.exists():
        import json
        with st.expander("Latest persisted evaluation report"):
            st.json(json.loads(report.read_text(encoding="utf-8")))

st.divider()
st.markdown("<div style='padding-top:10px;color:#61738D;font:10px DM Mono,monospace;letter-spacing:.08em'>AGRICAST AI / FIELD & CROP INTELLIGENCE · LOCAL WORKSPACE</div>", unsafe_allow_html=True)
