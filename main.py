import streamlit as st
import requests
from datetime import datetime

# --- 設定 ---
# 実際のCloud RunのURLに置き換えてください
BACKEND_URL = "https://medical-ai-engine-backend-895886568528.asia-northeast1.run.app"

st.set_page_config(page_title="医療AIプラットフォーム", layout="wide")
st.title("🏥 medical-ai-chat")

# --- セッション状態の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- サイドバー：チャット管理 ---
st.sidebar.header("チャット管理")

# 1. バックエンドからチャット一覧を取得
try:
    sessions_res = requests.get(f"{BACKEND_URL}/sessions")
    session_list = sessions_res.json().get("sessions", []) if sessions_res.status_code == 200 else []
except:
    session_list = []

# セッション選択
selected_session = st.sidebar.selectbox(
    "チャットを選択", 
    ["新規チャット"] + session_list
)

# セッションIDの確定
if selected_session == "新規チャット":
    default_id = datetime.now().strftime("%m%d-%H%M%S")
    session_id = st.sidebar.text_input("新規チャット名", value=default_id)
else:
    session_id = selected_session
    # 2. 過去チャットが選択された瞬間に履歴をバックエンドから取得
    # (既に読み込み済みでない場合のみ実行すると効率的)
    if st.sidebar.button("このチャットを読み込む"):
        with st.spinner("履歴を読み込み中..."):
            history_res = requests.get(f"{BACKEND_URL}/history/{session_id}")
            if history_res.status_code == 200:
                # 過去5往復（10件）を取得
                st.session_state.messages = history_res.json().get("history", [])[-10:]
                st.success("読み込み完了")

st.sidebar.divider()
st.sidebar.info(f"現在のセッション: {session_id}")

# --- メインチャット画面 ---

# 3. 履歴の表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 4. ユーザー入力
if prompt := st.chat_input("症状や解析したい内容を入力してください..."):
    # ユーザーの入力を画面と状態に追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # バックエンドへ送信（回答を待つ）
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("思考中...")
        
        try:
            # 入力とIDをバックエンドに投げる
            response = requests.post(
                f"{BACKEND_URL}/chat", 
                json={"message": prompt, "session_id": session_id},
                timeout=60
            )
            
            if response.status_code == 200:
                full_response = response.json().get("reply")
                message_placeholder.markdown(full_response)
                # 状態にAIの回答を追加
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                # 5往復（10件）に維持
                if len(st.session_state.messages) > 10:
                    st.session_state.messages = st.session_state.messages[-10:]
            else:
                message_placeholder.error("バックエンドでエラーが発生しました。")
        except Exception as e:
            message_placeholder.error(f"通信エラーが発生しました: {e}")
