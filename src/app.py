import streamlit as st
import pandas as pd
import os


@st.cache_data
def load_data(path: str):
    return pd.read_csv(path)


DATA_PATH = os.path.join("data", "sample", "transactions_sample.csv")


def main():
    st.title("Reporting Automation — Demo")
    df = load_data(DATA_PATH)
    st.subheader("Sample Transactions")
    st.dataframe(df)


if __name__ == "__main__":
    main()
