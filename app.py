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














































































import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import json


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="LogSentinel",
    page_icon="🛡️",
    layout="wide"
)


# --------------------------------------------------
# Load Model & Configuration
# --------------------------------------------------

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
    int(v): k for k, v in event_to_id.items()
}

SEQUENCE_LENGTH = config["sequence_length"]


# --------------------------------------------------
# Anomaly Detection
# --------------------------------------------------

def detect_anomalies(df):

    # Convert EventId → numerical event code
    events = df["EventId"].map(event_to_id)

    # Check for unknown events
    unknown_mask = events.isna()

    if unknown_mask.any():
        unknown_events = df.loc[unknown_mask, "EventId"].unique()

        raise ValueError(
            "Unknown EventId(s) found: "
            + ", ".join(map(str, unknown_events))
        )

    events = events.astype(int).values

    sequences = []
    actual_events = []
    line_numbers = []

    # Build sequences
    for i in range(SEQUENCE_LENGTH, len(events)):

        sequences.append(
            events[i - SEQUENCE_LENGTH:i]
        )

        actual_events.append(events[i])
        line_numbers.append(i + 1)

    # Not enough logs for one sequence
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

    # Batched prediction
    predictions = model.predict(
        sequences,
        batch_size=128,
        verbose=0
    )

    # Get top-3 predicted events
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

    # Build results
    results = pd.DataFrame({
        "Line": line_numbers,

        "Actual Event": [
            id_to_event[event_id]
            for event_id in actual_events
        ],

        "Predicted Events": predicted_events,

        "Anomaly": anomaly_flags
    })

    return results


# --------------------------------------------------
# User Interface
# --------------------------------------------------

st.title("🛡️ LogSentinel")

st.subheader(
    "Intelligent Log Anomaly Detection"
)

st.write(
    "Upload a structured log CSV to detect "
    "unusual event sequences using a DeepLog-style "
    "LSTM model."
)


uploaded_file = st.file_uploader(
    "Upload log CSV",
    type=["csv"]
)


# --------------------------------------------------
# Process Uploaded File
# --------------------------------------------------

if uploaded_file is not None:

    try:

        df = pd.read_csv(uploaded_file)

        st.write(
            f"Loaded **{len(df):,} log entries**."
        )

        # Check required column
        if "EventId" not in df.columns:

            st.error(
                "Invalid file: 'EventId' column is missing."
            )

        elif len(df) <= SEQUENCE_LENGTH:

            st.warning(
                f"The file must contain more than "
                f"{SEQUENCE_LENGTH} log entries."
            )

        else:

            # Run detection
            results = detect_anomalies(df)

            # Statistics
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

            # Metrics
            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Logs Analyzed",
                f"{len(results):,}"
            )

            col2.metric(
                "Normal",
                f"{normal_count:,}"
            )

            col3.metric(
                "Anomalies",
                f"{anomaly_count:,}"
            )

            col4.metric(
                "Anomaly Rate",
                f"{anomaly_rate:.2f}%"
            )

            # Results
            st.subheader(
                "Detection Results"
            )

            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )

            # Download results
            csv = results.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="⬇️ Download Results",
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