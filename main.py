import streamlit as st
import time

# --- セッション一覧の取得と選択 ---
recent_sessions = list_recent_sessions() # 上記の関数を呼び出し
selected_session = st.sidebar.selectbox("チャット履歴を選択", ["新規作成"] + recent_sessions)

if selected_session == "新規作成":
    default_name = datetime.now().strftime("%m%d%H%M%S")
    session_id = st.sidebar.text_input("チャット名を入力", value=default_name)
else:
    session_id = selected_session

# --- 送信処理 ---
if prompt := st.chat_input("医療相談を入力..."):
    # 1. バックエンドを叩いて「ユーザー入力の保存」だけ行わせる
    # (ここでは簡略化して直接関数を呼ぶイメージ)
    save_message(session_id, "user", prompt)
    
    # 2. 回答を待つループ（非同期の疑似実現）
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("思考中...")
        
        while True:
            # GCSのファイルを読みに行く
            history = get_history_from_gcs(session_id)
            last_msg = history[-1]
            
            if last_msg["role"] == "assistant":
                # AIの回答が書き込まれていたらループ終了
                message_placeholder.markdown(last_msg["content"])
                break
            
            time.sleep(2) # 2秒おきにチェック
