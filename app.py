import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import streamlit.components.v1 as components

# ================= 1. التصميم المتجاوب وتوافق جميع الشاشات =================
st.set_page_config(
    page_title="مزرعة عبد الله الشمندي - النظام الشامل",
    layout="wide",
    page_icon="🐟",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* دعم اللغة العربية */
    body, html, [class*="css"], .stMarkdown, p, div {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* تصميم متجاوب لكافة الشاشات (الهواتف والتابلت والكمبيوتر) */
    @media (max-width: 768px) {
        .stMetric {
            margin-bottom: 8px !important;
            padding: 10px !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        .main .block-container {
            padding: 10px 15px !important;
        }
    }
    
    .stMetric {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 10px;
        border-right: 6px solid #0284c7;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .checklist-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 12px;
    }
    
    @media print {
        header, .stSidebar, .stButton { display: none !important; }
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
        st.markdown("<p style='text-align: center; color: #64748b;'>منظومة الإدارة الذكية والدورة المحاسبية الشاملة</p>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with col_login := c2:
            st.info("🔒 يرجى إدخال رمز المرور السري للدخول")
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

# ================= 3. قاعدة البيانات الشاملة =================
def get_db():
    conn = sqlite3.connect("al_shamandy_farm.db", check_same_thread=False)
    cur = conn.cursor()
    # أحواض
    cur.execute("""CREATE TABLE IF NOT EXISTS ponds (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, fish_type TEXT, 
        stock_count INTEGER, initial_cost REAL, initial_weight REAL, stock_date TEXT, status TEXT DEFAULT 'نشط')""")
    # علف
    cur.execute("""CREATE TABLE IF NOT EXISTS feed (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pond_name TEXT, date TEXT, 
        feed_type TEXT, qty_kg REAL, price_per_kg REAL, total_cost REAL)""")
    # مصروفات عامة
    cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, amount REAL, notes TEXT)""")
    # مبيعات
    cur.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pond_name TEXT, date TEXT, 
        qty_kg REAL, price_per_kg REAL, total_price REAL, client TEXT)""")
    # أصول ورأس مال
    cur.execute("""CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, asset_name TEXT, category TEXT, value REAL, purchase_date TEXT)""")
    # الموظفون والعمال
    cur.execute("""CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, role TEXT, daily_wage REAL, phone TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS labor_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, emp_name TEXT, date TEXT, status TEXT, advance REAL, notes TEXT)""")
    # قياسات جودة المياه
    cur.execute("""CREATE TABLE IF NOT EXISTS water_quality (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pond_name TEXT, date TEXT, 
        temp REAL, dissolved_oxygen REAL, ph REAL, ammonia REAL, notes TEXT)""")
    # قوائم المراجعة والتدقيق
    cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pond_name TEXT, 
        pumps_status TEXT, nets_status TEXT, feeding_response TEXT, mortalities INTEGER, inspector TEXT, notes TEXT)""")
    conn.commit()
    return conn

conn = get_db()

# ================= 4. القائمة الرئيسية المتطورة =================
st.sidebar.title("🐟 مزرعة عبد الله الشمندي")
st.sidebar.caption("نظام التخطيط والتحكم السحابي المتكامل")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.authenticated = False
    st.rerun()

menu = st.sidebar.radio("الوحدات التشغيلية والمالية:", [
    "📊 لوحة المؤشرات التنفيذية",
    "⚖️ الدورة المحاسبية وميزان المراجعة",
    "📑 القوائم الختامية (الدخل والمركز المالي)",
    "👷 شؤون العمال والموظفين",
    "🔮 التوقعات ومحاكاة الإنتاج",
    "🧪 البحث العلمي ومختبر المياه",
    "✅ قائمة المراجعة والتدقيق اليومي",
    "🥣 الأعلاف والتشغيل اليومي",
    "💰 مبيعات الحصاد",
    "🚜 الأصول الثابتة ورأس المال",
    "🏞️ إدارة الأحواض"
])

# ----------------- 1. لوحة المؤشرات التنفيذية -----------------
if menu == "📊 لوحة المؤشرات التنفيذية":
    st.header("📊 لوحة القيادة والمؤشرات العامة")
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
        st.subheader("توزيع هيكل التكاليف")
        if total_costs > 0:
            exp_sum = df_exp.groupby('category')['amount'].sum().reset_index() if not df_exp.empty else pd.DataFrame(columns=['category', 'amount'])
            all_exp = pd.concat([
                exp_sum, 
                pd.DataFrame([{"category": "أعلاف", "amount": feed_c}, {"category": "سلف عمال", "amount": advances_c}])
            ], ignore_index=True)
            st.plotly_chart(px.pie(all_exp, values='amount', names='category', hole=0.45), use_container_width=True)
    with col2:
        st.subheader("تحليل الإيرادات عبر الزمن")
        if not df_sales.empty:
            st.plotly_chart(px.bar(df_sales.groupby('date')['total_price'].sum().reset_index(), x='date', y='total_price'), use_container_width=True)

# ----------------- 2. الدورة المحاسبية وميزان المراجعة -----------------
elif menu == "⚖️ الدورة المحاسبية وميزان المراجعة":
    st.header("⚖️ ميزان المراجعة والقيود المحاسبية")
    st.caption("التحقق من توازن الحسابات (الأرصدة المدينة والدائنة) للدورة المالية الحالية")

    df_sales = pd.read_sql("SELECT SUM(total_price) as total FROM sales", conn)
    df_feed = pd.read_sql("SELECT SUM(total_cost) as total FROM feed", conn)
    df_exp = pd.read_sql("SELECT category, SUM(amount) as total FROM expenses GROUP BY category", conn)
    df_assets = pd.read_sql("SELECT category, SUM(value) as total FROM assets GROUP BY category", conn)
    df_labor = pd.read_sql("SELECT SUM(advance) as total FROM labor_log", conn)

    # تجميع بنود ميزان المراجعة
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
        st.warning("⚠️ يوجد فارق تسوية في القيود يرجى تدقيق رأس المال الأولي أو حركات الكاش.")

# ----------------- 3. القوائم الختامية والطباعة -----------------
elif menu == "📑 القوائم الختامية (الدخل والمركز المالي)":
    st.header("📑 القوائم المالية الختامية")
    tab1, tab2 = st.tabs(["قائمة الدخل (P&L)", "الميزانية العمومية (Balance Sheet)"])

    with tab1:
        c1, c2 = st.columns(2)
        d_from = c1.date_input("من تاريخ", date(date.today().year, 1, 1))
        d_to = c2.date_input("إلى تاريخ", date.today())
        
        rev = (pd.read_sql(f"SELECT SUM(total_price) as r FROM sales WHERE date BETWEEN '{d_from}' AND '{d_to}'", conn)['r'].iloc[0] or 0.0)
        c_feed = (pd.read_sql(f"SELECT SUM(total_cost) as f FROM feed WHERE date BETWEEN '{d_from}' AND '{d_to}'", conn)['f'].iloc[0] or 0.0)
        c_power = (pd.read_sql(f"SELECT SUM(amount) as p FROM expenses WHERE category='سولار وكهرباء' AND date BETWEEN '{d_from}' AND '{d_to}'", conn)['p'].iloc[0] or 0.0)
        c_other = (pd.read_sql(f"SELECT SUM(amount) as o FROM expenses WHERE category != 'سولار وكهرباء' AND date BETWEEN '{d_from}' AND '{d_to}'", conn)['o'].iloc[0] or 0.0)
        
        gross = rev - (c_feed + c_power)
        net = gross - c_other

        pnl_html = f"""
        <div id="printArea" style="padding: 20px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff;">
            <h3 style="text-align: center; color: #0284c7; margin-bottom: 5px;">مزرعة أسماك عبد الله الشمندي</h3>
            <h5 style="text-align: center; color: #64748b; margin-top: 0;">قائمة الدخل عن الفترة من {d_from} إلى {d_to}</h5>
            <hr>
            <p><b>إيرادات النشاط (مبيعات الأسماك):</b> {rev:,.2f} ج.م</p>
            <p style="color: #b91c1c;"><b>يخصم تكلفة التشغيل المباشرة (علف + طاقة):</b> ({(c_feed + c_power):,.2f}) ج.م</p>
            <h4 style="background: #f1f5f9; padding: 8px;">مجمل الربح التشغيلي: {gross:,.2f} ج.م</h4>
            <p style="color: #b91c1c;"><b>يخصم المصروفات الإدارية والعمومية والصيانة:</b> ({c_other:,.2f}) ج.م</p>
            <h3 style="background: #0284c7; color: white; padding: 10px; border-radius: 5px;">صافي الربح القابل للتوزيع: {net:,.2f} ج.م</h3>
        </div>
        """
        st.markdown(pnl_html, unsafe_allow_html=True)
        components.html('<button onclick="window.print()" style="margin-top:10px; padding:10px 20px; background:#0284c7; color:#fff; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">🖨️ طباعة قائمة الدخل أو تصديرها كـ PDF</button>', height=60)

    with tab2:
        st.subheader("قائمة المركز المالي")
        # حسابات المركز المالي
        df_assets = pd.read_sql("SELECT category, SUM(value) as val FROM assets GROUP BY category", conn)
        cap = df_assets[df_assets['category'] == 'رأس مال نقدي مبدئي']['val'].sum() if not df_assets.empty else 0.0
        fixed = df_assets[df_assets['category'] != 'رأس مال نقدي مبدئي']['val'].sum() if not df_assets.empty else 0.0
        
        rev_all = (pd.read_sql("SELECT SUM(total_price) as r FROM sales", conn)['r'].iloc[0] or 0.0)
        exp_all = (pd.read_sql("SELECT SUM(amount) as e FROM expenses", conn)['e'].iloc[0] or 0.0)
        feed_all = (pd.read_sql("SELECT SUM(total_cost) as f FROM feed", conn)['f'].iloc[0] or 0.0)
        
        cash = (rev_all + cap) - (exp_all + feed_all)
        bio_inventory = feed_all * 0.85 # تقييم استرشادي للأسماك في المياه
        total_assets = cash + bio_inventory + fixed
        
        bs_html = f"""
        <div id="printArea" style="padding: 20px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff;">
            <h3 style="text-align: center; color: #0f766e; margin-bottom: 5px;">مزرعة أسماك عبد الله الشمندي</h3>
            <h5 style="text-align: center; color: #64748b; margin-top: 0;">الميزانية العمومية كما في {date.today()}</h5>
            <hr>
            <div style="display: flex; gap: 15px;">
                <div style="flex:1; border: 1px solid #e2e8f0; padding: 12px; border-radius: 5px;">
                    <h4 style="color: #0369a1;">الأصول (Assets)</h4>
                    <p>النقدية وشبه النقد: <b>{cash:,.2f} ج.م</b></p>
                    <p>المخزون البيولوجي التقديري: <b>{bio_inventory:,.2f} ج.م</b></p>
                    <p>الأصول الثابتة والمعدات: <b>{fixed:,.2f} ج.م</b></p>
                    <h4 style="background: #e0f2fe; padding: 8px;">إجمالي الأصول: {total_assets:,.2f} ج.م</h4>
                </div>
                <div style="flex:1; border: 1px solid #e2e8f0; padding: 12px; border-radius: 5px;">
                    <h4 style="color: #0f766e;">الخصوم وحقوق الملكية</h4>
                    <p>رأس المال الأساسي: <b>{cap:,.2f} ج.م</b></p>
                    <p>الأرباح المرحلة والاحتياطيات: <b>{(total_assets - cap):,.2f} ج.م</b></p>
                    <h4 style="background: #ccfbf1; padding: 8px;">إجمالي الالتزامات وحقوق الملكية: {total_assets:,.2f} ج.م</h4>
                </div>
            </div>
        </div>
        """
        st.markdown(bs_html, unsafe_allow_html=True)
        components.html('<button onclick="window.print()" style="margin-top:10px; padding:10px 20px; background:#0f766e; color:#fff; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">🖨️ طباعة الميزانية العمومية كـ PDF</button>', height=60)

# ----------------- 4. شؤون العمال والموظفين -----------------
elif menu == "👷 شؤون العمال والموظفين":
    st.header("👷 متابعة حركة العمالة واليوميات والسلف")
    
    t1, t2 = st.tabs(["تسجيل اليومية والحضور", "إضافة عامل جديد"])
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
                    st.error("الاسم مسجل بالفعل")

    with t1:
        emps = [r[0] for r in conn.cursor().execute("SELECT name FROM employees").fetchall()]
        if emps:
            with st.form("log_labor"):
                c1, c2 = st.columns(2)
                emp = c1.selectbox("اختر العامل", emps)
                l_date = c2.date_input("التاريخ", date.today())
                c3, c4 = st.columns(2)
                stat = c3.selectbox("حالة الحضور", ["حاضر", "غائب", "إجازة مدفوعة", "نصف يوم"])
                adv = c4.number_input("سلفة مسحوبة من الخزينة (ج.م)", min_value=0.0, step=50.0)
                notes = st.text_input("ملاحظات على الأداء أو الخصومات")
                
                if st.form_submit_button("تسجيل اليومية والسلفة"):
                    conn.cursor().execute("INSERT INTO labor_log (emp_name, date, status, advance, notes) VALUES (?, ?, ?, ?, ?)",
                                          (emp, str(l_date), stat, adv, notes))
                    conn.commit()
                    st.success("تم الحفظ")
                    st.rerun()
            
            st.subheader("سجل حركة العمالة الأخير")
            df_l = pd.read_sql("SELECT date as التاريخ, emp_name as العامل, status as الحالة, advance as 'السلفة (ج.م)', notes as ملاحظات FROM labor_log ORDER BY id DESC LIMIT 15", conn)
            st.dataframe(df_l, use_container_width=True)
        else:
            st.info("قم بتسجيل بيانات العمال أولاً في التبويب المجاور.")

# ----------------- 5. التوقعات ومحاكاة الإنتاج -----------------
elif menu == "🔮 التوقعات ومحاكاة الإنتاج":
    st.header("🔮 المحاكاة والتوقعات المستقبلية لدورات الأسماك")
    st.caption("التنبؤ بمواعيد الحصاد، كمية العلف المطلوبة، والعوائد المتوقعة بناءً على مؤشرات النمو العلمي (ADG)")

    ponds = [r[0] for r in conn.cursor().execute("SELECT name FROM ponds WHERE status='نشط'").fetchall()]
    if ponds:
        pond_sel = st.selectbox("اختر الحوض للمحاكاة والتوقع:", ponds)
        p_data = conn.cursor().execute("SELECT stock_count, initial_weight, stock_date, initial_cost FROM ponds WHERE name=?", (pond_sel,)).fetchone()
        
        count, init_w, s_date_str, seed_cost = p_data
        s_date = date.fromisoformat(s_date_str)
        days_passed = (date.today() - s_date).days
        
        c1, c2, c3 = st.columns(3)
        target_w = c1.number_input("الوزن النهائي المستهدف للسمكة (جرام)", value=350.0, step=25.0)
        expected_adg = c2.number_input("معدل النمو اليومي المتوقع ADG (جرام/يوم)", value=2.2, step=0.1)
        expected_fcr = c3.number_input("معدل التحويل الغذائي المستهدف (FCR)", value=1.4, step=0.05)
        
        # الحسابات العلمية
        current_est_weight = init_w + (expected_adg * days_passed)
        remaining_growth = max(0.0, target_w - current_est_weight)
        days_to_harvest = int(remaining_growth / expected_adg) if expected_adg > 0 else 0
        est_harvest_date = date.today() + timedelta(days=days_to_harvest)
        
        survival_rate = 0.90 # نسبة الحيوية الافتراضية
        est_live_fish = count * survival_rate
        est_total_harvest_kg = (est_live_fish * target_w) / 1000.0
        
        feed_already_used = (pd.read_sql(f"SELECT SUM(qty_kg) as q FROM feed WHERE pond_name='{pond_sel}'", conn)['q'].iloc[0] or 0.0)
        total_feed_needed_kg = (est_total_harvest_kg * expected_fcr)
        remaining_feed_kg = max(0.0, total_feed_needed_kg - feed_already_used)

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("عمر الدورة الحالي", f"{days_passed} يوم")
        m2.metric("متوسط الوزن التقديري الآن", f"{current_est_weight:.1f} جرام")
        m3.metric("الأيام المتبقية للحصاد", f"{days_to_harvest} يوم")
        m4.metric("تاريخ الحصاد المتوقع", f"{est_harvest_date}")

        m5, m6, m7 = st.columns(3)
        m5.metric("الإنتاج المتوقع للحوض", f"{est_total_harvest_kg:,.0f} كجم")
        m6.metric("العلف الإضافي المطلوب", f"{remaining_feed_kg:,.0f} كجم")
        est_rev = est_total_harvest_kg * 85.0 # افتراض 85 جنيه للكيلو
        m7.metric("الإيراد التقديري المتوقع (بمتوسط 85 ج/ك)", f"{est_rev:,.0f} ج.م")
    else:
        st.info("لا توجد أحواض نشطة حالياً.")

# ----------------- 6. البحث العلمي ومختبر المياه -----------------
elif menu == "🧪 البحث العلمي ومختبر المياه":
    st.header("🧪 مراقبة خواص المياه والبحث العلمي")
    ponds = [r[0] for r in conn.cursor().execute("SELECT name FROM ponds WHERE status='نشط'").fetchall()]
    
    with st.form("water_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        p_name = c1.selectbox("الحوض", ponds if ponds else ["عام"])
        w_date = c2.date_input("تاريخ القياس", date.today())
        
        c3, c4, c5, c6 = st.columns(4)
        oxy = c3.number_input("الأكسجين المذاب (DO) مجم/لتر", value=5.5, step=0.1)
        temp = c4.number_input("درجة الحرارة مئوية (°C)", value=27.0, step=0.5)
        ph = c5.number_input("درجة الحموضة (pH)", value=7.8, step=0.1)
        nh3 = c6.number_input("الأمونيا الكلية (NH3) مجم/لتر", value=0.05, step=0.01)
        notes = st.text_input("ملاحظات بيولوجية (لون المياه، الطحالب، الرائحة)")
        
        if st.form_submit_button("حفظ القراءة المعملية"):
            conn.cursor().execute("INSERT INTO water_quality (pond_name, date, temp, dissolved_oxygen, ph, ammonia, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  (p_name, str(w_date), temp, oxy, ph, nh3, notes))
            conn.commit()
            st.success("تم تسجيل بيانات المياه في السجل العلمي للمزرعة")
            st.rerun()

    # تنبيهات علمية فورية
    if oxy < 4.0:
        st.error("⚠️ تحذير علمي: الأكسجين المذاب أقل من 4 مجم/لتر! يجب تشغيل البدالات فوراً وتقليل التغذية.")
    if nh3 > 0.5:
        st.warning("⚠️ تحذير: نسبة الأمونيا مرتفعة! ينصح بتجديد مياه الحوض جزئياً فوراً.")

    st.subheader("سجل قراءات جودة المياه")
    df_w = pd.read_sql("SELECT date as التاريخ, pond_name as الحوض, temp as 'الحرارة', dissolved_oxygen as 'الأكسجين DO', ph as 'الحموضة pH', ammonia as 'الأمونيا NH3', notes as ملاحظات FROM water_quality ORDER BY id DESC LIMIT 10", conn)
    st.dataframe(df_w, use_container_width=True)

# ----------------- 7. قائمة المراجعة والتدقيق اليومي -----------------
elif menu == "✅ قائمة المراجعة والتدقيق اليومي":
    st.header("✅ قائمة الفحص والرقابة الميدانية اليومية")
    st.caption("بروتوكول ضبط الجودة ومراجعة تشغيل المزرعة اليومي")
    
    ponds = [r[0] for r in conn.cursor().execute("SELECT name FROM ponds WHERE status='نشط'").fetchall()]
    with st.form("audit_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        a_date = c1.date_input("تاريخ التدقيق", date.today())
        p_name = c2.selectbox("الحوض المفحوص", ponds if ponds else ["عام"])
        inspector = c3.text_input("اسم المراقب / الفاحص")
        
        st.markdown("##### عناصر التفتيش الميداني:")
        c4, c5, c6 = st.columns(3)
        pumps = c4.selectbox("حالة البدالات والطلمبات والمولدات", ["ممتازة وشغالة", "تحتاج صيانة دورية", "معطلة / طوارئ"])
        nets = c5.selectbox("حالة الجسور والشباك والمصافي", ["سليمة 100%", "تحتاج تدعيم", "يوجد هدر أو تسريب"])
        feed_resp = c6.selectbox("سلوك الأسماك وإقبالها على العلف", ["شراهة وإقبال ممتاز", "إقبال متوسط", "عزوف عن العلف (خطر)"])
        
        c7, c8 = st.columns(2)
        morts = c7.number_input("عدد الأسماك النافقة المجمعة اليوم", min_value=0, step=1)
        a_notes = c8.text_input("ملاحظات أمنية وتشغيلية خاصة")
        
        if st.form_submit_button("اعتماد تقرير التدقيق اليومي"):
            conn.cursor().execute("INSERT INTO audit_log (date, pond_name, pumps_status, nets_status, feeding_response, mortalities, inspector, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                  (str(a_date), p_name, pumps, nets, feed_resp, morts, inspector, a_notes))
            conn.commit()
            st.success("تم اعتماد تقرير المراجعة وأرشفته")
            st.rerun()

    df_a = pd.read_sql("SELECT date as التاريخ, pond_name as الحوض, pumps_status as الطلمبات, feeding_response as 'إقبال العلف', mortalities as النافق, inspector as الفاحص FROM audit_log ORDER BY id DESC LIMIT 10", conn)
    st.dataframe(df_a, use_container_width=True)

# ----------------- 8. الأعلاف والتشغيل اليومي -----------------
elif menu == "🥣 الأعلاف والتشغيل اليومي":
    st.header("🥣 حركة العلف والمصروفات اليومية")
    tab_f, tab_e = st.tabs(["تسجيل التغذية", "المصروفات النثرية والتشغيلية"])
    
    with tab_f:
        ponds = [r[0] for r in conn.cursor().execute("SELECT name FROM ponds WHERE status='نشط'").fetchall()]
        if ponds:
            with st.form("feed_entry", clear_on_submit=True):
                c1, c2 = st.columns(2)
                f_date = c1.date_input("التاريخ", date.today())
                p_sel = c2.selectbox("رقم الحوض", ponds)
                c3, c4, c5 = st.columns(3)
                f_t = c3.selectbox("النوع", ["طافي 30%", "طافي 25%", "غطاس 32%", "بادئ 35%", "أخرى"])
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
            e_date = c1.date_input("تاريخ المصروف", date.today())
            cat = c2.selectbox("البند", ["سولار وكهرباء", "أدوية ومخصبات", "صيانة ومعدات", "إيجار", "نثريات"])
            c3, c4 = st.columns(2)
            amt = c3.number_input("المبلغ (ج.م)", min_value=0.0, step=50.0)
            notes = c4.text_input("البيان والمستند")
            if st.form_submit_button("حفظ المصروف") and amt > 0:
                conn.cursor().execute("INSERT INTO expenses (date, category, amount, notes) VALUES (?, ?, ?, ?)",
                                      (str(e_date), cat, amt, notes))
                conn.commit()
                st.success("تم ترحيل المصروف")
                st.rerun()

# ----------------- 9. مبيعات الحصاد -----------------
elif menu == "💰 مبيعات الحصاد":
    st.header("💰 مبيعات الحصاد والإيرادات")
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
            st.success("تم تسجيل الفاتورة")
            st.rerun()

# ----------------- 10. الأصول الثابتة ورأس المال -----------------
elif menu == "🚜 الأصول الثابتة ورأس المال":
    st.header("🚜 تسجيل الأصول الثابتة ورأس المال")
    with st.form("asset_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        a_name = c1.text_input("اسم الأصل (مولد، بدالة، طلمبة، رأس مال نقدي)")
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

# ----------------- 11. إدارة الأحواض -----------------
elif menu == "🏞️ إدارة الأحواض":
    st.header("🏞️ تعريف الأحواض وتسكين الزريعة")
    with st.form("pond_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم أو رقم الحوض")
        f_type = c2.selectbox("نوع الأسماك", ["بلطي نيللي", "بوري", "طوبار", "قاروص", "دنيس", "مبروك"])
        c3, c4, c5 = st.columns(3)
        count = c3.number_input("عدد الزريعة", min_value=0, step=1000)
        cost = c4.number_input("تكلفة الشراء (ج.م)", min_value=0.0, step=500.0)
        init_w = c5.number_input("متوسط وزن الزريعة عند الإنزال (جرام)", value=1.0, step=0.5)
        s_date = st.date_input("تاريخ التسكين", date.today())
        if st.form_submit_button("تسكين الحوض") and name:
            try:
                conn.cursor().execute("INSERT INTO ponds (name, fish_type, stock_count, initial_cost, initial_weight, stock_date) VALUES (?, ?, ?, ?, ?, ?)",
                                      (name, f_type, count, cost, init_w, str(s_date)))
                conn.commit()
                st.success("تم تسكين الحوض بنجاح")
                st.rerun()
            except:
                st.error("اسم الحوض موجود مسبقاً")

    df_p = pd.read_sql("SELECT name as الحوض, fish_type as النوع, stock_count as 'عدد الزريعة', initial_weight as 'الوزن المبدئي (جم)', stock_date as التسكين FROM ponds", conn)
    st.dataframe(df_p, use_container_width=True)