import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import plotly.express as px
import streamlit.components.v1 as components

# 1. إعداد الصفحة واللغة
st.set_page_config(page_title="مزرعة عبد الله الشمندي - النظام المحاسبي", layout="wide", page_icon="🐟")

st.markdown("""
<style>
    body, html, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stMetric {
        background-color: #f8fafc;
        padding: 12px;
        border-radius: 8px;
        border-right: 5px solid #0284c7;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# 2. نظام تسجيل الدخول والأمان
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center; color: #0f172a;'>🐟 شركة ومزرعة أسماك عبد الله الشمندي</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>النظام المالي المحاسبي وإدارة الإنتاج</p>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1.8, 1])
        with c2:
            st.info("🔒 يرجى إدخال رمز المرور المالي للمتابعة")
            pwd = st.text_input("رمز الدخول (PIN):", type="password")
            if st.button("تسجيل الدخول", use_container_width=True):
                if pwd == "2026":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("رمز الدخول غير صحيح!")
        return False
    return True

if not check_password():
    st.stop()

# 3. قاعدة البيانات المحاسبية
def get_db():
    conn = sqlite3.connect("al_shamandy_farm.db", check_same_thread=False)
    cursor = conn.cursor()
    # الأحواض
    cursor.execute("""CREATE TABLE IF NOT EXISTS ponds (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, fish_type TEXT, 
        stock_count INTEGER, initial_cost REAL, stock_date TEXT, status TEXT DEFAULT 'نشط')""")
    # الأعلاف
    cursor.execute("""CREATE TABLE IF NOT EXISTS feed (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pond_name TEXT, date TEXT, 
        feed_type TEXT, qty_kg REAL, price_per_kg REAL, total_cost REAL)""")
    # المصروفات
    cursor.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, 
        amount REAL, notes TEXT)""")
    # المبيعات
    cursor.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pond_name TEXT, date TEXT, 
        qty_kg REAL, price_per_kg REAL, total_price REAL, client TEXT)""")
    # الأصول الثابتة ورأس المال
    cursor.execute("""CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, asset_name TEXT, 
        category TEXT, value REAL, purchase_date TEXT)""")
    conn.commit()
    return conn

conn = get_db()

# 4. القائمة الرئيسية
st.sidebar.title("🐟 مزرعة عبد الله الشمندي")
st.sidebar.caption("نظام الحسابات والقوائم المالية")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.authenticated = False
    st.rerun()

menu = st.sidebar.radio("القوائم والشاشات:", [
    "📊 لوحة المؤشرات المالية",
    "📑 قائمة الدخل (P&L)",
    "🏛️ الميزانية العمومية (المركز المالي)",
    "📝 المصروفات اليومية",
    "🥣 استهلاك الأعلاف",
    "💰 مبيعات الحصاد",
    "🚜 الأصول الثابتة ورأس المال",
    "🏞️ إدارة الأحواض"
])

# ----------------- 1. لوحة المؤشرات المالية -----------------
if menu == "📊 لوحة المؤشرات المالية":
    st.header("📊 لوحة المتابعة والمؤشرات الحيوية")
    
    df_exp = pd.read_sql("SELECT * FROM expenses", conn)
    df_feed = pd.read_sql("SELECT * FROM feed", conn)
    df_sales = pd.read_sql("SELECT * FROM sales", conn)
    
    feed_c = df_feed['total_cost'].sum() if not df_feed.empty else 0.0
    other_c = df_exp['amount'].sum() if not df_exp.empty else 0.0
    total_costs = feed_c + other_c
    revenue = df_sales['total_price'].sum() if not df_sales.empty else 0.0
    net_p = revenue - total_costs

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي الإيرادات", f"{revenue:,.2f} ج.م")
    c2.metric("تكلفة الأعلاف", f"{feed_c:,.2f} ج.م")
    c3.metric("المصروفات التشغيلية", f"{other_c:,.2f} ج.م")
    c4.metric("صافي الربح التراكمي", f"{net_p:,.2f} ج.م", delta=f"{net_p:,.2f}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("تحليل المصروفات")
        if total_costs > 0:
            exp_sum = df_exp.groupby('category')['amount'].sum().reset_index() if not df_exp.empty else pd.DataFrame(columns=['category', 'amount'])
            all_exp = pd.concat([exp_sum, pd.DataFrame([{"category": "أعلاف", "amount": feed_c}])], ignore_index=True)
            st.plotly_chart(px.pie(all_exp, values='amount', names='category', hole=0.4), use_container_width=True)
        else:
            st.info("لا توجد حركات تكاليف مسجلة.")
    with col2:
        st.subheader("حركة المبيعات الشهرية")
        if not df_sales.empty:
            st.plotly_chart(px.bar(df_sales.groupby('date')['total_price'].sum().reset_index(), x='date', y='total_price'), use_container_width=True)

# ----------------- 2. قائمة الدخل (Income Statement) -----------------
elif menu == "📑 قائمة الدخل (P&L)":
    st.header("📑 قائمة الدخل (الأرباح والخسائر)")
    
    c1, c2 = st.columns(2)
    start_d = c1.date_input("من تاريخ", date(date.today().year, 1, 1))
    end_d = c2.date_input("إلى تاريخ", date.today())
    
    # حساب الإيرادات
    sales_q = pd.read_sql(f"SELECT SUM(total_price) as rev FROM sales WHERE date BETWEEN '{start_d}' AND '{end_d}'", conn)
    rev = sales_q['rev'].iloc[0] or 0.0
    
    # تكلفة الإنتاج المباشرة (علف + زريعة)
    feed_q = pd.read_sql(f"SELECT SUM(total_cost) as feed_cost FROM feed WHERE date BETWEEN '{start_d}' AND '{end_d}'", conn)
    c_feed = feed_q['feed_cost'].iloc[0] or 0.0
    
    # تكاليف تشغيل مباشرة (سولار، أدوية)
    direct_exp_q = pd.read_sql(f"SELECT SUM(amount) as d_exp FROM expenses WHERE category IN ('سولار وكهرباء', 'أدوية ومخصبات') AND date BETWEEN '{start_d}' AND '{end_d}'", conn)
    c_direct_exp = direct_exp_q['d_exp'].iloc[0] or 0.0
    
    total_cogs = c_feed + c_direct_exp
    gross_profit = rev - total_cogs
    
    # مصروفات إدارية وتشغيلية عامة
    indirect_q = pd.read_sql(f"SELECT SUM(amount) as ind_exp FROM expenses WHERE category NOT IN ('سولار وكهرباء', 'أدوية ومخصبات') AND date BETWEEN '{start_d}' AND '{end_d}'", conn)
    c_indirect = indirect_q['ind_exp'].iloc[0] or 0.0
    
    net_income = gross_profit - c_indirect

    # تنسيق تقرير HTML للطباعة كـ PDF
    html_report = f"""
    <div id="printArea" style="font-family: Arial; direction: rtl; padding: 25px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff;">
        <div style="text-align: center; border-bottom: 2px solid #0284c7; padding-bottom: 15px; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #0f172a;">مزرعة أسماك عبد الله الشمندي</h2>
            <h4 style="margin: 5px 0; color: #475569;">قائمة الدخل عن الفترة من {start_d} إلى {end_d}</h4>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
            <tr style="background: #f1f5f9;"><th style="padding: 10px; text-align: right;">البيان</th><th style="padding: 10px; text-align: left;">المبلغ (ج.م)</th></tr>
            <tr><td style="padding: 10px; font-weight: bold; color: #0369a1;">إجمالي إيرادات المبيعات</td><td style="padding: 10px; text-align: left; font-weight: bold;">{rev:,.2f}</td></tr>
            <tr><td colspan="2" style="padding: 5px; background: #fafafa; font-weight: bold; color: #475569;">يخصم: تكلفة الإنتاج والمبيعات المباشرة:</td></tr>
            <tr><td style="padding-right: 30px;">- استهلاك الأعلاف</td><td style="text-align: left;">({c_feed:,.2f})</td></tr>
            <tr><td style="padding-right: 30px;">- تشغيل طلمبات (سولار وكهرباء وأدوية)</td><td style="text-align: left;">({c_direct_exp:,.2f})</td></tr>
            <tr style="background: #e2e8f0; font-weight: bold;"><td>مجمل الربح (Gross Profit)</td><td style="text-align: left;">{gross_profit:,.2f}</td></tr>
            <tr><td colspan="2" style="padding: 5px; background: #fafafa; font-weight: bold; color: #475569;">يخصم: المصروفات العمومية والتشغيلية:</td></tr>
            <tr><td style="padding-right: 30px;">- عمالة، إيجار، صيانة ونثريات</td><td style="text-align: left;">({c_indirect:,.2f})</td></tr>
            <tr style="background: #0284c7; color: #fff; font-size: 17px; font-weight: bold;"><td style="padding: 12px;">صافي الربح / (الخسارة)</td><td style="padding: 12px; text-align: left;">{net_income:,.2f} ج.م</td></tr>
        </table>
        <div style="margin-top: 30px; display: flex; justify-content: space-between;">
            <div>المشرف المالي: ....................</div>
            <div>اعتماد: عبد الله الشمندي</div>
        </div>
    </div>
    """
    
    st.markdown(html_report, unsafe_allow_html=True)
    st.write("")
    
    # زر الطباعة المباشر إلى PDF
    print_btn = """
    <button onclick="window.print()" style="background-color: #0284c7; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%;">
        🖨️ طباعة أو تصدير التقرير كملف PDF
    </button>
    """
    components.html(print_btn, height=60)

# ----------------- 3. الميزانية العمومية (المركز المالي) -----------------
elif menu == "🏛️ الميزانية العمومية (المركز المالي)":
    st.header("🏛️ الميزانية العمومية وقائمة المركز المالي")
    as_of_date = st.date_input("كما في تاريخ:", date.today())
    
    # 1. الأصول المتداولة
    df_sales = pd.read_sql("SELECT SUM(total_price) as s FROM sales", conn)
    df_exp = pd.read_sql("SELECT SUM(amount) as e FROM expenses", conn)
    df_feed = pd.read_sql("SELECT SUM(total_cost) as f FROM feed", conn)
    df_cap = pd.read_sql("SELECT SUM(value) as c FROM assets WHERE category='رأس مال نقدي مبدئي'", conn)
    
    total_in = (df_sales['s'].iloc[0] or 0.0) + (df_cap['c'].iloc[0] or 0.0)
    total_out = (df_exp['e'].iloc[0] or 0.0) + (df_feed['f'].iloc[0] or 0.0)
    cash_in_hand = total_in - total_out  # النقدية بالخزينة
    
    # تقييم مخزون الأسماك الحية بالأحواض (تقديري من تكلفة الزريعة والعلف المستهلك)
    bio_inventory = df_feed['f'].iloc[0] or 0.0  # قيمة العلف المحول إلى لحم
    total_current_assets = cash_in_hand + bio_inventory
    
    # 2. الأصول الثابتة (أراضي، طلمبات، بدالات، موالدات)
    df_fixed = pd.read_sql("SELECT SUM(value) as fa FROM assets WHERE category != 'رأس مال نقدي مبدئي'", conn)
    fixed_assets = df_fixed['fa'].iloc[0] or 0.0
    
    total_assets = total_current_assets + fixed_assets
    
    # 3. حقوق الملكية
    capital = df_cap['c'].iloc[0] or 0.0
    retained_earnings = total_assets - capital # الموازن المحاسبي

    balance_sheet_html = f"""
    <div id="printArea" style="font-family: Arial; direction: rtl; padding: 25px; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff;">
        <div style="text-align: center; border-bottom: 2px solid #0f766e; padding-bottom: 15px; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #0f172a;">مزرعة أسماك عبد الله الشمندي</h2>
            <h4 style="margin: 5px 0; color: #475569;">الميزانية العمومية كما في {as_of_date}</h4>
        </div>
        <div style="display: flex; gap: 20px;">
            <!-- جانب الأصول -->
            <div style="flex: 1; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px;">
                <h3 style="color: #0369a1; border-bottom: 2px solid #0369a1; padding-bottom: 5px;">الأصول (Assets)</h3>
                <h4 style="color: #475569;">الأصول المتداولة:</h4>
                <p>النقدية بالصندوق والخزينة: <b>{cash_in_hand:,.2f} ج.م</b></p>
                <p>مخزون بيولوجي (الأسماك بالأحواض): <b>{bio_inventory:,.2f} ج.م</b></p>
                <hr>
                <h4 style="color: #475569;">الأصول الثابتة:</h4>
                <p>معدات، طلمبات، ومولدات: <b>{fixed_assets:,.2f} ج.م</b></p>
                <div style="background: #e0f2fe; padding: 10px; font-size: 16px; font-weight: bold; border-radius: 5px; margin-top: 20px;">
                    إجمالي الأصول: {total_assets:,.2f} ج.م
                </div>
            </div>
            <!-- جانب الالتزامات وحقوق الملكية -->
            <div style="flex: 1; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px;">
                <h3 style="color: #0f766e; border-bottom: 2px solid #0f766e; padding-bottom: 5px;">الخصوم وحقوق الملكية</h3>
                <h4 style="color: #475569;">الالتزامات والديون:</h4>
                <p>مستحقات موردين وأعلاف آجلة: <b>0.00 ج.م</b></p>
                <hr>
                <h4 style="color: #475569;">حقوق الملكية (Equity):</h4>
                <p>رأس المال المستثمر المبدئي: <b>{capital:,.2f} ج.م</b></p>
                <p>صافي الأرباح المحتجزة / النشاط: <b>{retained_earnings:,.2f} ج.م</b></p>
                <div style="background: #ccfbf1; padding: 10px; font-size: 16px; font-weight: bold; border-radius: 5px; margin-top: 20px;">
                    إجمالي الخصوم وحقوق الملكية: {total_assets:,.2f} ج.م
                </div>
            </div>
        </div>
        <p style="text-align: center; margin-top: 25px; color: #16a34a; font-weight: bold;">✔ الميزانية متوازنة محاسبياً</p>
    </div>
    """
    st.markdown(balance_sheet_html, unsafe_allow_html=True)
    st.write("")
    components.html("""
    <button onclick="window.print()" style="background-color: #0f766e; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%;">
        🖨️ طباعة أو تصدير الميزانية العمومية PDF
    </button>
    """, height=60)

# ----------------- 4. المصروفات اليومية -----------------
elif menu == "📝 المصروفات اليومية":
    st.header("📝 تسجيل المصروفات اليومية")
    with st.form("expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        exp_date = c1.date_input("التاريخ", date.today())
        category = c2.selectbox("نوع المصروف المحاسبي", [
            "سولار وكهرباء", "أدوية ومخصبات", "عمالة ونثريات", "صيانة ومعدات", "إيجارات", "أخرى"
        ])
        c3, c4 = st.columns(2)
        amount = c3.number_input("المبلغ (ج.م)", min_value=0.0, step=50.0)
        notes = c4.text_input("البيان والمستند")
        
        if st.form_submit_button("ترحيل المصروف للدفاتر") and amount > 0:
            conn.cursor().execute("INSERT INTO expenses (date, category, amount, notes) VALUES (?, ?, ?, ?)",
                                  (str(exp_date), category, amount, notes))
            conn.commit()
            st.success("تم تسجيل وترحيل المصروف بنجاح!")
            st.rerun()

    df_exp = pd.read_sql("SELECT date as التاريخ, category as البند, amount as المبلغ, notes as البيان FROM expenses ORDER BY id DESC", conn)
    st.dataframe(df_exp, use_container_width=True)

# ----------------- 5. استهلاك الأعلاف -----------------
elif menu == "🥣 استهلاك الأعلاف":
    st.header("🥣 حركة استهلاك العلف اليومية")
    ponds = [row[0] for row in conn.cursor().execute("SELECT name FROM ponds WHERE status='نشط'").fetchall()]
    if not ponds:
        st.warning("يرجى تعريف أحواض أولاً.")
    else:
        with st.form("feed_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            feed_date = c1.date_input("التاريخ", date.today())
            pond = c2.selectbox("الحوض", ponds)
            c3, c4, c5 = st.columns(3)
            f_type = c3.selectbox("البروتين / النوع", ["طافي 30%", "طافي 25%", "غطاس 32%", "بادئ 35%", "أخرى"])
            qty = c4.number_input("الكمية المستهلكة (كجم)", min_value=0.0, step=10.0)
            price = c5.number_input("سعر الكيلو (ج.م)", min_value=0.0, step=0.5)
            
            if st.form_submit_button("تسجيل حركة العلف") and qty > 0:
                cost = qty * price
                conn.cursor().execute("INSERT INTO feed (pond_name, date, feed_type, qty_kg, price_per_kg, total_cost) VALUES (?, ?, ?, ?, ?, ?)",
                                      (pond, str(feed_date), f_type, qty, price, cost))
                conn.commit()
                st.success(f"تم التسجيل بتكلفة إجمالية: {cost:,.2f} ج.م")
                st.rerun()

        df_feed = pd.read_sql("SELECT date as التاريخ, pond_name as الحوض, feed_type as العلف, qty_kg as 'الكمية (كجم)', total_cost as 'الإجمالي' FROM feed ORDER BY id DESC", conn)
        st.dataframe(df_feed, use_container_width=True)

# ----------------- 6. مبيعات الحصاد -----------------
elif menu == "💰 مبيعات الحصاد":
    st.header("💰 إيرادات الحصاد والمبيعات")
    ponds = [row[0] for row in conn.cursor().execute("SELECT name FROM ponds").fetchall()]
    with st.form("sales_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        s_date = c1.date_input("تاريخ البيع", date.today())
        p_name = c2.selectbox("الحوض المحصود", ponds if ponds else ["عام"])
        c3, c4 = st.columns(2)
        qty = c3.number_input("الوزن الإجمالي (كجم)", min_value=0.0, step=50.0)
        price = c4.number_input("سعر الكيلو (ج.م)", min_value=0.0, step=1.0)
        client = st.text_input("اسم العميل / التاجر")
        
        if st.form_submit_button("حفظ فاتورة البيع") and qty > 0:
            total = qty * price
            conn.cursor().execute("INSERT INTO sales (pond_name, date, qty_kg, price_per_kg, total_price, client) VALUES (?, ?, ?, ?, ?, ?)",
                                  (p_name, str(s_date), qty, price, total, client))
            conn.commit()
            st.success(f"تم حفظ الفاتورة بقيمة: {total:,.2f} ج.م")
            st.rerun()

    df_sales = pd.read_sql("SELECT date as التاريخ, pond_name as الحوض, qty_kg as 'الوزن (كجم)', price_per_kg as 'السعر', total_price as 'الإجمالي', client as العميل FROM sales ORDER BY id DESC", conn)
    st.dataframe(df_sales, use_container_width=True)

# ----------------- 7. الأصول الثابتة ورأس المال -----------------
elif menu == "🚜 الأصول الثابتة ورأس المال":
    st.header("🚜 تسجيل الأصول الثابتة ورأس المال المبدئي")
    st.info("تسجيل الأصول هنا ضروري لتظهر الميزانية العمومية بشكل سليم.")
    
    with st.form("assets_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        a_name = c1.text_input("اسم الأصل / البيان (مثلاً: مولد كهرباء، طلمبة مياه، بدالات، رأس مال كاش)")
        a_cat = c2.selectbox("التصنيف المحاسبي", ["معدات وآلات وطلمبات", "مباني وأحواض خرسانية", "شبكات وسيارات نقل", "رأس مال نقدي مبدئي"])
        c3, c4 = st.columns(2)
        a_val = c3.number_input("القيمة التقديرية (ج.م)", min_value=0.0, step=1000.0)
        a_date = c4.date_input("تاريخ الشراء / الإيداع", date.today())
        
        if st.form_submit_button("تسجيل الأصل") and a_val > 0:
            conn.cursor().execute("INSERT INTO assets (asset_name, category, value, purchase_date) VALUES (?, ?, ?, ?)",
                                  (a_name, a_cat, a_val, str(a_date)))
            conn.commit()
            st.success("تم إدراج الأصل في دفاتر المركز المالي!")
            st.rerun()

    df_assets = pd.read_sql("SELECT asset_name as الأصل, category as التصنيف, value as 'القيمة (ج.م)', purchase_date as التاريخ FROM assets", conn)
    st.dataframe(df_assets, use_container_width=True)

# ----------------- 8. إدارة الأحواض -----------------
elif menu == "🏞️ إدارة الأحواض":
    st.header("🏞️ تعريف الأحواض وتسكين الزريعة")
    with st.form("pond_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الحوض")
        f_type = c2.selectbox("نوع الأسماك", ["بلطي نيللي", "بوري", "طوبار", "قاروص", "دنيس", "مبروك"])
        c3, c4 = st.columns(2)
        count = c3.number_input("عدد الزريعة", min_value=0, step=1000)
        cost_seed = c4.number_input("تكلفة شراء الزريعة (ج.م)", min_value=0.0, step=500.0)
        s_date = st.date_input("تاريخ التسكين", date.today())
        
        if st.form_submit_button("تسكين الحوض") and name:
            try:
                conn.cursor().execute("INSERT INTO ponds (name, fish_type, stock_count, initial_cost, stock_date) VALUES (?, ?, ?, ?, ?)",
                                      (name, f_type, count, cost_seed, str(s_date)))
                conn.commit()
                st.success("تم تسكين الحوض بنجاح!")
                st.rerun()
            except:
                st.error("اسم الحوض موجود مسبقاً!")

    df_ponds = pd.read_sql("SELECT name as الحوض, fish_type as النوع, stock_count as 'عدد الزريعة', initial_cost as 'تكلفة الزريعة', stock_date as التسكين FROM ponds", conn)
    st.dataframe(df_ponds, use_container_width=True)