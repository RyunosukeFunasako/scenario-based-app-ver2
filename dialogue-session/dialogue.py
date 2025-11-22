import streamlit as st
from openai import OpenAI
import json
import time

# ストリーム表示を行う関数
def stream_counselor_reply(counselor_reply):
    for chunk in counselor_reply:
        yield chunk
        time.sleep(0.02)

@st.dialog("CBTの対象", width="large")
def cbt_attention_modal():
    st.markdown("""
    対話セッションでは認知行動療法（CBT）を体験していただきます。
    CBTは「認知」に働きかけて気分を楽にする精神療法です。

    そのため、患者さんの困りごととして取り上げる内容は、「 **物事の受け取り方や考え方によって気分が変わるような悩み** 」が望ましいです。
    一方で、身体の病気や深刻な危機はCBTの直接の対象とはならず、本実験の想定範囲から外れてしまいます。

    対話セッションの中で「 **あなたが今お困りのことを簡単にお話しいただけますか？** 」という質問がありますが、上記の点を考慮してお答えください。
    また、「 **今** 」困っていることがない場合は、 **過去に困った出来事** についてお答えください。


    #### 対象となる困りごとの例：
    - 既読がついているのに返信が来ない
    - 小さなミスをすると自分はダメだと思ってしまう
    - 人前で話す時に過度に緊張してしまう

    #### 対象外となる困りごとの例：
    - 肩こりや頭痛がひどくて眠れない（身体の病気や症状）
    - 借金が返せず生活が成り立たない（経済問題）
    - 暴力やいじめを受けている（安全確保が必要な深刻な問題）
    """)

# 対話セッション
if st.session_state.current_page == "dialogue":
    st.title("対話セッション")

    scenario_file = "dialogue-session/counselor_scenario.json"

    if "counselor_turn" not in st.session_state:
        st.session_state.counselor_turn = 1

    if "messages_for_counselor" not in st.session_state:
        st.session_state.messages_for_counselor = []

    # どちらが発話したか
    if "speaker" not in st.session_state:
        st.session_state.speaker = "counselor"

    with open(scenario_file, "r") as f:
        scenario_data = json.load(f)["counselor_scenario"]

    # サイドバー
    with st.sidebar:
        st.markdown(f"### 実験の進度")
        st.progress(2 / 5)
        st.markdown(f"### 先ほどの画面の内容")
        if st.button("CBTの対象"):
            cbt_attention_modal()

    # 対話履歴を表示し続ける
    for dialogue_history in st.session_state.dialogue_history:
        with st.chat_message(dialogue_history["role"]):
            st.markdown(dialogue_history["content"])

    # 現在のターンのカウンセラーエージェントの発話を生成・表示
    if st.session_state.speaker == "counselor":
        counselor_scenario_message = scenario_data[st.session_state.counselor_turn - 1]["counselor_message"]
 
        # 表示を遅らせる
        time.sleep(2)
        counselor_reply = counselor_scenario_message

        # カウンセラーエージェントの発話をストリーム表示
        with st.chat_message("assistant"):
            st.write_stream(stream_counselor_reply(counselor_reply))
 
        # 対話履歴に追加
        st.session_state.dialogue_history.append({"role": "assistant", "content": counselor_reply})
        st.session_state.messages_for_counselor.append({"role": "assistant", "content": counselor_reply})

        if st.session_state.counselor_turn < len(scenario_data):
            st.session_state.speaker = "client"

    # 被験者の入力（21ターン目は入力を求めない）
    if st.session_state.speaker == "client":
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area("あなたの返答を入力してください", height=100, placeholder="ShiftまたはShift+Enterで改行できます")
            submitted = st.form_submit_button("送信")

        if submitted and user_input:
            st.session_state.dialogue_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.counselor_turn += 1
            st.session_state.speaker = "counselor"
            st.rerun()

    # 21ターン終了
    if st.session_state.counselor_turn == len(scenario_data):
        st.session_state.speaker = "finished"
        time.sleep(1)
        st.success("これで対話セッションは終了です。")
        if st.button("「認知の変化の回答」に進む"):
            st.session_state.current_page = "cc_immediate"
            st.rerun()

else:
    st.session_state.current_page = "description"
    st.rerun()
