import streamlit as st
import pandas as pd
import ollama

from modules.career_chat import career_chat
from modules.parser import extract_text
from modules.skill_gap import (
    extract_skills,
    missing_skills
)

from modules.matcher import match_score
from modules.ai_feedback import get_feedback
from modules.career_recommender import recommend_roles

from modules.database_manager import (
    create_table,
    save_job_result,
    get_resume_history,
    clear_history
)

# Database Setup
create_table()

# Page Config
st.set_page_config(
    page_title="CareerMatch AI",
    page_icon="🎯",
    layout="wide"
)

# Custom Styling for Badges
def render_badges(skills, color="#2ecc71"):
    if not skills:
        return "<span style='color: gray; font-style: italic;'>None</span>"
    badge_html = ""
    for skill in skills:
        cap_skill = skill.title()
        badge_html += f'<span style="display: inline-block; background-color: {color}; color: white; padding: 4px 10px; margin: 3px 3px 3px 0px; border-radius: 12px; font-size: 13px; font-weight: 500;">{cap_skill}</span>'
    return badge_html

# Header
st.title("🎯 CareerMatch AI")
st.subheader(
    "AI-Powered Job Discovery & Career Optimization Assistant"
)

# Sidebar - Configuration and Models
st.sidebar.title("⚙️ Configuration")

# Dynamic Model Loading
@st.cache_data(ttl=15)
@st.cache_data(ttl=15)
def fetch_ollama_models():
    try:
        models_data = ollama.list()

        st.sidebar.write("DEBUG:", models_data)

        model_list = []

        # Handle dictionary response
        if isinstance(models_data, dict):
            models = models_data.get("models", [])

        # Handle object response
        elif hasattr(models_data, "models"):
            models = models_data.models

        else:
            models = []

        for model in models:

            if isinstance(model, dict):
                name = model.get("name", "")

            elif hasattr(model, "name"):
                name = model.name

            elif hasattr(model, "model"):
                name = model.model

            else:
                name = str(model)

            if ":latest" in name:
                name = name.replace(":latest", "")

            if name:
                model_list.append(name)

        return sorted(list(set(model_list)))

    except Exception as e:
        st.sidebar.error(f"Ollama Error: {e}")
        return []
ollama_connected = False
available_models = fetch_ollama_models()

if available_models:
    ollama_connected = True
    st.sidebar.success("🟢 Connected to Ollama")
    options = available_models + ["Custom..."]
    
    # Try to find llama3 or llama3.2 as default if present
    default_idx = 0
    for idx, model in enumerate(options):
        if "llama" in model.lower():
            default_idx = idx
            break
            
    selected_option = st.sidebar.selectbox(
        "Select Ollama Model",
        options,
        index=default_idx
    )
    
    if selected_option == "Custom...":
        selected_model = st.sidebar.text_input("Enter model name (e.g. mistral):")
    else:
        selected_model = selected_option
else:
    st.sidebar.warning("⚠️ Cannot connect to Ollama.")
    st.sidebar.info("Please start the Ollama service on your local machine.")
    selected_model = st.sidebar.text_input("Enter model name manually:", value="llama3")

# Sidebar Upload Controls
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Document Upload")

resume_file = st.sidebar.file_uploader(
    "Upload Your Resume (PDF)",
    type=["pdf"]
)

jd_files = st.sidebar.file_uploader(
    "Upload Multiple Job Descriptions (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

# Initialize Active Page state
if "active_page" not in st.session_state:
    st.session_state.active_page = "📊 Dashboard"

# Reset chat session if files change
if "last_resume_name" not in st.session_state:
    st.session_state.last_resume_name = None

if resume_file and resume_file.name != st.session_state.last_resume_name:
    st.session_state.last_resume_name = resume_file.name
    # Clear chat messages and AI outputs for new uploads
    st.session_state.chat_messages = []
    # Clear general cache keys for recommendations and feedback
    for key in list(st.session_state.keys()):
        if key.startswith("feedback_") or key.startswith("recommendations_"):
            del st.session_state[key]
    # Reset view to dashboard
    st.session_state.active_page = "📊 Dashboard"

# Initialize Analysis Session State
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
    st.session_state.resume_skills = []
    st.session_state.resume_text = ""
    st.session_state.jobs_summary = ""

# Trigger analysis when uploads are present
if resume_file and jd_files:
    current_jd_names = sorted([jd.name for jd in jd_files])
    
    if (st.session_state.analysis_results is None or 
        st.session_state.get("last_processed_jds") != current_jd_names or
        st.session_state.get("last_processed_resume") != resume_file.name):
        
        with st.spinner("Extracting resume content..."):
            resume_text = extract_text(resume_file)
            resume_skills = extract_skills(resume_text)
            
        results = []
        with st.spinner("Processing job descriptions..."):
            for jd in jd_files:
                jd_text = extract_text(jd)
                jd_skills = extract_skills(jd_text)
                score = match_score(resume_text, jd_text)
                gaps = missing_skills(resume_skills, jd_skills)
                matching = list(set(resume_skills) & set(jd_skills))
                
                results.append({
                    "job_name": jd.name,
                    "score": float(score),
                    "matching_skills": matching,
                    "missing_skills": gaps,
                    "jd_text": jd_text,
                    "jd_skills": jd_skills
                })
                
        # Sort results by match score
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        
        # Save results to DB
        for job in results:
            save_job_result(resume_file.name, job["job_name"], float(job["score"]))
            
        # Update session state
        st.session_state.analysis_results = results
        st.session_state.resume_skills = resume_skills
        st.session_state.resume_text = resume_text
        st.session_state.last_processed_jds = current_jd_names
        st.session_state.last_processed_resume = resume_file.name
        
        # Build jobs summary for chat context
        jobs_summary = ""
        for job in results:
            jobs_summary += f"Job: {job['job_name']}\nMatch Score: {job['score']:.2f}%\nMissing Skills: {', '.join(job['missing_skills'])}\n--------------------------------\n"
        st.session_state.jobs_summary = jobs_summary

# Navigation Options
nav_options = [
    "📊 Dashboard",
    "🔍 Match Details & Feedback",
    "🎯 Career Recommendations",
    "💬 Career AI Chat",
    "📜 Analysis History"
]

# Set default page if not set
if "active_page" not in st.session_state:
    st.session_state.active_page = "📊 Dashboard"

# Main Application Area
if resume_file and jd_files and st.session_state.analysis_results is not None:
    results = st.session_state.analysis_results
    resume_skills = st.session_state.resume_skills
    resume_text = st.session_state.resume_text
    jobs_summary = st.session_state.jobs_summary
    
    # Render Horizontal Top Navigation Menu
    selected_page = st.radio(
        "Navigation",
        nav_options,
        index=nav_options.index(st.session_state.active_page),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.active_page = selected_page
    st.divider()
    
    # --- PAGE 1: Dashboard ---
    if st.session_state.active_page == "📊 Dashboard":
        st.markdown("### 📊 Analysis Overview")
        best_job = results[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Jobs Evaluated", len(results))
        with col2:
            st.metric("Best Match Job", best_job["job_name"])
        with col3:
            st.metric("Highest Match Score", f"{best_job['score']:.2f}%")
            
        st.divider()
        
        st.markdown("### 🏆 Job Match Leaderboard")
        df_data = []
        for idx, r in enumerate(results, start=1):
            score = r["score"]
            if score >= 75:
                level = "🟢 Strong Match"
            elif score >= 50:
                level = "🟡 Moderate Match"
            else:
                level = "🔴 Low Match"
            df_data.append({
                "Rank": idx,
                "Job Name": r["job_name"],
                "Match Score": f"{score:.2f}%",
                "Match Level": level,
                "Missing Skills Count": len(r["missing_skills"])
            })
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("### 🛠 Detected Resume Skills")
        st.markdown(render_badges(resume_skills, color="#3498db"), unsafe_allow_html=True)
        
        # Shortcut Jump Button
        st.write("")
        st.info("💡 **Want customized guidance on your skills?** Talk directly to our career advisor:")
        if st.button("💬 Talk to AI Advisor", key="btn_jump_dash"):
            st.session_state.active_page = "💬 Career AI Chat"
            st.rerun()
        
    # --- PAGE 2: Match Details & Feedback ---
    elif st.session_state.active_page == "🔍 Match Details & Feedback":
        st.markdown("### 🔍 Detailed Skill Matching & AI Feedback")
        
        selected_jd_name = st.selectbox(
            "Select Job Description to Analyze Details",
            [r["job_name"] for r in results]
        )
        
        # Get selected job details
        job_detail = next(r for r in results if r["job_name"] == selected_jd_name)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Match Score", f"{job_detail['score']:.2f}%")
            score = job_detail['score']
            st.progress(min(int(score), 100))
        with col2:
            with st.expander("📝 View Job Description Text"):
                st.write(job_detail["jd_text"])
                
        st.divider()
        
        col_skills1, col_skills2 = st.columns(2)
        with col_skills1:
            st.markdown("#### 🟢 Matching Skills")
            st.markdown(render_badges(job_detail["matching_skills"], color="#2ecc71"), unsafe_allow_html=True)
        with col_skills2:
            st.markdown("#### 🔴 Missing Skills")
            st.markdown(render_badges(job_detail["missing_skills"], color="#e74c3c"), unsafe_allow_html=True)
            
        st.divider()
        st.markdown("### 🤖 AI Resume Feedback")
        
        feedback_key = f"feedback_{selected_jd_name}_{selected_model}"
        if feedback_key not in st.session_state:
            st.session_state[feedback_key] = None
            
        if st.button("✨ Generate/Refresh AI Feedback", key=f"btn_{selected_jd_name}"):
            with st.spinner("Analyzing resume against job description using AI..."):
                feedback_text = get_feedback(
                    resume_text, 
                    job_detail["jd_text"], 
                    model_name=selected_model
                )
                st.session_state[feedback_key] = feedback_text
                
        if st.session_state[feedback_key]:
            st.markdown(st.session_state[feedback_key])
            
            # Form report content for download
            report_markdown = f"""# ResumeIQ AI Feedback Report
**Job Name**: {selected_jd_name}
**Match Score**: {job_detail['score']:.2f}%
**Matching Skills**: {', '.join(job_detail['matching_skills']) if job_detail['matching_skills'] else 'None'}
**Missing Skills**: {', '.join(job_detail['missing_skills']) if job_detail['missing_skills'] else 'None'}

---

## AI Analysis
{st.session_state[feedback_key]}
"""
            col_dl, col_chat = st.columns([1, 2])
            with col_dl:
                st.download_button(
                    label="📥 Download Feedback Report",
                    data=report_markdown,
                    file_name=f"ResumeIQ_Feedback_{selected_jd_name.replace(' ', '_')}.md",
                    mime="text/markdown"
                )
            
            with col_chat:
                if st.button("💬 Ask AI Advisor about this Job"):
                    seeded_question = f"I am looking at the job '{selected_jd_name}' where I have a match score of {job_detail['score']:.2f}%. What are the best ways I can address the missing skills: {', '.join(job_detail['missing_skills']) if job_detail['missing_skills'] else 'None'}?"
                    if "chat_messages" not in st.session_state:
                        st.session_state.chat_messages = []
                    st.session_state.chat_messages.append({"role": "user", "content": seeded_question})
                    st.session_state.trigger_assistant_chat = True
                    st.session_state.active_page = "💬 Career AI Chat"
                    st.rerun()
            
    # --- PAGE 3: Career Recommendations ---
    elif st.session_state.active_page == "🎯 Career Recommendations":
        st.markdown("### 🎯 AI Career Recommendations")
        st.write("Get top career paths and roles based on your uploaded resume skills and details.")
        
        recommender_key = f"recommendations_{selected_model}"
        if recommender_key not in st.session_state:
            st.session_state[recommender_key] = None
            
        if st.button("Generate Career Recommendations"):
            with st.spinner("Analyzing profile..."):
                recs = recommend_roles(resume_text, model_name=selected_model)
                st.session_state[recommender_key] = recs
                
        if st.session_state[recommender_key]:
            st.markdown(st.session_state[recommender_key])
            
            st.download_button(
                label="📥 Download Recommendations",
                data=st.session_state[recommender_key],
                file_name="Career_Recommendations.md",
                mime="text/markdown"
            )
            
    # --- PAGE 4: Career AI Chat ---
    elif st.session_state.active_page == "💬 Career AI Chat":
        st.markdown("### 💬 Career AI Chat")
        st.write("Have a conversation with our Career AI Advisor about your resume, potential roles, skill gaps, or interview prep.")
        
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
            
        # Display chat messages from history on app rerun
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Check if we have a trigger to run seeded query assistant response immediately
        if st.session_state.get("trigger_assistant_chat", False) and st.session_state.chat_messages:
            st.session_state.trigger_assistant_chat = False
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("Thinking..."):
                    system_message = {
                        "role": "system",
                        "content": f"You are an expert career advisor. Candidate Resume:\n{resume_text}\n\nJob Analysis:\n{jobs_summary}\n\nProvide practical, detailed, and actionable advice."
                    }
                    messages_payload = [system_message] + st.session_state.chat_messages
                    
                    try:
                        assistant_response = career_chat(
                            messages_payload, 
                            model_name=selected_model
                        )
                        message_placeholder.markdown(assistant_response)
                        st.session_state.chat_messages.append(
                            {"role": "assistant", "content": assistant_response}
                        )
                    except Exception as e:
                        err_msg = f"Error communicating with Ollama: {e}"
                        message_placeholder.error(err_msg)
                        
        # Accept normal user input
        if chat_prompt := st.chat_input("Ask anything about your career path..."):
            with st.chat_message("user"):
                st.markdown(chat_prompt)
            st.session_state.chat_messages.append({"role": "user", "content": chat_prompt})
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("Thinking..."):
                    system_message = {
                        "role": "system",
                        "content": f"You are an expert career advisor. Candidate Resume:\n{resume_text}\n\nJob Analysis:\n{jobs_summary}\n\nProvide practical, detailed, and actionable advice."
                    }
                    messages_payload = [system_message] + st.session_state.chat_messages
                    
                    try:
                        assistant_response = career_chat(
                            messages_payload, 
                            model_name=selected_model
                        )
                        message_placeholder.markdown(assistant_response)
                        st.session_state.chat_messages.append(
                            {"role": "assistant", "content": assistant_response}
                        )
                    except Exception as e:
                        err_msg = f"Error communicating with Ollama: {e}"
                        message_placeholder.error(err_msg)
                        
    # --- PAGE 5: Analysis History ---
    elif st.session_state.active_page == "📜 Analysis History":
        st.markdown("### 📜 Analysis History")
        
        col_hist_header, col_hist_btn = st.columns([4, 1])
        with col_hist_header:
            st.write("Past analyses performed on this machine:")
        with col_hist_btn:
            if st.button("🗑️ Clear All History", type="primary"):
                clear_history()
                st.success("History cleared successfully!")
                st.rerun()
                
        history = get_resume_history()
        if history:
            for resume_name, jobs in history.items():
                with st.expander(f"📄 Resume: {resume_name}"):
                    hist_df_data = []
                    for job in jobs:
                        hist_df_data.append({
                            "Job Name": job[0],
                            "Match Score": f"{float(job[1]):.2f}%",
                            "Date Evaluated": job[2]
                        })
                    st.dataframe(pd.DataFrame(hist_df_data), use_container_width=True, hide_index=True)
        else:
            st.info("No previous analyses found in the database.")
            
else:
    # Landing page message when uploads are missing
    st.info("👋 Welcome to CareerMatch AI! Please upload your resume and job descriptions in the sidebar to begin.")
    
    st.divider()
    st.markdown("### 📜 Analysis History")
    history = get_resume_history()
    if history:
        col_hist_header, col_hist_btn = st.columns([4, 1])
        with col_hist_header:
            st.write("Past analyses performed on this machine:")
        with col_hist_btn:
            if st.button("🗑️ Clear All History", type="primary", key="btn_clear_empty"):
                clear_history()
                st.success("History cleared successfully!")
                st.rerun()
                
        for resume_name, jobs in history.items():
            with st.expander(f"📄 Resume: {resume_name}"):
                hist_df_data = []
                for job in jobs:
                    hist_df_data.append({
                        "Job Name": job[0],
                        "Match Score": f"{float(job[1]):.2f}%",
                        "Date Evaluated": job[2]
                    })
                st.dataframe(pd.DataFrame(hist_df_data), use_container_width=True, hide_index=True)
    else:
        st.write("No previous analyses found.")