import streamlit as st
# from utils import *
from streamlit_option_menu import option_menu
from btc_st import btc_st
import os
import sys
# from configs import VERSION
# from server.utils import api_address


if __name__ == "__main__":
    is_lite = "lite" in sys.argv
    VERSION = 'V1.0'
    st.set_page_config(
        "Langchain-Chatchat WebUI",
        os.path.join("img", "chatchat_icon_blue_square_v2.png"),
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.bing.com',
            'Report a bug': "https://www.bing.com",
            'About': f"""欢迎使用 Langchain-Chatchat WebUI {VERSION}！"""
        }
    )

    pages = {
        "BTC": {
            "icon": "hdd-stack",
            "func": btc_st,
        },
    }

    with st.sidebar:
        st.image(
            os.path.join(
                "img",
                "ximo.png"
            ),
            # width=50
            use_column_width=True
        )
        st.caption(
            f"""<p align="right">当前版本：{VERSION}</p>""",
            unsafe_allow_html=True,
        )
        options = list(pages)
        icons = [x["icon"] for x in pages.values()]

        default_index = 0
        selected_page = option_menu(
            "",
            options=options,
            icons=icons,
            # menu_icon="chat-quote",
            default_index=default_index,
        )

    if selected_page in pages:
        pages[selected_page]["func"](is_lite=is_lite)
