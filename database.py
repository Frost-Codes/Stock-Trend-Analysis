import datetime
from deta import Deta
import streamlit as st
import streamlit_authenticator as stauth
import re


DETA_KEY = 'd0dxul6jsv4_Wz5dgTMCd7vCNndRZsN1yT8sAPbgsjMN'
TOKEN = 'yYN1FEhN_cwuW1kuFqEZPtMxWarvJx6n1jgaBjydH'

deta = Deta(DETA_KEY)

db = deta.Base('users_db')


def insert_user(email, username, password):
    """
    :param email:
    :param username:
    :param password:
    :return User on successful creation otherwise error:
    """
    date_joined = str(datetime.datetime.now())
    validated = False
    return db.put({'key': email, 'username': username, 'password': password,
                   'date_joined': date_joined, 'validated': validated})


def fetch_users_emails():
    """Returns all users in database"""
    emails = []
    users = db.fetch()
    for user in users.items:
        emails.append(user['key'])
    return emails


def fetch_usernames():
    names = []
    users = db.fetch()
    for user in users.items:
        names.append(user['username'])
    return names


def get_users():
    return db.fetch().items


def get_user(email):
    """Returns a particular user if exits else None"""
    return db.get(email)


def validate_email(email):
    pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"

    if re.match(pattern, email):
        return True
    return False


def sign_up():
    with st.form(key='signup', clear_on_submit=True):
        st.subheader('Sign up')
        email = st.text_input('Email', placeholder='Enter email')
        username = st.text_input('Username', placeholder='Enter Username')
        password = st.text_input('Password', placeholder='Enter password', type='password')
        password2 = st.text_input('Password', placeholder='Confirm password', type='password')

        if email:
            if validate_email(email):
                if email not in fetch_users_emails():
                    if len(username) >= 2:
                        if username not in fetch_usernames():
                            if len(password) >= 6:
                                if password == password2:
                                    hashed_password = stauth.Hasher([password]).generate()
                                    insert_user(email=email, username=username, password=hashed_password[0])
                                    st.success('Account created Successfully')
                                    st.balloons()
                                else:
                                    st.warning('Passwords do not match')
                            else:
                                st.warning('Password should be at least 6 characters')
                        else:
                            st.warning('Username Already Exists')
                    else:
                        st.warning('Username too short')
                else:
                    st.warning('Email Already Exists!!')
            else:
                st.warning('Invalid email Address')

        col1, col2, col3, col4, col5 = st.columns(5)
        with col3:
            st.form_submit_button('Sign up')


def login():
    with st.form(key='login', clear_on_submit=True):
        st.subheader('Login')
        email = st.text_input('Email', placeholder='Enter email')
        password = st.text_input('Password', placeholder='Enter password', type='password')
        if email:
            if validate_email(email):
                if email in fetch_users_emails():
                    user = get_user(email)

                else:
                    st.warning('Email Does Not Exist Please Sign up')
            else:

                st.warning('Invalid Email Address')
        col1, col2, col3, col4, col5 = st.columns(5)
        with col3:
            st.form_submit_button('Login')

##############
# users = get_users()
# emails = []
# passwords = []
# user_names = []
# for user in users:
#     emails.append(user['key'])
#     user_names.append(user['username'])
#     passwords.append(user['password'])
#
# credentials = {'usernames': {}}
# for index in range(len(emails)):
#     credentials['usernames'][user_names[index]] = {'name': emails[index], 'password': passwords[index]}


# authenticator = stauth.Authenticate(credentials, cookie_name='MLStosks', key='abcdef', cookie_expiry_days=5)
#
# authenticator.logout('Log out', 'main')
#
# ########
#
# email, authentication_status, user_name = authenticator.login('Login', 'main')
#
# if user_name:
#     if user_name in user_names:
#         if authentication_status:
#             st.success('Logged in')
#         elif not authentication_status:
#             st.error('Incorrect Username/Password')
#         elif authentication_status is None:
#             st.warning('Please Enter your password')
#     else:
#         st.warning('Username does not exist, Please Sign up ')

# print(authentication_status, email, user_name)
# print(authenticator.credentials.items())
# print(authenticator.username, authenticator.password)
# print(st.session_state)
# login()
# sign_up()
# print(get_users())
# print(get_user('lynxian52@gmail.com')['password'])



