import streamlit as st
import datetime
import os
from fpdf import FPDF

# 로그인 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# 로그인 화면
if not st.session_state.logged_in:
    st.title("🔐 Toolbox Talk 로그인")
    username = st.text_input("이름")
    role = st.radio("역할", ["관리자", "팀원"])
    if st.button("입장") and username:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = role
    else:
        st.stop()  # 로그인 완료되기 전까지만 멈춤

# 이후: 회의록 본문
user = st.session_state.username
is_admin = st.session_state.role == "관리자"

if "attendees" not in st.session_state:
    st.session_state.attendees = []
if "confirmations" not in st.session_state:
    st.session_state.confirmations = []
if "discussion" not in st.session_state:
    st.session_state.discussion = [("", "") for _ in range(3)]
if "tasks" not in st.session_state:
    st.session_state.tasks = [("", "", datetime.date.today()) for _ in range(3)]

if user not in st.session_state.attendees:
    st.session_state.attendees.append(user)

st.title("📋 Toolbox Talk 회의록 서식")

# 회의 정보
st.header("1️⃣ 회의 정보")
today = datetime.date.today()
now = datetime.datetime.now().strftime("%H:%M")

col1, col2 = st.columns(2)
with col1:
    date = st.date_input("날짜", today)
    place = st.text_input("장소", "현장 A")
with col2:
    time = st.text_input("시간", now)
    task = st.text_input("작업 내용", "고소작업")

# 참석자
st.header("2️⃣ 참석자 명단")
for name in st.session_state.attendees:
    st.markdown(f"- {name}")

# 논의 내용
st.header("3️⃣ 논의 내용 (위험요소 & 안전대책)")
if is_admin:
    for i in range(len(st.session_state.discussion)):
        r, m = st.session_state.discussion[i]
        st.session_state.discussion[i] = (
            st.text_input(f"위험요소 {i+1}", value=r, key=f"risk_{i}"),
            st.text_input(f"안전대책 {i+1}", value=m, key=f"measure_{i}")
        )
else:
    for i, (r, m) in enumerate(st.session_state.discussion):
        st.markdown(f"**{i+1}. 위험요소:** {r}  \\n➡️ **안전대책:** {m}")

# 추가 논의
st.header("4️⃣ 추가 논의 사항")
if is_admin:
    additional = st.text_area("추가 사항", "")
else:
    additional = ""

# 결정사항 및 조치
st.header("5️⃣ 결정사항 및 조치")
if is_admin:
    for i in range(len(st.session_state.tasks)):
        p, r, d = st.session_state.tasks[i]
        cols = st.columns([3, 4, 3])
        st.session_state.tasks[i] = (
            cols[0].text_input(f"담당자 {i+1}", value=p, key=f"t_person_{i}"),
            cols[1].text_input(f"업무/역할 {i+1}", value=r, key=f"t_role_{i}"),
            cols[2].date_input(f"완료 예정일 {i+1}", value=d, key=f"t_due_{i}")
        )
else:
    for p, r, d in st.session_state.tasks:
        st.markdown(f"- **{p}**: {r} (완료일: {d})")

# 회의록 확인
st.header("6️⃣ 회의록 확인 및 서명")
if user not in st.session_state.confirmations:
    if st.button("📥 회의 내용 확인"):
        st.session_state.confirmations.append(user)
        st.success(f"{user}님의 확인이 저장되었습니다.")
else:
    st.success(f"{user}님은 이미 확인하셨습니다.")

# PDF 저장
if is_admin:
    if st.button("📄 회의록 PDF 저장"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"📋 Toolbox Talk 회의록\n\n일시: {date} {time}\n장소: {place}\n작업내용: {task}\n\n리더: {user}")
        pdf.multi_cell(0, 10, f"\n참석자: {', '.join(st.session_state.attendees)}")
        pdf.multi_cell(0, 10, "\n🧠 논의 내용")
        for idx, (r, m) in enumerate(st.session_state.discussion):
            pdf.multi_cell(0, 10, f"{idx+1}. 위험요소: {r} / 안전대책: {m}")
        pdf.multi_cell(0, 10, f"\n➕ 추가 논의 사항:\n{additional}")
        pdf.multi_cell(0, 10, "\n✅ 결정사항 및 조치")
        for p, r, d in st.session_state.tasks:
            pdf.multi_cell(0, 10, f"- {p}: {r} (완료 예정일: {d})")
        pdf.multi_cell(0, 10, "\n✍ 확인자 목록")
        for n in st.session_state.confirmations:
            pdf.multi_cell(0, 10, f"- {n} (확인 완료)")

        filename = f"회의록_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        pdf.output(filename)
        with open(filename, "rb") as f:
            st.download_button("📥 PDF 다운로드", f, file_name=filename)
        os.remove(filename)