
<!--
Yep bro. **You can delete/close the Colab runtime now.** Your deployed app has everything it needs:

```text
LogSentinel.keras
event_mapping.json
config.json
app.py
requirements.txt
README.md
```

The trained model is already saved and deployed, so **you don't need to keep the Colab GPU/runtime alive**. You may want to keep the notebook itself in Drive as a project/training record, but the active runtime can be terminated.

---

## README.md

For the GitHub repo, I'd make it **professional + detailed**, but not bloated. It should showcase the ML work, architecture, dataset, methodology, results, deployment and usage.

Replace your current `README.md` with this:

````markdown
-->
# 🛡️ LogSentinel

### Intelligent Log Anomaly Detection using Deep Learning

> **LogSentinel** is a lightweight deep-learning system that learns sequential patterns in system logs and identifies unusual event sequences using a DeepLog-style LSTM architecture.

<p align="center">

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?logo=tensorflow)](https://www.tensorflow.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)

</p>

---

## 🚀 Live Demo

### 🌐 [Launch LogSentinel](https://logsentinel---intelligent-log-anomaly-detection-hdrydjzpqyejam.streamlit.app/)

Upload a compatible structured log CSV and let LogSentinel analyze the event sequence for anomalous behavior.

---

# 📌 Overview

Modern computing systems continuously generate logs containing information about processes, services, components and system events.

Manually inspecting thousands of log entries is inefficient and makes it difficult to identify subtle abnormal behavior.

**LogSentinel approaches this problem as a sequential prediction task.**

Instead of explicitly defining rules such as:

```text
IF ERROR → anomaly
````

the model learns:

```text
Previous Event Sequence
        ↓
    LSTM Model
        ↓
Predicted Next Events
        ↓
Compare with Actual Event
        ↓
Normal / Anomaly
```

If the actual next event is not among the model's **Top-3 predicted events**, the event is flagged as anomalous.

---

# 🎯 Objectives

The project was designed around the following goals:

* Detect unusual patterns in system logs
* Model log events as sequential data
* Use deep learning rather than manually written rules
* Keep the model lightweight enough for practical deployment
* Provide an interactive web interface
* Produce interpretable anomaly predictions
* Avoid dependency on external AI APIs

---

# 🧠 Core Approach

LogSentinel follows a **DeepLog-style next-event prediction approach**.

The system converts categorical log events into numerical representations and feeds sequences of previous events into an LSTM network.

For every sequence:

```text
E5 → E26 → E11 → E9 → ... → ?
```

the model predicts the most likely next event.

The actual event is then compared with the model's top predictions.

### Anomaly Rule

```text
Actual Event ∈ Top-3 Predictions
        ↓
      Normal

Actual Event ∉ Top-3 Predictions
        ↓
     Anomaly
```

This allows the system to identify deviations from learned sequential behavior.

---

# 🏗️ Architecture

```text
                 ┌──────────────────────┐
                 │   Structured Logs    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     EventId          │
                 │      Encoding        │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Sequence Construction│
                 │   Length = 10        │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │      Embedding       │
                 │      32 dimensions   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │        LSTM          │
                 │      64 units        │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Dense + Softmax    │
                 │   19 Event Classes   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Top-3 Prediction   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Normal / Anomaly     │
                 └──────────────────────┘
```

---

# ⚙️ Model Architecture

The final LogSentinel model uses a compact neural architecture:

| Layer      | Configuration                   |
| ---------- | ------------------------------- |
| Input      | Sequence of 10 event codes      |
| Embedding  | 32 dimensions                   |
| LSTM       | 64 units                        |
| Output     | 19 event classes                |
| Activation | Softmax                         |
| Optimizer  | Adam                            |
| Loss       | Sparse Categorical Crossentropy |

### Model Size

**26,675 trainable parameters**

Approximate model size:

**~104 KB**

This keeps the model lightweight while still providing meaningful sequential anomaly detection.

---

# 📊 Dataset

The project uses the **HDFS 100K structured log dataset** from the LogPAI/Loglizer ecosystem.

Dataset characteristics used during development:

| Property       |   Value |
| -------------- | ------: |
| Log entries    | 104,815 |
| Event types    |      19 |
| Components     |       8 |
| Missing values |       0 |
| Normal logs    | 101,544 |
| Anomalous logs |   3,271 |

The logs contain fields such as:

```text
LineId
Date
Time
Pid
Level
Component
Content
EventId
EventTemplate
```

The model primarily uses:

```text
EventId
```

as the sequential representation of system behavior.

---

# 🔢 Event Encoding

Categorical event IDs are converted into integer codes before being passed to the neural network.

Example:

```text
E10 → 0
E11 → 1
E13 → 2
...
E9  → 18
```

The mapping is stored separately in:

```text
event_mapping.json
```

This ensures that the exact same encoding is used during deployment.

---

# 🔄 Sequence Generation

A sequence length of **10 events** was selected.

For example:

```text
[E5, E26, E11, E9, E22,
 E5, E26, E11, E9, E22]
```

is used to predict the next event:

```text
Target → E5
```

Sequences are constructed within individual HDFS blocks rather than arbitrarily crossing block boundaries.

---

# 🧪 Training

The dataset was divided chronologically into training and testing portions.

```text
80% → Training
20% → Testing
```

The training sequences contained:

```text
21,018 training sequences
5,255 test sequences
```

Test-set distribution:

```text
Normal   : 4,921
Anomaly  :   334
```

The model was trained using Google Colab with an NVIDIA T4 GPU.

---

# 📈 Training Results

The final model achieved:

```text
Training Accuracy : ~96.43%
Validation Accuracy: ~92.82%
Test Accuracy     : ~91.49%
```

The model was intentionally kept small to balance:

* prediction quality
* training time
* memory requirements
* deployment practicality

---

# 🔍 Anomaly Detection Results

Using the **Top-3 prediction strategy**, the final model achieved:

| Metric    | Normal | Anomaly |
| --------- | -----: | ------: |
| Precision | 95.78% |  88.06% |
| Recall    | 99.67% |  35.33% |
| F1 Score  | 97.69% |  50.43% |

Overall classification accuracy:

**~95.59%**

### Confusion Matrix

```text
                    Predicted
                 Normal  Anomaly

Actual Normal      ...      ...
Actual Anomaly     ...      ...
```

The model performs particularly well at recognizing normal sequential behavior.

The comparatively lower anomaly recall reflects the difficulty of detecting relatively rare anomalous sequences in the dataset.

---

# 💡 Why Top-3 Prediction?

A strict top-1 prediction can be overly sensitive because several event types may represent plausible next events.

Instead, LogSentinel considers the three most likely next events:

```text
Prediction #1
Prediction #2
Prediction #3
```

If the actual event appears in any of these three predictions, it is considered consistent with the learned behavior.

Otherwise:

```text
⚠️ Anomaly
```

This provides a more practical anomaly criterion for sequential logs.

---

# 🖥️ Web Application

The project includes an interactive Streamlit interface.

The dashboard provides:

### 📂 Log Upload

Upload a structured CSV containing an `EventId` column.

### 📊 Detection Overview

Displays:

* Logs analyzed
* Normal events
* Anomalous events
* Anomaly rate

### 📈 Visual Analytics

The dashboard provides visual summaries of:

* Normal vs anomalous events
* Event frequency distribution

### 🔎 Interactive Results

Detection results can be filtered by:

```text
All Events
Anomalies Only
Normal Only
```

### 📥 Export

The complete detection report can be downloaded as:

```text
logsentinel_results.csv
```

---

# 🧰 Technology Stack

### Machine Learning

* Python
* TensorFlow / Keras
* NumPy
* Pandas
* Scikit-learn

### Web Application

* Streamlit

### Development / Training

* Google Colab
* NVIDIA T4 GPU

### Dataset

* HDFS structured logs
* LogPAI / Loglizer ecosystem

---

# 📁 Project Structure

```text
LogSentinel/
│
├── app.py
│
├── LogSentinel.keras
│
├── event_mapping.json
│
├── config.json
│
├── requirements.txt
│
└── README.md
```

### File Description

| File                 | Purpose                                      |
| -------------------- | -------------------------------------------- |
| `app.py`             | Streamlit application and inference pipeline |
| `LogSentinel.keras`  | Trained LSTM model                           |
| `event_mapping.json` | EventId → numerical encoding                 |
| `config.json`        | Model configuration                          |
| `requirements.txt`   | Python dependencies                          |
| `README.md`          | Project documentation                        |

---

# ▶️ Running Locally

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/LogSentinel.git
cd LogSentinel
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 📄 Input Format

LogSentinel currently expects a **structured CSV** containing an:

```text
EventId
```

column.

Example:

```csv
LineId,Date,Time,Pid,Level,Component,Content,EventId,EventTemplate
1,081109,203615,143,INFO,dfs.DataNode,...,E5,...
2,081109,203615,143,INFO,dfs.DataNode,...,E26,...
```

The application validates event IDs against the event mapping used during training.

---

# ⚠️ Important Dataset Compatibility

The current model was trained on **HDFS EventIds**.

Therefore, arbitrary log datasets cannot be uploaded directly.

For example:

```text
HDFS logs
    ↓
Compatible ✅

Hadoop logs
    ↓
Different EventId vocabulary ❌
```

A different log source would require its own preprocessing and potentially model retraining.

---

# 🚀 Deployment

The application is deployed using **Streamlit Community Cloud**.

Deployment flow:

```text
GitHub Repository
        ↓
Streamlit Community Cloud
        ↓
Load TensorFlow Model
        ↓
Interactive Web Application
```

No external AI inference API is required.

---

# 🔬 Research Foundation

The project is primarily inspired by:

### DeepLog

> **DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning**

Min Du, Feifei Li, Guineng Zheng, Vivek Srikumar.

Proceedings of ACM CCS, 2017.

DeepLog introduced a deep-learning-based approach for modeling system log sequences and predicting subsequent log events.

### LogBERT

> **LogBERT: Log Anomaly Detection via BERT**

This work provides a more modern Transformer-based perspective on log anomaly detection.

LogSentinel intentionally uses an LSTM architecture instead of BERT to keep the system lightweight and practical for a fresher-scale deployable project.

---

# 🧠 Design Decisions

### Why LSTM?

System logs are sequential by nature.

An LSTM can capture temporal dependencies between previous log events while remaining considerably smaller than Transformer-based alternatives.

### Why 10-event sequences?

A fixed sequence length provides enough local context for next-event prediction while keeping the input representation lightweight.

### Why Top-3?

Multiple event types can be plausible continuations of a sequence.

Top-3 prediction reduces unnecessary false anomaly flags compared with strict top-1 prediction.

### Why a lightweight model?

The project prioritizes:

```text
Practicality
    +
Interpretability
    +
Fast inference
    +
Easy deployment
```

rather than maximizing model size.

---

# 📌 Current Limitations

LogSentinel is intentionally a focused prototype.

Current limitations include:

* Trained specifically on HDFS log event patterns
* Requires structured logs containing compatible `EventId` values
* Does not currently perform automatic raw-log parsing
* Anomaly detection is based on sequential next-event prediction
* Rare anomalies remain more difficult to detect than normal patterns

---

# 🔮 Future Improvements

Potential extensions include:

* Automatic raw log parsing
* Support for multiple log datasets
* Adaptive anomaly thresholds
* Sequence-level anomaly scoring
* Attention-based architectures
* Transformer / LogBERT comparison
* Explainable anomaly reports
* Real-time log stream monitoring
* Multi-dataset benchmarking
* Per-block anomaly visualization

---

# 📚 References

1. M. Du, F. Li, G. Zheng, V. Srikumar.
   **DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning.**
   ACM CCS, 2017.

2. Y. Guo et al.
   **LogBERT: Log Anomaly Detection via BERT.**

3. LogPAI / Loglizer
   HDFS structured log dataset and log analysis resources.

---

# 👨‍💻 Author

**Pratik Maity**

Built as a practical deep-learning project focused on:

```text
Machine Learning
Deep Learning
Anomaly Detection
Sequential Modeling
MLOps / Deployment
```

---

# 📜 License

This project is released under the **MIT License**.

---

<p align="center">

### 🛡️ LogSentinel

**Learn the pattern. Detect the deviation.**

</p>
```
<!--
### One important note

I deliberately **didn't invent a confusion matrix** in the README. We have the exact improved-model precision/recall/F1 and overall accuracy from our work, but the exact confusion-matrix values weren't retained for that final model. Better to leave that out than put fake numbers in a portfolio project.

After replacing the README, your repo will be in a **very solid portfolio-ready state**.
-->
