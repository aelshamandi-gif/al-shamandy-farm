import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import plotly.express as px

# 1. تهيئة الصفحة والاتجاه العربي
st.set_page_config(page_title="مزرعة عبد الله الشمندي", layout="wide", page_icon="🐟")

st.markdown("""
<style>
    body, html, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stMetric {
        background-color: #f8fafc;
        padding: 15px;
        border-radius: 10px;
        border-right: 5px solid #0284c7;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 2. نظام تسجيل الدخول وحماية الحسابات
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h2 style='text-align: center;'>🔒 مزرعة أسماك عبد الله الشمندي</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>نظام الإدارة المالية والتشغيلية - أدخل رمز الدخول</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pwd = st.text_input("رمز الدخول (PIN):", type="password")
            if st.button("دخول للنظام", use_container_width=True):
                if pwd == "2026":  # الرقم السري الافتراضي
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("رمز الدخول غير صحيح!")
        return False
    return True

if not check_password():
    st.stop()

# 3. إعداد قاعدة البيانات
def get_db():
    conn = sqlite3.connect("al_shamandy_farm.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ponds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        fish_type TEXT,
        stock_count INTEGER,
        stock_date TEXT,
        status TEXT DEFAULT 'نشط'
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pond_name TEXT,
        date TEXT,
        feed_type TEXT,
        qty_kg REAL,
        price_per_kg REAL,
        total_cost REAL
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        notes TEXT
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pond_name TEXT,
        date TEXT,
        qty_kg REAL,
        price_per_kg REAL,
        total_price REAL,
        client TEXT
    )""")
    conn.commit()
    return conn

conn = get_db()

# 4. القائمة الجانبية
st.sidebar.title("🐟 مزرعة عبد الله الشمندي")
st.sidebar.caption("الحسابات والعمليات اليومية")

if st.sidebar.button("تسجيل الخروج"):
    st.session_state.authenticated = False
    st.rerun()

menu = st.sidebar.radio("الانتقال إلى:", [
    "📊 لوحة التحكم والميزانية",
    "📝 المصروفات اليومية",
    "🥣 استهلاك العلف اليومي",
    "💰 مبيعات الحصاد",
    "🏞️ إدارة الأحواض والتسكين"
])

# ----------------- 1. لوحة التحكم -----------------
if menu == "📊 لوحة التحكم والميزانية":
    st.header("📊 ميزانية وأرباح المزرعة")
    
    df_exp = pd.read_sql("SELECT * FROM expenses", conn)
    df_feed = pd.read_sql("SELECT * FROM feed", conn)
    df_sales = pd.read_sql("SELECT * FROM sales", conn)
    
    total_feed_cost = df_feed['total_cost'].sum() if not df_feed.empty else 0.0
    total_other_exp = df_exp['amount'].sum() if not df_exp.empty else 0.0
    total_expenses = total_feed_cost + total_other_exp
    total_revenue = df_sales['total_price'].sum() if not df_sales.empty else 0.0
    net_profit = total_revenue - total_expenses

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي المبيعات", f"{total_revenue:,.2f} ج.م")
    c2.metric("تكلفة الأعلاف", f"{total_feed_cost:,.2f} ج.م")
    c3.metric("المصروفات الأخرى", f"{total_other_exp:,.2f} ج.م")
    c4.metric("صافي الربح / الخسارة", f"{net_profit:,.2f} ج.م", delta=f"{net_profit:,.2f}")

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("توزيع التكاليف")
        if total_expenses > 0:
            exp_summary = df_exp.groupby('category')['amount'].sum().reset_index() if not df_exp.empty else pd.DataFrame(columns=['category', 'amount'])
            feed_row = pd.DataFrame([{"category": "أعلاف", "amount": total_feed_cost}])
            all_exp_df = pd.concat([exp_summary, feed_row], ignore_index=True)
            fig = px.pie(all_exp_df, values='amount', names='category', hole=0.45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد مصروفات مسجلة حتى الآن.")

    with col_b:
        st.subheader("سجل الإيرادات")
        if not df_sales.empty:
            sales_trend = df_sales.groupby('date')['total_price'].sum().reset_index()
            fig2 = px.bar(sales_trend, x='date', y='total_price', labels={'date': 'التاريخ', 'total_price': 'المبلغ (ج.م)'})
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("لا توجد مبيعات مسجلة حتى الآن.")

# ----------------- 2. المصروفات اليومية -----------------
elif menu == "📝 المصروفات اليومية":
    st.header("📝 تسجيل المصروفات اليومية")
    with st.form("expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        exp_date = c1.date_input("التاريخ", date.today())
        category = c2.selectbox("البند", ["سولار وكهرباء", "أدوية ومخصبات", "عمالة ونثريات", "صيانة ومعدات", "إيجار", "أخرى"])
        c3, c4 = st.columns(2)
        amount = c3.number_input("المبلغ (ج.م)", min_value=0.0, step=50.0)
        notes = c4.text_input("البيان / ملاحظات")
        
        if st.form_submit_button("حفظ المصروف") and amount > 0:
            conn.cursor().execute("INSERT INTO expenses (date, category, amount, notes) VALUES (?, ?, ?, ?)",
                                  (str(exp_date), category, amount, notes))
            conn.commit()
            st.success("تم الحفظ بنجاح!")
            st.rerun()

    st.subheader("سجل المصروفات")
    df_exp = pd.read_sql("SELECT date as التاريخ, category as البند, amount as المبلغ, notes as البيان FROM expenses ORDER BY id DESC", conn)
    st.dataframe(df_exp, use_container_width=True)

# ----------------- 3. استهلاك العلف اليومي -----------------
elif menu == "🥣 استهلاك العلف اليومي":
    st.header("🥣 متابعة العلف والتغذية")
    ponds = [row[0] for row in conn.cursor().execute("SELECT name FROM ponds WHERE status='نشط'").fetchall()]
    
    if not ponds:
        st.warning("يرجى إضافة أحواض أولاً من شاشة 'إدارة الأحواض والتسكين'.")
    else:
        with st.form("feed_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            feed_date = c1.date_input("التاريخ", date.today())
            pond = c2.selectbox("اسم / رقم الحوض", ponds)
            c3, c4, c5 = st.columns(3)
            f_type = c3.selectbox("نوع ونسبة البروتين", ["طافي 30%", "طافي 25%", "غطاس 32%", "بادئ 35%", "أخرى"])
            qty = c4.number_input("الكمية (كيلوجرام)", min_value=0.0, step=10.0)
            price = c5.number_input("سعر الكيلو (ج.م)", min_value=0.0, step=0.5)
            
            if st.form_submit_button("حفظ حركة العلف") and qty > 0:
                cost = qty * price
                conn.cursor().execute("INSERT INTO feed (pond_name, date, feed_type, qty_kg, price_per_kg, total_cost) VALUES (?, ?, ?, ?, ?, ?)",
                                      (pond, str(feed_date), f_type, qty, price, cost))
                conn.commit()
                st.success(f"تم التسجيل: إجمالي التكلفة = {cost:,.2f} ج.م")
                st.rerun()

        st.subheader("سجل التغذية")
        df_feed = pd.read_sql("SELECT date as التاريخ, pond_name as الحوض, feed_type as العلف, qty_kg as 'الكمية (كجم)', total_cost as 'التكلفة الإجمالية' FROM feed ORDER BY id DESC", conn)
        st.dataframe(df_feed, use_container_width=True)

# ----------------- 4. مبيعات الحصاد -----------------
elif menu == "💰 مبيعات الحصاد":
    st.header("💰 تسجيل مبيعات الحصاد")
    ponds = [row[0] for row in conn.cursor().execute("SELECT name FROM ponds").fetchall()]
    with st.form("sales_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        s_date = c1.date_input("تاريخ البيع", date.today())
        p_name = c2.selectbox("الحوض المحصود", ponds if ponds else ["عام"])
        c3, c4 = st.columns(2)
        qty = c3.number_input("الوزن الإجمالي المباع (كجم)", min_value=0.0, step=50.0)
        price = c4.number_input("سعر الكيلو (ج.م)", min_value=0.0, step=1.0)
        client = st.text_input("اسم التاجر / العميل")
        
        if st.form_submit_button("حفظ عملية البيع") and qty > 0:
            total = qty * price
            conn.cursor().execute("INSERT INTO sales (pond_name, date, qty_kg, price_per_kg, total_price, client) VALUES (?, ?, ?, ?, ?, ?)",
                                  (p_name, str(s_date), qty, price, total, client))
            conn.commit()
            st.success(f"تم تسجيل البيع: {total:,.2f} ج.م")
            st.rerun()

    st.subheader("سجل المبيعات")
    df_sales = pd.read_sql("SELECT date as التاريخ, pond_name as الحوض, qty_kg as 'الوزن (كجم)', price_per_kg as 'سعر الكيلو', total_price as 'الإجمالي', client as التاجر FROM sales ORDER BY id DESC", conn)
    st.dataframe(df_sales, use_container_width=True)

# ----------------- 5. إدارة الأحواض -----------------
elif menu == "🏞️ إدارة الأحواض والتسكين":
    st.header("🏞️ تعريف الأحواض وتسكين الزريعة")
    with st.form("pond_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم أو رقم الحوض (مثال: حوض 1)")
        f_type = c2.selectbox("نوع الأسماك", ["بلطي نيللي", "بوري", "طوبار", "قاروص", "دنيس", "مبروك"])
        c3, c4 = st.columns(2)
        count = c3.number_input("عدد الزريعة المدخلة", min_value=0, step=1000)
        s_date = c4.date_input("تاريخ التسكين", date.today())
        
        if st.form_submit_button("إضافة الحوض") and name:
            try:
                conn.cursor().execute("INSERT INTO ponds (name, fish_type, stock_count, stock_date) VALUES (?, ?, ?, ?)",
                                      (name, f_type, count, str(s_date)))
                conn.commit()
                st.success("تمت إضافة الحوض بنجاح!")
                st.rerun()
            except:
                st.error("اسم الحوض موجود بالفعل!")

    st.subheader("الأحواض القائمة")
    df_ponds = pd.read_sql("SELECT name as الحوض, fish_type as النوع, stock_count as 'عدد الزريعة', stock_date as 'تاريخ التسكين' FROM ponds", conn)
    st.dataframe(df_ponds, use_container_width=True)