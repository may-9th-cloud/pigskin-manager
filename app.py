import streamlit as st
from database import *

from database import init_db
init_db()

st.set_page_config(page_title="豬皮管理系統", layout="wide")
st.title("豬皮取用紀錄系統")
menu = st.sidebar.radio("請選擇功能", ["取皮紀錄", "實驗使用", "查看庫存"])

if menu == "取皮紀錄":
    st.header("取皮資料登錄")
    
    date = st.date_input("取皮日期")
    source = st.text_input("豬隻來源")
    breed = st.text_input("品系")
    reason = st.text_input("犧牲原因")
    drug = st.text_input("用藥資訊")
    packages = st.number_input("取皮包數(每包約6片)", min_value=1, step=1)
    not_full = st.checkbox("有不足6片的情況")
    note = ""
    if not_full:
        pieces = st.number_input("實際片數(總數)", min_value=1, step=1)
        note = "不足6片"
    else:
        pieces = packages * 6

    if st.button("送出"):
        insert_pigskin_record(str(date), source, breed, reason, drug, packages, pieces, note)
        st.success("已成功登陸取皮資料")


elif menu == "實驗使用":
    st.header("實驗用豬皮登陸")
    available_packages = get_available_packages()

    if not available_packages:
        st.warning("目前無庫存可用")
    else:
        with st.form("use_form"):
            date = st.date_input("使用日期")
            st.markdown("### 可用庫存 (以包為單位)")
            options = [
                f"{r['id']}: 取皮日期={r['date']} / {r['pieces']}片" + (" ⚠️" if r['pieces'] < 6 else "")
                for r in available_packages
            ]
            selected_package = st.radio("選擇要使用的豬皮包：", options=options)
            submitted = st.form_submit_button("送出")
            if submitted:
                selected_id = int(selected_package.split(":")[0])
                use_package(selected_id, str(date))
                st.success("已成功登陸使用資料")


elif menu == "查看庫存":
    st.header("豬皮庫存紀錄")

    df = get_all_records_df()
    if df.empty:
        st.warning("尚無資料")
        st.stop()

    # 顯示剩餘片數
    remaining_total = df[df["used"] == 0]["pieces"].sum()
    st.subheader(f"目前剩餘片數: {remaining_total} 片")

    # 先處理欄位轉換
    df["date"] = pd.to_datetime(df["date"])
    df["used_date"] = pd.to_datetime(df["used_date"])
    df["取皮年份"] = df["date"].dt.year
    df["使用年份"] = df["used_date"].dt.year

    # 取皮紀錄篩選
    st.subheader("所有取皮紀錄")
    unique_input_years = sorted(df["取皮年份"].dropna().unique(), reverse=True)
    selected_input_years = st.multiselect("選擇取皮年份", unique_input_years, default=unique_input_years[:1])
    input_df = df[df["取皮年份"].isin(selected_input_years)]
    st.dataframe(input_df.drop(columns=["取皮年份", "使用年份"]), use_container_width=True)

    # 使用紀錄篩選
    st.subheader("豬皮使用紀錄")
    used_df = df[df["used"] == 1]
    unique_used_years = sorted(used_df["使用年份"].dropna().unique(), reverse=True)
    selected_used_years = st.multiselect("選擇使用年份", unique_used_years, default=unique_used_years[:1])
    filtered_used_df = used_df[used_df["使用年份"].isin(selected_used_years)]
    st.dataframe(filtered_used_df.drop(columns=["取皮年份", "使用年份"]), use_container_width=True)


