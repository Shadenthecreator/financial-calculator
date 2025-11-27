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

# --------------------------------
# 1. إعدادات الصفحة وتحميل الأنماط (CSS)
# --------------------------------

# --- التعديل: إضافة أيقونة الصفحة (Favicon) وتغيير العنوان ---
st.set_page_config(
    page_title="حاسبة الفوائد والقسط الشهري",
    page_icon="icon.png",  # <-- استخدام ملف icon.png كأيقونة للمتصفح
    layout="centered",
    initial_sidebar_state="collapsed"
)
# --- نهاية التعديل ---

def load_css(file_name: str):
    """تحميل ملف الأنماط CSS خارجي وتطبيقه على التطبيق."""
    try:
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"ملف الأنماط {file_name} غير موجود. سيتم استخدام الأنماط الافتراضية.")

# تحميل الأنماط من ملف final style.css
load_css("final style.css")

# --------------------------------
# 2. الدوال الرياضية والمالية الأساسية
# --------------------------------

def fmt(x: float) -> str:
    """تنسيق الرقم كعملة."""
    return f"{x:,.2f}"

def simple_interest(P: float, r: float, t_months: int) -> Tuple[float, float]:
    """حساب الفائدة البسيطة والمبلغ النهائي."""
    t_years = t_months / 12.0
    A = P * (1 + r * t_years)
    I = A - P
    return I, A

def compound_interest(P: float, r: float, t_months: int, m: int) -> Tuple[float, float]:
    """حساب الفائدة المركبة (متقطعة)."""
    t_years = t_months / 12.0
    if t_years == 0: return 0.0, P
    A = P * ((1 + r / m) ** (m * t_years))
    I = A - P
    return I, A

def continuous_compound(P: float, r: float, t_months: int) -> Tuple[float, float]:
    """حساب الفائدة المركبة المستمرة."""
    t_years = t_months / 12.0
    A = P * math.exp(r * t_years)
    I = A - P
    return I, A

def monthly_payment(P: float, r: float, t_months: int) -> float:
    """تحسب القسط الشهري الثابت (PMT) للقرض."""
    if t_months <= 0: return P
    i = r / 12.0
    if i == 0: return P / t_months
    return P * i / (1 - (1 + i) ** -t_months)

def amortization_schedule(P: float, r: float, t_months: int) -> pd.DataFrame:
    """تنشئ جدول استهلاك القرض (Amortization Schedule) شهراً بشهر."""
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
# 3. بنية العمليات (Configuration)
# --------------------------------

CALCULATION_MODES = {
    "الفائدة البسيطة": {"description": "تحسب الفائدة على الأصل فقط.", "func": simple_interest, "params": ["P", "r", "t_months"], "result_labels": ("إجمالي الفائدة", "المبلغ النهائي")},
    "الفائدة المركبة (متقطعة)": {"description": "تُضاف الفائدة للأصل على دفعات خلال السنة.", "func": compound_interest, "params": ["P", "r", "t_months", "m"], "result_labels": ("إجمالي الفائدة", "المبلغ النهائي")},
    "الفائدة المركبة المستمرة": {"description": "الفائدة تُحسب بشكل مستمر باستخدام الأسس.", "func": continuous_compound, "params": ["P", "r", "t_months"], "result_labels": ("إجمالي الفائدة", "المبلغ النهائي")},
    "القسط الشهري للقرض (تحليل الاستهلاك)": {"description": "يحسب القسط الشهري ويقدم جدول استهلاك تفصيلي للقرض.", "func": monthly_payment, "params": ["P", "r", "t_months"], "result_labels": ("القسط الشهري",)}
}

# --------------------------------
# 4. واجهة المستخدم الرئيسية (UI)
# --------------------------------

# --- التعديلات النهائية هنا ---
# 1. استخدام البنر الأصلي (banner.png)
try:
    st.image("banner.png", use_column_width=True)
except FileNotFoundError:
    st.error("ملف البنر 'banner.png' غير موجود. يرجى التأكد من وجوده في نفس المجلد.")

# 2. استخدام عنوان أصغر (subheader) تحت البنر
st.subheader("حاسبة الفوائد والقسط الشهري")

# 3. وضع المربع الأزرق تحت العنوان مباشرة
st.info("طالبات د.ريم القثامي | مقرر برمجة رياضية")
# --- نهاية التعديلات ---

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
# 5. منطق الحساب وعرض النتائج
# --------------------------------

if calculate_button:
    P = inputs["P"]
    r_pct = inputs["r_pct"]
    t_months = int(inputs.get("t_months", 0))
    m_val = int(inputs.get("m", 1))

    if not P or P <= 0 or not r_pct or r_pct < 0 or not t_months or t_months <= 0:
        st.error("يرجى إدخال قيم صحيحة وموجبة لجميع الحقول.")
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
# 6. قسم المعلومات الإضافية (Footer)
# --------------------------------

st.markdown("---")
st.info("💡 ملاحظة: هذه النتائج هي تقديرات رياضية. للحصول على عرض مالي رسمي، يرجى استشارة مختص.")

with st.expander("المنهجية والمعادلات الرياضية المستخدمة"):
    st.markdown("""
    **1. القسط الشهري للقرض:** $M = P \\frac{i(1+i)^n}{(1+i)^n - 1}$
    
    **2. الفائدة المركبة:** $A = P (1 + \\frac{r}{m})^{mt}$
    
    **3. الفائدة المركبة المستمرة:** $A = P e^{rt}$
    
    **4. الفائدة البسيطة:** $A = P(1 + rt)$
    """)
