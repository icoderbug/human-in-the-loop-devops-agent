import streamlit as st
import pandas as pd

from agents.docker_agent import docker_agent
from agents.kubernetes_agent import kubernetes_agent
from agents.cicd_agent import cicd_agent

from agents.github_agent import get_repo_readme
from agents.review_agent import github_review_agent
from agents.risk_agent import risk_agent

from database.db import conn, cursor
from utils.pdf_generator import generate_pdf

st.set_page_config(
    page_title="Human-in-the-Loop DevOps Agent",
    layout="wide"
)

st.title(" Human-in-the-Loop DevOps Agent")



if "docker_output" not in st.session_state:
    st.session_state.docker_output = ""

if "k8s_output" not in st.session_state:
    st.session_state.k8s_output = ""

if "cicd_output" not in st.session_state:
    st.session_state.cicd_output = ""

if "review_output" not in st.session_state:
    st.session_state.review_output = ""

if "risk_output" not in st.session_state:
    st.session_state.risk_output = ""

if "generated" not in st.session_state:
    st.session_state.generated = False



project = st.text_area(
    "Enter Project Description"
)

repo_name = st.text_input(
    "GitHub Repository",
    placeholder="pallets/flask"
)



if st.button("Review Repository"):

    try:

        with st.spinner("Reading Repository..."):
            #  Right: passing the user input variable
            content = get_repo_readme(repo_name)

        with st.spinner("Generating Review..."):
            st.session_state.review_output = (
                github_review_agent(content)
            )

        with st.spinner("Analyzing Risk..."):
            st.session_state.risk_output = (
                risk_agent(
                    st.session_state.review_output
                )
            )

    except Exception as e:
        st.error(f"Error: {e}")


if st.session_state.review_output:

    st.subheader(" Repository Review")

    st.write(
        st.session_state.review_output
    )

    st.subheader(" Risk Analysis")

    st.write(
        st.session_state.risk_output
    )

    st.divider()


if st.button(" Generate DevOps Assets"):

    try:

        with st.spinner("Generating Dockerfile..."):
            st.session_state.docker_output = (
                docker_agent(project)
            )

        with st.spinner("Generating Kubernetes YAML..."):
            st.session_state.k8s_output = (
                kubernetes_agent(project)
            )

        with st.spinner("Generating GitHub Actions Workflow..."):
            st.session_state.cicd_output = (
                cicd_agent(project)
            )

        st.session_state.generated = True

    except Exception as e:
        st.error(f"Error: {e}")




if st.session_state.generated:

    tab1, tab2, tab3 = st.tabs(
        [
            "Dockerfile",
            "Kubernetes YAML",
            "GitHub Actions"
        ]
    )

    with tab1:

        st.code(
            st.session_state.docker_output,
            language="dockerfile"
        )

        st.download_button(
            "Download Dockerfile",
            st.session_state.docker_output,
            file_name="Dockerfile"
        )

    with tab2:

        st.code(
            st.session_state.k8s_output,
            language="yaml"
        )

        st.download_button(
            "Download Kubernetes YAML",
            st.session_state.k8s_output,
            file_name="deployment.yaml"
        )

    with tab3:

        st.code(
            st.session_state.cicd_output,
            language="yaml"
        )

        st.download_button(
            "Download GitHub Actions",
            st.session_state.cicd_output,
            file_name="github-actions.yml"
        )

    st.divider()

    st.subheader("Human Approval")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(" Approve Deployment"):

            cursor.execute(
                """
                INSERT INTO approvals
                (
                    project_name,
                    risk_score,
                    status
                )
                VALUES (?,?,?)
                """,
                (
                    project,
                    st.session_state.risk_output,
                    "Approved"
                )
            )

            conn.commit()

            st.success(
                "Deployment Approved Successfully"
            )

            st.balloons()

    with col2:

        if st.button(" Reject Deployment"):

            cursor.execute(
                """
                INSERT INTO approvals
                (
                    project_name,
                    risk_score,
                    status
                )
                VALUES (?,?,?)
                """,
                (
                    project,
                    st.session_state.risk_output,
                    "Rejected"
                )
            )

            conn.commit()

            st.error(
                "Deployment Rejected"
            )

    

    pdf_file = generate_pdf(
        project,
        st.session_state.review_output,
        st.session_state.risk_output,
        st.session_state.docker_output,
        st.session_state.k8s_output,
        st.session_state.cicd_output
    )

    with open(pdf_file, "rb") as file:

        st.download_button(
            label=" Download Full DevOps Report",
            data=file,
            file_name="DevOps_Report.pdf",
            mime="application/pdf"
        )



st.divider()

st.subheader(" Dashboard Metrics")

cursor.execute("SELECT COUNT(*) FROM approvals")
total_deployments = cursor.fetchone()[0]

cursor.execute(
    "SELECT COUNT(*) FROM approvals WHERE status='Approved'"
)
approved_count = cursor.fetchone()[0]

cursor.execute(
    "SELECT COUNT(*) FROM approvals WHERE status='Rejected'"
)
rejected_count = cursor.fetchone()[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Deployments", total_deployments)

with col2:
    st.metric("Approved", approved_count)

with col3:
    st.metric("Rejected", rejected_count)



st.divider()

st.subheader(" Approval History")

try:

    cursor.execute(
        """
        SELECT
        project_name,
        risk_score,
        status,
        timestamp
        FROM approvals
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    df = pd.DataFrame(
        rows,
        columns=[
            "Project",
            "Risk Score",
            "Status",
            "Timestamp"
        ]
    )

    st.dataframe(
        df,
        use_container_width=True
    )

except Exception:

    st.warning(
        "Delete old approval.db and restart application once."
    )