from io import BytesIO
import streamlit as st
from deta import Deta
import yaml
from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader

st.set_page_config(page_icon='favicon.ico', page_title='Admin Portal')

deta = Deta(st.secrets['data_key'])

students_data = deta.Base('submitted')
students_files = deta.Drive('audit-files')


def main():
    _info = students_data.fetch().items

    st.markdown("<h1 style='text-align: center;'>ADMIN PORTAL</h1>", unsafe_allow_html=True)
    st.markdown('\n\n\n\n')
    update, download = st.tabs(['Update Student Attendance', 'Download Degree Audits'])

    def update_attendance(user_key):
        students_data.update({'Attended Session': True}, user_key)

    with update:
        st.data_editor(_info, column_order=('Name', 'Major', 'Date', 'Attended Session'),
                       disabled=['Name', 'Major', 'Date'], key='edited_data')
        try:
            _altered = _info[int(list(st.session_state['edited_data']['edited_rows'].keys())[0])]
            if _altered['Attended Session']:
                students_data.update({'Attended Session': False}, _altered['key'])
            else:
                students_data.update({'Attended Session': True}, _altered['key'])
        except:
            pass

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
