import streamlit as st
import pandas as pd


def show_design():
    st.title("My title")
    st.header("My header")
    st.subheader("My sub")
    st.text("My text")
    st.write("My write")
    st.markdown("_Markdown_ **Markdown**")  # see #*
    st.caption("Caption")
    st.divider()

    st.button("Button")
    st.divider()
    st.checkbox("Checkbox")
    st.divider()
    st.radio("Picker:", ["one", "two"])
    st.divider()
    st.selectbox("Select", [1, 2, 3])
    st.divider()
    st.multiselect("Multiselect", [1, 2, 3])
    st.divider()
    st.slider("Slide me", min_value=0, max_value=10)
    st.divider()
    st.select_slider("Slide to select", options=[1, "2"])
    st.divider()
    st.text_input("Enter some text")
    st.divider()
    st.number_input("Enter a number")
    st.divider()
    st.text_area("Area for textual entry")
    st.divider()
    st.date_input("Date input")
    st.divider()
    st.time_input("Time entry")
    st.divider()
    st.file_uploader("File uploader")
    st.divider()
    st.color_picker("Pick a color")
    st.divider()
    st.write("Table")
    data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    st.table(data.iloc[0:10])
    st.divider()
    st.metric(label="Metrics", value="273 K", delta="1.2 K")
    st.divider()
    # Insert containers separated into tabs:
    tab1, tab2 = st.tabs(["Tab 1", "Tab2"])
    tab1.write("this is tab 1")
    tab2.write("this is tab 2")
    st.divider()

    with st.spinner(text="In progress"):
        st.success("Done")
        st.warning("Warning")
        st.error("Error")

    st.divider()
    # Show and update progress bar
    st.write("Progress bar")
    st.progress(50)

    st.divider()
