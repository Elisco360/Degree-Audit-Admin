from io import BytesIO
import time
import streamlit as st
from deta import Deta
import yaml
from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader
import pandas as pd

st.set_page_config(page_icon='favicon.ico', page_title='Admin Portal', layout='wide')

deta = Deta(st.secrets['data_key'])

students_data = deta.Base('submitted')
students_files = deta.Drive('audit-files')

def update_details(update_data):
    for k in update_data.items():
        students_data.update(k[1], k[0])
    st.success('Student details updated')

def main():
    _info = students_data.fetch().items

    st.markdown("<h1 style='text-align: center;'>ADMIN PORTAL</h1>", unsafe_allow_html=True)
    st.markdown('\n\n\n\n')
    update, download = st.tabs(['Student List', 'Download Degree Audits'])

    with update:
        st.data_editor(_info, column_order=('Name', 'Major', 'Date', 'Attended Session 1', 'Attended Session 2', 'Attended Session 3', 'Notes'),
                       disabled=['Name', 'Major', 'Date'], key='data_editor', use_container_width=True)
        
        val = list(st.session_state["data_editor"]['edited_rows'].items())

        new_data = dict()
        df = pd.DataFrame(_info)
        for i in val:
            row = df.iloc[i[0]]
            new_data[row['key']] = i[1]
            update_details(new_data)

        st.metric('Students Submissions', len(_info))

    with download:
        students = students_files.list()['names']
        student_file = st.selectbox("Choose student's file", options=list(students))
        if student_file:
            new_name = student_file[:-5]
            workbook = students_files.get(student_file)
            workbook_data = workbook.read()
            workbook_buffer = BytesIO(workbook_data)
            st.download_button(f"Download **{new_name}'s** Degree Audit 🗃️", workbook_buffer,
                               file_name=f'{new_name}.xlsx')


with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

uname, authentication_status, username = authenticator.login('Admin Login', 'main')

if authentication_status:
    st.success(f'Administrator logged in, **{uname}**')
    main()
    st.markdown('\n\n\n\n\n\n')
    st.markdown('\n\n\n\n\n\n')
    authenticator.logout('Logout', 'main')
elif not authentication_status:
    st.warning('Please enter a correct username and password')
elif authentication_status == None:
    st.warning('Please enter your username and password')
