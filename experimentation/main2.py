import getpass
import json
import os
import random
import re
from collections import Counter
from dataclasses import dataclass

import duckdb
import faiss
import numpy as np
import pandas as pd
import pickle
import requests
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames
from langchain_ibm import WatsonxLLM
from sentence_transformers import SentenceTransformer
from colorama import Fore, Style

from bohour.qafiah import get_qafiyah

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import json
import uvicorn


# Global variables

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



OPEN_API_KEY = os.getenv("OPEN_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
IBM_API_KEY = "a2F0DVBnfePotsn-P7K5iIAoHOTUC3-SyS4G2YW5CUFK"
PROJECT_ID = "85b95f9c-2602-4bbe-85cf-abae5a6bb091"
 

credentials = Credentials(
    url="https://eu-de.ml.cloud.ibm.com",
    api_key=IBM_API_KEY,
)
project_id = PROJECT_ID

embedding_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

themes = [
    "قصيدة اعتذار",
    "قصيدة الاناشيد",
    "قصيدة المعلقات",
    "قصيدة حزينه",
    "قصيدة دينية",
    "قصيدة ذم",
    "قصيدة رثاء",
    "قصيدة رومنسيه",
    "قصيدة سياسية",
    "قصيدة شوق",
    "قصيدة عامه",
    "قصيدة عتاب",
    "قصيدة غزل",
    "قصيدة فراق",
    "قصيدة قصيره",
    "قصيدة مدح",
    "قصيدة هجاء",
    "قصيدة وطنيه"
]


poets = [
  "آمنة بنت عتيبة",
  "آمنة بنت وهب",
  "أبان الالحقي",
  "أبد الصغير العلوي",
  "أبو الأخيل العجلي",
  "أبو الأسود الدؤلي",
  "أبو البحر الخطي",
  "أبو البقاء الرندي",
  "أبو الحسن الششتري",
  "أبو الحسن بن حريق",
  "أبو الحسن بن خروف",
  "أبو الحسين الجزار",
  "أبو الشمقمق",
  "أبو العباس الجراوي",
  "أبو العلاء المعري",
  "أبو العيناء",
  "أبو الفتح البستي",
  "أبو الفرج الأصبهاني",
  "أبو الفضل الكناني",
  "أبو الفضل الوليد",
  "أبو الفيض الكتاني",
  "أبو القاسم الشابي",
  "أبو المحاسن الشواء",
  "أبو الهدى الصيادي",
  "أبو اليمن الكندي",
  "أبو بكر الخوارزمي",
  "أبو بكر الصديق",
  "أبو بكر بن مجبر",
  "أبو بكر بن مغاور",
  "أبو تمام",
  "أبو جعفر الملاحي",
  "أبو حريز الشريف",
  "أبو دُلامة",
  "أبو ذؤيب الهذلي",
  "أبو زيد الفازازي",
  "أبو طالب",
  "أبو فراس الحمداني",
  "أبو محجن الثقفي",
  "أبو مدين التلمساني",
  "أحلام مستغانمي",
  "أحمد الكيواني",
  "أحمد بامبا",
  "أحمد رامي",
  "أحمد زكي أبو شادي",
  "أحمد شوقي",
  "أحمد محرم",
  "أسامة بن منقذ",
  "أسامه محمد زامل",
  "أم أبي جدابة",
  "أم الأغر بنت ربيعة التغلبية",
  "أم الضحاك المحاربية",
  "أم النحيف",
  "أم موسى الكلابية",
  "أمل دنقل",
  "أمية بن أبي الصلت",
  "أميمة بنت أمية",
  "أميمة بنت عبد المطلب",
  "أنسي الحاج",
  "أوس العبدي",
  "أوس الهجيمي",
  "أوس بن حارثة",
  "إبراهيم الأسطى",
  "إبراهيم الصولي",
  "إبراهيم اليازجي",
  "إبراهيم بن هرمة",
  "إبراهيم طوقان",
  "إبراهيم عبد القادر المازني",
  "إدريس جمّاع",
  "إسماعيل صبري",
  "إلياس أبو شبكة",
  "إيليا ابو ماضي",
  "ابراهيم ناجي",
  "ابن الأبار البلنسي",
  "ابن الأطنابة",
  "ابن الجزري",
  "ابن الجنان",
  "ابن الخياط",
  "ابن الخيمي",
  "ابن الدمينة",
  "ابن الرعلاء",
  "ابن الرومي",
  "ابن الزقاق",
  "ابن الساعاتي",
  "ابن العجلان النهدي",
  "ابن الفارض",
  "ابن المعتز",
  "ابن المُقري",
  "ابن النطروني",
  "ابن النقيب",
  "ابن الوردي",
  "ابن الياسمين",
  "ابن بشري الصقلي",
  "ابن تيمية",
  "ابن جبير الشاطبي",
  "ابن جرج الذهبي",
  "ابن جيا",
  "ابن حجاج",
  "ابن حربون",
  "ابن حزمون",
  "ابن حمديس",
  "ابن حموية",
  "ابن حيوس",
  "ابن حيون",
  "ابن خفاجه",
  "ابن خلدون",
  "ابن داود الظاهري",
  "ابن دراج القسطلي",
  "ابن دريد الأزدي",
  "ابن دنينير",
  "ابن دهن الحصي",
  "ابن رازكه",
  "ابن راشد الحمامي",
  "ابن رشيق القيرواني",
  "ابن رواحة الحموي",
  "ابن زاكور",
  "ابن زريق البغدادي",
  "ابن زمرك",
  "ابن زهر الحفيد",
  "ابن زيدون",
  "ابن سالم الهمداني",
  "ابن سعد البلنسي",
  "ابن سناء الملك",
  "ابن سهل الأندلسي",
  "ابن شكيل",
  "ابن شهاب العلوي",
  "ابن شيخان السالمي",
  "ابن صابر المنجنيقي",
  "ابن طاهر",
  "ابن طفيل",
  "ابن عبد ربه",
  "ابن عطاء الله المصري",
  "ابن علوي الحداد",
  "ابن عمرو الأغماتي",
  "ابن عنين",
  "ابن عياش التجيبي",
  "ابن قلاقس",
  "ابن كسرى",
  "ابن لبال الشريشي",
  "ابن مجاور",
  "ابن مسعود الخشني",
  "ابن مسعود القرطبي",
  "ابن مطروح البلنسي",
  "ابن معتوق",
  "ابن معصوم",
  "ابن مليك الحموي",
  "ابن منجا الدمشقي",
  "ابن مواهب",
  "ابن نباته المصري",
  "ابن نجيب الهاشمي",
  "ابن نفادة",
  "ابن نوفل الحلبي",
  "ابن هانئ الأندلسي",
  "ابو العتاهية",
  "ابو محمد الفقعسي",
  "ابو نواس",
  "احمد مطر",
  "الأبيوردي",
  "الأحنف العكبري",
  "الأحوص الأنصاري",
  "الأخطل",
  "الأرجاني",
  "الأصمعي",
  "الأعشى",
  "الأقرع بن معاذ",
  "الأمير الصنعاني",
  "الأمين العباسي",
  "الإمام الشافعي",
  "الامير منجك باشا",
  "الباخرزي",
  "الباعونية",
  "الببغاء",
  "البحتري",
  "البرعي",
  "البوصيري",
  "التهامي",
  "الجاحظ",
  "الحارث بن حلزة",
  "الحارث بن عباد",
  "الحسين بن علي",
  "الحطيئة",
  "الحلاج",
  "الحيص بيص",
  "الخبز أرز",
  "الخنساء",
  "الراضي بالله",
  "الراعي النميري",
  "الزمخشري",
  "السراج الوراق",
  "السري الرفاء",
  "السمهري العلكي",
  "الشاب الظريف",
  "الشاذلي خزنه دار",
  "الشريف الرضي",
  "الشريف العقيلي",
  "الشريف المرتضى",
  "الشماخ الذبياني",
  "الصاحب بن عباد",
  "الصرصري",
  "الطرماح",
  "الطغرائي",
  "الطفيل الغنوي",
  "العباس بن الأحنف",
  "العباس بن مرداس",
  "العجاج",
  "العجلان بن خليد",
  "العرجي",
  "العقار بن سليل",
  "العنبر الخضم",
  "العوراء الذبيانية",
  "العوراء اليربوعية",
  "الغزالي",
  "الغطمش الضبي",
  "الفارعة بنت معاوية",
  "الفرزدق",
  "الفند الزماني",
  "القاضي الفاضل",
  "القعقاع بن شبث اليهودي",
  "القعقاع بن عمرو",
  "الكذاب الطابخي",
  "الكذاب الكلبي",
  "الكلحبة العرني",
  "الكميت بن زيد",
  "اللواح",
  "المتلمس الضبعي",
  "المتنبي",
  "المتنخل",
  "المثقب العبدي",
  "المثلم الفزاري",
  "المثلم المري",
  "المثلم بن عمرو التنوخي",
  "المثلم بن قرط البلوي",
  "المحيا الهمداني",
  "المرار الكلبي",
  "المرار بن منقذ",
  "المرقش الأصغر",
  "المرقش الأكبر",
  "المسجاح الضبي",
  "المسيب بن علس",
  "المشؤوم",
  "المعان بن روق",
  "المعتمد بن عباد",
  "المفضل النكري",
  "المقنع الكندي",
  "المكزون السنجاري",
  "الملك الأمجد",
  "الممزق العبدي",
  "المنخل اليشكري",
  "المنفلوطي",
  "الميكالي",
  "النابغة التغلبي",
  "النابغة الجعدي",
  "النابغة الحارثي",
  "النابغة الذبياني",
  "النابغة الشيباني",
  "النابغة الغنوي",
  "النوار الجل",
  "الهبل",
  "الهبل بن عامر",
  "الهجرس التغلبي",
  "الهدم بن امرئ القيس",
  "الهذلول بن كعب",
  "الهذيل الأكبر التغلبي",
  "الهذيل بن أم عفاش",
  "الهيبان الفهمي",
  "الهيفاء بنت صبيح القضاعية",
  "الوأواء الدمشقي",
  "الوقي الهمداني",
  "الوليد بن يزيد",
  "امرؤ القيس",
  "امرؤ القيس الزهيري",
  "امرؤ القيس السكوني",
  "امرؤ القيس الكلبي",
  "بداء بن سليمان",
  "بدر الفزاري",
  "بدر شاكر السياب",
  "بديع الزمان الهمذاني",
  "بديع القشاعلة",
  "برة بنت عبد المطلب",
  "بسام بن شريح",
  "بشار بن برد",
  "بشامة بن الغدير",
  "بشر الفزاري",
  "بشر بن أبي خازم",
  "بشر بن عمرو",
  "بشير بن النكث",
  "بطرس كرامة",
  "بغثر بن لقيط الأسدي",
  "بكر الجرهمي",
  "بلبل الغرام الحاجري",
  "بلعاء بن قيس الكناني",
  "بلند الحيدري",
  "بنت الشحنة",
  "بهاء الدين الصيادي",
  "بهاء الدين زهير",
  "بيهس الغطفاني",
  "بيهس الفزاري",
  "تأبط شراً",
  "تماضر بنت الشريد",
  "تميم البرغوثي",
  "تميم الفاطمي",
  "تنها بنت قرط العبدية",
  "توبة الخفاجي",
  "توفيق زياد",
  "ثعلبة المازني",
  "ثعلبة بن بكر الأزدي",
  "ثعلبة بن عامر",
  "جابر المرني",
  "جابر المري",
  "جاسم الصحيح",
  "جبار الفزاري",
  "جبار بن قرط",
  "جبر المعاوي",
  "جبران خليل جبران",
  "جبلة بن الحارث",
  "جبيهاء الأشجعي",
  "جحدر الوائلي",
  "جحيش الهمداني",
  "جرمانوس فرحات",
  "جرير",
  "جساس بن مرة",
  "جلواح",
  "جميل بثينة",
  "جميل صدقي الزهاوي",
  "جورج جرداق",
  "جورج جريس فرح",
  "حافظ ابراهيم",
  "حبيب الهلالي",
  "حذيفة العرجي",
  "حسان بن ثابت",
  "حسن كامل الصيرفي",
  "حفني ناصف",
  "حمد بن خليفة أبو شهاب",
  "حمزة الملك طمبل",
  "خالد الفرج",
  "خفاف بن ندبة السلمي",
  "خليل مردم بك",
  "خليل مطران",
  "دريد بن الصمة",
  "دعبل الخزاعي",
  "دويد القضاعي",
  "ديك الجن",
  "ذو الرمة",
  "رفعت الصليبي",
  "زكي مبارك",
  "زهير بن أبي سلمى",
  "زياد التميمي",
  "زياد السعودي",
  "سالم أبو جمهور القبيسي",
  "سامي المالكي",
  "سبط ابن التعاويذي",
  "سعيد بن أحمد البوسعيدي",
  "سعيد عقل",
  "سلطان السبهان",
  "سلم الخاسر",
  "سليم عبدالقادر",
  "سليمان الباروني",
  "سليمان بن سحمان",
  "سميح القاسم",
  "سهام آل براهمي",
  "سيد قطب",
  "سيف الدولة الحمداني",
  "سيف الرحبي",
  "شاعر الحمراء",
  "شريف بقنه",
  "شمر الحنفي",
  "صالح الشرنوبي",
  "صالح الفهدي",
  "صخر الغي",
  "صردر",
  "صريع الغواني",
  "صفي الدين الحلي",
  "صلاح الدين الصفدي",
  "صلاح عبد الصبور",
  "ضرار الفهري",
  "طرفة بن العبد",
  "ظافر الحداد",
  "عارف الخاجة",
  "عباس بن فرناس",
  "عبد الرحمن بن مساعد",
  "عبد الرزاق عبد الواحد",
  "عبد الغفار الأخرس",
  "عبد الغني النابلسي",
  "عبد القادر الجزائري",
  "عبد المجيد الأزدي",
  "عبد المحسن الصوري",
  "عبد الناصر الجوهري",
  "عبد الولي الشميرى",
  "عبدالرحمن العشماوي",
  "عبدالله البردوني",
  "عبدالله الشبراوي",
  "عبدالله الفيصل",
  "عبده صالح",
  "عبيد بن الأبرص",
  "عدنان الصائغ",
  "عدي بن الرقاع",
  "عدي بن ربيعة",
  "عروة بن أذينة",
  "عروة بن الورد",
  "عروة بن حزام",
  "علقمة الفحل",
  "علي بن أبي طالب",
  "علي بن سعود آل ثاني",
  "عمارة اليمني",
  "عمر أبو ريشة",
  "عمر الأنسي",
  "عمر الخيام",
  "عمر اليافي",
  "عمر بن أبي ربيعة",
  "عمر محمد عبدالرحمن",
  "عمرو الباهلي",
  "عمرو بن كلثوم",
  "عمرو بن معد يكرب",
  "عنترة بن شداد",
  "غازي الجمل",
  "غازي القصيبي",
  "فؤاد الخطيب",
  "فاروق جويدة",
  "فاطمة الزهراء",
  "فتيان الشاغوري",
  "فهد العسكر",
  "قاسم حداد",
  "قسطاكي الحمصي",
  "قيس بن الملوح",
  "قيس بن ذريح",
  "قيس بن زهير",
  "كثير عزة",
  "كريم معتوق",
  "كشاجم",
  "كعب بن زهير",
  "لبيد بن ربيعة",
  "لسان الدين بن الخطيب",
  "ماء العينين",
  "مالك الأشتر",
  "محمد الثبيتي",
  "محمد الشوكاني",
  "محمد المعولي",
  "محمد بن عبود العمودي",
  "محمد عبد الباري",
  "محمد فضولي",
  "محمد مهدي الجواهري",
  "محمد ولد ابن ولد أحميدا",
  "محمود الوراق",
  "محمود درويش",
  "محمود سامى البارودى",
  "محمود قابادو",
  "مدثر بن إبراهيم بن الحجاز",
  "مروان بن أبي حفصة",
  "مسكين الدرامي",
  "مصطفى التل",
  "مصطفى بن زكري",
  "مصطفى صادق الرافعي",
  "مطلق عبد الخالق",
  "معروف الرصافي",
  "مهيار الديلمي",
  "مَحمد اسموني",
  "نازك الملائكة",
  "ناصيف اليازجي",
  "نزار قباني",
  "نسيب عريضة",
  "نصيب بن رباح",
  "نوري سراج الوائلي",
  "هشام الجخ",
  "هلال بن سعيد العماني",
  "هند بنت عتبة",
  "وضاح اليمن",
  "ولادة بنت المستكفي",
  "يزيد بن الطثرية",
  "يزيد بن معاوية",
  "يوسف النبهاني",
]

# Load the ashaar database
df = pd.read_csv("./data_folder/ashaar.csv")

# load themes embeddings from disk
with open('./data_folder/theme_embeddings.pkl', 'rb') as f:
    theme_embeddings = pickle.load(f)

# Normalize the embeddings
faiss.normalize_L2(theme_embeddings)

# Create a FAISS index
index_theme = faiss.IndexFlatIP(theme_embeddings.shape[1])
index_theme.add(theme_embeddings)

# Load poets embedding model
with open('./data_folder/poet_embeddings.pkl', 'rb') as f:
    poet_embeddings = pickle.load(f)

# Normalize the embeddings
faiss.normalize_L2(poet_embeddings)

# Create a FAISS index
index_poet = faiss.IndexFlatIP(poet_embeddings.shape[1])
index_poet.add(poet_embeddings)

def find_similar(query, index, ground_truth, k=1):
    """
    args:
      query: theme or poet
      index: index_theme or index_poet
      ground_truth: list
    """
    # Encode the query
    query_vector = embedding_model.encode([query])
    faiss.normalize_L2(query_vector)

    # Perform the search
    distances, indices = index.search(query_vector, k)

    # Return the results
    top = indices[0][0]
    return ground_truth[top]

### Simulation Globals

# From the UI
# POET1 = "أحمد شوقي"
# POET2 = "خليل مطران"
# ROUND_THEMES = ["حزين", "وطني", "رومانسي"]
# NUM_ROUNDS = 1

# Runtime
ROUND_SCORES = {"poet1":[], "poet2":[]} # for each round
ROUND_COMMENTS = {"poet1":[], "poet2":[]}
LOGGER_LEVEL = 2
NUMBER_TO_ORDINAL = {
    1: "الأولى",
    2: "الثانية",
    3: "الثالثة",
    4: "الرابعة",
    5: "الخامسة",
    6: "السادسة",
    7: "السابعة",
    8: "الثامنة",
    9: "التاسعة",
    10: "العاشرة"
}

## Global Utils

def log_messages(msg, level):
   """
   args:
      msg: string text to be logged to stdout
      level: 1 for user pretty output, 2 for adding intermediate steps
   """
   if level <= LOGGER_LEVEL:
      print(msg)
   


#################
#  JUDGE AGENT  #
#################

###LLMs####
# Might change temperature later (or dynamically ?)
commentator_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
		GenTextParamsMetaNames.REPETITION_PENALTY: 1,
}


summarizer_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
		GenTextParamsMetaNames.REPETITION_PENALTY: 1,
}

commentator_llm = WatsonxLLM(
    url=credentials.get('url'),
    apikey=credentials.get('apikey'),
    project_id=project_id,
    model_id="sdaia/allam-1-13b-instruct",
    params=commentator_parameters
)

summarizer_llm = WatsonxLLM(
    url=credentials.get('url'),
    apikey=credentials.get('apikey'),
    project_id=project_id,
    model_id="sdaia/allam-1-13b-instruct",
    params=summarizer_parameters
)

#### System Prompts
commentator_prompt = """
[INST] <<SYS>>
أنت خبير في التعليق علي الشعر العربي و تخيل أنك تتحدث للشاعر الذي كتب البيت
سأعطيك البيت و أنت أعطني التعليق بنفس اسلوب الأمثلة كأنك تتحدث إلي الشاعر نفسه 

شكل التعليق المتوقع من كتابته
    التعليق: {التعليق علي البيت}

The INST block will always be a json string:
    {
        "prompt": {البيت}
    }

الأمثلة
"أَركَبُ البَحرَ تارَةً وَأَجوبُ البَرَّ طَوراً وَأَقطَعُ الأَيّاما"
التعليق: و أقطع الأياما, ممتاز انت تشير إلى الترحال عبر البحر والبر وتجاوز الأيام كرمز للتحدي المستمر

"صرح الفلاح على الفضيل مشيد فالفضل ركن الخير والعمرانِ"
التعليق: الخير و العمران, جميل أنت تشير إلي الفلاح في فضيلة بناء الخير و العمران و العمل الجاد

"أهيمُ في الصحارى طَرِبًا والجبالُ تسيرُ معي"
التعليق: الجبال تسير معي، رائع، أنت تستعمل الجبال كرمز للقوة والاستمرارية في رحلتك التي تعكس سمو النفس

"كأن النجومَ تُهدي النورَ في ظلمةِ الليالي الحائرة"
التعليق: النجوم تهدي النور, رائع أنت استخدمت استخدام رائع للاستعارة، حيث تشير النجوم إلى الأمل والإرشاد في أوقات الشدائد

"سيف العزِّ يمضي بغير هوادة، يقطع طريقَ اليأسِ بلا رجوع"
التعليق: سيف العز، قوي! هنا السيف رمز للقوة والشجاعة، وقطع طريق اليأس يعكس الانتصار على العقبات

تذكر رجاء أعطني التعليق فقط لا تقوم بشرح او كتابة اي شيء سوي التعليق

<</SYS>> [/INST]
"""

quality_scorer_prompt = """
[INST] <<SYS>>
أنت خبير في تقييم الشعر العربي. 
لديك بيت واحد من الشعر و أنت ستقيمه من 1 إلي 3 بناءا علي جودة البيت
جودة البيت تعتمد علي اختيار الكلمات و القافية و وزن البيت و جودة معني البيت

The expected output from you has to be: 
    score: {verse_score}

The INST block will always be a json string:
    {
        "prompt": {البيت}
    }

Here are the examples for the input and the corresponding output you can generate:
"verse": "أَركَبُ البَحرَ تارَةً وَأَجوبُ ال بَرَّ طَوراً وَأَقطَعُ الأَيّاما"
"output":
    score: 3

"verse": "صرح الفلاح على الفضيل مشيد فالفضل ركن الخير والعمرانِ"
"output":
    score: 2

"verse": "برز الثعلب يوما فى ثياب الواعظينا"
"output":
    score: 2

Remember Give me only the score in the output format specified. Don't give me any explanation.

<</SYS>> [/INST]
"""
# TODO: Write it
summarizer_prompt = """
/n
"""

### Utils

def qafya_comment(score):
   
  if score == 1:
    comment = "أيضا مع الأسف انت لم تحافظ علي القافية المطلوبة"
  else:
    comment = "أيضا ممتاز لقد حافظت علي القافية المطلوبة"

  return comment

def get_score_llm_output(score_str):
   score = int(score_str.split(":")[1].strip())
   return score

def prepare_commentator_prompt(bait):
  commentator_prompt = f"""
[INST] <<SYS>>
أنت خبير في التعليق علي الشعر العربي و تخيل أنك تتحدث للشاعر الذي كتب البيت
سأعطيك البيت و أنت أعطني التعليق بنفس اسلوب الأمثلة كأنك تتحدث إلي الشاعر نفسه 

شكل التعليق المتوقع من كتابته
    التعليق: {{التعليق علي البيت}}

The INST block will always be a json string:
    {{
        "prompt": {{البيت}}
    }}

الأمثلة
أَركَبُ البَحرَ تارَةً وَأَجوبُ البَرَّ طَوراً وَأَقطَعُ الأَيّاما
التعليق: و أقطع الأياما, ممتاز انت تشير إلى الترحال عبر البحر والبر وتجاوز الأيام كرمز للتحدي المستمر

صرح الفلاح على الفضيل مشيد فالفضل ركن الخير والعمرانِ
التعليق: الخير و العمران, جميل أنت تشير إلي الفلاح في فضيلة بناء الخير و العمران و العمل الجاد

أهيمُ في الصحارى طَرِبًا والجبالُ تسيرُ معي
التعليق: الجبال تسير معي، رائع، أنت تستعمل الجبال كرمز للقوة والاستمرارية في رحلتك التي تعكس سمو النفس

كأن النجومَ تُهدي النورَ في ظلمةِ الليالي الحائرة
التعليق: النجوم تهدي النور, رائع أنت استخدمت استخدام رائع للاستعارة، حيث تشير النجوم إلى الأمل والإرشاد في أوقات الشدائد

سيف العزِّ يمضي بغير هوادة، يقطع طريقَ اليأسِ بلا رجوع
التعليق: سيف العز، قوي! هنا السيف رمز للقوة والشجاعة، وقطع طريق اليأس يعكس الانتصار على العقبات

تذكر رجاء أعطني التعليق فقط لا تقوم بشرح او كتابة اي شيء سوي التعليق

<</SYS>> [/INST]
[INST] 
{{
    "prompt": "{bait}"
}}
[/INST]
"""
  return commentator_prompt

def prepare_quality_scorer_prompt(bait):
  instruction = f"""
[INST] 
{{
    "prompt": "{bait}"
}}
[/INST]
  """
  return quality_scorer_prompt + instruction

def majority_vote(a):
  return Counter(a).most_common()[0][0]

def qafya_scorer(bait, desired_qafya):
  true_qafya = majority_vote(get_qafiyah([bait], short=False))[0]
  if true_qafya == desired_qafya:
    return 4
  else:
    return 1

meters_scores = {
    "الرجز": 2,
    "الكامل": 2,
    "الوافر": 2,
    "نثر": 1,
}

@dataclass
class PredictionRequest:
    text: str

@dataclass
class PredictionResponse:
    predicted_meter: str

def send_request(text: str) -> tuple[float, PredictionResponse]:

    base_url = "http://localhost:8000/predict/"

    request_data = PredictionRequest(text=text)

    try:
        response = requests.post(
            base_url,
            json=request_data.__dict__,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        prediction_response = PredictionResponse(**response.json())
        
        return prediction_response

    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    
def meters_scorer(bait):
    response = send_request(bait)
    meter = response.predicted_meter

    if meter in meters_scores.keys():
        score = meters_scores[meter]
    else:
        score = 3

    return score

qawafi_rhymes = [
    "قافية الميم",  # Mīm
    "قافية النون",  # Nūn
    "قافية اللام",  # Lām
    "قافية الألف",  # Alif
    "قافية السين",  # Sīn
    "قافية الياء",  # Yā'
    "قافية الراء",  # Rā'
]

qawafi_weights = [
    0.40,
    0.30,
    0.10,
    0.05,
    0.05,
    0.05,
    0.05,
]


######################
#  COMPETITOR AGENT  #
######################

###LLMs####
# Might change temperature later (or dynamically ?)

competitior_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
		GenTextParamsMetaNames.REPETITION_PENALTY: 1,
    GenTextParamsMetaNames.TEMPERATURE: 0.3,
}

generator_parameters = {
    GenTextParamsMetaNames.MAX_NEW_TOKENS: 1500,
    GenTextParamsMetaNames.DECODING_METHOD: "greedy",
		GenTextParamsMetaNames.REPETITION_PENALTY: 1,
}

competitor_llm = WatsonxLLM(
    url=credentials.get('url'),
    apikey=credentials.get('apikey'),
    project_id=project_id,
    model_id="sdaia/allam-1-13b-instruct",
    params=competitior_parameters
)

generator_llm = WatsonxLLM(
    url=credentials.get('url'),
    apikey=credentials.get('apikey'),
    project_id=project_id,
    model_id="sdaia/allam-1-13b-instruct",
    params=generator_parameters
)

competitor_prompt = """
[INST] <<SYS>>

You are a helpful assistent, that only communicates using JSON files.
All output must be in valid JSON. Don’t add explanation beyond the JSON
The expected output from you has to be: 
    {
        "poet_name": {"poet_name"},
        "poem_theme": {"poem_theme"},
        "poem_qafya": {"poem_qafya"},
        "poem_qafya_letter": {poem_qafya_letter},
    }
The INST block will always be a json string:
    {
        "prompt": {user_prompt}
    }
Here are the examples for the input and the corresponding output you can generate:
{
"input": "بيت شعر عن الوطنية علي طريقة الشاعر أحمد شوقي ينتهي بقافية الميم",
"output": {
    "poet_name": {"أحمد شوقي"},
    "poem_theme": {"قصيدة وطنية"},
    "poem_qafya": {"قافية الميم"}
    "poem_qafya_letter": {"م"}
}
},
{
    "input": "بيت شعر عن الرومنسيه علي طريقة الشاعر إيليا أبو ماضي ينتهي بقافية النون",
    "output": {
        "poet_name": {"إيليا أبو ماضي"},
        "poem_theme": {"قصيدة رومنسيه"},
        "poem_qafya": {"قافية النون"}
        "poem_qafya_letter": {"ن"}
    }
},
{
    "input": "بيت شعر عن الحرية علي طريقة الشاعر محمود درويش ينتهي بقافية الراء",
    "output": {
        "poet_name": {"محمود درويش"},
        "poem_theme": {"قصيدة حرية"},
        "poem_qafya": {"قافية الراء"}
        "poem_qafya_letter": {"ر"}
    }
},
{
    "input": "أريد بيت شعر عن الحب علي طريقة الشاعرة نازك الملائكة ينتهي بقافية الباء",
    "output": {
        "poet_name": {"نازك الملائكة"},
        "poem_theme": {"قصيدة حب"},
        "poem_qafya": {"قافية الباء"}
        "poem_qafya_letter": {"ب"}
    }
},
{
    "input": " أعطني بيت شعر حزين علي طريقة الشاعر بدر شاكر السياب ينتهي بقافية الدال",
    "output": {
        "poet_name": {"بدر شاكر السياب"},
        "poem_theme": {"قصيدة حزينة"},
        "poem_qafya": {"قافية الدال"}
        "poem_qafya_letter": {"د"}
    }
}
<</SYS>> [/INST]
"""

### Utils

def int_to_arabic(number):
    arabic_numerals = '٠١٢٣٤٥٦٧٨٩'
    return ''.join(arabic_numerals[int(d)] for d in str(number))

def prepare_competitor_prompt (user_prompt):
  instruction_prompt = f"""
  [INST] 
  {{
      "prompt": "{user_prompt}"
  }}
  [/INST]
  """
  return competitor_prompt + instruction_prompt

def prepare_generator_prompt(poet_name, poem_qafya, true_poem_theme, examples):
  generation_prompt = f"""
<s> [INST]<<SYS>>
انت الشاعر العربي المشهور {poet_name}.
قم بتأليف بيت شعر جديد واحد فقط ب{poem_qafya} و نوع البيت من {true_poem_theme}
ابني البيت الجديد بناء علي اسلوب الامثلة المعطاه
تذكر رجاء أعطني أول بيت فقط من القصيدة
<</SYS>>

أمثلة للبيت المتوقع منك كتابته
{
    ''.join([f"{int_to_arabic(i+1)}-{example}\n" for i, example in enumerate(examples)])
}
[/INST]
"""
  return generation_prompt

def do_query(poet_name, poem_theme):
  query = f"""
    SELECT *
    FROM df
    WHERE "poet name" = '{poet_name}'
    AND "poem theme" = '{poem_theme}'
    """
  return duckdb.sql(query).to_df()

def parser(unstructured):

  pattern = r'"(\w+)":\s*"?{"(.+?)"}"?'
  data =  dict(re.findall(pattern, unstructured))

  poet_name = data['poet_name']
  poem_theme = data['poem_theme']
  poem_qafya = data['poem_qafya']
  poem_qafya_letter = data['poem_qafya_letter']

  return poet_name, poem_theme,poem_qafya, poem_qafya_letter

def construct_baits(input_string):
    items = [item.strip().strip("'\"") for item in input_string.strip('[]').split(',')]
    
    pairs = [f"{items[i]} {items[i+1]}" for i in range(0, len(items)-1, 2)]
    
    return pairs

def construct_examples(result, desired_qafya):
  all_baits = []
  examples = []
  poems = result["poem verses"].to_list()
  random.shuffle(poems)

  for i, poem in enumerate(poems):
    # get all baits
    baits = construct_baits(poem)
    all_baits.extend(baits)

  # use only baits with matching qafya
  for bait in all_baits:
    # get the qafya
    qafya = majority_vote(
        get_qafiyah([bait], short=False)
    )
    qafya_letter = qafya[0]

    # add only if qafya matches
    if desired_qafya == qafya_letter:
      if len(examples) == 15:
        break
      examples.append(bait)
    random.shuffle(examples)

  if len(examples) < 10:
    for i, poem in enumerate(poems):
      # check only max 2 poems
      if i == 5:
        break
      baits = construct_baits(poem)
      random.shuffle(baits)
      examples.extend(baits[0:3])

  return examples

def postprocess_bait(bait):
  parts = bait.split('\n', 2)
  bait = '\n'.join(parts[:2]) if len(parts) > 2 else bait
  bait = bait.replace('،', '')
  bait = bait.replace('.', '')
  bait = bait.replace('\n', ' ')

  return bait

def postprocess_comment(comment):
  return comment.split('\n', 1)[0]

##############
# SIMULATION # 
##############

async def run_simulation(websocket,POET1,POET2,ROUND_THEMES,NUM_ROUNDS):

  ## Prepare all rounds prompts by the judge to the 2 competitiors
  POET1_PROMPTS = []
  POET2_PROMPTS = []

  for theme in ROUND_THEMES:
    round_qafya = random.choices(qawafi_rhymes, weights=qawafi_weights, k=1)[0]
    POET1_PROMPTS.append(f"أريد بيت شعر عن {theme} علي طريقة الشاعر {POET1} ينتهي ب{round_qafya}")
    POET2_PROMPTS.append(f"أريد بيت شعر عن {theme} علي طريقة الشاعر {POET2} ينتهي ب{round_qafya}")

  log_messages(msg="Prepared all rounds prompts for the competitors", level=2)
  log_messages(msg=f"Competitor 1 prompts: {POET1_PROMPTS}", level=2)
  log_messages(msg=f"Competitor 2 prompts: {POET2_PROMPTS}", level=2)

  ## do prefetching for all sql queries (Good optimization ?)
  ## simulation loop


  for round in range(NUM_ROUNDS): 
    log_messages(msg=Fore.RED + f"الحكم: لنبدأ الجولة {NUMBER_TO_ORDINAL[round+1]} يا متبارزين" +  Style.RESET_ALL,level=1)
    log_messages(msg=Fore.BLUE + f"الحكم للشاعر الأول: {POET1_PROMPTS[round]}" + Style.RESET_ALL, level=1)
    log_messages(msg=Fore.BLUE + f"الحكم للشاعر الثاني: {POET2_PROMPTS[round]}" + Style.RESET_ALL, level=1)
    
    poet1_prompt = prepare_competitor_prompt(POET1_PROMPTS[round])
    poet2_prompt = prepare_competitor_prompt(POET2_PROMPTS[round])
    log_messages(msg="Prepared fetch prompts for the two competitors",level=2)
    log_messages(msg=f"Poet1 fetch prompt: {poet1_prompt}", level=2)
    log_messages(msg=f"Poet2 fetch prompt: {poet2_prompt}", level=2)

    # Async ?
    poet1_query_output = competitor_llm.invoke(poet1_prompt)
    poet2_query_output = competitor_llm.invoke(poet2_prompt)
    log_messages(msg="Invoked LLM with fetch prompts for the two competitors",level=2)
    log_messages(msg=f"structured output of competitor 1 {poet1_query_output}",level=2)
    log_messages(msg=f"structured output of competitor 2 {poet2_query_output}",level=2)

    poet_name1, poem_theme1, poem_qafya1, desired_qafya1 = parser(poet1_query_output)
    poet_name2, poem_theme2, poem_qafya2, desired_qafya2 = parser(poet2_query_output)
    log_messages(msg="Parsed output of the fetch prompts for the two competitors",level=2)

    true_poet_name1 = find_similar(query=poet_name1, index=index_poet, ground_truth=poets)
    true_poem_theme1 = find_similar(query=poem_theme1, index=index_theme, ground_truth=themes)

    true_poet_name2 = find_similar(query=poet_name2, index=index_poet, ground_truth=poets)
    true_poem_theme2 = find_similar(query=poem_theme2, index=index_theme, ground_truth=themes)

    fetch_result1 = do_query(true_poet_name1, true_poem_theme1)
    fetch_result2 = do_query(true_poet_name2, true_poem_theme2)
    log_messages(msg="Fetched verses for the two competitors",level=2)

    examples1 = construct_examples(fetch_result1, desired_qafya1)
    examples2 = construct_examples(fetch_result2, desired_qafya2)
    log_messages(msg="Constructed example verses as few shot prompts for the two competitors",level=2)
    log_messages(msg=f"Poet1 examples: {examples1}", level=2)
    log_messages(msg=f"Poet2 examples: {examples2}", level=2)

    generator1_prompt = prepare_generator_prompt(true_poet_name1, poem_qafya1, true_poem_theme1, examples1)
    generator2_prompt = prepare_generator_prompt(true_poet_name2, poem_qafya2, true_poem_theme2, examples2)
    log_messages(msg="Prepared generation for the two competitors",level=2)
    log_messages(msg=f"Poet1 generation prompt: {generator1_prompt}", level=2)
    log_messages(msg=f"Poet2 generation prompt: {generator2_prompt}", level=2)

    poet1_bait = generator_llm.invoke(generator1_prompt)
    poet2_bait = generator_llm.invoke(generator2_prompt)
    log_messages(msg="Each competitor generated his bait", level=2)

    poet1_bait = postprocess_bait(poet1_bait)
    poet2_bait = postprocess_bait(poet2_bait)
    log_messages(msg=Fore.BLUE + f"الشاعر الأول: {poet1_bait}" + Style.RESET_ALL, level=1)
    log_messages(msg=Fore.BLUE + f"الشاعر الثاني: {poet2_bait}" + Style.RESET_ALL, level=1)


    # Send verses character by character
    await send_verse(websocket, "poet1", poet1_bait)
    await asyncio.sleep(2)  # Pause between verses
    await send_verse(websocket, "poet2", poet2_bait)
    await asyncio.sleep(2)  # Pause between verses

    json_response={'poet1':poet1_bait,'poet2':poet2_bait}

    log_messages(msg="Judge starting evaluation", level=2)

    # Evaluating qafya score
    qafya_score1 = qafya_scorer(poet1_bait, desired_qafya1)
    qafya_score2 = qafya_scorer(poet2_bait, desired_qafya2)
    qafya_comment1 = qafya_comment(qafya_score1)
    qafya_comment2 = qafya_comment(qafya_score2)
    log_messages(msg="Judge calculated qafya score", level=2)

    # Evaluating meters score
    meters_score1 = meters_scorer(poet1_bait)
    meters_score2 = meters_scorer(poet2_bait)
    log_messages(msg="Judge calculated meters score", level=2)

    # Evaluating quality score
    quality_score1 = get_score_llm_output(commentator_llm.invoke(prepare_quality_scorer_prompt(poet1_bait)))
    quality_score2 = get_score_llm_output(commentator_llm.invoke(prepare_quality_scorer_prompt(poet2_bait)))
    log_messages(msg="Judge calculated quality score", level=2)

    # Saving round scores
    total_round_score1 = qafya_score1 + meters_score1 + quality_score1
    total_round_score2 = qafya_score2 + meters_score2 + quality_score2
    log_messages(msg=f"Competitor1: qafya_score: {qafya_score1}, meters_score: {meters_score1}, quality_score: {quality_score1}", level=2)
    log_messages(msg=f"Competitor2: qafya_score: {qafya_score2}, meters_score: {meters_score2}, quality_score: {quality_score2}", level=2)

    ROUND_SCORES["poet1"].append(total_round_score1)
    ROUND_SCORES["poet2"].append(total_round_score2)

    ## commentating on each poet bait in the round
    commentator_prompt1 = prepare_commentator_prompt(poet1_bait)
    commentator_prompt2 = prepare_commentator_prompt(poet2_bait)
    log_messages(msg="Prepared commentator prompts", level=2)
    log_messages(msg=f"First commentator_prompt: {commentator_prompt1}", level=2)
    log_messages(msg=f"Second commentator_prompt: {commentator_prompt2}", level=2)

    comment1 = postprocess_comment(commentator_llm.invoke(commentator_prompt1))
    comment2 = postprocess_comment(commentator_llm.invoke(commentator_prompt2))

    ## Saving each round comments (for the summarization agent in the end)
    judge_comment1 = comment1 + qafya_comment1
    judge_comment2 = comment2 + qafya_comment2

    ROUND_COMMENTS["poet1"].append(judge_comment1)
    ROUND_COMMENTS["poet2"].append(judge_comment2)

    log_messages(msg=Fore.RED + f"الحكم للشاعر الأول: {judge_comment1}" + Style.RESET_ALL, level=1)
    log_messages(msg=Fore.RED + f"الحكم للشاعر الثاني: {judge_comment2}" + Style.RESET_ALL, level=1)

    await send_judge_comment(websocket, f"الحكم للشاعر الأول: {judge_comment1}" +'\n'+f"الحكم للشاعر الثاني: {judge_comment2}")

    log_messages(msg=f"poet1 score: {ROUND_SCORES['poet1'][round]}", level=2)
    log_messages(msg=f"poet2 score: {ROUND_SCORES['poet2'][round]}", level=2)

    if ROUND_SCORES['poet1'][round] > ROUND_SCORES['poet2'][round]:
      log_messages(msg=Fore.RED + f"يبدو أن الشاعر {POET1} تفوق في الجولة {NUMBER_TO_ORDINAL[round+1]}" + Style.RESET_ALL, level=1)
      json_response['judge']= f"يبدو أن الشاعر {POET1} تفوق في الجولة {NUMBER_TO_ORDINAL[round+1]}"
      await send_judge_comment(websocket, json_response['judge'])
    elif ROUND_SCORES['poet1'][round] < ROUND_SCORES['poet2'][round]:
      log_messages(msg=Fore.RED + f"يبدو أن الشاعر {POET2} تفوق في الجولة {NUMBER_TO_ORDINAL[round+1]}" + Style.RESET_ALL, level=1)
      json_response['judge']=f"يبدو أن الشاعر {POET2} تفوق في الجولة {NUMBER_TO_ORDINAL[round+1]}"
      await send_judge_comment(websocket, json_response['judge'])
    else:
       log_messages(msg=f"تعادل الشاعران في الجولة {NUMBER_TO_ORDINAL[round+1]}",level=1)
       json_response['judge']=f"تعادل الشاعران في الجولة {NUMBER_TO_ORDINAL[round+1]}"
       await send_judge_comment(websocket, json_response['judge'])

  poet1_total_score = sum(ROUND_SCORES["poet1"])
  poet2_total_score = sum(ROUND_SCORES["poet2"])

  if poet1_total_score > poet2_total_score:
    log_messages(msg=Fore.RED + f"أنتصر الشاعر {POET1} في هذه المساجلة الشعرية" + Style.RESET_ALL, level=1)
    battle_result=f"أنتصر الشاعر {POET1} في هذه المساجلة الشعرية"
    await send_judge_comment(websocket, battle_result)

  elif poet1_total_score < poet2_total_score:
    log_messages(msg=Fore.RED + f"أنتصر الشاعر {POET2} في هذه المساجلة الشعرية" + Style.RESET_ALL, level=1)
    json_response['judge']=f"أنتصر الشاعر {POET2} في هذه المساجلة الشعرية" 
    battle_result=f"أنتصر الشاعر {POET2} في هذه المساجلة الشعرية"
    await send_judge_comment(websocket, battle_result)

  else:
    log_messages(msg=Fore.RED + "تعادل الشاعران في هذه المبارزة الشعرية" + Style.RESET_ALL,level=1)
    json_response['judge']="تعادل الشاعران في هذه المبارزة الشعرية"
    battle_result=f"تعادل الشاعران في هذه الجولة الشعرية"
    await send_judge_comment(websocket, battle_result)


async def send_verse(websocket, poet_key, verse):
    for char in verse:
        await websocket.send_text(json.dumps({poet_key: char}))
        await asyncio.sleep(0.1)  # Simulate slow processing

async def send_judge_comment(websocket, comment):
    await websocket.send_text(json.dumps({"Judge": comment}))
# WebSocket endpoint
@app.websocket("/ws/battle")
async def websocket_endpoint(
    websocket: WebSocket,
    poet1: str = Query(...),
    poet2: str = Query(...),
    topics: str = Query(...)
):
    await websocket.accept()
    # global POET1, POET2, ROUND_THEMES
    # POET1 = poet1
    # POET2 = poet2
    ROUND_THEMES = topics.split(',')
    NUM_ROUNDS=len(ROUND_THEMES)

    try:
        await run_simulation(websocket,POET1=poet1,POET2=poet2,ROUND_THEMES=ROUND_THEMES,NUM_ROUNDS=NUM_ROUNDS)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8002)
