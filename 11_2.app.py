import streamlit as st
import json
import os
from datetime import datetime

# -------------------------------------------------------------------
# 1. 설정 및 데이터베이스(JSON) 연동
# -------------------------------------------------------------------
st.set_page_config(page_title="11학년 2반 학급 웹사이트", page_icon="🏫", layout="wide")

DATA_FILE = "class_data.json"
ADMIN_PASSWORD = "1234"  # 선생님 관리자 비밀번호

default_data = {
    "schedules": [],
    "board": [],
    "gallery": [],
    "subject_chem": [],
    "subject_soc": [],
    "subject_jp": [],
    "subject_code": []
}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

# -------------------------------------------------------------------
# 2. 사이드바 (모드 변경 및 안내)
# -------------------------------------------------------------------
st.sidebar.title("🏫 11학년 2반")
mode = st.sidebar.radio("모드 선택", ["학생 모드 👩‍🎓", "선생님(관리자) 모드 👨‍🏫"])

is_admin = False
if mode == "선생님(관리자) 모드 👨‍🏫":
    pw = st.sidebar.text_input("비밀번호 입력", type="password")
    if pw == ADMIN_PASSWORD:
        st.sidebar.success("관리자 인증 성공!")
        is_admin = True
    elif pw:
        st.sidebar.error("비밀번호가 틀렸습니다.")

st.sidebar.divider()
st.sidebar.info("💡 실시간 학급 데이터가 서버에 자동 저장됩니다.")

# -------------------------------------------------------------------
# 3. 메인 화면 (헤더 및 탭 구성을 통한 페이지 이동)
# -------------------------------------------------------------------
st.title("✨ 11학년 2반 학급 공간")

tab_home, tab_schedule, tab_subject, tab_meal, tab_gallery, tab_board = st.tabs([
    "🏠 대시보드", "📅 주요 일정", "📚 선택과목", "🍱 급식/생일", "📸 사진첩", "📮 익명 건의함"
])

# -------------------------------------------------------------------
# TAB 1: 대시보드
# -------------------------------------------------------------------
with tab_home:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 최근 학급 일정")
        schedules = sorted(data["schedules"], key=lambda x: (not x.get("pinned", False), x.get("id", 0)), reverse=True)
        if schedules:
            for s in schedules[:3]:
                pin = "📌 " if s.get("pinned") else ""
                st.write(f"- {pin}**[{s.get('subject', '공통')}]** {s.get('title')} (`{s.get('date')}`)")
        else:
            st.caption("등록된 일정이 없습니다.")

        st.subheader("🍱 오늘의 급식")
        st.info("발아현미밥 · 돈육김치찌개 · 수제치즈돈까스 · 마카로니콘샐러드 · 깍두기 · 멜론")

    with col2:
        st.subheader("🎂 이번 달 생일")
        st.success("🎉 8월 12일: 김철수 | 🎉 8월 25일: 이영희")

        st.subheader("📢 최신 과목 공지")
        for sub_name, sub_key in [("화학 I", "subject_chem"), ("사회·문화", "subject_soc"), ("일본어 I", "subject_jp"), ("프로그래밍", "subject_code")]:
            posts = data.get(sub_key, [])
            latest = posts[-1]["title"] if posts else "공지 없음"
            st.text(f"• {sub_name}: {latest}")

# -------------------------------------------------------------------
# TAB 2: 주요 일정
# -------------------------------------------------------------------
with tab_schedule:
    st.subheader("📅 전체 학급 일정")
    
    with st.expander("+ 새 일정 등록하기"):
        with st.form("add_schedule"):
            sub = st.text_input("과목/구분 (예: 수학, 학급행사)")
            title = st.text_input("일정 제목")
            date_val = st.date_input("날짜")
            author = st.text_input("작성자 이름", "익명")
            submit = st.form_submit_button("등록")
            
            if submit and title:
                new_item = {
                    "id": int(datetime.now().timestamp() * 1000),
                    "subject": sub if sub else "공통",
                    "title": title,
                    "date": str(date_val),
                    "author": author,
                    "pinned": False
                }
                data["schedules"].append(new_item)
                save_data(data)
                st.success("일정이 추가되었습니다!")
                st.rerun()

    schedules = sorted(data["schedules"], key=lambda x: (not x.get("pinned", False), x.get("id", 0)), reverse=True)
    for item in schedules:
        with st.container(border=True):
            cols = st.columns([4, 1])
            with cols[0]:
                pin_mark = "📌 [고정] " if item.get("pinned") else ""
                st.markdown(f"### {pin_mark}{item['title']}")
                st.caption(f"구분: {item['subject']} | 작성자: {item['author']} | 날짜: {item['date']}")
            
            if is_admin:
                with cols[1]:
                    if st.button("고정/해제", key=f"pin_sch_{item['id']}"):
                        item["pinned"] = not item.get("pinned", False)
                        save_data(data)
                        st.rerun()
                    if st.button("삭제 🗑️", key=f"del_sch_{item['id']}"):
                        data["schedules"] = [i for i in data["schedules"] if i["id"] != item["id"]]
                        save_data(data)
                        st.rerun()

# -------------------------------------------------------------------
# TAB 3: 선택과목 안내
# -------------------------------------------------------------------
with tab_subject:
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["🧪 화학 I", "🌍 사회·문화", "🏮 일본어 I", "💻 프로그래밍"])
    
    sub_mapping = {
        "🧪 화학 I": "subject_chem",
        "🌍 사회·문화": "subject_soc",
        "🏮 일본어 I": "subject_jp",
        "💻 프로그래밍": "subject_code"
    }

    for tab_obj, (sub_title, sub_key) in zip([sub_tab1, sub_tab2, sub_tab3, sub_tab4], sub_mapping.items()):
        with tab_obj:
            st.subheader(f"{sub_title} 공지사항")
            
            with st.expander("+ 공지 작성하기"):
                with st.form(f"form_{sub_key}"):
                    t = st.text_input("제목")
                    c = st.text_area("내용")
                    a = st.text_input("작성자", "익명")
                    sub_btn = st.form_submit_button("등록")
                    if sub_btn and t:
                        data[sub_key].append({
                            "id": int(datetime.now().timestamp() * 1000),
                            "title": t, "content": c, "author": a,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "pinned": False
                        })
                        save_data(data)
                        st.rerun()

            posts = sorted(data[sub_key], key=lambda x: (not x.get("pinned", False), x.get("id", 0)), reverse=True)
            for item in posts:
                with st.container(border=True):
                    cols = st.columns([4, 1])
                    with cols[0]:
                        pin_mark = "📌 " if item.get("pinned") else ""
                        st.markdown(f"#### {pin_mark}{item['title']}")
                        st.write(item["content"])
                        st.caption(f"작성자: {item['author']} | 날짜: {item['date']}")
                    if is_admin:
                        with cols[1]:
                            if st.button("고정/해제", key=f"pin_{sub_key}_{item['id']}"):
                                item["pinned"] = not item.get("pinned", False)
                                save_data(data)
                                st.rerun()
                            if st.button("삭제 🗑️", key=f"del_{sub_key}_{item['id']}"):
                                data[sub_key] = [i for i in data[sub_key] if i["id"] != item["id"]]
                                save_data(data)
                                st.rerun()

# -------------------------------------------------------------------
# TAB 4: 급식 / 생일
# -------------------------------------------------------------------
with tab_meal:
    st.subheader("🍱 이번 주 급식표")
    st.table({
        "요일": ["월요일", "화요일", "수요일", "목요일", "금요일"],
        "메뉴": [
            "치킨마요덮밥 · 팽이버섯장국 · 떡볶이",
            "발아현미밥 · 돈육김치찌개 · 수제치즈돈까스",
            "짜장밥 · 계란파국 · 탕수육 · 샐러드",
            "비빔밥 · 콩나물국 · LA갈비구이",
            "해물칼국수 · 미니주먹밥 · 겉절이"
        ]
    })

# -------------------------------------------------------------------
# TAB 5: 사진첩
# -------------------------------------------------------------------
with tab_gallery:
    st.subheader("📸 학급 활동 기록")
    with st.expander("+ 사진/기록 올리기"):
        with st.form("add_gallery"):
            gt = st.text_input("제목")
            gd = st.text_area("설명")
            g_btn = st.form_submit_button("등록")
            if g_btn and gt:
                data["gallery"].append({
                    "id": int(datetime.now().timestamp() * 1000),
                    "title": gt, "desc": gd,
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                save_data(data)
                st.rerun()

    for item in reversed(data["gallery"]):
        with st.container(border=True):
            st.markdown(f"#### 🖼️ {item['title']}")
            st.write(item["desc"])
            st.caption(f"등록일: {item['date']}")
            if is_admin:
                if st.button("삭제 🗑️", key=f"del_gal_{item['id']}"):
                    data["gallery"] = [i for i in data["gallery"] if i["id"] != item["id"]]
                    save_data(data)
                    st.rerun()

# -------------------------------------------------------------------
# TAB 6: 익명 건의함
# -------------------------------------------------------------------
with tab_board:
    st.subheader("📮 익명 건의함")
    with st.expander("+ 건의글 작성하기"):
        with st.form("add_board"):
            bt = st.text_input("제목")
            bc = st.text_area("내용")
            ba = st.text_input("작성자 (익명 가능)", "익명")
            b_btn = st.form_submit_button("제출")
            if b_btn and bt:
                data["board"].append({
                    "id": int(datetime.now().timestamp() * 1000),
                    "title": bt, "content": bc, "author": ba,
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                save_data(data)
                st.rerun()

    for item in reversed(data["board"]):
        with st.container(border=True):
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f"#### {item['title']}")
                st.write(item["content"])
                st.caption(f"작성자: {item['author']} | 날짜: {item['date']}")
            if is_admin:
                with cols[1]:
                    if st.button("삭제 🗑️", key=f"del_brd_{item['id']}"):
                        data["board"] = [i for i in data["board"] if i["id"] != item["id"]]
                        save_data(data)
                        st.rerun()