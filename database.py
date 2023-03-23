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
    """
    Fetch user emails
    :return List of user emails:
    """
    emails = []
    users = db.fetch()
    for user in users.items:
        emails.append(user['key'])
    return emails


def fetch_usernames():
    """
    Fetch all usernames in the database
    :return: a list of usernames:
    """
    names = []
    users = db.fetch()
    for user in users.items:
        names.append(user['username'])
    return names


def get_users():
    """
    Get all users in the database
    :return: Dictionary of users
    """
    users = db.fetch()
    return users.items


def get_user(email):
    """
    Returns a particular user if exits else None
    :param email:
    :return User info:
    """
    return db.get(email)


def validate_username(username):
    """
    Checks if a username is valid upon sign up
    :param username:
    :return: True if username is valid else False
    """
    pattern = "^[a-z]*$"
    if re.match(pattern, username):
        return True
    return False


def validate_email(email):
    """
    Checks if an email is valid
    :param email:
    :return: True if email is valid else False
    """
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
                    if validate_username(username):
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
                        st.warning('Invalid characters in Username')
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


print(get_users())