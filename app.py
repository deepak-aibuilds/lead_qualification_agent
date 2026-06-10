import streamlit as st
import httpx
import time

API_URL = "http://localhost:8000"

st.title("AI Lead Qualification Agent")
st.caption("Submit a lead and get an AI-generated score and follow-up email.")

with st.form("lead_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    company = st.text_input("Company")
    required_service = st.text_area("What service do you need?")
    budget = st.text_input("Budget (e.g. 5000)")
    submitted = st.form_submit_button("Submit Lead")

if submitted:
    with st.spinner("Submitting lead..."):
        try:
            response = httpx.post(f"{API_URL}/leads", data={
                "name": name,
                "email": email,
                "company": company,
                "required_service": required_service,
                "budget": budget,
            })
            data = response.json()
            lead_id = data.get("id")
        except Exception as e:
            st.error(f"Failed to submit lead: {e}")
            st.stop()

    st.info(f"Lead submitted. ID: {lead_id} — waiting for qualification...")

    with st.spinner("Processing..."):
        for _ in range(20):
            time.sleep(3)
            try:
                poll = httpx.get(f"{API_URL}/leads/{lead_id}")
 
                result = poll.json()
                if result.get("lead_status") == "scored":
                    break
            except Exception:
                pass

    if result.get("lead_status") == "scored":
        score = result.get("lead_score")
        qualification = result.get("lead_qualification", "").upper()

        color = {"QUALIFIED": "green", "NURTURE": "orange", "DISQUALIFIED": "red"}.get(qualification, "gray")

        st.markdown(f"### Result")
        st.markdown(f"**Score:** {score}/100")
        st.markdown(f"**Qualification:** :{color}[{qualification}]")

        st.markdown("---")
        st.markdown("### Follow-up Email")
        st.markdown(f"**Subject:** {result.get('email_subject')}")
        st.text_area("Email Body", value=result.get("email_body", ""), height=200)
    else:
        st.warning("Processing took too long. Check back via GET /leads/" + str(lead_id))