# import streamlit as st
# import pandas as pd
# import numpy as np
# import tensorflow as tf
# import json

# # Load model
# model = tf.keras.models.load_model("LogSentinel.keras")

# # Load configuration
# with open("config.json", "r") as f:
#     config = json.load(f)

# with open("event_mapping.json", "r") as f:
#     event_to_id = json.load(f)

# id_to_event = {v: k for k, v in event_to_id.items()}

# SEQUENCE_LENGTH = config["sequence_length"]

# st.set_page_config(
#     page_title="LogSentinel",
#     page_icon="🛡️",
#     layout="wide"
# )

# st.title("🛡️ LogSentinel")
# st.subheader("Intelligent Log Anomaly Detection")

# st.write(
#     "Upload a structured log file to detect unusual event sequences."
# )

# uploaded_file = st.file_uploader(
#     "Upload log CSV",
#     type=["csv"]
# )


# def detect_anomalies(df):
#     events = df["EventId"].map(event_to_id).values

#     results = []

#     for i in range(SEQUENCE_LENGTH, len(events)):
#         sequence = events[i - SEQUENCE_LENGTH:i]
#         actual_event = events[i]

#         prediction = model.predict(
#             np.array([sequence]),
#             verbose=0
#         )[0]

#         top_3 = np.argsort(prediction)[-3:]

#         results.append({
#             "Line": i + 1,
#             "Actual Event": id_to_event[actual_event],
#             "Predicted Events": ", ".join(
#                 id_to_event[x] for x in reversed(top_3)
#             ),
#             "Anomaly": actual_event not in top_3
#         })

#     return pd.DataFrame(results)

# if uploaded_file is not None:
#     df = pd.read_csv(uploaded_file)

#     st.write(f"Loaded **{len(df):,} log entries**.")

#     if "EventId" not in df.columns:
#         st.error("Invalid file: 'EventId' column is missing.")
#     else:
#         results = detect_anomalies(df)

#         anomaly_count = results["Anomaly"].sum()
#         normal_count = len(results) - anomaly_count

#         col1, col2, col3 = st.columns(3)

#         col1.metric("Logs Analyzed", len(results))
#         col2.metric("Normal", normal_count)
#         col3.metric("Anomalies", anomaly_count)

#         st.subheader("Detection Results")
#         st.dataframe(results, use_container_width=True)














































































# import streamlit as st
# import pandas as pd
# import numpy as np
# import tensorflow as tf
# import json


# # --------------------------------------------------
# # Page Configuration
# # --------------------------------------------------

# st.set_page_config(
#     page_title="LogSentinel",
#     page_icon="🛡️",
#     layout="wide"
# )


# # --------------------------------------------------
# # Load Model & Configuration
# # --------------------------------------------------

# @st.cache_resource
# def load_model():
#     return tf.keras.models.load_model("LogSentinel.keras")


# @st.cache_data
# def load_config():
#     with open("config.json", "r") as f:
#         config = json.load(f)

#     with open("event_mapping.json", "r") as f:
#         event_to_id = json.load(f)

#     return config, event_to_id


# model = load_model()
# config, event_to_id = load_config()

# id_to_event = {
#     int(v): k for k, v in event_to_id.items()
# }

# SEQUENCE_LENGTH = config["sequence_length"]


# # --------------------------------------------------
# # Anomaly Detection
# # --------------------------------------------------

# def detect_anomalies(df):

#     # Convert EventId → numerical event code
#     events = df["EventId"].map(event_to_id)

#     # Check for unknown events
#     unknown_mask = events.isna()

#     if unknown_mask.any():
#         unknown_events = df.loc[unknown_mask, "EventId"].unique()

#         raise ValueError(
#             "Unknown EventId(s) found: "
#             + ", ".join(map(str, unknown_events))
#         )

#     events = events.astype(int).values

#     sequences = []
#     actual_events = []
#     line_numbers = []

#     # Build sequences
#     for i in range(SEQUENCE_LENGTH, len(events)):

#         sequences.append(
#             events[i - SEQUENCE_LENGTH:i]
#         )

#         actual_events.append(events[i])
#         line_numbers.append(i + 1)

#     # Not enough logs for one sequence
#     if len(sequences) == 0:
#         return pd.DataFrame(
#             columns=[
#                 "Line",
#                 "Actual Event",
#                 "Predicted Events",
#                 "Anomaly"
#             ]
#         )

#     sequences = np.array(sequences)
#     actual_events = np.array(actual_events)

#     # Batched prediction
#     predictions = model.predict(
#         sequences,
#         batch_size=128,
#         verbose=0
#     )

#     # Get top-3 predicted events
#     top_3 = np.argsort(
#         predictions,
#         axis=1
#     )[:, -3:]

#     anomaly_flags = []

#     predicted_events = []

#     for i in range(len(actual_events)):

#         predicted = [
#             id_to_event[event_id]
#             for event_id in reversed(top_3[i])
#         ]

#         predicted_events.append(
#             ", ".join(predicted)
#         )

#         anomaly_flags.append(
#             actual_events[i] not in top_3[i]
#         )

#     # Build results
#     results = pd.DataFrame({
#         "Line": line_numbers,

#         "Actual Event": [
#             id_to_event[event_id]
#             for event_id in actual_events
#         ],

#         "Predicted Events": predicted_events,

#         "Anomaly": anomaly_flags
#     })

#     return results


# # --------------------------------------------------
# # User Interface
# # --------------------------------------------------

# st.title("🛡️ LogSentinel")

# st.subheader(
#     "Intelligent Log Anomaly Detection"
# )

# st.write(
#     "Upload a structured log CSV to detect "
#     "unusual event sequences using a DeepLog-style "
#     "LSTM model."
# )


# uploaded_file = st.file_uploader(
#     "Upload log CSV",
#     type=["csv"]
# )


# # --------------------------------------------------
# # Process Uploaded File
# # --------------------------------------------------

# if uploaded_file is not None:

#     try:

#         df = pd.read_csv(uploaded_file)

#         st.write(
#             f"Loaded **{len(df):,} log entries**."
#         )

#         # Check required column
#         if "EventId" not in df.columns:

#             st.error(
#                 "Invalid file: 'EventId' column is missing."
#             )

#         elif len(df) <= SEQUENCE_LENGTH:

#             st.warning(
#                 f"The file must contain more than "
#                 f"{SEQUENCE_LENGTH} log entries."
#             )

#         else:

#             # Run detection
#             results = detect_anomalies(df)

#             # Statistics
#             anomaly_count = int(
#                 results["Anomaly"].sum()
#             )

#             normal_count = (
#                 len(results) - anomaly_count
#             )

#             anomaly_rate = (
#                 anomaly_count / len(results) * 100
#                 if len(results) > 0
#                 else 0
#             )

#             # Metrics
#             col1, col2, col3, col4 = st.columns(4)

#             col1.metric(
#                 "Logs Analyzed",
#                 f"{len(results):,}"
#             )

#             col2.metric(
#                 "Normal",
#                 f"{normal_count:,}"
#             )

#             col3.metric(
#                 "Anomalies",
#                 f"{anomaly_count:,}"
#             )

#             col4.metric(
#                 "Anomaly Rate",
#                 f"{anomaly_rate:.2f}%"
#             )

#             # Results
#             st.subheader(
#                 "Detection Results"
#             )

#             st.dataframe(
#                 results,
#                 use_container_width=True,
#                 hide_index=True
#             )

#             # Download results
#             csv = results.to_csv(
#                 index=False
#             ).encode("utf-8")

#             st.download_button(
#                 label="⬇️ Download Results",
#                 data=csv,
#                 file_name="logsentinel_results.csv",
#                 mime="text/csv"
#             )

#     except ValueError as e:

#         st.error(str(e))

#     except Exception as e:

#         st.error(
#             f"An error occurred while processing "
#             f"the file: {e}"
#         )














































# import streamlit as st
# import pandas as pd
# import numpy as np
# import tensorflow as tf
# import json


# # ============================================================
# # PAGE CONFIGURATION
# # ============================================================

# st.set_page_config(
#     page_title="LogSentinel",
#     page_icon="🛡️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )


# # ============================================================
# # CUSTOM UI STYLING
# # ============================================================

# st.markdown("""
# <style>

#     /* Main background */
#     .stApp {
#         background: #0b0f14;
#     }

#     /* Main content width */
#     .block-container {
#         padding-top: 2rem;
#         padding-bottom: 3rem;
#         max-width: 1400px;
#     }

#     /* Header */
#     .hero {
#         padding: 1.5rem 0 1rem 0;
#     }

#     .hero-title {
#         font-size: 3.2rem;
#         font-weight: 800;
#         letter-spacing: -1px;
#         margin-bottom: 0.2rem;
#     }

#     .hero-subtitle {
#         font-size: 1.15rem;
#         color: #9ca3af;
#         margin-bottom: 1.5rem;
#     }

#     .badge {
#         display: inline-block;
#         padding: 0.35rem 0.75rem;
#         border-radius: 999px;
#         background: rgba(59, 130, 246, 0.12);
#         border: 1px solid rgba(59, 130, 246, 0.30);
#         color: #60a5fa;
#         font-size: 0.8rem;
#         font-weight: 600;
#         margin-bottom: 0.8rem;
#     }

#     /* Metric cards */
#     div[data-testid="stMetric"] {
#         background: #111720;
#         border: 1px solid #1f2937;
#         border-radius: 14px;
#         padding: 1rem 1.2rem;
#         box-shadow: 0 4px 18px rgba(0,0,0,0.18);
#     }

#     div[data-testid="stMetricLabel"] {
#         color: #9ca3af;
#     }

#     div[data-testid="stMetricValue"] {
#         font-weight: 700;
#     }

#     /* Section headings */
#     .section-title {
#         font-size: 1.45rem;
#         font-weight: 700;
#         margin-top: 2rem;
#         margin-bottom: 0.8rem;
#     }

#     /* Info cards */
#     .info-card {
#         background: #111720;
#         border: 1px solid #1f2937;
#         border-radius: 14px;
#         padding: 1rem 1.2rem;
#         margin-bottom: 1rem;
#     }

#     .info-label {
#         color: #9ca3af;
#         font-size: 0.8rem;
#         text-transform: uppercase;
#         letter-spacing: 0.6px;
#     }

#     .info-value {
#         font-size: 1.05rem;
#         font-weight: 600;
#         margin-top: 0.25rem;
#     }

#     /* Upload area */
#     section[data-testid="stFileUploaderDropzone"] {
#         background: #111720;
#         border: 1px dashed #374151;
#         border-radius: 14px;
#     }

#     /* Buttons */
#     .stDownloadButton button {
#         border-radius: 10px;
#         font-weight: 600;
#     }

#     /* Divider */
#     hr {
#         border-color: #1f2937;
#     }

# </style>
# """, unsafe_allow_html=True)


# # ============================================================
# # LOAD MODEL & CONFIGURATION
# # ============================================================

# @st.cache_resource
# def load_model():
#     return tf.keras.models.load_model("LogSentinel.keras")


# @st.cache_data
# def load_config():

#     with open("config.json", "r") as f:
#         config = json.load(f)

#     with open("event_mapping.json", "r") as f:
#         event_to_id = json.load(f)

#     return config, event_to_id


# model = load_model()
# config, event_to_id = load_config()

# id_to_event = {
#     int(v): k for k, v in event_to_id.items()
# }

# SEQUENCE_LENGTH = config["sequence_length"]


# # ============================================================
# # ANOMALY DETECTION
# # CORE LOGIC UNCHANGED
# # ============================================================

# def detect_anomalies(df):

#     events = df["EventId"].map(event_to_id)

#     unknown_mask = events.isna()

#     if unknown_mask.any():

#         unknown_events = df.loc[
#             unknown_mask,
#             "EventId"
#         ].unique()

#         raise ValueError(
#             "Unknown EventId(s) found: "
#             + ", ".join(map(str, unknown_events))
#         )

#     events = events.astype(int).values

#     sequences = []
#     actual_events = []
#     line_numbers = []

#     for i in range(SEQUENCE_LENGTH, len(events)):

#         sequences.append(
#             events[i - SEQUENCE_LENGTH:i]
#         )

#         actual_events.append(events[i])
#         line_numbers.append(i + 1)

#     if len(sequences) == 0:

#         return pd.DataFrame(
#             columns=[
#                 "Line",
#                 "Actual Event",
#                 "Predicted Events",
#                 "Anomaly"
#             ]
#         )

#     sequences = np.array(sequences)
#     actual_events = np.array(actual_events)

#     predictions = model.predict(
#         sequences,
#         batch_size=128,
#         verbose=0
#     )

#     top_3 = np.argsort(
#         predictions,
#         axis=1
#     )[:, -3:]

#     anomaly_flags = []
#     predicted_events = []

#     for i in range(len(actual_events)):

#         predicted = [
#             id_to_event[event_id]
#             for event_id in reversed(top_3[i])
#         ]

#         predicted_events.append(
#             ", ".join(predicted)
#         )

#         anomaly_flags.append(
#             actual_events[i] not in top_3[i]
#         )

#     results = pd.DataFrame({

#         "Line": line_numbers,

#         "Actual Event": [
#             id_to_event[event_id]
#             for event_id in actual_events
#         ],

#         "Predicted Events": predicted_events,

#         "Anomaly": anomaly_flags
#     })

#     return results


# # ============================================================
# # HERO SECTION
# # ============================================================

# st.markdown("""
# <div class="hero">

# <div class="badge">AI-POWERED LOG MONITORING</div>

# <div class="hero-title">
# 🛡️ LogSentinel
# </div>

# <div class="hero-subtitle">
# Intelligent Log Anomaly Detection using a DeepLog-style LSTM model
# </div>

# </div>
# """, unsafe_allow_html=True)


# # ============================================================
# # SIDEBAR
# # ============================================================

# with st.sidebar:

#     st.markdown("## 🛡️ LogSentinel")

#     st.markdown("---")

#     st.markdown("### About")

#     st.write(
#         "LogSentinel analyzes sequences of system log events "
#         "and identifies unusual patterns using deep learning."
#     )

#     st.markdown("### Model")

#     st.caption("Architecture")
#     st.write("LSTM")

#     st.caption("Sequence Length")
#     st.write(f"{SEQUENCE_LENGTH} events")

#     st.caption("Prediction Strategy")
#     st.write("Top-3 Event Prediction")

#     st.caption("Known Event Types")
#     st.write(f"{len(event_to_id)}")

#     st.markdown("---")

#     st.caption(
#         "Built for intelligent system log monitoring."
#     )


# # ============================================================
# # UPLOAD SECTION
# # ============================================================

# st.markdown(
#     '<div class="section-title">📂 Upload Log Data</div>',
#     unsafe_allow_html=True
# )

# st.write(
#     "Upload a **structured HDFS log CSV** containing an `EventId` column."
# )

# uploaded_file = st.file_uploader(
#     "Upload log CSV",
#     type=["csv"],
#     label_visibility="collapsed"
# )


# # ============================================================
# # PROCESS FILE
# # ============================================================

# if uploaded_file is not None:

#     try:

#         df = pd.read_csv(uploaded_file)

#         st.success(
#             f"Successfully loaded **{len(df):,} log entries**."
#         )

#         # ----------------------------------------------------
#         # Validate
#         # ----------------------------------------------------

#         if "EventId" not in df.columns:

#             st.error(
#                 "Invalid file: `EventId` column is missing."
#             )

#         elif len(df) <= SEQUENCE_LENGTH:

#             st.warning(
#                 f"The file must contain more than "
#                 f"{SEQUENCE_LENGTH} log entries."
#             )

#         else:

#             # ------------------------------------------------
#             # File Information
#             # ------------------------------------------------

#             info1, info2, info3 = st.columns(3)

#             with info1:
#                 st.markdown("""
#                 <div class="info-card">
#                     <div class="info-label">File</div>
#                     <div class="info-value">
#                 """, unsafe_allow_html=True)

#                 st.write(uploaded_file.name)

#                 st.markdown(
#                     "</div></div>",
#                     unsafe_allow_html=True
#                 )

#             with info2:
#                 st.markdown("""
#                 <div class="info-card">
#                     <div class="info-label">Log Entries</div>
#                     <div class="info-value">
#                 """, unsafe_allow_html=True)

#                 st.write(f"{len(df):,}")

#                 st.markdown(
#                     "</div></div>",
#                     unsafe_allow_html=True
#                 )

#             with info3:
#                 st.markdown("""
#                 <div class="info-card">
#                     <div class="info-label">Event Types</div>
#                     <div class="info-value">
#                 """, unsafe_allow_html=True)

#                 st.write(df["EventId"].nunique())

#                 st.markdown(
#                     "</div></div>",
#                     unsafe_allow_html=True
#                 )


#             # ------------------------------------------------
#             # Detection
#             # ------------------------------------------------

#             with st.spinner(
#                 "🔍 Analyzing log event sequences..."
#             ):

#                 results = detect_anomalies(df)


#             # ------------------------------------------------
#             # Statistics
#             # ------------------------------------------------

#             anomaly_count = int(
#                 results["Anomaly"].sum()
#             )

#             normal_count = (
#                 len(results) - anomaly_count
#             )

#             anomaly_rate = (
#                 anomaly_count / len(results) * 100
#                 if len(results) > 0
#                 else 0
#             )


#             # ------------------------------------------------
#             # Metrics
#             # ------------------------------------------------

#             st.markdown(
#                 '<div class="section-title">📊 Detection Overview</div>',
#                 unsafe_allow_html=True
#             )

#             col1, col2, col3, col4 = st.columns(4)

#             with col1:
#                 st.metric(
#                     "Logs Analyzed",
#                     f"{len(results):,}"
#                 )

#             with col2:
#                 st.metric(
#                     "Normal",
#                     f"{normal_count:,}"
#                 )

#             with col3:
#                 st.metric(
#                     "Anomalies",
#                     f"{anomaly_count:,}"
#                 )

#             with col4:
#                 st.metric(
#                     "Anomaly Rate",
#                     f"{anomaly_rate:.2f}%"
#                 )


#             # ------------------------------------------------
#             # Status
#             # ------------------------------------------------

#             if anomaly_rate >= 10:

#                 st.error(
#                     f"🚨 **High anomaly activity detected** — "
#                     f"{anomaly_rate:.2f}% of analyzed events "
#                     f"were flagged."
#                 )

#             elif anomaly_rate > 0:

#                 st.warning(
#                     f"⚠️ **Potential anomalies detected** — "
#                     f"{anomaly_rate:.2f}% of analyzed events "
#                     f"were flagged."
#                 )

#             else:

#                 st.success(
#                     "✅ **No anomalous event sequences detected.**"
#                 )


#             # ------------------------------------------------
#             # Visual Overview
#             # ------------------------------------------------

#             st.markdown(
#                 '<div class="section-title">📈 Visual Overview</div>',
#                 unsafe_allow_html=True
#             )

#             chart_col1, chart_col2 = st.columns(2)

#             with chart_col1:

#                 chart_data = pd.DataFrame({
#                     "Status": ["Normal", "Anomaly"],
#                     "Count": [
#                         normal_count,
#                         anomaly_count
#                     ]
#                 })

#                 st.bar_chart(
#                     chart_data,
#                     x="Status",
#                     y="Count",
#                     use_container_width=True
#                 )

#             with chart_col2:

#                 event_distribution = (
#                     results["Actual Event"]
#                     .value_counts()
#                     .head(10)
#                 )

#                 st.bar_chart(
#                     event_distribution,
#                     use_container_width=True
#                 )


#             # ------------------------------------------------
#             # Detection Results
#             # ------------------------------------------------

#             st.markdown(
#                 '<div class="section-title">🔎 Detection Results</div>',
#                 unsafe_allow_html=True
#             )

#             # Interactive filter
#             filter_option = st.selectbox(
#                 "Filter results",
#                 [
#                     "All Events",
#                     "Anomalies Only",
#                     "Normal Only"
#                 ]
#             )

#             if filter_option == "Anomalies Only":

#                 display_results = results[
#                     results["Anomaly"] == True
#                 ]

#             elif filter_option == "Normal Only":

#                 display_results = results[
#                     results["Anomaly"] == False
#                 ]

#             else:

#                 display_results = results


#             st.dataframe(
#                 display_results,
#                 use_container_width=True,
#                 hide_index=True,
#                 height=520
#             )


#             # ------------------------------------------------
#             # Download Results
#             # ------------------------------------------------

#             csv = results.to_csv(
#                 index=False
#             ).encode("utf-8")

#             st.download_button(
#                 label="⬇️ Download Full Detection Report",
#                 data=csv,
#                 file_name="logsentinel_results.csv",
#                 mime="text/csv"
#             )


# # ============================================================
# # FOOTER
# # ============================================================

# st.markdown("---")

# st.caption(
#     "🛡️ LogSentinel • Deep Learning based Log Anomaly Detection"
# )




































































import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import json


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LogSentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM UI
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #0b0f14;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .hero {
        padding: 1rem 0 1.5rem 0;
    }

    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: #9ca3af;
        margin-bottom: 1rem;
    }

    .badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #60a5fa;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    div[data-testid="stMetric"] {
        background: #111720;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.18);
    }

    div[data-testid="stMetricLabel"] {
        color: #9ca3af;
    }

    div[data-testid="stMetricValue"] {
        font-weight: 700;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 0.8rem;
    }

    .info-card {
        background: #111720;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }

    .info-label {
        color: #9ca3af;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    .info-value {
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }

    section[data-testid="stFileUploaderDropzone"] {
        background: #111720;
        border: 1px dashed #374151;
        border-radius: 14px;
    }

    .stDownloadButton button {
        border-radius: 10px;
        font-weight: 600;
    }

    hr {
        border-color: #1f2937;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD MODEL & CONFIGURATION
# ============================================================

@st.cache_resource
def load_model():
    return tf.keras.models.load_model("LogSentinel.keras")


@st.cache_data
def load_config():

    with open("config.json", "r") as f:
        config = json.load(f)

    with open("event_mapping.json", "r") as f:
        event_to_id = json.load(f)

    return config, event_to_id


model = load_model()

config, event_to_id = load_config()

id_to_event = {
    int(v): k
    for k, v in event_to_id.items()
}

SEQUENCE_LENGTH = config["sequence_length"]


# ============================================================
# ANOMALY DETECTION
# CORE LOGIC PRESERVED
# ============================================================

def detect_anomalies(df):

    events = df["EventId"].map(event_to_id)

    unknown_mask = events.isna()

    if unknown_mask.any():

        unknown_events = df.loc[
            unknown_mask,
            "EventId"
        ].unique()

        raise ValueError(
            "Unknown EventId(s) found: "
            + ", ".join(map(str, unknown_events))
        )

    events = events.astype(int).values

    sequences = []
    actual_events = []
    line_numbers = []

    for i in range(SEQUENCE_LENGTH, len(events)):

        sequences.append(
            events[i - SEQUENCE_LENGTH:i]
        )

        actual_events.append(
            events[i]
        )

        line_numbers.append(
            i + 1
        )

    if len(sequences) == 0:

        return pd.DataFrame(
            columns=[
                "Line",
                "Actual Event",
                "Predicted Events",
                "Anomaly"
            ]
        )

    sequences = np.array(sequences)

    actual_events = np.array(actual_events)

    predictions = model.predict(
        sequences,
        batch_size=128,
        verbose=0
    )

    top_3 = np.argsort(
        predictions,
        axis=1
    )[:, -3:]

    anomaly_flags = []

    predicted_events = []

    for i in range(len(actual_events)):

        predicted = [
            id_to_event[event_id]
            for event_id in reversed(top_3[i])
        ]

        predicted_events.append(
            ", ".join(predicted)
        )

        anomaly_flags.append(
            actual_events[i] not in top_3[i]
        )

    results = pd.DataFrame(
        {
            "Line": line_numbers,

            "Actual Event": [
                id_to_event[event_id]
                for event_id in actual_events
            ],

            "Predicted Events": predicted_events,

            "Anomaly": anomaly_flags
        }
    )

    return results


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="badge">
            AI-POWERED LOG MONITORING
        </div>

        <div class="hero-title">
            🛡️ LogSentinel
        </div>

        <div class="hero-subtitle">
            Intelligent Log Anomaly Detection using a
            DeepLog-style LSTM model
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🛡️ LogSentinel")

    st.markdown("---")

    st.markdown("### About")

    st.write(
        "LogSentinel analyzes sequences of system log "
        "events and identifies unusual patterns using "
        "deep learning."
    )

    st.markdown("### Model")

    st.caption("Architecture")
    st.write("LSTM")

    st.caption("Sequence Length")
    st.write(f"{SEQUENCE_LENGTH} events")

    st.caption("Prediction Strategy")
    st.write("Top-3 Event Prediction")

    st.caption("Known Event Types")
    st.write(f"{len(event_to_id)}")

    st.markdown("---")

    st.caption(
        "Built for intelligent system log monitoring."
    )


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📂 Upload Log Data</div>',
    unsafe_allow_html=True
)

st.write(
    "Upload a **structured HDFS log CSV** containing "
    "an `EventId` column."
)

uploaded_file = st.file_uploader(
    "Upload log CSV",
    type=["csv"],
    label_visibility="collapsed"
)


# ============================================================
# PROCESS UPLOADED FILE
# ============================================================

if uploaded_file is not None:

    try:

        df = pd.read_csv(uploaded_file)

        st.success(
            f"Successfully loaded **{len(df):,} log entries**."
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if "EventId" not in df.columns:

            st.error(
                "Invalid file: `EventId` column is missing."
            )

        elif len(df) <= SEQUENCE_LENGTH:

            st.warning(
                f"The file must contain more than "
                f"{SEQUENCE_LENGTH} log entries."
            )

        else:

            # ------------------------------------------------
            # FILE INFORMATION
            # ------------------------------------------------

            info1, info2, info3 = st.columns(3)

            with info1:

                st.markdown(
                    """
                    <div class="info-card">
                        <div class="info-label">
                            File
                        </div>
                        <div class="info-value">
                    """,
                    unsafe_allow_html=True
                )

                st.write(uploaded_file.name)

                st.markdown(
                    """
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with info2:

                st.markdown(
                    """
                    <div class="info-card">
                        <div class="info-label">
                            Log Entries
                        </div>
                        <div class="info-value">
                    """,
                    unsafe_allow_html=True
                )

                st.write(f"{len(df):,}")

                st.markdown(
                    """
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with info3:

                st.markdown(
                    """
                    <div class="info-card">
                        <div class="info-label">
                            Event Types
                        </div>
                        <div class="info-value">
                    """,
                    unsafe_allow_html=True
                )

                st.write(
                    df["EventId"].nunique()
                )

                st.markdown(
                    """
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ------------------------------------------------
            # RUN DETECTION
            # ------------------------------------------------

            with st.spinner(
                "🔍 Analyzing log event sequences..."
            ):

                results = detect_anomalies(df)


            # ------------------------------------------------
            # STATISTICS
            # ------------------------------------------------

            anomaly_count = int(
                results["Anomaly"].sum()
            )

            normal_count = (
                len(results) - anomaly_count
            )

            anomaly_rate = (
                anomaly_count / len(results) * 100
                if len(results) > 0
                else 0
            )


            # ------------------------------------------------
            # METRICS
            # ------------------------------------------------

            st.markdown(
                '<div class="section-title">'
                '📊 Detection Overview'
                '</div>',
                unsafe_allow_html=True
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Logs Analyzed",
                    f"{len(results):,}"
                )

            with col2:

                st.metric(
                    "Normal",
                    f"{normal_count:,}"
                )

            with col3:

                st.metric(
                    "Anomalies",
                    f"{anomaly_count:,}"
                )

            with col4:

                st.metric(
                    "Anomaly Rate",
                    f"{anomaly_rate:.2f}%"
                )


            # ------------------------------------------------
            # STATUS MESSAGE
            # ------------------------------------------------

            if anomaly_rate >= 10:

                st.error(
                    f"🚨 **High anomaly activity detected** — "
                    f"{anomaly_rate:.2f}% of analyzed events "
                    f"were flagged."
                )

            elif anomaly_rate > 0:

                st.warning(
                    f"⚠️ **Potential anomalies detected** — "
                    f"{anomaly_rate:.2f}% of analyzed events "
                    f"were flagged."
                )

            else:

                st.success(
                    "✅ **No anomalous event sequences detected.**"
                )


            # ------------------------------------------------
            # VISUAL OVERVIEW
            # ------------------------------------------------

            st.markdown(
                '<div class="section-title">'
                '📈 Visual Overview'
                '</div>',
                unsafe_allow_html=True
            )

            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:

                chart_data = pd.DataFrame(
                    {
                        "Status": [
                            "Normal",
                            "Anomaly"
                        ],

                        "Count": [
                            normal_count,
                            anomaly_count
                        ]
                    }
                )

                st.bar_chart(
                    chart_data,
                    x="Status",
                    y="Count",
                    use_container_width=True
                )

            with chart_col2:

                event_distribution = (
                    results["Actual Event"]
                    .value_counts()
                    .head(10)
                )

                st.bar_chart(
                    event_distribution,
                    use_container_width=True
                )


            # ------------------------------------------------
            # DETECTION RESULTS
            # ------------------------------------------------

            st.markdown(
                '<div class="section-title">'
                '🔎 Detection Results'
                '</div>',
                unsafe_allow_html=True
            )

            filter_option = st.selectbox(
                "Filter results",
                [
                    "All Events",
                    "Anomalies Only",
                    "Normal Only"
                ]
            )

            if filter_option == "Anomalies Only":

                display_results = results[
                    results["Anomaly"] == True
                ]

            elif filter_option == "Normal Only":

                display_results = results[
                    results["Anomaly"] == False
                ]

            else:

                display_results = results


            st.dataframe(
                display_results,
                use_container_width=True,
                hide_index=True,
                height=520
            )


            # ------------------------------------------------
            # DOWNLOAD RESULTS
            # ------------------------------------------------

            csv = results.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="⬇️ Download Full Detection Report",
                data=csv,
                file_name="logsentinel_results.csv",
                mime="text/csv"
            )


    except ValueError as e:

        st.error(str(e))

    except Exception as e:

        st.error(
            f"An error occurred while processing "
            f"the file: {e}"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "🛡️ LogSentinel • Deep Learning based "
    "Log Anomaly Detection"
)
