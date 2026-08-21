import streamlit as st
import json
import os
from datetime import datetime

# -------------------------------------------------------------------
# 1. 기본 설정 및 데이터베이스(JSON) 연동
# -------------------------------------------------------------------
st.set_page_config(page_title="11학년 2반 학급 웹사이트", page_icon="🏫", layout="wide")

DATA_FILE = "class_data.json"
ADMIN_PASSWORD = "1120"  # [수정 5] 선생님 관리자 비밀번호 변경

# [수정 1] 선택과목 목록 정의
SUBJECTS = [
    "International Business", "Introduction to Biology", "Introduction to Chemistry",
    "Practical Academic Reading", "Practical English Grammar", "미적분II",
    "세포와 물질대사", "현대사회와 윤리", "확률과 통계", "물리학 실험",
    "미디어와 비판적사고", "주제 탐구 독서", "미술 전공 실기 응용", "세계 시민과 지리",
    "소프트웨어와 생활", "화학 실험", "삶과 글쓰기", "물질과 에너지",
    "실용 베트남어", "정치", "경제"
]

default_data = {
    "schedules": [],
    "board": [],
    "gallery": [],
    "subject_posts": {}  # 과목별 데이터 통합 저장
}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if "subject_posts" not in data:
            data["subject_posts"] = {}
        return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

# -------------------------------------------------------------------
# 2. 사이드바 (관리자 모드 접속)
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
        st.sidebar.error("비밀번호가 올바르지 않습니다.")

st.sidebar.divider()
st.sidebar.info("💡 모든 게시글 및 일정 데이터는 서버에 자동 저장됩니다.")

# -------------------------------------------------------------------
# 3. 메인 화면 및 탭 구성
# -------------------------------------------------------------------
st.title("✨ 11학년 2반 학급 공간")

# [수정 4] '주요 일정' -> '공통 일정'으로 명칭 변경
tab_home, tab_schedule, tab_subject, tab_meal, tab_gallery, tab_board = st.tabs([
    "🏠 대시보드", "📅 공통 일정", "📚 선택과목", "🍱 급식/생일", "📸 사진첩", "📮 익명 건의함"
])

# -------------------------------------------------------------------
# TAB 1: 대시보드
# -------------------------------------------------------------------
with tab_home:
    col1, col2 = st.columns(2)
    
    with col1:
        # [수정 4] 명칭 변경
        st.subheader("📅 최근 공통 일정")
        schedules = sorted(data["schedules"], key=lambda x: (not x.get("pinned", False), x.get("id", 0)), reverse=True)
        if schedules:
            for s in schedules[:3]:
                pin = "📌 " if s.get("pinned") else ""
                st.write(f"- {pin}**[{s.get('subject', '공통')}]** {s.get('title')} (`{s.get('date')}`)")
        else:
            st.caption("등록된 일정이 없습니다.")

        # [수정 3] 급식 메뉴 변경
        st.subheader("🍱 오늘의 급식")
        st.info("흑미밥 · 열무된장국 · 삼겹살구이 · 콩나물파채무침 · 볶음김치 · 상추쌈(추가배식대) · 수박")

    with col2:
        # [수정 2] 생일 정보 변경
        st.subheader("🎂 학급 생일 안내")
        st.caption("이번 달(8월) 생일자는 없습니다.")
        st.success("🎉 **지난 달(7월) 생일자**\n- 7월 15일: 구소명\n- 7월 27일: 김재영")

        st.subheader("📢 선택과목 최신 공지")
        has_post = False
        for sub in SUBJECTS:
            posts = data["subject_posts"].get(sub, [])
            if posts:
                st.text(f"• [{sub}] {posts[-1]['title']}")
                has_post = True
        if not has_post:
            st.caption("등록된 선택과목 공지가 없습니다.")

# -------------------------------------------------------------------
# TAB 2: 공통 일정 [수정 4]
# -------------------------------------------------------------------
with tab_schedule:
    st.subheader("📅 전체 공통 일정")
    
    with st.expander("+ 새 공통 일정 등록하기"):
        with st.form("add_schedule"):
            sub = st.text_input("구분 (예: 학급행사, 시험, 동아리)", "공통")
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
                st.success("일정이 등록되었습니다!")
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
# TAB 3: 선택과목 안내 [수정 1]
# -------------------------------------------------------------------
with tab_subject:
    st.subheader("📚 선택과목 게시판")
    selected_subject = st.selectbox("조회/작성할 과목을 선택하세요:", SUBJECTS)
    
    st.divider()
    st.markdown(f"### 📖 {selected_subject} 공지사항")
    
    with st.expander(f"+ [{selected_subject}] 공지 작성하기"):
        with st.form(f"form_{selected_subject}"):
            t = st.text_input("제목")
            c = st.text_area("내용")
            a = st.text_input("작성자", "익명")
            sub_btn = st.form_submit_button("등록")
            if sub_btn and t:
                if selected_subject not in data["subject_posts"]:
                    data["subject_posts"][selected_subject] = []
                data["subject_posts"][selected_subject].append({
                    "id": int(datetime.now().timestamp() * 1000),
                    "title": t, "content": c, "author": a,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "pinned": False
                })
                save_data(data)
                st.success("공지가 등록되었습니다.")
                st.rerun()

    posts = data["subject_posts"].get(selected_subject, [])
    posts_sorted = sorted(posts, key=lambda x: (not x.get("pinned", False), x.get("id", 0)), reverse=True)
    
    if posts_sorted:
        for item in posts_sorted:
            with st.container(border=True):
                cols = st.columns([4, 1])
                with cols[0]:
                    pin_mark = "📌 " if item.get("pinned") else ""
                    st.markdown(f"#### {pin_mark}{item['title']}")
                    st.write(item["content"])
                    st.caption(f"작성자: {item['author']} | 날짜: {item['date']}")
                if is_admin:
                    with cols[1]:
                        if st.button("고정/해제", key=f"pin_sub_{item['id']}"):
                            item["pinned"] = not item.get("pinned", False)
                            save_data(data)
                            st.rerun()
                        if st.button("삭제 🗑️", key=f"del_sub_{item['id']}"):
                            data["subject_posts"][selected_subject] = [i for i in data["subject_posts"][selected_subject] if i["id"] != item["id"]]
                            save_data(data)
                            st.rerun()
    else:
        st.info("등록된 공지가 없습니다.")

# -------------------------------------------------------------------
# TAB 4: 급식 / 생일 [수정 2, 3]
# -------------------------------------------------------------------
with tab_meal:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🍱 오늘의 급식")
        st.info("🍚 **흑미밥**\n\n🥣 **열무된장국**\n\n🥩 **삼겹살구이**\n\n🥗 **콩나물파채무침**\n\n🥬 **볶음김치**\n\n🥬 **상추쌈 (추가배식대)**\n\n🍉 **수박**")
    
    with col_b:
        st.subheader("🎂 생일 안내")
        st.warning("📅 **8월 생일자**: 없음")
        st.success("🎉 **7월 생일자**\n- 7월 15일: **구소명**\n- 7월 27일: **김재영**")

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
