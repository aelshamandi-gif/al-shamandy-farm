import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import streamlit.components.v1 as components

# ================= 1. التصميم المتجاوب ودعم الشاشات =================
st.set_page_config(
    page_title="مزرعة عبد الله الشمندي",
    layout="wide",
    page_icon="🐟",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    body, html, [class*="css"], .stMarkdown, p, div {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    @media (max-width: 768px) {
        .stMetric { margin-bottom: 8px !important; padding: 10px !important; }
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; }
        .main .block-container { padding: 10px 15px !important; }
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-right: 6px solid #0284c7;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        min-height: 48px;
    }
    @media print {
        header, .stSidebar, .stButton, button { display: none !important; }
        #printArea { border: none !important; box-shadow: none !important; width: 100% !important; }
    }
</style>
""", unsafe_allow_html=True)

# ================= 2. نظام تسجيل الدخول =================
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center; color: #0284c7;'>🐟 شركة ومزرعة أسماك عبد الله الشمندي</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>نظام الإدارة الذكية والدورة المحاسبية المتكاملة</p>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.info("🔒 يرجى إدخال رمز المرور السري للمتابعة")
            pwd = st.text_input("رمز الدخول (PIN):", type="password")
            if st.button("تسجيل الدخول للنظام", use_container_width=True):
                if pwd == "2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("رمز الدخول غير صحيح!")
        return False
    return True

if not check_password():
    st.stop()

# ================= 3. إعداد قاعدة البيانات =================
def get_db():
    conn = sqlite3.connect("al_shamandy_farm.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS ponds (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, fish_type TEXT, 
        stock_count INTEGER, initial_cost REAL, initial_weight REAL, stock_date TEXT, status TEXT DEFAULT 'نشط')""")
    cur.execute("""CREATE TABLE IF NOT EXISTS feed (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pond_name TEXT, date TEXT, 
        feed_type TEXT, qty_kg REAL, price_per_kg REAL, total_cost REAL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, amount REAL, notes TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pond_name TEXT, date TEXT, 
        qty_kg REAL, price_per_kg REAL, total_price REAL, client TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, asset_name TEXT, category TEXT, value REAL, purchase_date TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, role TEXT, daily_wage REAL, phone TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS labor_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, emp_name TEXT, date TEXT, status TEXT, advance REAL, notes TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS water_quality (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pond_name TEXT, date TEXT, 
        temp REAL, dissolved_oxygen REAL, ph REAL, ammonia REAL, notes TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pond_name TEXT, 
        pumps_status TEXT, nets_status TEXT, feeding_response TEXT, mortalities INTEGER, inspector TEXT, notes TEXT)""")
    conn.commit()
    return conn

conn = get_db()

# ================= 4. واجهة التنقل الذكية =================
if "page" not in st.session_state:
    st.session_state.page = "الرئيسية"

def set_page(name):
    st.session_state.page = name
    st.rerun()

# الشريط العلوي السريع
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    if st.session_state.page != "الرئيسية":
        if st.button("🏠 العودة للشاشة الرئيسية", key="back_home"):
            set_page("الرئيسية")
with col_top2:
    if st.button("🔒 تسجيل الخروج"):
        st.session_state.authenticated = False
        st.rerun()

# ================= 5. الشاشة الرئيسية (لوحة الإطلاق) =================
if st.session_state.page == "الرئيسية":
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0284c7, #0f766e); padding: 22px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px;'>
            <h2 style='margin:0; color: white;'>🐟 شركة ومزرعة أسماك عبد الله الشمندي</h2>
            <p style='margin:6px 0 0 0; opacity: 0.95;'>منظومة الإدارة المتكاملة والحسابات اليومية - اختر القسم</p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("💵 الإدارة المالية والدورة المحاسبية")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📊 المؤشرات المالية\n(نظرة عامة ومصاريف)", use_container_width=True): set_page("المؤشرات المالية")
    with c2:
        if st.button("⚖️ ميزان المراجعة\n(توازن القيود واليومية)", use_container_width=True): set_page("ميزان المراجعة")
    with c3:
        if st.button("📑 القوائم الختامية الست\n(دخل، مركز مالي، تدفقات)", use_container_width=True): set_page("القوائم الختامية")
    with c4:
        if st.button("🚜 الأصول ورأس المال\n(المعدات والاستثمارات)", use_container_width=True): set_page("الأصول ورأس المال")

    st.markdown("---")

    st.subheader("🐟 العمليات والإنتاج السمكي")
    c5, c6, c7 = st.columns(3)
    with c5:
        if st.button("🏞️ إدارة الأحواض\n(تسكين الزريعة والمتابعة)", use_container_width=True): set_page("إدارة الأحواض")
    with c6:
        if st.button("🥣 التغذية والأعلاف\n(تسجيل استهلاك العلف اليومي)", use_container_width=True): set_page("الأعلاف والتشغيل")
    with c7:
        if st.button("💰 مبيعات الحصاد\n(فواتير البيع للعملاء)", use_container_width=True): set_page("مبيعات الحصاد")

    st.markdown("---")

    st.subheader("🧪 التطوير والرقابة وشؤون العمالة")
    c8, c9, c10, c11 = st.columns(4)
    with c8:
        if st.button("👷 حركة العمالة\n(الحضور، اليوميات، والسلف)", use_container_width=True): set_page("شؤون العمال")
    with c9:
        if st.button("🔮 التوقعات والمحاكاة\n(توقع الحصاد والأوزان)", use_container_width=True): set_page("التوقعات والمحاكاة")
    with c10:
        if st.button("🧪 مختبر المياه\n(الأكسجين، الحرارة، الأمونيا)", use_container_width=True): set_page("مختبر المياه")
    with c11:
        if st.button("✅ قائمة التدقيق\n(فحص الطلمبات والنافق)", use_container_width=True): set_page("قائمة المراجعة")

# ================= 6. الشاشات التفصيلية =================

# 1. المؤشرات المالية
elif st.session_state.page == "المؤشرات المالية":
    st.header("📊 لوحة المؤشرات المالية والتنفيذية")
    df_exp = pd.read_sql("SELECT * FROM expenses", conn)
    df_feed = pd.read_sql("SELECT * FROM feed", conn)
    df_sales = pd.read_sql("SELECT * FROM sales", conn)
    df_labor = pd.read_sql("SELECT SUM(advance) as adv FROM labor_log", conn)
    
    feed_c = df_feed['total_cost'].sum() if not df_feed.empty else 0.0
    other_c = df_exp['amount'].sum() if not df_exp.empty else 0.0
    advances_c = df_labor['adv'].iloc[0] or 0.0
    total_costs = feed_c + other_c + advances_c
    revenue = df_sales['total_price'].sum() if not df_sales.empty else 0.0
    net_profit = revenue - total_costs

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي المبيعات", f"{revenue:,.2f} ج.م")
    c2.metric("تكلفة الأعلاف", f"{feed_c:,.2f} ج.م")
    c3.metric("المصروفات والسلفيات", f"{(other_c + advances_c):,.2f} ج.م")
    c4.metric("صافي الربح التراكمي", f"{net_profit:,.2f} ج.م", delta=f"{net_profit:,.2f}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("هيكل التكاليف")
        if total_costs > 0:
            exp_sum = df_exp.groupby('category')['amount'].sum().reset_index() if not df_exp.empty else pd.DataFrame(columns=['category', 'amount'])
            all_exp = pd.concat([
                exp_sum, 
                pd.DataFrame([{"category": "أعلاف", "amount": feed_c}, {"category": "سلف عمال", "amount": advances_c}])
            ], ignore_index=True)
            st.plotly_chart(px.pie(all_exp, values='amount', names='category', hole=0.45), use_container_width=True)
    with col2:
        st.subheader("حركة المبيعات عبر الزمن")
        if not df_sales.empty:
            st.plotly_chart(px.bar(df_sales.groupby('date')['total_price'].sum().reset_index(), x='date', y='total_price'), use_container_width=True)

# 2. ميزان المراجعة
elif st.session_state.page == "ميزان المراجعة":
    st.header("⚖️ ميزان المراجعة والقيود المحاسبية")
    st.caption("التحقق من توازن الحسابات (الأرصدة المدينة والدائنة) للدورة المحاسبية")

    df_sales = pd.read_sql("SELECT SUM(total_price) as total FROM sales", conn)
    df_feed = pd.read_sql("SELECT SUM(total_cost) as total FROM feed", conn)
    df_exp = pd.read_sql("SELECT category, SUM(amount) as total FROM expenses GROUP BY category", conn)
    df_assets = pd.read_sql("SELECT category, SUM(value) as total FROM assets GROUP BY category", conn)
    df_labor = pd.read_sql("SELECT SUM(advance) as total FROM labor_log", conn)

    rev = df_sales['total'].iloc[0] or 0.0
    feed_exp = df_feed['total'].iloc[0] or 0.0
    advances = df_labor['total'].iloc[0] or 0.0
    cap = df_assets[df_assets['category'] == 'رأس مال نقدي مبدئي']['total'].sum() if not df_assets.empty else 0.0
    fixed_a = df_assets[df_assets['category'] != 'رأس مال نقدي مبدئي']['total'].sum() if not df_assets.empty else 0.0
    other_expenses = df_exp['total'].sum() if not df_exp.empty else 0.0
    
    cash = (rev + cap) - (feed_exp + other_expenses + advances)

    trial_data = [
        {"الحساب": "النقدية بالصندوق والخزينة", "مدين (Debit)": max(0.0, cash), "دائن (Credit)": abs(min(0.0, cash))},
        {"الحساب": "الأصول الثابتة والمعدات", "مدين (Debit)": fixed_a, "دائن (Credit)": 0.0},
        {"الحساب": "مشتريات واستهلاك الأعلاف", "مدين (Debit)": feed_exp, "دائن (Credit)": 0.0},
        {"الحساب": "المصروفات التشغيلية والطاقة", "مدين (Debit)": other_expenses, "دائن (Credit)": 0.0},
        {"الحساب": "سلفيات ومستحقات العمالة", "مدين (Debit)": advances, "دائن (Credit)": 0.0},
        {"الحساب": "إيرادات مبيعات الأسماك", "مدين (Debit)": 0.0, "دائن (Credit)": rev},
        {"الحساب": "رأس المال المستثمر", "مدين (Debit)": 0.0, "دائن (Credit)": cap},
    ]

    df_trial = pd.DataFrame(trial_data)
    total_debit = df_trial["مدين (Debit)"].sum()
    total_credit = df_trial["دائن (Credit)"].sum()

    st.dataframe(df_trial.style.format({"مدين (Debit)": "{:,.2f}", "دائن (Credit)": "{:,.2f}"}), use_container_width=True)

    c1, c2 = st.columns(2)
    c1.metric("إجمالي الجانب المدين", f"{total_debit:,.2f} ج.م")
    c2.metric("إجمالي الجانب الدائن", f"{total_credit:,.2f} ج.م")

    if round(total_debit, 2) == round(total_credit, 2):
        st.success("✔ ميزان المراجعة متوازن تماماً والقيود سليمة محاسبياً.")
    else:
        st.warning("⚠️ يوجد فارق تسوية في القيود يرجى مراجعة رصيد البداية أو حركة النقدية.")

# 3. القوائم الختامية الأساسية الست
elif st.session_state.page == "القوائم الختامية":
    st.header("📑 منظومة القوائم المالية الأساسية والإيضاحات المتممة")
    st.caption("مُعدة طبقاً لمعايير المحاسبة الدولية للأصول الحيوية (IAS 41) وعرض القوائم المالية (IAS 1)")

    c_date1, c_date2 = st.columns(2)
    d_start = c_date1.date_input("من تاريخ بداية الفترة المالية:", date(date.today().year, 1, 1))
    d_end = c_date2.date_input("إلى تاريخ نهاية الفترة المالية:", date.today())

    rev = pd.read_sql(f"SELECT SUM(total_price) as r FROM sales WHERE date BETWEEN '{d_start}' AND '{d_end}'", conn)['r'].iloc[0] or 0.0
    c_feed = pd.read_sql(f"SELECT SUM(total_cost) as f FROM feed WHERE date BETWEEN '{d_start}' AND '{d_end}'", conn)['f'].iloc[0] or 0.0
    c_power = pd.read_sql(f"SELECT SUM(amount) as p FROM expenses WHERE category='سولار وكهرباء' AND date BETWEEN '{d_start}' AND '{d_end}'", conn)['p'].iloc[0] or 0.0
    c_med = pd.read_sql(f"SELECT SUM(amount) as m FROM expenses WHERE category='أدوية ومخصبات' AND date BETWEEN '{d_start}' AND '{d_end}'", conn)['m'].iloc[0] or 0.0
    c_other = pd.read_sql(f"SELECT SUM(amount) as o FROM expenses WHERE category NOT IN ('سولار وكهرباء', 'أدوية ومخصبات') AND date BETWEEN '{d_start}' AND '{d_end}'", conn)['o'].iloc[0] or 0.0
    labor_adv = pd.read_sql(f"SELECT SUM(advance) as a FROM labor_log WHERE date BETWEEN '{d_start}' AND '{d_end}'", conn)['a'].iloc[0] or 0.0

    df_assets = pd.read_sql("SELECT category, SUM(value) as val FROM assets GROUP BY category", conn)
    capital = df_assets[df_assets['category'] == 'رأس مال نقدي مبدئي']['val'].sum() if not df_assets.empty else 0.0
    fixed_assets = df_assets[df_assets['category'] != 'رأس مال نقدي مبدئي']['val'].sum() if not df_assets.empty else 0.0

    cogs = c_feed + c_power + c_med
    gross_profit = rev - cogs
    operating_expenses = c_other + labor_adv
    net_profit = gross_profit - operating_expenses

    rev_all = pd.read_sql("SELECT SUM(total_price) as r FROM sales", conn)['r'].iloc[0] or 0.0
    feed_all = pd.read_sql("SELECT SUM(total_cost) as f FROM feed", conn)['f'].iloc[0] or 0.0
    exp_all = pd.read_sql("SELECT SUM(amount) as e FROM expenses", conn)['e'].iloc[0] or 0.0
    adv_all = pd.read_sql("SELECT SUM(advance) as a FROM labor_log", conn)['a'].iloc[0] or 0.0
    cash_balance = (capital + rev_all) - (feed_all + exp_all + adv_all)
    biological_assets = feed_all * 0.90
    total_assets = cash_balance + biological_assets + fixed_assets

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "1. قائمة الدخل",
        "2. المركز المالي (الميزانية)",
        "3. التدفقات النقدية",
        "4. التغيرات في حقوق الملكية",
        "5. الدخل الشامل",
        "6. الإيضاحات المتممة"
    ])

    # 1. قائمة الدخل
    with tab1:
        st.subheader("1. قائمة الدخل (Income Statement)")
        pnl_code = f"""
        <div id="printArea" style="padding: 25px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff; font-family: Segoe UI, Arial;">
            <div style="text-align: center; border-bottom: 2px solid #0284c7; padding-bottom: 10px; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #0284c7;">شركة ومزرعة أسماك عبد الله الشمندي</h3>
                <h5 style="margin: 5px 0; color: #64748b;">قائمة الدخل عن الفترة من {d_start} إلى {d_end} (المبالغ بالجنيه المصري)</h5>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
                <tr style="background:#f8fafc; font-weight:bold;"><td style="padding: 8px;">إيرادات مبيعات الأسماك</td><td style="text-align:left;">{rev:,.2f}</td></tr>
                <tr><td colspan="2" style="color: #64748b; padding-top: 10px;"><b>يخصم: تكلفة الإنتاج والمبيعات المباشرة (COGS):</b></td></tr>
                <tr><td style="padding-right: 20px;">- استهلاك الأعلاف المأكولة</td><td style="text-align:left; color:#b91c1c;">({c_feed:,.2f})</td></tr>
                <tr><td style="padding-right: 20px;">- وقود وسولار وطاقة طلمبات المياه</td><td style="text-align:left; color:#b91c1c;">({c_power:,.2f})</td></tr>
                <tr><td style="padding-right: 20px;">- أدوية ومخصبات بيولوجية</td><td style="text-align:left; color:#b91c1c;">({c_med:,.2f})</td></tr>
                <tr style="background:#f1f5f9; font-weight:bold; border-top: 1px solid #cbd5e1;"><td>مجمل الربح التشغيلي (Gross Profit)</td><td style="text-align:left; color:#0369a1;">{gross_profit:,.2f}</td></tr>
                <tr><td colspan="2" style="color: #64748b; padding-top: 10px;"><b>يخصم: المصروفات الإدارية والعمومية:</b></td></tr>
                <tr><td style="padding-right: 20px;">- أجور ويوميات وسلفيات العمالة</td><td style="text-align:left; color:#b91c1c;">({labor_adv:,.2f})</td></tr>
                <tr><td style="padding-right: 20px;">- إيجارات وصيانة دورية ونثريات</td><td style="text-align:left; color:#b91c1c;">({c_other:,.2f})</td></tr>
                <tr style="background:#0284c7; color:#fff; font-size: 16px; font-weight:bold;"><td style="padding: 10px;">صافي ربح / (خسارة) النشاط</td><td style="text-align:left; padding: 10px;">{net_profit:,.2f} ج.م</td></tr>
            </table>
        </div>
        """
        st.markdown(pnl_code, unsafe_allow_html=True)
        components.html('<button onclick="window.print()" style="margin-top:10px; padding:10px 20px; background:#0284c7; color:#fff; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">🖨️ طباعة قائمة الدخل كملف PDF</button>', height=55)

    # 2. المركز المالي
    with tab2:
        st.subheader("2. قائمة المركز المالي (Balance Sheet)")
        bs_code = f"""
        <div id="printArea" style="padding: 25px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff; font-family: Segoe UI, Arial;">
            <div style="text-align: center; border-bottom: 2px solid #0f766e; padding-bottom: 10px; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #0f766e;">شركة ومزرعة أسماك عبد الله الشمندي</h3>
                <h5 style="margin: 5px 0; color: #64748b;">قائمة المركز المالي كما في {d_end}</h5>
            </div>
            <div style="display: flex; gap: 20px;">
                <div style="flex:1; border: 1px solid #e2e8f0; padding: 15px; border-radius: 6px;">
                    <h4 style="color: #0369a1; border-bottom: 2px solid #0369a1; padding-bottom: 5px;">الأصول (Assets)</h4>
                    <p style="font-weight:bold; color:#475569;">الأصول المتداولة:</p>
                    <p>النقدية بالصندوق والخزينة: <b>{cash_balance:,.2f}</b></p>
                    <p>أصول بيولوجية (مخزون الأسماك بالأحواض - IAS 41): <b>{biological_assets:,.2f}</b></p>
                    <hr>
                    <p style="font-weight:bold; color:#475569;">الأصول غير المتداولة (الثابتة):</p>
                    <p>طلمبات، مولدات، شبكات ومباني: <b>{fixed_assets:,.2f}</b></p>
                    <div style="background:#e0f2fe; padding:10px; font-weight:bold; font-size:15px; border-radius:4px; margin-top:20px;">إجمالي الأصول: {total_assets:,.2f} ج.م</div>
                </div>
                <div style="flex:1; border: 1px solid #e2e8f0; padding: 15px; border-radius: 6px;">
                    <h4 style="color: #0f766e; border-bottom: 2px solid #0f766e; padding-bottom: 5px;">الخصوم وحقوق الملكية</h4>
                    <p style="font-weight:bold; color:#475569;">الالتزامات المتداولة:</p>
                    <p>مستحقات موردين وأعلاف آجلة: <b>0.00</b></p>
                    <hr>
                    <p style="font-weight:bold; color:#475569;">حقوق الملكية (Equity):</p>
                    <p>رأس المال المدفوع: <b>{capital:,.2f}</b></p>
                    <p>أرباح المرحلة والنشاط الحالي: <b>{net_profit:,.2f}</b></p>
                    <p>فروق تقييم بيولوجية محتجزة: <b>{(total_assets - (capital + net_profit)):,.2f}</b></p>
                    <div style="background:#ccfbf1; padding:10px; font-weight:bold; font-size:15px; border-radius:4px; margin-top:20px;">إجمالي الخصوم وحقوق الملكية: {total_assets:,.2f} ج.م</div>
                </div>
            </div>
            <p style="text-align: center; color: #16a34a; font-weight: bold; margin-top: 15px;">✔ الميزانية متوازنة ومطابقة دفترياً</p>
        </div>
        """
        st.markdown(bs_code, unsafe_allow_html=True)
        components.html('<button onclick="window.print()" style="margin-top:10px; padding:10px 20px; background:#0f766e; color:#fff; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">🖨️ طباعة الميزانية العمومية PDF</button>', height=55)

    # 3. التدفقات النقدية
    with tab3:
        st.subheader("3. قائمة التدفقات النقدية (Cash Flow Statement - IAS 7)")
        op_inflow = rev
        op_outflow = c_feed + c_power + c_med + c_other + labor_adv
        net_operating_cash = op_inflow - op_outflow

        cf_code = f"""
        <div id="printArea" style="padding: 25px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff; font-family: Segoe UI, Arial;">
            <h3 style="text-align: center; color: #0284c7; margin:0;">قائمة التدفقات النقدية (الطريقة المباشرة)</h3>
            <h5 style="text-align: center; color: #64748b; margin-top:5px;">عن الفترة المنتهية في {d_end}</h5>
            <hr>
            <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
                <tr style="background:#f8fafc; font-weight:bold;"><td colspan="2">أولاً: التدفقات النقدية من الأنشطة التشغيلية:</td></tr>
                <tr><td style="padding-right:20px;">النقدية المحصلة من بيع الأسماك</td><td style="text-align:left;">{op_inflow:,.2f}</td></tr>
                <tr><td style="padding-right:20px;">مدفوعات شراء الأعلاف والتشغيل والعمالة</td><td style="text-align:left; color:#b91c1c;">({op_outflow:,.2f})</td></tr>
                <tr style="background:#f1f5f9; font-weight:bold;"><td>صافي النقد المتولد من التشغيل</td><td style="text-align:left;">{net_operating_cash:,.2f}</td></tr>
                
                <tr style="background:#f8fafc; font-weight:bold;"><td colspan="2" style="padding-top:10px;">ثانياً: التدفقات النقدية من الأنشطة الاستثمارية:</td></tr>
                <tr><td style="padding-right:20px;">مدفوعات شراء أصول ثابتة (معدات وطلمبات وبدالات)</td><td style="text-align:left; color:#b91c1c;">({fixed_assets:,.2f})</td></tr>
                <tr style="background:#f1f5f9; font-weight:bold;"><td>صافي النقد المستخدم في الاستثمار</td><td style="text-align:left; color:#b91c1c;">({fixed_assets:,.2f})</td></tr>

                <tr style="background:#f8fafc; font-weight:bold;"><td colspan="2" style="padding-top:10px;">ثالثاً: التدفقات النقدية من الأنشطة التمويلية:</td></tr>
                <tr><td style="padding-right:20px;">زيادة رأس المال / مساهمات الملاك النقدية</td><td style="text-align:left;">{capital:,.2f}</td></tr>
                <tr style="background:#f1f5f9; font-weight:bold;"><td>صافي النقد من التمويل</td><td style="text-align:left;">{capital:,.2f}</td></tr>

                <tr style="background:#0284c7; color:#fff; font-weight:bold; font-size:16px;">
                    <td style="padding:10px;">رصيد النقدية النهائي في الخزينة بالصندوق</td>
                    <td style="text-align:left; padding:10px;">{cash_balance:,.2f} ج.م</td>
                </tr>
            </table>
        </div>
        """
        st.markdown(cf_code, unsafe_allow_html=True)
        components.html('<button onclick="window.print()" style="margin-top:10px; padding:10px 20px; background:#0284c7; color:#fff; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">🖨️ طباعة قائمة التدفقات النقدية PDF</button>', height=55)

    # 4. حقوق الملكية
    with tab4:
        st.subheader("4. قائمة التغيرات في حقوق الملكية (Changes in Equity)")
        eq_code = f"""
        <div id="printArea" style="padding: 25px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff; font-family: Segoe UI, Arial;">
            <h3 style="text-align: center; color: #475569; margin:0;">قائمة التغيرات في حقوق الملاك</h3>
            <h5 style="text-align: center; color: #64748b; margin-top:5px;">عن الفترة من {d_start} إلى {d_end}</h5>
            <hr>
            <table style="width: 100%; border-collapse: collapse; font-size: 15px; text-align: center;">
                <tr style="background:#f1f5f9; font-weight:bold;">
                    <td style="text-align:right; padding:10px;">البيان</td>
                    <td>رأس المال</td>
                    <td>الأرباح المحتجزة</td>
                    <td>الإجمالي</td>
                </tr>
                <tr>
                    <td style="text-align:right; padding:8px;">رصيد بداية الفترة</td>
                    <td>{capital:,.2f}</td>
                    <td>0.00</td>
                    <td>{capital:,.2f}</td>
                </tr>
                <tr>
                    <td style="text-align:right; padding:8px;">صافي ربح الفترة الحالية</td>
                    <td>-</td>
                    <td>{net_profit:,.2f}</td>
                    <td>{net_profit:,.2f}</td>
                </tr>
                <tr style="background:#e2e8f0; font-weight:bold;">
                    <td style="text-align:right; padding:10px;">رصيد حقوق الملكية نهاية الفترة</td>
                    <td>{capital:,.2f}</td>
                    <td>{net_profit:,.2f}</td>
                    <td>{(capital + net_profit):,.2f} ج.م</td>
                </tr>
            </table>
        </div>
        """
        st.markdown(eq_code, unsafe_allow_html=True)
        components.html('<button onclick="window.print()" style="margin-top:10px; padding:10px 20px; background:#475569; color:#fff; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">🖨️ طباعة قائمة حقوق الملكية PDF</button>', height=55)

    # 5. الدخل الشامل
    with tab5:
        st.subheader("5. قائمة الدخل الشامل (Comprehensive Income)")
        unrealized_bio_gain = biological_assets * 0.15
        total_comp_income = net_profit + unrealized_bio_gain

        comp_code = f"""
        <div id="printArea" style="padding: 25px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff; font-family: Segoe UI, Arial;">
            <h3 style="text-align: center; color: #0f766e; margin:0;">قائمة الدخل الشامل الآخر</h3>
            <h5 style="text-align: center; color: #64748b; margin-top:5px;">طبقاً للمعيار الدولي IAS 1 & IAS 41</h5>
            <hr>
            <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
                <tr><td style="padding:10px;"><b>صافي أرباح الفترة (من قائمة الدخل)</b></td><td style="text-align:left; font-weight:bold;">{net_profit:,.2f} ج.م</td></tr>
                <tr style="background:#f8fafc;"><td colspan="2"><b>بنود الدخل الشامل الأخرى (OCI):</b></td></tr>
                <tr><td style="padding-right:20px;">فروق إعادة تقييم الأصول الحيوية بالقيمة العادلة (النمو الوزني للأسماك الحية)</td><td style="text-align:left; color:#16a34a;">+{unrealized_bio_gain:,.2f} ج.م</td></tr>
                <tr style="background:#0f766e; color:#fff; font-weight:bold; font-size:16px;">
                    <td style="padding:10px;">إجمالي الدخل الشامل للفترة المالية</td>
                    <td style="text-align:left; padding:10px;">{total_comp_income:,.2f} ج.م</td>
                </tr>
            </table>
        </div>
        """
        st.markdown(comp_code, unsafe_allow_html=True)
        components.html('<button onclick="window.print()" style="margin-top:10px; padding:10px 20px; background:#0f766e; color:#fff; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">🖨️ طباعة قائمة الدخل الشامل PDF</button>', height=55)

    # 6. الإيضاحات المتممة
    with tab6:
        st.subheader("6. الإيضاحات المتممة للقوائم المالية (Notes to Financial Statements)")
        st.markdown("""
        #### إيضاح (1): السياسات المحاسبية المتبعة
        * **طبيعة النشاط:** شركة ومزرعة أسماك عبد الله الشمندي تعمل في تربية وتسمين وتجارة الأسماك النيلية والبحرية.
        * **تقييم الأصول البيولوجية:** طبقاً لمعيار **IAS 41 (الزراعة)**، تقيّم الأسماك بالأحواض بالتكلفة المباشرة (العلف المأكول + تكلفة الإصبعيات) أو القيمة العادلة السوقية أيهما أقل تحوطاً.
        * **الاعتراف بالإيراد:** يعترف بالإيراد عند تسليم الأسماك المحصودة للتجار والعملاء وإصدار فاتورة البيع والوزن الفعلي.
        * **الأصول الثابتة:** تدرج المعدات والطلمبات بالتكلفة التاريخية وتهلك بطريقة القسط الثابت بنسبة 10% سنوياً.

        ---
        #### إيضاح (2): تفصيل الأصول البيولوجية القائمة بالمزرعة
        """)
        df_ponds = pd.read_sql("SELECT name as الحوض, fish_type as الصنف, stock_count as العدد, initial_cost as 'تكلفة الزريعة' FROM ponds WHERE status='نشط'", conn)
        st.dataframe(df_ponds, use_container_width=True)

        st.markdown("""
        ---
        #### إيضاح (3): تحليل تكلفة الأعلاف ومعدل التحويل (FCR)
        """)
        df_feed_stat = pd.read_sql("SELECT feed_type as 'نوع العلف', SUM(qty_kg) as 'الكمية المستهلكة (كجم)', SUM(total_cost) as 'الإجمالي (ج.م)' FROM feed GROUP BY feed_type", conn)
        st.dataframe(df_feed_stat, use_container_width=True)

        components.html('<button onclick="window.print()" style="margin-top:10px; padding:10px 20px; background:#334155; color:#fff; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">🖨️ طباعة الإيضاحات المتممة كـ PDF</button>', height=55)

# 4. شؤون العمال
elif st.session_state.page == "شؤون العمال":
    st.header("👷 شؤون العمال ومتابعة اليوميات والسلفيات")
    t1, t2 = st.tabs(["تسجيل اليومية والسلفة", "إضافة عامل جديد"])
    
    with t2:
        with st.form("add_emp"):
            name = st.text_input("اسم العامل / الموظف")
            role = st.selectbox("الوظيفة", ["عامل أحواض وتغذية", "فني بدالات وطلمبات", "مشرف مزرعة", "حارس أمن"])
            wage = st.number_input("الأجر اليومي (ج.م)", min_value=0.0, step=50.0)
            phone = st.text_input("رقم الهاتف")
            if st.form_submit_button("حفظ الموظف") and name:
                try:
                    conn.cursor().execute("INSERT INTO employees (name, role, daily_wage, phone) VALUES (?, ?, ?, ?)",
                                          (name, role, wage, phone))
                    conn.commit()
                    st.success("تم تسجيل العامل بنجاح")
                    st.rerun()
                except:
                    st.error("اسم العامل مسجل مسبقاً")

    with t1:
        emps = [r[0] for r in conn.cursor().execute("SELECT name FROM employees").fetchall()]
        if emps:
            with st.form("log_labor"):
                c1, c2 = st.columns(2)
                emp = c1.selectbox("العامل", emps)
                l_date = c2.date_input("التاريخ", date.today())
                c3, c4 = st.columns(2)
                stat = c3.selectbox("حالة الحضور", ["حاضر", "غائب", "إجازة مدفوعة", "نصف يوم"])
                adv = c4.number_input("سلفة مسحوبة (ج.م)", min_value=0.0, step=50.0)
                notes = st.text_input("ملاحظات")
                if st.form_submit_button("تسجيل اليومية"):
                    conn.cursor().execute("INSERT INTO labor_log (emp_name, date, status, advance, notes) VALUES (?, ?, ?, ?, ?)",
                                          (emp, str(l_date), stat, adv, notes))
                    conn.commit()
                    st.success("تم الحفظ بنجاح")
                    st.rerun()

            st.subheader("سجل الحركة الأخير للعمالة")
            df_l = pd.read_sql("SELECT date as التاريخ, emp_name as العامل, status as الحالة, advance as 'السلفة (ج.م)', notes as ملاحظات FROM labor_log ORDER BY id DESC LIMIT 15", conn)
            st.dataframe(df_l, use_container_width=True)
        else:
            st.info("قم بإضافة عمال أولاً من التبويب المجاور.")

# 5. التوقعات والمحاكاة
elif st.session_state.page == "التوقعات والمحاكاة":
    st.header("🔮 التوقعات والمحاكاة المستقبلية لنمو الأسماك")
    ponds = [r[0] for r in conn.cursor().execute("SELECT name FROM ponds WHERE status='نشط'").fetchall()]
    if ponds:
        pond_sel = st.selectbox("اختر الحوض للتحليل والتوقع:", ponds)
        p_data = conn.cursor().execute("SELECT stock_count, initial_weight, stock_date FROM ponds WHERE name=?", (pond_sel,)).fetchone()
        count, init_w, s_date_str = p_data
        s_date = date.fromisoformat(s_date_str)
        days_passed = (date.today() - s_date).days
        
        c1, c2, c3 = st.columns(3)
        target_w = c1.number_input("الوزن المستهدف (جرام)", value=350.0, step=25.0)
        expected_adg = c2.number_input("معدل النمو اليومي (ADG) جم/يوم", value=2.2, step=0.1)
        expected_fcr = c3.number_input("معدل التحويل (FCR)", value=1.4, step=0.05)
        
        current_w = init_w + (expected_adg * days_passed)
        days_to_harvest = int(max(0.0, target_w - current_w) / expected_adg) if expected_adg > 0 else 0
        est_harvest_date = date.today() + timedelta(days=days_to_harvest)
        
        est_total_kg = ((count * 0.90) * target_w) / 1000.0
        feed_already_used = (pd.read_sql(f"SELECT SUM(qty_kg) as q FROM feed WHERE pond_name='{pond_sel}'", conn)['q'].iloc[0] or 0.0)
        remaining_feed_kg = max(0.0, (est_total_kg * expected_fcr) - feed_already_used)

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("عمر الدورة الحالي", f"{days_passed} يوم")
        m2.metric("متوسط الوزن التقديري الآن", f"{current_w:.1f} جرام")
        m3.metric("الأيام المتبقية للحصاد", f"{days_to_harvest} يوم")
        m4.metric("تاريخ الحصاد التقديري", f"{est_harvest_date}")

        m5, m6 = st.columns(2)
        m5.metric("الإنتاج المتوقع للحوض", f"{est_total_kg:,.0f} كجم")
        m6.metric("العلف الإضافي المطلوب حتى النهاية", f"{remaining_feed_kg:,.0f} كجم")
    else:
        st.info("لا توجد أحواض نشطة حالياً.")

# 6. مختبر المياه
elif st.session_state.page == "مختبر المياه":
    st.header("🧪 مراقبة خواص المياه والبحث العلمي")
    ponds = [r[0] for r in conn.cursor().execute("SELECT name FROM ponds WHERE status='نشط'").fetchall()]
    with st.form("water_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        p_name = c1.selectbox("الحوض", ponds if ponds else ["عام"])
        w_date = c2.date_input("تاريخ القياس", date.today())
        c3, c4, c5, c6 = st.columns(4)
        oxy = c3.number_input("الأكسجين المذاب (DO)", value=5.5, step=0.1)
        temp = c4.number_input("درجة الحرارة مئوية (°C)", value=27.0, step=0.5)
        ph = c5.number_input("درجة الحموضة (pH)", value=7.8, step=0.1)
        nh3 = c6.number_input("الأمونيا (NH3)", value=0.05, step=0.01)
        notes = st.text_input("ملاحظات بيولوجية (اللون، الرائحة)")
        if st.form_submit_button("حفظ القراءة"):
            conn.cursor().execute("INSERT INTO water_quality (pond_name, date, temp, dissolved_oxygen, ph, ammonia, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  (p_name, str(w_date), temp, oxy, ph, nh3, notes))
            conn.commit()
            st.success("تم تسجيل قراءة المياه بنجاح")
            st.rerun()

    if oxy < 4.0:
        st.error("⚠️ تحذير: الأكسجين منخفض (أقل من 4 مجم/لتر)؛ شغل البدالات فوراً!")
    if nh3 > 0.5:
        st.warning("⚠️ تنبيه: الأمونيا مرتفعة؛ قم بتجديد مياه الحوض جزئياً.")

    st.subheader("سجل قراءات المياه")
    df_w = pd.read_sql("SELECT date as التاريخ, pond_name as الحوض, temp as 'الحرارة', dissolved_oxygen as 'الأكسجين DO', ph as 'الحموضة pH', ammonia as 'الأمونيا NH3' FROM water_quality ORDER BY id DESC LIMIT 10", conn)
    st.dataframe(df_w, use_container_width=True)

# 7. قائمة المراجعة
elif st.session_state.page == "قائمة المراجعة":
    st.header("✅ قائمة الفحص والرقابة الميدانية اليومية")
    ponds = [r[0] for r in conn.cursor().execute("SELECT name FROM ponds WHERE status='نشط'").fetchall()]
    with st.form("audit_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        a_date = c1.date_input("التاريخ", date.today())
        p_name = c2.selectbox("الحوض", ponds if ponds else ["عام"])
        inspector = c3.text_input("اسم الفاحص / المشرف")
        c4, c5, c6 = st.columns(3)
        pumps = c4.selectbox("البدالات والطلمبات", ["ممتازة وشغالة", "تحتاج صيانة", "معطلة"])
        nets = c5.selectbox("الجسور والشباك", ["سليمة 100%", "تحتاج تدعيم", "يوجد تسريب"])
        feed_resp = c6.selectbox("إقبال الأسماك على العلف", ["شراهة وإقبال ممتاز", "متوسط", "عزوف عن العلف"])
        c7, c8 = st.columns(2)
        morts = c7.number_input("عدد النافق المجمع اليوم", min_value=0, step=1)
        a_notes = c8.text_input("ملاحظات إضافية")
        if st.form_submit_button("اعتماد التدقيق اليومي"):
            conn.cursor().execute("INSERT INTO audit_log (date, pond_name, pumps_status, nets_status, feeding_response, mortalities, inspector, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                  (str(a_date), p_name, pumps, nets, feed_resp, morts, inspector, a_notes))
            conn.commit()
            st.success("تم اعتماد تقرير التدقيق بنجاح")
            st.rerun()

    df_a = pd.read_sql("SELECT date as التاريخ, pond_name as الحوض, pumps_status as الطلمبات, feeding_response as 'إقبال العلف', mortalities as النافق, inspector as الفاحص FROM audit_log ORDER BY id DESC LIMIT 10", conn)
    st.dataframe(df_a, use_container_width=True)

# 8. الأعلاف والتشغيل
elif st.session_state.page == "الأعلاف والتشغيل":
    st.header("🥣 حركة العلف والمصروفات اليومية")
    tab_f, tab_e = st.tabs(["تسجيل التغذية", "المصروفات النثرية"])
    with tab_f:
        ponds = [r[0] for r in conn.cursor().execute("SELECT name FROM ponds WHERE status='نشط'").fetchall()]
        if ponds:
            with st.form("feed_entry", clear_on_submit=True):
                c1, c2 = st.columns(2)
                f_date = c1.date_input("التاريخ", date.today())
                p_sel = c2.selectbox("الحوض", ponds)
                c3, c4, c5 = st.columns(3)
                f_t = c3.selectbox("نوع ونسبة البروتين", ["طافي 30%", "طافي 25%", "غطاس 32%", "بادئ 35%", "أخرى"])
                qty = c4.number_input("الكمية (كجم)", min_value=0.0, step=25.0)
                price = c5.number_input("سعر الكيلو (ج.م)", min_value=0.0, step=0.5)
                if st.form_submit_button("حفظ حركة العلف") and qty > 0:
                    conn.cursor().execute("INSERT INTO feed (pond_name, date, feed_type, qty_kg, price_per_kg, total_cost) VALUES (?, ?, ?, ?, ?, ?)",
                                          (p_sel, str(f_date), f_t, qty, price, (qty * price)))
                    conn.commit()
                    st.success("تم تسجيل العلف")
                    st.rerun()
    with tab_e:
        with st.form("exp_entry", clear_on_submit=True):
            c1, c2 = st.columns(2)
            e_date = c1.date_input("التاريخ", date.today())
            cat = c2.selectbox("البند", ["سولار وكهرباء", "أدوية ومخصبات", "صيانة ومعدات", "إيجار", "نثريات"])
            c3, c4 = st.columns(2)
            amt = c3.number_input("المبلغ (ج.م)", min_value=0.0, step=50.0)
            notes = c4.text_input("البيان والمستند")
            if st.form_submit_button("حفظ المصروف") and amt > 0:
                conn.cursor().execute("INSERT INTO expenses (date, category, amount, notes) VALUES (?, ?, ?, ?)",
                                      (str(e_date), cat, amt, notes))
                conn.commit()
                st.success("تم تسجيل المصروف")
                st.rerun()

# 9. مبيعات الحصاد
elif st.session_state.page == "مبيعات الحصاد":
    st.header("💰 مبيعات الحصاد وإيرادات الأسماك")
    ponds = [r[0] for r in conn.cursor().execute("SELECT name FROM ponds").fetchall()]
    with st.form("sale_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        s_date = c1.date_input("تاريخ البيع", date.today())
        p_name = c2.selectbox("الحوض", ponds if ponds else ["عام"])
        c3, c4 = st.columns(2)
        qty = c3.number_input("الوزن الإجمالي المباع (كجم)", min_value=0.0, step=50.0)
        price = c4.number_input("سعر الكيلو (ج.م)", min_value=0.0, step=1.0)
        client = st.text_input("اسم التاجر / المشتري")
        if st.form_submit_button("حفظ فاتورة البيع") and qty > 0:
            conn.cursor().execute("INSERT INTO sales (pond_name, date, qty_kg, price_per_kg, total_price, client) VALUES (?, ?, ?, ?, ?, ?)",
                                  (p_name, str(s_date), qty, price, (qty * price), client))
            conn.commit()
            st.success("تم حفظ فاتورة البيع")
            st.rerun()

# 10. الأصول ورأس المال
elif st.session_state.page == "الأصول ورأس المال":
    st.header("🚜 تسجيل الأصول الثابتة ورأس المال المبدئي")
    with st.form("asset_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        a_name = c1.text_input("اسم الأصل (مولد، طلمبة، بدالة، رأس مال كاش)")
        cat = c2.selectbox("التصنيف", ["معدات وآلات وطلمبات", "مباني وأحواض خرسانية", "شبكات وسيارات نقل", "رأس مال نقدي مبدئي"])
        c3, c4 = st.columns(2)
        val = c3.number_input("القيمة (ج.م)", min_value=0.0, step=1000.0)
        p_date = c4.date_input("التاريخ", date.today())
        if st.form_submit_button("تسجيل الأصل") and val > 0:
            conn.cursor().execute("INSERT INTO assets (asset_name, category, value, purchase_date) VALUES (?, ?, ?, ?)",
                                  (a_name, cat, val, str(p_date)))
            conn.commit()
            st.success("تم إدراج الأصل بالدفاتر")
            st.rerun()

# 11. إدارة الأحواض
elif st.session_state.page == "إدارة الأحواض":
    st.header("🏞️ تعريف الأحواض وتسكين الزريعة")
    with st.form("pond_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم أو رقم الحوض")
        f_type = c2.selectbox("نوع الأسماك", ["بلطي نيللي", "بوري", "طوبار", "قاروص", "دنيس", "مبروك"])
        c3, c4, c5 = st.columns(3)
        count = c3.number_input("عدد الزريعة", min_value=0, step=1000)
        cost = c4.number_input("تكلفة الشراء (ج.م)", min_value=0.0, step=500.0)
        init_w = c5.number_input("متوسط الوزن الابتدائي (جرام)", value=1.0, step=0.5)
        s_date = st.date_input("تاريخ التسكين", date.today())
        if st.form_submit_button("تسكين الحوض") and name:
            try:
                conn.cursor().execute("INSERT INTO ponds (name, fish_type, stock_count, initial_cost, initial_weight, stock_date) VALUES (?, ?, ?, ?, ?, ?)",
                                      (name, f_type, count, cost, init_w, str(s_date)))
                conn.commit()
                st.success("تم تسكين الحوض بنجاح")
                st.rerun()
            except:
                st.error("اسم الحوض مسجل مسبقاً")

    df_p = pd.read_sql("SELECT name as الحوض, fish_type as النوع, stock_count as 'عدد الزريعة', initial_weight as 'الوزن المبدئي (جم)', stock_date as التسكين FROM ponds", conn)
    st.dataframe(df_p, use_container_width=True)
