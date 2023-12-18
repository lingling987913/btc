import streamlit as st
from utils import *
from streamlit_chatbox import *
from streamlit_modal import Modal
from datetime import datetime
import os,re,time
from io import BytesIO
from typing import Union
from pathlib import Path
# from configs import (TEMPERATURE, HISTORY_LEN, PROMPT_TEMPLATES,
#                      DEFAULT_KNOWLEDGE_BASE, DEFAULT_SEARCH_ENGINE, SUPPORT_AGENT_MODEL)
# from server.knowledge_base.utils import LOADER_DICT
import uuid
from typing import List, Dict
from btc_model import btc_model
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 或其他支持中文的字体
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号



chat_box = ChatBox(
    assistant_avatar=os.path.join(
        "BTC/img",
        "chatchat_icon_blue_square_v2.png"
    )
)


def get_messages_history(history_len: int, content_in_expander: bool = False) -> List[Dict]:
    '''
    返回消息历史。
    content_in_expander控制是否返回expander元素中的内容，一般导出的时候可以选上，传入LLM的history不需要
    '''

    def filter(msg):
        content = [x for x in msg["elements"] if x._output_method in ["markdown", "text"]]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }

    return chat_box.filter_history(history_len=history_len, filter=filter)


def btc_st(is_lite: bool = False):
    st.session_state.setdefault("conversation_ids", {})
    st.session_state["conversation_ids"].setdefault(chat_box.cur_chat_name, uuid.uuid4().hex)
    st.session_state.setdefault("file_chat_id", None)
    default_model = '时间维度'

    if not chat_box.chat_inited:
        st.toast(
            f"欢迎使用 [`BTC_GPT`](https://www.bing.com) ! \n\n"
            f"当前运行的模型`{default_model}`, 您可以开始提问了."
        )
        chat_box.init_session()

    with st.sidebar:
        # 多会话
        conv_names = list(st.session_state["conversation_ids"].keys())
        index = 0
        if st.session_state.get("cur_conv_name") in conv_names:
            index = conv_names.index(st.session_state.get("cur_conv_name"))
        conversation_name = st.selectbox("当前会话：", conv_names, index=index)
        chat_box.use_chat_name(conversation_name)
        conversation_id = st.session_state["conversation_ids"][conversation_name]

        # TODO: 对话模型与会话绑定
        def on_mode_change():
            mode = st.session_state.dialogue_mode
            text = f"已切换到 {mode} 模式。"
            if mode == "知识库问答":
                cur_kb = st.session_state.get("selected_kb")
                if cur_kb:
                    text = f"{text} 当前知识库： `{cur_kb}`。"
            st.toast(text)

        dialogue_modes = ["BTC分析",
                          "LLM 对话",
                        "知识库问答",
                        "文件对话",
                        "搜索引擎问答",
                        ]
        dialogue_mode = st.selectbox("请选择对话模式：",
                                     dialogue_modes,
                                     index=0,
                                     on_change=on_mode_change,
                                     key="dialogue_mode",
                                     )

        running_models = []
        available_models =  ['时间维度','频次维度','交易笔数(稳定币内部转换)']
        llm_models = running_models + available_models
        cur_llm_model = st.session_state.get("cur_llm_model", default_model)
        if cur_llm_model in llm_models:
            index = llm_models.index(cur_llm_model)
        else:
            index = 0
        # llm_model = st.selectbox("选择分析维度：",
        #                          llm_models,
        #                          index,
        #                          format_func=llm_model_format_func,
        #                          on_change=on_llm_change,
        #                          key="llm_model",
        #                          )
        
        llm_model = st.multiselect("选择分析维度：",
                            llm_models,
                            default='时间维度'
                            )

        if dialogue_mode == "文件对话":
            with st.expander("文件对话配置", True):
                files = st.file_uploader("上传知识文件：",
                                        # [i for ls in LOADER_DICT.values() for i in ls],
                                        accept_multiple_files=True,
                                        )
                
                if st.button("开始上传", disabled=len(files)==0):
                    st.session_state["file_chat_id"] = upload_temp_docs(files)
    # 上传文件
    files = st.file_uploader("人员数据",
                            #  [i for ls in LOADER_DICT.values() for i in ls],
                             accept_multiple_files=False,
                             )
    if st.button("开始分析", disabled=files is None):
        # st.session_state["file_chat_id"] = upload_temp_docs(files)
        if files.name.endswith(('.xls','.xlsx')):
            merged_df = btc_model(file_path=files)
        # merged_df = upload_and_read_docs(files)
        # st.write(merged_df)
        st.dataframe(merged_df)
        st_plot(merged_df)
    # Display chat messages from history on app rerun
    chat_box.output_messages()

    chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter。输入/help查看自定义命令 "

    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        chat_box.user_say(prompt)
        if dialogue_mode == "BTC分析":
            chat_box.ai_say("正在分析...")
            if prompt == '开始分析':
                if files.name.endswith(('.xls','.xlsx')):
                    merged_df = btc_model(file_path=files)
                    # merged_df = upload_and_read_docs(files)
                    st.write(merged_df)
        elif dialogue_mode == "LLM 对话":
            chat_box.ai_say("正在思考...")
            text = ""
            message_id = ""
            r = [{'text':'1'},{'text':'2'},{'text':'3'}]
            for t in r:
                if error_msg := check_error_msg(t):  # check whether error occured
                    st.error(error_msg)
                    break
                text += t.get("text", "")
                chat_box.update_msg(text)
                message_id = t.get("message_id", "")

            metadata = {
                "message_id": message_id,
                }
            chat_box.update_msg(text, streaming=False, metadata=metadata)  # 更新最终的字符串，去除光标
        elif dialogue_mode == "文件对话":
            if st.session_state["file_chat_id"] is None:
                st.error("请先上传文件再进行对话")
                st.stop()
            chat_box.ai_say([
                f"正在查询文件 `{st.session_state['file_chat_id']}` ...",
                Markdown("...", in_expander=True, title="文件匹配结果", state="complete"),
            ])
            text = ""
            for d in res_list:
                if error_msg := check_error_msg(d):  # check whether error occured
                    st.error(error_msg)
                elif chunk := d.get("answer"):
                    text += chunk
                    chat_box.update_msg(text, element_index=0)
            chat_box.update_msg(text, element_index=0, streaming=False)
            chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)

    if st.session_state.get("need_rerun"):
        st.session_state["need_rerun"] = False
        st.rerun()

    now = datetime.now()
    with st.sidebar:

        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
                "清空对话",
                use_container_width=True,
        ):
            chat_box.reset_history()
            st.rerun()

    export_btn.download_button(
        "导出记录",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
        mime="text/markdown",
        use_container_width=True,
    )
    
def convert_file(file, filename=None):
    if isinstance(file, bytes): # raw bytes
        file = BytesIO(file)
    elif hasattr(file, "read"): # a file io like object
        filename = filename or file.name
    else: # a local path
        file = Path(file).absolute().open("rb")
        filename = filename or os.path.split(file.name)[-1]
    return filename, file


def upload_temp_docs(uploaded_files):
    save_paths = []
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            # 设置文件保存的路径
            save_path = os.path.join("upload", uploaded_file.name)

            # 使用 UploadedFile 对象的内容写入新文件
            with open(save_path, "wb") as f:
                f.write(uploaded_file.read())

            st.write(f"File saved to {save_path}")
        save_paths.append(save_path)
    return save_paths

def upload_and_read_docs(uploaded_file):
    if uploaded_file is not None:
        # 文件已上传
        # 读取文件内容
        # 示例：读取文本文件
        if uploaded_file.type == "text/plain":
            # 读取为字符串
            content = uploaded_file.read().decode("utf-8")
            st.write(content)
        # 示例：处理CSV文件
        elif uploaded_file.type == "text/csv":
            import pandas as pd
            # 读取为DataFrame
            df = pd.read_csv(uploaded_file)
            st.write(df)
        elif uploaded_file.name.endswith(('.xls','.xlsx')):
            import pandas as pd
            # 读取为DataFrame
            xls = pd.ExcelFile(uploaded_file)
            sheet_dict = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}

            # 现在 sheet_dict 是一个字典，其键为工作表名称，值为对应的 DataFrame
            for sheet_name, df in sheet_dict.items():
                st.write(f"Sheet name: {sheet_name}")
                st.write(df)
        # 为其他文件类型添加更多处理逻辑
        else:
            st.error("Unsupported file type")
            
    return df

def check_error_msg(data: Union[str, dict, list], key: str = "errorMsg") -> str:
    '''
    return error message if error occured when requests API
    '''
    if isinstance(data, dict):
        if key in data:
            return data[key]
        if "code" in data and data["code"] != 200:
            return data["msg"]
    return ""

def check_success_msg(data: Union[str, dict, list], key: str = "msg") -> str:
    '''
    return error message if error occured when requests API
    '''
    if (isinstance(data, dict)
        and key in data
        and "code" in data
        and data["code"] == 200):
        return data[key]
    return ""

def st_plot(df):
    # 绘图
    fig, ax = plt.subplots()
    df.plot(kind='line', ax=ax)
    plt.title('示例图表')
    plt.xlabel('X轴')
    plt.ylabel('Y轴')
    st.pyplot(fig)