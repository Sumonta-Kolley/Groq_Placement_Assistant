import streamlit as st
from assistant import ask_navigator, get_saved_drafts
from data import OPPORTUNITIES

st.set_page_config(
    page_title="Campus Opportunity Navigator",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Campus Opportunity Navigator")
st.caption(
    "Discover internships, check eligibility, estimate stipend, "
    "and prepare application drafts."
)

with st.sidebar:
    st.header("Student profile")
    student_name = st.text_input("Full name")
    student_email = st.text_input("Email address")
    student_year = st.selectbox(
        "Current academic year",
        [1, 2, 3, 4],
        index=2,
    )
    student_skills = st.text_area(
        "Skills (comma separated)",
        "python, sql, pandas, prompt engineering",
    )
    preferred_location = st.selectbox(
        "Preferred location",
        ["Any", "Kolkata", "India"],
    )

    st.divider()
    st.subheader("Try asking")
    st.write("Find internships for Python and SQL.")
    st.write("Check whether I qualify for INT102.")
    st.write("Estimate the stipend for INT103.")
    st.write("Save a draft for INT101.")

tab_chat, tab_catalogue, tab_drafts = st.tabs(
    ["AI Assistant", "Opportunity Catalogue", "Saved Drafts"]
)

if "chat" not in st.session_state:
    st.session_state.chat = []

with tab_chat:
    st.subheader("Talk to the placement assistant")

    for item in st.session_state.chat:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

    question = st.chat_input(
        "Ask about internships, eligibility, stipend, or drafts..."
    )

    if question:
        profile_context = (
            f"Student profile: name={student_name or 'Not provided'}, "
            f"email={student_email or 'Not provided'}, year={student_year}, "
            f"skills={student_skills}, location={preferred_location}. "
            f"Student request: {question}"
        )

        st.session_state.chat.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Using opportunity tools..."):
                answer = ask_navigator(profile_context)
            st.markdown(answer)

        st.session_state.chat.append({"role": "assistant", "content": str(answer)})

with tab_catalogue:
    st.subheader("Sample internship listings")
    for item in OPPORTUNITIES:
        with st.expander(f'{item["id"]} | {item["role"]} — {item["company"]}'):
            st.write("Skills:", ", ".join(item["skills"]))
            st.write("Minimum year:", item["min_year"])
            st.write("Duration:", item["duration_months"], "months")
            st.write(
                "Monthly stipend:",
                f'₹{item["stipend_min"]:,} - ₹{item["stipend_max"]:,}',
            )
            st.write("Mode:", item["mode"])
            st.write("Location:", item["location"])

with tab_drafts:
    st.subheader("Application drafts")
    st.warning(
        "Drafts are saved locally for human review. They are NOT submitted applications."
    )
    if st.button("Refresh saved drafts"):
        st.rerun()

    drafts = get_saved_drafts()
    if drafts:
        st.dataframe(drafts, use_container_width=True)
    else:
        st.info("No application drafts saved yet.")