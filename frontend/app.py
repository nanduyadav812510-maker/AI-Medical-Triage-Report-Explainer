import streamlit as st
import requests
import json
import os
from datetime import datetime

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Common Symptoms for Quick Selection
COMMON_SYMPTOMS = [
    "High fever and body aches",
    "Persistent cough and sore throat",
    "Headache and dizziness",
    "Chest pain or pressure",
    "Shortness of breath",
    "Nausea and vomiting",
    "Abdominal pain",
    "Rash or skin irritation",
    "Joint pain and swelling",
    "Fatigue and weakness",
]

# Page Configuration
st.set_page_config(
    page_title="AI Medical Triage & Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for dark mode
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Custom Styling with Dark Mode Support
def get_css_styles():
    if st.session_state.dark_mode:
        bg_color = "#0e1117"
        text_color = "#c9d1d9"
        header_color = "#58a6ff"
        card_bg = "#161b22"
    else:
        bg_color = "#ffffff"
        text_color = "#333333"
        header_color = "#0F52BA"
        card_bg = "#f0f2f6"
    
    return f"""
    <style>
        :root {{
            --bg-color: {bg_color};
            --text-color: {text_color};
            --header-color: {header_color};
            --card-bg: {card_bg};
        }}
        
        .main-header {{
            font-size: 2.2rem;
            font-weight: 700;
            color: {header_color};
            margin-bottom: 0.2rem;
        }}
        .sub-header {{
            font-size: 1.1rem;
            color: {text_color};
            margin-bottom: 1.5rem;
        }}
        .badge-emergency {{
            background-color: #DC3545;
            color: white;
            padding: 8px 16px;
            border-radius: 16px;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
        }}
        .badge-urgent {{
            background-color: #FD7E14;
            color: white;
            padding: 8px 16px;
            border-radius: 16px;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
        }}
        .badge-routine {{
            background-color: #0D6EFD;
            color: white;
            padding: 8px 16px;
            border-radius: 16px;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
        }}
        .badge-selfcare {{
            background-color: #198754;
            color: white;
            padding: 8px 16px;
            border-radius: 16px;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
        }}
        .disclaimer-box {{
            background-color: #FFF8E7;
            border-left: 5px solid #FFC107;
            padding: 12px 16px;
            border-radius: 4px;
            font-size: 0.88rem;
            color: #856404;
            margin-top: 1rem;
        }}
        .stats-card {{
            background-color: {card_bg};
            padding: 16px;
            border-radius: 8px;
            margin: 8px 0;
        }}
        .symptom-pill {{
            background-color: {header_color};
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin: 4px 4px 4px 0;
            display: inline-block;
            cursor: pointer;
        }}
    </style>
    """

st.markdown(get_css_styles(), unsafe_allow_html=True)

# Enhanced Sidebar Setup
with st.sidebar:
    st.image("https://img.icons8.com/color/96/medical-heart.png", width=70)
    st.title("Navigation & Settings")
    
    st.markdown("---")
    
    # User Profile Section
    st.subheader("User Profile")
    user_id = st.text_input("Your User ID", value=st.session_state.user_id or "", key="user_id_input", placeholder="e.g., user123")
    if user_id:
        st.session_state.user_id = user_id
    
    # Language Selection
    language = st.selectbox(
        "Preferred Language",
        ["English", "Hindi", "Telugu", "Tamil", "Kannada", "Spanish", "French"]
    )
    
    # Dark Mode Toggle
    st.markdown("---")
    col_theme = st.columns([1, 1])
    with col_theme[0]:
        st.write("**Theme:**")
    with col_theme[1]:
        if st.button("🌙" if not st.session_state.dark_mode else "☀️", help="Toggle Dark Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    st.markdown("---")
    st.subheader("Quick Links")
    
    if st.button("📊 View Analytics", use_container_width=True):
        st.session_state.page = "analytics"
    
    if st.session_state.user_id:
        if st.button("📜 View My History", use_container_width=True):
            st.session_state.page = "history"
    
    st.markdown("---")
    st.subheader("System Status")
    try:
        res = requests.get(f"{BACKEND_URL}/api/health", timeout=3)
        if res.status_code == 200 and res.json().get("ollama_connected"):
            st.success("🟢 Ollama (Gemma 3:1B) Connected")
        else:
            st.warning("🟡 Backend Running (Ollama Model Offline)")
    except Exception:
        st.error("🔴 Backend API Offline (Start main.py)")
        
    st.markdown("---")
    st.caption("AI Medical Triage v2.0 • Enhanced Features • Powered by Gemma 3:1B & FastAPI")


# Main Content Area
if "page" not in st.session_state:
    st.session_state.page = "home"

# Page Router
if st.session_state.page == "analytics":
    st.markdown('<div class="main-header">📊 Application Analytics</div>', unsafe_allow_html=True)
    
    try:
        stats_res = requests.get(f"{BACKEND_URL}/api/triage/statistics", timeout=5)
        if stats_res.status_code == 200:
            stats = stats_res.json()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Assessments", stats.get("total_assessments", 0))
            with col2:
                st.metric("Total Users", stats.get("total_users", 0))
            with col3:
                st.metric("Emergency Cases", stats.get("urgency_breakdown", {}).get("EMERGENCY", 0))
            with col4:
                st.metric("Last Assessment", stats.get("last_assessment", "N/A")[:10] if stats.get("last_assessment") else "N/A")
            
            st.markdown("---")
            st.subheader("Urgency Distribution")
            
            urgency_data = stats.get("urgency_breakdown", {})
            if urgency_data:
                import pandas as pd
                df = pd.DataFrame({
                    "Category": ["Emergency", "Urgent", "Routine", "Self-Care"],
                    "Count": [
                        urgency_data.get("EMERGENCY", 0),
                        urgency_data.get("URGENT", 0),
                        urgency_data.get("ROUTINE", 0),
                        urgency_data.get("SELF_CARE", 0)
                    ]
                })
                st.bar_chart(df.set_index("Category"))
    except Exception as e:
        st.error(f"Failed to load analytics: {e}")
    
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

elif st.session_state.page == "history" and st.session_state.user_id:
    st.markdown('<div class="main-header">📜 Assessment History</div>', unsafe_allow_html=True)
    
    try:
        hist_res = requests.get(f"{BACKEND_URL}/api/triage/history/{st.session_state.user_id}", timeout=5)
        if hist_res.status_code == 200:
            history_data = hist_res.json()
            assessments = history_data.get("assessments", [])
            
            if assessments:
                st.write(f"Found **{len(assessments)}** assessments")
                
                for assessment in reversed(assessments):
                    with st.expander(f"📋 {assessment.get('timestamp', 'N/A')[:10]} - {assessment.get('urgency_level', 'UNKNOWN')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Age:** {assessment.get('age')}")
                            st.write(f"**Gender:** {assessment.get('gender')}")
                            st.write(f"**Duration:** {assessment.get('duration')}")
                        with col2:
                            st.write(f"**Severity:** {assessment.get('severity_score')}/10")
                            st.write(f"**Urgency:** {assessment.get('urgency_level')}")
                            st.write(f"**Recommended:** {assessment.get('recommended_action')[:50]}...")
                        
                        st.markdown("**Symptoms:**")
                        st.write(assessment.get('symptoms'))
                        
                        # Export button
                        if st.button(f"📥 Export PDF", key=f"export_{assessment.get('id')}"):
                            try:
                                pdf_res = requests.get(
                                    f"{BACKEND_URL}/api/triage/export/{st.session_state.user_id}/{assessment.get('id')}",
                                    timeout=10
                                )
                                if pdf_res.status_code == 200:
                                    st.download_button(
                                        label="Download PDF",
                                        data=pdf_res.content,
                                        file_name=f"triage_{assessment.get('id')[:8]}.pdf",
                                        mime="application/pdf"
                                    )
                            except Exception as e:
                                st.error(f"Export failed: {e}")
            else:
                st.info("No assessments found for this user ID.")
    except Exception as e:
        st.error(f"Failed to load history: {e}")
    
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

else:
    # App Title Header
    st.markdown('<div class="main-header">🩺 AI Medical Triage & Report Explainer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Local, private, safety-first symptom assessment and PDF lab report analyzer.</div>', unsafe_allow_html=True)

    # Main Navigation Tabs
    tab_triage, tab_report, tab_chat = st.tabs([
        "🩺 Symptom Triage", 
        "📄 Medical Report Explainer", 
        "💬 Health Assistant Chat"
    ])


    # ==========================================
    # TAB 1: SYMPTOM TRIAGE - ENHANCED
    # ==========================================
    with tab_triage:
        st.subheader("Symptom & Patient Details")
        st.write("Fill in patient symptoms to receive an immediate urgency rating and actionable guidance.")

        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Patient Age", min_value=0, max_value=120, value=30, key="triage_age")
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"], key="triage_gender")
            duration = st.text_input("Symptom Duration", value="2 days", help="e.g. 3 hours, 2 days, 1 week", key="triage_duration")

        with col2:
            severity_score = st.slider("Severity Level (1 = Very Mild, 10 = Severe Pain)", 1, 10, 5, key="triage_severity")
            existing_conditions = st.text_input("Pre-existing Medical Conditions", value="None", help="e.g. Asthma, Diabetes, Hypertension", key="triage_conditions")

        # Quick Symptom Suggestions
        st.write("**Quick Symptom Selection (optional):**")
        cols = st.columns(3)
        selected_symptom = None
        for i, symptom in enumerate(COMMON_SYMPTOMS[:9]):
            if cols[i % 3].button(symptom, use_container_width=True, key=f"symptom_{i}"):
                selected_symptom = symptom
        
        symptoms = st.text_area(
            "Describe Symptoms in Detail", 
            height=120,
            value=selected_symptom or "",
            placeholder="e.g., I have had a high fever (101°F), persistent cough, and body aches for two days.",
            key="triage_symptoms"
        )

        col_submit_1, col_submit_2 = st.columns([2, 1])
        with col_submit_1:
            submit_triage = st.button("Submit Symptom Triage Assessment", type="primary", use_container_width=True, key="submit_triage_btn")
        
        if submit_triage:
            if not symptoms.strip():
                st.warning("Please enter a description of your symptoms.")
            else:
                with st.spinner("Analyzing symptoms with local Gemma model and checking red flags..."):
                    try:
                        payload = {
                            "age": age,
                            "gender": gender,
                            "symptoms": symptoms,
                            "duration": duration,
                            "severity_score": severity_score,
                            "existing_conditions": existing_conditions,
                            "language": language,
                            "user_id": st.session_state.user_id
                        }
                        response = requests.post(f"{BACKEND_URL}/api/triage/assess", json=payload, timeout=60)
                        
                        if response.status_code == 200:
                            data = response.json()
                            urgency = data.get("urgency_level", "ROUTINE")

                            st.markdown("---")
                            st.subheader("Triage Assessment Results")

                            # Display Urgency Badge
                            if urgency == "EMERGENCY":
                                st.markdown('<span class="badge-emergency">🚨 EMERGENCY - IMMEDIATE CARE REQUIRED</span>', unsafe_allow_html=True)
                                st.error("⚠️ CRITICAL WARNING: Red flag symptoms detected! Seek emergency care (Call 911 or visit ER) immediately.")
                            elif urgency == "URGENT":
                                st.markdown('<span class="badge-urgent">⚠️ URGENT - SEE DOCTOR WITHIN 24-48 HOURS</span>', unsafe_allow_html=True)
                            elif urgency == "ROUTINE":
                                st.markdown('<span class="badge-routine">ℹ️ ROUTINE - SCHEDULE APPOINTMENT</span>', unsafe_allow_html=True)
                            else:
                                st.markdown('<span class="badge-selfcare">✅ SELF CARE - MONITOR AT HOME</span>', unsafe_allow_html=True)

                            st.write(f"**Recommended Action:** {data.get('recommended_action')}")

                            if data.get("red_flags_detected"):
                                st.warning(f"**Red Flags Detected:** {', '.join(data.get('red_flags_detected'))}")

                            st.markdown("### Clinical Explanation")
                            st.write(data.get("summary"))

                            st.markdown("### Questions to Ask Your Doctor")
                            for q in data.get("questions_for_doctor", []):
                                st.markdown(f"- {q}")

                            st.markdown(f'<div class="disclaimer-box"><strong>Disclaimer:</strong> {data.get("disclaimer")}</div>', unsafe_allow_html=True)
                            
                            # Export button
                            if st.button("📥 Export as PDF", key="export_result_pdf"):
                                st.info("Assessment saved to your history. Use the History tab to export.")

                        else:
                            st.error(f"Error from API: {response.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}. Ensure backend is running at {BACKEND_URL}.")


    # ==========================================
    # TAB 2: MEDICAL REPORT EXPLAINER
    # ==========================================
    with tab_report:
        st.subheader("Upload & Explain Medical PDF Reports")
        st.write("Upload blood test results, lab reports, or diagnostic summaries for clear plain-English explanation.")

        uploaded_file = st.file_uploader("Choose a PDF medical report", type=["pdf"], key="pdf_uploader")

        if uploaded_file is not None:
            if st.button("Process & Explain PDF Report", type="primary", key="process_pdf_btn"):
                with st.spinner("Extracting PDF text and generating patient-friendly explanation..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        upload_res = requests.post(f"{BACKEND_URL}/api/reports/upload", files=files, timeout=30)

                        if upload_res.status_code == 200:
                            upload_data = upload_res.json()
                            extracted_text = upload_data.get("extracted_text", "")

                            st.success(f"Successfully extracted text from {uploaded_file.name} ({upload_data.get('total_pages')} pages).")

                            # Analyze extracted text
                            analyze_payload = {
                                "report_text": extracted_text,
                                "language": language
                            }
                            analyze_res = requests.post(f"{BACKEND_URL}/api/reports/analyze", json=analyze_payload, timeout=90)

                            if analyze_res.status_code == 200:
                                report_data = analyze_res.json()

                                st.markdown("### Executive Plain-Language Summary")
                                st.info(report_data.get("summary"))

                                if report_data.get("abnormal_values"):
                                    st.markdown("### ⚠️ Highlighted Out-of-Range / Abnormal Values")
                                    for val in report_data.get("abnormal_values"):
                                        st.warning(f"- {val}")

                                st.markdown("### 💡 Medical Jargon Explained")
                                terms = report_data.get("simplified_terms", {})
                                for term, expl in terms.items():
                                    st.markdown(f"**{term}**: {expl}")

                                st.markdown("### 📋 Suggested Next Steps")
                                for step in report_data.get("next_steps", []):
                                    st.markdown(f"- {step}")

                                st.markdown(f'<div class="disclaimer-box"><strong>Disclaimer:</strong> {report_data.get("disclaimer")}</div>', unsafe_allow_html=True)
                            else:
                                st.error(f"Analysis failed: {analyze_res.text}")
                        else:
                            st.error(f"Upload failed: {upload_res.text}")
                    except Exception as e:
                        st.error(f"Report processing error: {e}")


    # ==========================================
    # TAB 3: HEALTH ASSISTANT CHAT
    # ==========================================
    with tab_chat:
        st.subheader("Interactive Health Q&A Assistant")
        st.write("Ask general wellness questions, understand medical terms, or inquire about healthcare guidance.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hello! I am your AI Health Assistant. How can I help you understand health concepts or terms today?"}
            ]

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input("Ask a health or medical term question...", key="chat_input")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        payload = {
                            "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history],
                            "language": language
                        }
                        res = requests.post(f"{BACKEND_URL}/api/chat/query", json=payload, timeout=60)
                        if res.status_code == 200:
                            ans_data = res.json()
                            reply = ans_data.get("response")
                            st.write(reply)
                            st.session_state.chat_history.append({"role": "assistant", "content": reply})
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Chat connection error: {e}")
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I am your AI Health Assistant. How can I help you understand health concepts or terms today?"}
        ]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask a health or medical term question...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    payload = {
                        "messages": st.session_state.chat_history,
                        "language": language
                    }
                    res = requests.post(f"{BACKEND_URL}/api/chat/query", json=payload, timeout=60)
                    if res.status_code == 200:
                        ans_data = res.json()
                        reply = ans_data.get("response")
                        st.write(reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Chat connection error: {e}")
