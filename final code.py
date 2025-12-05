# -*- coding: utf-8 -*-
"""
تطبيق Streamlit للحاسبة المالية المتقدمة.

يوفر هذا التطبيق واجهة لحساب الفائدة البسيطة، الفائدة المركبة، والفائدة المركبة المستمرة،
بالإضافة إلى تحليل استهلاك القروض (Amortization Schedule) مع رسوم بيانية توضيحية.
"""
import streamlit as st
import math
import pandas as pd
from typing import Callable, Dict, Tuple, List

# -------------------------------------------------------------------
# الخطوة 1: إضافة كود تتبع Google Analytics لإثبات الملكية و SEO
# -------------------------------------------------------------------

# !! هام جداً: بمعرّف القياس  Google Analytics
GA_MEASUREMENT_ID = "G-NJML7HP1M9"  

# هذا الكود يقوم بحقن شفرة التتبع في رأس الصفحة
st.markdown(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag( ){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
    """, unsafe_allow_html=True)
# --------------------------------
# 1. إعدادات الصفحة وتحميل الأنماط (CSS)
# --------------------------------

st.set_page_config(
    page_title="الحاسبة المالية المتقدمة | فوائد وقروض",
    page_icon="llogo.png",
    layout="centered",
    initial_sidebar_state="collapsed" # Shaden Al-Ghamdi
)


def load_css(file_name: str):
    """تحميل ملف الأنماط CSS خارجي وتطبيقه على التطبيق."""
    try:
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"ملف الأنماط {file_name} غير موجود. سيتم استخدام الأنماط الافتراضية.")

load_css("final style.css")

# --------------------------------
# 2. تحسينات SEO (لجذب محركات البحث)
# --------------------------------

# العنوان الرئيسي الذي يراه المستخدم ومحرك البحث
st.title("الحاسبة المالية ")

# وصف موجز وغني بالكلمات المفتاحية
st.markdown("""
أداة مالية شاملة لحساب **الفائدة البسيطة**، **الفائدة المركبة**، **الفائدة المركبة المستمرة**، و**القسط الشهري للقروض**. 
احصل على تحليل استهلاك تفصيلي ورسوم بيانية توضيحية لتخطيط مالي أفضل.
""")

# عرض البنر بعد العنوان الرئيسي
try:
    st.image("banner.png", use_column_width=True)
except FileNotFoundError:
    st.error("ملف البنر 'banner.png' غير موجود.")


# --------------------------------
# 3. الدوال الرياضية والمالية الأساسية (بدون تغيير)
# --------------------------------

def fmt(x: float) -> str:
    return f"{x:,.2f}"

def simple_interest(P: float, r: float, t_months: int) -> Tuple[float, float]:
    t_years = t_months / 12.0
    A = P * (1 + r * t_years)
    I = A - P
    return I, A

def compound_interest(P: float, r: float, t_months: int, m: int) -> Tuple[float, float]:
    t_years = t_months / 12.0
    if t_years == 0: return 0.0, P
    A = P * ((1 + r / m) ** (m * t_years))
    I = A - P
    return I, A

def continuous_compound(P: float, r: float, t_months: int) -> Tuple[float, float]:
    t_years = t_months / 12.0
    A = P * math.exp(r * t_years)
    I = A - P
    return I, A

def monthly_payment(P: float, r: float, t_months: int) -> float:
    if t_months <= 0: return P
    i = r / 12.0
    if i == 0: return P / t_months
    return P * i / (1 - (1 + i) ** -t_months)

def amortization_schedule(P: float, r: float, t_months: int) -> pd.DataFrame:
    monthly_rate = r / 12.0
    payment = monthly_payment(P, r, t_months)
    schedule_data = []
    remaining_balance = P
    
    for month in range(1, t_months + 1):
        interest_paid = remaining_balance * monthly_rate
        principal_paid = payment - interest_paid
        remaining_balance -= principal_paid
        
        if month == t_months or remaining_balance < 0:
            principal_paid += remaining_balance
            remaining_balance = 0.0
        
        schedule_data.append({
            "الشهر": month, "القسط الشهري": payment, "الفائدة المدفوعة": interest_paid,
            "أصل الدين المسدد": principal_paid, "الرصيد المتبقي": remaining_balance
        })
            
    df = pd.DataFrame(schedule_data)
    for col in ["القسط الشهري", "الفائدة المدفوعة", "أصل الدين المسدد", "الرصيد المتبقي"]:
        df[col] = df[col].apply(lambda x: round(x, 2))
    return df

# --------------------------------
# 4. بنية العمليات وواجهة المستخدم (بدون تغيير جوهري)
# --------------------------------

CALCULATION_MODES = {
    "الفائدة البسيطة": {"description": "تحسب الفائدة على الأصل فقط", "func": simple_interest, "params": ["P", "r", "t_months"], "result_labels": ("إجمالي الفائدة", "المبلغ النهائي")},
    "الفائدة المركبة (متقطعة)": {"description": "تُضاف الفائدة للأصل على دفعات خلال السنة", "func": compound_interest, "params": ["P", "r", "t_months", "m"], "result_labels": ("إجمالي الفائدة", "المبلغ النهائي")},
    "الفائدة المركبة المستمرة": {"description": "الفائدة تُحسب بشكل مستمر باستخدام الأسس", "func": continuous_compound, "params": ["P", "r", "t_months"], "result_labels": ("إجمالي الفائدة", "المبلغ النهائي")},
    "القسط الشهري للقرض (تحليل الاستهلاك)": {"description": "يحسب القسط الشهري ويقدم جدول استهلاك تفصيلي للقرض", "func": monthly_payment, "params": ["P", "r", "t_months"], "result_labels": ("القسط الشهري",)}
}

st.markdown("---") # فاصل بصري

choice = st.selectbox("اختر العملية:", list(CALCULATION_MODES.keys()))
mode_config = CALCULATION_MODES[choice]
st.caption(mode_config["description"])

inputs: Dict[str, float | None] = {}
inputs["P"] = st.number_input("المبلغ (P):", min_value=0.0, format="%.2f", step=1.0, key="P")
inputs["r_pct"] = st.number_input("النسبة السنوية (%):", min_value=0.0, format="%.2f", step=1.0, key="r_pct")
inputs["t_months"] = st.number_input("المدة (بالأشهر):", min_value=1, step=1, format="%d", key="t_months")

if "m" in mode_config["params"]:
    inputs["m"] = st.number_input("عدد الدفعات في السنة (m):", min_value=1, step=1, format="%d", key="m")

def clear_fields():
    for key in ["P", "r_pct", "t_months", "m"]:
        if key in st.session_state:
            st.session_state[key] = 0.0 if key in ['P', 'r_pct'] else 1

col1, col2 = st.columns(2)
with col1:
    calculate_button = st.button("احسب", type="primary")
with col2:
    st.button("مسح الحقول", on_click=clear_fields)

# --------------------------------
# 5. منطق الحساب وعرض النتائج (بدون تغيير)
# --------------------------------

if calculate_button:
    P = inputs["P"]
    r_pct = inputs["r_pct"]
    t_months = int(inputs.get("t_months", 0))
    m_val = int(inputs.get("m", 1))

    if not P or P <= 0 or not r_pct or r_pct < 0 or not t_months or t_months <= 0:
        st.error("يرجى إدخال قيم صحيحة وموجبة لجميع الحقول")
    else:
        r = r_pct / 100.0
        func = mode_config["func"]
        params = {"P": P, "r": r, "t_months": t_months}
        if "m" in mode_config["params"]:
            params["m"] = m_val

        result = func(**params)
        st.subheader("النتائج")
        
        if isinstance(result, tuple):
            cols = st.columns(len(result))
            for i, (label, value) in enumerate(zip(mode_config["result_labels"], result)):
                with cols[i]:
                    st.metric(label=label, value=fmt(value))
        else:
            st.metric(label=mode_config["result_labels"][0], value=fmt(result))

        if choice == "القسط الشهري للقرض (تحليل الاستهلاك)":
            st.subheader("جدول استهلاك القرض")
            amort_df = amortization_schedule(P, r, t_months)
            st.dataframe(amort_df, use_container_width=True)
            
            st.subheader("توزيع القسط الشهري (فائدة مقابل أصل)")
            chart_data = amort_df[["الشهر", "الفائدة المدفوعة", "أصل الدين المسدد"]].set_index("الشهر")
            st.bar_chart(chart_data)
            
            st.subheader("الرصيد المتبقي شهراً بشهر")
            balance_chart = amort_df[["الشهر", "الرصيد المتبقي"]].set_index("الشهر")
            st.line_chart(balance_chart)
            
        else:
            st.subheader("الرسم البياني للنمو")
            num_points = min(t_months, 120)
            step = max(1, t_months // num_points)
            months_range = list(range(1, t_months + 1, step))
            if t_months not in months_range: months_range.append(t_months)
            
            values: List[float] = []
            for m in months_range:
                if choice == "الفائدة البسيطة": values.append(simple_interest(P, r, m)[1])
                elif choice == "الفائدة المركبة (متقطعة)": values.append(compound_interest(P, r, m, m_val)[1])
                elif choice == "الفائدة المركبة المستمرة": values.append(continuous_compound(P, r, m)[1])

            chart_data = pd.DataFrame({"الشهر": months_range, "القيمة المتراكمة": values})
            st.line_chart(chart_data.set_index("الشهر"))

# --------------------------------
# 6. قسم المعلومات الإضافية (بدون تغيير)
# --------------------------------

st.markdown("---")
st.info("💡 ملاحظة: هذه النتائج هي تقديرات رياضية. للحصول على عرض مالي رسمي، يرجى استشارة مختص")

with st.expander("المعادلات الرياضية المستخدمة"):
    st.markdown("""
     **ملاحظة مهمة:** جميع هذه المعادلات تفترض أن سعر الفائدة ثابت طوال المدة
     
   **1. القسط الشهري للقرض (Amortization):**
    يتم حسابه باستخدام معادلة القسط الثابت:
    $$
    M = P \\frac{i(1+i)^n}{(1+i)^n - 1}
    $$
    حيث:
    *   $M$: القسط الشهري
    *   $P$: أصل القرض
    *   $i$: سعر الفائدة الشهري (السنوي مقسوم على 12)
    *   $n$: عدد الأشهر الكلي

    **2. الفائدة المركبة (Compound Interest):**
    $$
    A = P \\left(1 + \\frac{r}{m}\\right)^{mt}
    $$
    حيث:
    *   $A$: المبلغ النهائي
    *   $P$: أصل المبلغ
    *   $r$: سعر الفائدة السنوي
    *   $m$: عدد مرات إضافة الفائدة في السنة
    *   $t$: المدة بالسنوات

    **3. الفائدة المركبة المستمرة (Continuous Compounding):**
    $$
    A = P e^{rt}
    $$
    حيث:
    *   $A$: المبلغ النهائي
    *   $P$: أصل المبلغ
    *   $e$: الثابت الرياضي (قاعدة اللوغاريتم الطبيعي)
    *   $r$: سعر الفائدة السنوي
    *   $t$: المدة بالسنوات

    **4. الفائدة البسيطة (Simple Interest):**
    $$
    A = P(1 + rt)
    $$
    حيث:
    *   $A$: المبلغ النهائي
    *   $P$: أصل المبلغ
    *   $r$: سعر الفائدة السنوي
    *   $t$: المدة بالسنوات

    """)

# المربع الأزرق الخاص بالحقوق الأكاديمية
st.markdown(
    """
    <style>
    .footer-academic {
        text-align: center;
        padding: 12px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
    }
    @media (prefers-color-scheme: dark) {
        .footer-academic { background-color: #333333; color: #FFFFFF; }
    }
    @media (prefers-color-scheme: light) {
        .footer-academic { background-color: #EAF4FF; color: #000000; }
    }
    </style>
    <div class="footer-academic">
          طالبات د.ريم القثامي | مقرر برمجة رياضية
    </div>
    """,
    unsafe_allow_html=True
)
