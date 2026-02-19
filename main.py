import streamlit as st
import requests
from datetime import datetime

# --- 設定 ---
BACKEND_URL = "https://medical-ai-engine-backend-895886568528.asia-northeast1.run.app"

st.set_page_config(page_title="医療AIプラットフォーム", layout="wide")
st.title("🏥 medical-ai-chat")

# --- 1. セッション状態の初期化 (ここが重要) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_session_id" not in st.session_state:
    # 初回だけデフォルトIDを作る
    st.session_state.current_session_id = datetime.now().strftime("%m%d-%H%M%S")

# --- サイドバー：チャット管理 ---
st.sidebar.header("チャット管理")

# バックエンドからチャット一覧を取得
try:
    sessions_res = requests.get(f"{BACKEND_URL}/sessions")
    session_list = sessions_res.json().get("sessions", []) if sessions_res.status_code == 200 else []
except:
    session_list = []

# セッション選択
selected_session = st.sidebar.selectbox(
    "チャットを選択", 
    ["新規チャット"] + session_list,
    key="session_selector"
)

# セッションIDの確定ロジック
if selected_session == "新規チャット":
    # ユーザーが自由に入力できるようにし、入力されたら session_state を更新する
    new_id = st.sidebar.text_input("新規チャット名（英数字推奨）", value=st.session_state.current_session_id)
    if new_id != st.session_state.current_session_id:
        st.session_state.current_session_id = new_id
        st.session_state.messages = [] # 名前を変えたら画面もクリア
    session_id = st.session_state.current_session_id
else:
    # 既存チャットを選んだ場合
    session_id = selected_session
    if st.sidebar.button("履歴を読み込む"):
        with st.spinner("ロード中..."):
            res = requests.get(f"{BACKEND_URL}/history/{session_id}")
            if res.status_code == 200:
                st.session_state.messages = res.json().get("history", [])
                st.session_state.current_session_id = session_id # IDを固定
                st.success("ロード完了")

st.sidebar.divider()
st.sidebar.info(f"送信先ID: {session_id}")

# --- メインチャット画面 ---

# 履歴の表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ユーザー入力
if prompt := st.chat_input("メッセージを入力..."):
    # 画面に即座に反映
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # バックエンドへ送信
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("思考中...")
        
        try:
            # 固定された session_id を送る
            response = requests.post(
                f"{BACKEND_URL}/chat", 
                json={"message": prompt, "session_id": session_id},
                timeout=60
            )
            
            if response.status_code == 200:
                ai_reply = response.json().get("reply")
                placeholder.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            else:
                placeholder.error(f"エラー: {response.status_code}")
        except Exception as e:
            placeholder.error(f"接続失敗: {e}")
