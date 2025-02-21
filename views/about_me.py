import streamlit as st

# from forms.contact import contact_form


# @st.experimental_dialog("Contact Me")
# def show_contact_form():
#     contact_form()


# --- HERO SECTION ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.image("./assets/profile_image.png", width=300)

with col2:
    st.title("Doui", anchor=False)
    st.write("14-years old full-stack dev | Turning ideas into code")
    st.write(
        """
    - Email: doui.coder@gmail.com
    - Discord: douicoder
    """
    )
    # if st.button("✉️ Contact Me"):
    #     print("HI")
    #     # show_contact_form()


# --- EXPERIENCE & QUALIFICATIONS ---
st.write("\n")
st.subheader("Experience & Qualifications", anchor=False)
st.write(
    """
    - Full-stack developer (14 years old) with experience in .NET, C#, Blazor, and MAUI.
    - Intermediate in Python, currently exploring AI model development and fine-tuning.
    - Strong problem-solving skills with a hands-on approach to coding and development.
    - Passionate about innovation, always eager to learn and build efficient solutions.
    """
)

# --- SKILLS ---
st.write("\n")
st.subheader("Hard Skills", anchor=False)
st.write(
    """
    - Programming: C#, Python
    - Databases: MSSQL, MongoDB, Firebase
    - Development: .NET, Blazor, MAUI, Full-Stack Web & App Development
    - AI & Learning: Exploring AI model development and fine-tuning
    """
)
