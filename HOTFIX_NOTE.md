# Hotfix

Fixed Streamlit navigation by assigning a unique `url_path` to every `st.Page`.
The prior build used several lambda callables without unique paths, which caused `st.navigation()` to reject the page list on Streamlit Cloud.
