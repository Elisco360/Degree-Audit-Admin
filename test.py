import streamlit_authenticator as stauth

hashes = stauth.Hasher(['entow@adv01', 'eboat@adv10']).generate()

print(hashes)