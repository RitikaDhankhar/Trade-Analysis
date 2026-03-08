import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Page title
st.title("Trader Behavior Analysis Dashboard")

# Load datasets
trades = pd.read_csv("historical_data.csv")
sentiment = pd.read_csv("fear_greed_index.csv")

# Convert timestamps
trades["date"] = pd.to_datetime(trades["Timestamp IST"], dayfirst=True).dt.date
sentiment["date"] = pd.to_datetime(sentiment["date"], format="mixed", dayfirst=True).dt.date

# Merge datasets
df = pd.merge(trades, sentiment, on="date", how="left")

# ---------------------------------
# Feature Engineering
# ---------------------------------

# Profitability bucket
def profit_bucket(x):
    if x > 0:
        return 1
    else:
        return 0

df["profit_label"] = df["Closed PnL"].apply(profit_bucket)

# Features for model
features = df[["Size USD", "value"]].fillna(0)
target = df["profit_label"]

# Train model
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)

pred = model.predict(X_test)

accuracy = accuracy_score(y_test, pred)

# ---------------------------------
# Show dataset preview
# ---------------------------------

st.subheader("Merged Dataset Preview")
st.dataframe(df.head())

# ---------------------------------
# Prediction Model Result
# ---------------------------------

st.subheader("Prediction Model Performance")

st.write("Model Accuracy:", accuracy)

# ---------------------------------
# User Prediction Input
# ---------------------------------

st.subheader("Predict Trader Profitability")

trade_size = st.number_input("Trade Size (USD)", value=1000)
sentiment_value = st.slider("Fear & Greed Index", 0, 100, 50)

if st.button("Predict Profitability"):

    input_data = pd.DataFrame([[trade_size, sentiment_value]],
                              columns=["Size USD", "value"])

    prediction = model.predict(input_data)

    if prediction[0] == 1:
        st.success("Predicted: Profitable Trade")
    else:
        st.error("Predicted: Not Profitable")

# -------------------------------
# Chart 1: Average PnL by Sentiment
# -------------------------------

st.subheader("Average Profit/Loss by Market Sentiment")

pnl_sentiment = df.groupby("classification")["Closed PnL"].mean()

fig, ax = plt.subplots()
pnl_sentiment.plot(kind="bar", ax=ax)

ax.set_xlabel("Market Sentiment")
ax.set_ylabel("Average Closed PnL")
ax.set_title("Average PnL by Market Sentiment")

st.pyplot(fig)

# -------------------------------
# Chart 2: Trade Size vs Profit
# -------------------------------

st.subheader("Trade Size vs Profit")

fig2, ax2 = plt.subplots()
ax2.scatter(df["Size USD"], df["Closed PnL"])

ax2.set_xlabel("Trade Size (USD)")
ax2.set_ylabel("Closed PnL")
ax2.set_title("Trade Size vs Profit")

st.pyplot(fig2)

# -------------------------------
# Chart 3: Most Traded Coins
# -------------------------------

st.subheader("Top 10 Most Traded Coins")

coin_counts = df["Coin"].value_counts().head(10)

fig3, ax3 = plt.subplots()
coin_counts.plot(kind="bar", ax=ax3)

ax3.set_xlabel("Coin")
ax3.set_ylabel("Number of Trades")
ax3.set_title("Top 10 Most Traded Coins")

st.pyplot(fig3)