import streamlit as st
from search import search, messages, get_context
from parser import parse_whatsapp_chat
import hashlib


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ConvoLens",
    page_icon="💬",
    layout="centered"
)


# =========================================================
# SESSION STATE
# =========================================================

if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "use_demo" not in st.session_state:
    st.session_state.use_demo = False

if "uploaded_messages" not in st.session_state:
    st.session_state.uploaded_messages = None


# =========================================================
# AVATAR COLORS
# =========================================================

AVATAR_COLORS = [
    "#FF9F68",
    "#4ECDC4",
    "#FF6B9D",
    "#A78BFA",
    "#4FACFE",
    "#FFB84C",
    "#6BCB77"
]


def avatar_color(name):
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    return AVATAR_COLORS[h % len(AVATAR_COLORS)]


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       APP BACKGROUND
       ===================================================== */

    .stApp {
        background: linear-gradient(
            160deg,
            #FFF9F5 0%,
            #F5EBFA 50%,
            #EFF3FF 100%
        );
    }


    /* =====================================================
       MAIN TITLE
       ===================================================== */

    .main-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #7C3AED, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }

    .subtitle {
        color: #6B6478;
        font-size: 1rem;
        margin-bottom: 26px;
        font-weight: 500;
    }


    /* =====================================================
       OVERVIEW BOX
       ===================================================== */

    .overview-box {
        background: rgba(255,255,255,0.78);
        border: 1px solid #E8DDF2;
        border-radius: 20px;
        padding: 22px;
        margin: 10px 0 25px 0;
        box-shadow: 0 5px 18px rgba(124,58,237,0.06);
    }


    /* =====================================================
       METRICS
       ===================================================== */

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #F0E5F5;
        border-radius: 14px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 3px 10px rgba(124,58,237,0.05);
    }

    div[data-testid="stMetricLabel"] {
        color: #8C8299 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #7C3AED !important;
        font-weight: 800;
    }


    /* =====================================================
       FILE UPLOADER
       ===================================================== */

    div[data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.65);
        border: 2px dashed #D8C8E8;
        border-radius: 16px;
        padding: 8px;
    }


    /* =====================================================
       TEXT INPUT
       ===================================================== */

    div[data-testid="stTextInput"] input {
        background-color: #FFFFFF;
        border: 2px solid #E2D5F0;
        border-radius: 16px;
        padding: 16px 20px;
        font-size: 1.05rem;
        color: #2D2438;
        box-shadow: 0 4px 14px rgba(124,58,237,0.08);
    }

    div[data-testid="stTextInput"] input:focus {
        border: 2px solid #A78BFA;
        box-shadow: 0 4px 18px rgba(124,58,237,0.18);
    }


    /* =====================================================
       TYPE BADGE
       ===================================================== */

    .type-badge {
        display: inline-block;
        background: linear-gradient(90deg, #4FACFE, #7C3AED);
        color: white;
        padding: 7px 18px;
        border-radius: 20px;
        font-size: 0.83rem;
        font-weight: 700;
        margin-bottom: 20px;
        box-shadow: 0 3px 10px rgba(79,172,254,0.3);
    }


    /* =====================================================
       RESULT CARD
       ===================================================== */

    .result-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 18px 22px;
        margin: 10px 0 8px 0;
        border: 1px solid #F0E5F5;
        box-shadow: 0 4px 16px rgba(124,58,237,0.07);
    }


    /* =====================================================
       MESSAGE TEXT
       ===================================================== */

    .message-text {
        color: #2D2438;
        font-size: 1.08rem;
        font-weight: 600;
        line-height: 1.55;
        margin-top: 8px;
    }

    .score-tag {
        display: inline-block;
        margin-top: 10px;
        background-color: #F3E8FF;
        color: #7C3AED;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 10px;
    }


    /* =====================================================
       CONTEXT
       ===================================================== */

    .context-box {
        background: #FAF6FF;
        border-radius: 12px;
        padding: 12px 15px;
        margin-top: 5px;
    }

    .context-line {
        color: #6F667C;
        font-size: 0.9rem;
        padding: 6px 0;
        line-height: 1.4;
    }

    .highlight-line {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.92rem;
        padding: 9px 12px;
        background: linear-gradient(90deg, #A78BFA, #EC4899);
        border-radius: 10px;
        margin: 4px 0;
    }


    /* =====================================================
       EMPTY STATE
       ===================================================== */

    .empty-state {
        color: #A899BC;
        text-align: center;
        padding: 60px 20px;
        font-size: 1.05rem;
        font-style: italic;
    }


    /* =====================================================
       NOT FOUND
       ===================================================== */

    .not-found-box {
        background: linear-gradient(90deg, #FFE8E8, #FFF0F0);
        color: #D14F4F;
        padding: 18px 22px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 1rem;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        border: 1px solid #E2D5F0;
    }


    /* =====================================================
       EXPANDER
       ===================================================== */

    div[data-testid="stExpander"] {
        border: none;
        background-color: #FAF6FF;
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">💬 ConvoLens</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Semantic search over a group chat — understands meaning, not just keywords.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# CONVERSATION SELECTION SCREEN
# =========================================================

if not st.session_state.conversation_started:

    # -----------------------------------------------------
    # CONVERSATION OVERVIEW
    # -----------------------------------------------------

    st.markdown(
        '<div class="overview-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div style="font-size:1.3rem;font-weight:800;'
        'color:#2D2438;margin-bottom:14px;">'
        '📊 Conversation Overview'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # DEFAULT DEMO STATISTICS
    # -----------------------------------------------------

    overview_messages = 4287
    overview_participants = 8
    overview_date_range = "Jan–Jun 2026"

    # -----------------------------------------------------
    # UPLOADED FILE STATISTICS
    # -----------------------------------------------------

    if st.session_state.uploaded_messages:

        uploaded_messages = st.session_state.uploaded_messages

        overview_messages = len(uploaded_messages)

        overview_participants = len(
            set(
                message["sender"]
                for message in uploaded_messages
            )
        )

        timestamps = [
            message["timestamp"]
            for message in uploaded_messages
            if message.get("timestamp")
        ]

        if timestamps:
            try:
                dates = [
                    timestamp[:10]
                    for timestamp in timestamps
                ]

                start_date = min(dates)
                end_date = max(dates)

                overview_date_range = (
                    f"{start_date} → {end_date}"
                )

            except Exception:
                overview_date_range = "Available"


    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Messages",
            value=f"{overview_messages:,}"
        )

    with col2:
        st.metric(
            label="Participants",
            value=overview_participants
        )

    with col3:
        st.metric(
            label="Date Range",
            value=overview_date_range
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # UPLOAD CONVERSATION
    # -----------------------------------------------------

    st.markdown(
        '<div style="font-size:1.15rem;font-weight:800;'
        'color:#2D2438;margin-bottom:8px;">'
        '📂 Upload Conversation'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Choose WhatsApp .txt",
        type=["txt"],
        label_visibility="collapsed"
    )


    # -----------------------------------------------------
    # HANDLE UPLOAD
    # -----------------------------------------------------

    if uploaded_file is not None:

        st.session_state.uploaded_file = uploaded_file
        st.session_state.use_demo = False

        try:

            parsed_messages = parse_whatsapp_chat(
                uploaded_file.getvalue()
            )

            st.session_state.uploaded_messages = parsed_messages

            if parsed_messages:

                st.success(
                    f"✅ {uploaded_file.name} loaded successfully — "
                    f"{len(parsed_messages):,} messages parsed."
                )

                participants = sorted(
                    set(
                        message["sender"]
                        for message in parsed_messages
                    )
                )

                st.info(
                    f"👥 {len(participants)} participants detected"
                )

            else:

                st.session_state.uploaded_messages = None

                st.error(
                    "❌ Could not parse this WhatsApp conversation. "
                    "Please check the exported .txt format."
                )

        except Exception as e:

            st.session_state.uploaded_messages = None

            st.error(
                f"❌ Error while parsing conversation: {e}"
            )


    # -----------------------------------------------------
    # OR
    # -----------------------------------------------------

    st.markdown(
        '<div style="text-align:center;color:#A899BC;'
        'margin:14px 0;">OR</div>',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # DEMO BUTTON
    # -----------------------------------------------------

    if st.button(
        "💬 Use Demo Conversation",
        use_container_width=True
    ):

        st.session_state.use_demo = True
        st.session_state.uploaded_file = None
        st.session_state.uploaded_messages = None


    # -----------------------------------------------------
    # SHOW DEMO SELECTION
    # -----------------------------------------------------

    if st.session_state.use_demo:

        st.info(
            "💬 Demo Conversation selected"
        )


    # -----------------------------------------------------
    # START SEARCHING
    # -----------------------------------------------------

    if (
        st.session_state.uploaded_messages
        or st.session_state.use_demo
    ):

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        if st.button(
            "🚀 Start Searching",
            use_container_width=True
        ):

            st.session_state.conversation_started = True

            st.rerun()


    # -----------------------------------------------------
    # STOP SELECTION SCREEN
    # -----------------------------------------------------

    st.stop()


# =========================================================
# SEARCH SCREEN
# =========================================================

query = st.text_input(
    "",
    placeholder=(
        "🔍  Ask something... "
        "e.g. what did we decide about the trip"
    ),
    label_visibility="collapsed"
)


st.write("")

st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# =========================================================
# KEY DECISIONS BUTTON
# =========================================================

show_decisions = st.button(
    "📌 Show Key Decisions"
)


# =========================================================
# KEY DECISIONS
# =========================================================

if show_decisions and not query:

    st.markdown(
        '<div class="type-badge">'
        '📌 Key decisions made in this chat'
        '</div>',
        unsafe_allow_html=True
    )

    decision_ids = [
        310,     # Manali trip
        662,     # Party budget
        2821     # Deadline extension
    ]


    # -----------------------------------------------------
    # DISPLAY EACH DECISION
    # -----------------------------------------------------

    for did in decision_ids:

        msg = next(
            (
                m for m in messages
                if m["id"] == did
            ),
            None
        )

        if msg is None:
            continue


        # -------------------------------------------------
        # RESULT CARD
        # -------------------------------------------------

        with st.container():

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True
            )

            col_avatar, col_message = st.columns(
                [0.12, 0.88]
            )


            # ---------------------------------------------
            # AVATAR
            # ---------------------------------------------

            with col_avatar:

                initial = msg["sender"][0].upper()

                color = avatar_color(
                    msg["sender"]
                )

                st.markdown(
                    f"""
                    <div style="
                        width:38px;
                        height:38px;
                        border-radius:50%;
                        background:{color};
                        color:white;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-weight:800;
                        font-size:1rem;
                    ">
                        {initial}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ---------------------------------------------
            # MESSAGE
            # ---------------------------------------------

            with col_message:

                st.markdown(
                    f"""
                    <div style="
                        font-weight:800;
                        color:#2D2438;
                        font-size:1rem;
                    ">
                        {msg["sender"]}
                    </div>

                    <div style="
                        color:#B5ABC4;
                        font-size:0.78rem;
                        margin-top:2px;
                    ">
                        {msg["timestamp"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="message-text">
                        {msg["text"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


        # -------------------------------------------------
        # FULL THREAD
        # -------------------------------------------------

        with st.expander(
            "💭 Show full thread"
        ):

            context = get_context(
                did,
                window=4
            )

            for c in context:

                if c["id"] == did:

                    st.markdown(
                        f"""
                        <div class="highlight-line">
                            ➤ <b>{c["sender"]}:</b>
                            {c["text"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        f"""
                        <div class="context-line">
                            <b>{c["sender"]}:</b>
                            {c["text"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


# =========================================================
# NORMAL SEARCH
# =========================================================

elif query:

    with st.spinner(
        "Searching through the chat..."
    ):

        results, explanation = search(
            query,
            top_k=5
        )


    # -----------------------------------------------------
    # SEARCH TYPE
    # -----------------------------------------------------

    st.markdown(
        f'<div class="type-badge">'
        f'🧠 {explanation}'
        f'</div>',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # NO RESULTS
    # -----------------------------------------------------

    if not results:

        st.markdown(
            '<div class="not-found-box">'
            '🤷 No matching messages found — '
            "this chat doesn't seem to cover that."
            '</div>',
            unsafe_allow_html=True
        )


    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    else:

        for r in results:

            initial = r["sender"][0].upper()

            color = avatar_color(
                r["sender"]
            )


            # ---------------------------------------------
            # RESULT CARD
            # ---------------------------------------------

            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True
            )

            col_avatar, col_message = st.columns(
                [0.12, 0.88]
            )


            # ---------------------------------------------
            # AVATAR
            # ---------------------------------------------

            with col_avatar:

                st.markdown(
                    f"""
                    <div style="
                        width:38px;
                        height:38px;
                        border-radius:50%;
                        background:{color};
                        color:white;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-weight:800;
                        font-size:1rem;
                    ">
                        {initial}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ---------------------------------------------
            # MESSAGE
            # ---------------------------------------------

            with col_message:

                st.markdown(
                    f"""
                    <div style="
                        font-weight:800;
                        color:#2D2438;
                        font-size:1rem;
                    ">
                        {r["sender"]}
                    </div>

                    <div style="
                        color:#B5ABC4;
                        font-size:0.78rem;
                        margin-top:2px;
                    ">
                        {r["timestamp"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="message-text">
                        {r["text"]}
                    </div>

                    <div class="score-tag">
                        Score: {r["score"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


            # ---------------------------------------------
            # SURROUNDING CONVERSATION
            # ---------------------------------------------

            with st.expander(
                "💭 Show surrounding conversation"
            ):

                for c in r["context"]:

                    if c["id"] == r["id"]:

                        st.markdown(
                            f"""
                            <div class="highlight-line">
                                ➤ <b>{c["sender"]}:</b>
                                {c["text"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    else:

                        st.markdown(
                            f"""
                            <div class="context-line">
                                <b>{c["sender"]}:</b>
                                {c["text"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


# =========================================================
# EMPTY SEARCH SCREEN
# =========================================================

else:

    st.markdown(
        '<div class="empty-state">'
        'Try queries like '
        '<i>"when did we finalize the trip"</i> '
        'or '
        '<i>"what did Palak say about the budget"</i>'
        '</div>',
        unsafe_allow_html=True
    )