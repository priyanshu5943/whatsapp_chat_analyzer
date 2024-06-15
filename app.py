import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns
from whatstk import df_from_txt_whatsapp
import zipfile
import os
from whatstk import FigureBuilder
import plotly.express as px
import plotly
from streamlit_extras.buy_me_a_coffee import button as coffee_button
import plotly.graph_objs as go
import pandas as pd
import tempfile
from pathlib import Path
import zipfile




st.set_page_config(
    page_title="Whatsapp Chat Analyzer",
    page_icon="favicon.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items=None
)
st.title("Whatsapp Chat Analyzer")
# Side bar
with st.sidebar:
    hformat = st.text_input(
        "Header format",
        
    )
    encoding = st.text_input(
        "Encoding",
        value="utf-8",
        help="Encoding of the chat.",
    )


ENCODING_DEFAULT = "utf-8"
st.title("Whatsapp Chat Analyzer")
# uploaded_file = st.sidebar.file_uploader("Choose a file")
uploaded_file = st.file_uploader(
    label="Upload your WhatsApp chat file.",
    type=["txt", "zip"],
    # label_visibility="collapsed",
)
# Define temporary file (chat will be stored here temporarily)
temp_dir = tempfile.TemporaryDirectory()
uploaded_file_path = Path(temp_dir.name) / "chat"

if uploaded_file is not None:

    with open(uploaded_file_path, 'wb') as output_temporary_file:
        output_temporary_file.write(uploaded_file.read())
    
    try:

        if uploaded_file.name.endswith(".zip"):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Uncompress the file
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                files = os.listdir(temp_dir)
                assert len(files) == 1, "Unexpected number of files in the compressed file! Only one is expected (the chat txt file)"
                # Read
                df = df_from_txt_whatsapp(
                    temp_dir / Path(files[0]),
                    hformat=hformat,
                    encoding=encoding,
                )

        else:
            df = df_from_txt_whatsapp(
                output_temporary_file.name,
                hformat=hformat,
                encoding=encoding,
            )
    except RuntimeError:
        st.error(
            "The chat could not be parsed automatically! You can try to set custom `hformat` "
            "value in the side bar config."
            "Additionally, please report to https://github.com/lucasrodes/whatstk/issues. If possible, "
            "please provide a sample of your chat (feel free to replace the actual messages with dummy text)."
        )

    data = preprocessor.preprocess(df)

    
    # fetch unique users
    user_list = data['username'].unique().tolist()
    user_list.sort()
    user_list.insert(0,"Overall")
    st.title('Select a User')
    selected_user = st.selectbox('',user_list)

    if st.button("Show Analysis"):



        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user,data)
        fig,ax = plt.subplots()
        fig = px.line(timeline, x='time', y='message', color_discrete_sequence=['yellow'])

        fig.update_layout(
            
            width=800,  # Adjust width as needed
            height=400,  # Adjust height as needed
            xaxis=dict(
                title="Month",
                title_font=dict(size=23, family="Arial, sans-serif", color="white"),
            ),
            yaxis=dict(
                title="Message",
                title_font=dict(size=23, family="Arial, sans-serif", color="white"),
            ),
            font=dict(size=12, family="Arial, sans-serif", color="black"),  # Adjust font globally if needed
            showlegend=False,  # Optionally hide legend
        )
        fig.update_traces(line=dict(width=3)) 
        fig.update_xaxes(tickangle=-45)
        fig
       

        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, data)
        fig, ax = plt.subplots()
        fig = px.line(daily_timeline, x='only_date', y='message',  color_discrete_sequence=['yellow'])
        fig.update_layout(
            
            width=800,  # Adjust width as needed
            height=400,  # Adjust height as needed
            xaxis=dict(
                title="Date",
                title_font=dict(size=23, family="Arial, sans-serif", color="white"),
            ),
            yaxis=dict(
                title="Message",
                title_font=dict(size=23, family="Arial, sans-serif", color="white"),
            ),
            font=dict(size=12, family="Arial, sans-serif", color="black"),  # Adjust font globally if needed
            showlegend=False,  # Optionally hide legend
        )
        fig.update_traces(line=dict(width=3)) 
        fig       

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,data)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        st.title("Interaction between Users")
        data_whatsapp = df[['date','username','message']]
        fig = FigureBuilder(data_whatsapp).user_message_responses_heatmap(title=None)
        fig.update_xaxes(tickangle=-45)
        fig.update_layout(
            width=1800,  # Set the width
            height=500  # Set the height
        )
        fig.update_xaxes(
            title_font={"size": 20},  # Increase x-axis label font size
            # Increase x-axis tick font size
        )

        fig.update_yaxes(
            title_font={"size": 20},  # Increase y-axis label font size
            # Increase y-axis tick font size
        )

        st.plotly_chart(fig)

        st.title('User message_length')

        fig = FigureBuilder(data_whatsapp).user_msg_length_boxplot(title=None)
        fig.update_xaxes(tickangle=-45)
        fig.update_xaxes(
            title_font={"size": 30},  # Increase x-axis label font size
             # Increase x-axis tick font size
        )

     
        st.plotly_chart(fig)



        


        # activity map
        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user,data)
            fig,ax = plt.subplots()
            fig=px.bar(x=busy_day.index,y=busy_day.values,color=busy_day.index,labels={'x': 'Day', 'y': 'Activity Count'})
            fig.update_xaxes(tickangle=-45)
            fig.update_layout(
            width=1800,  # Set the width
            height=400  # Set the height
            )
            fig.update_xaxes(
            title_font={"size": 20},  # Increase x-axis label font size
            # Increase x-axis tick font size
            )

            fig.update_yaxes(
            title_font={"size": 20},  # Increase y-axis label font size
            # Increase y-axis tick font size
            )

            fig

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, data)
            fig, ax = plt.subplots()
            fig=px.bar(x=busy_month.index,y=busy_month.values,labels={'x': 'Month', 'y': 'Activity Count'},color=busy_month.index)
            fig.update_xaxes(tickangle=-45)
            fig.update_layout(
            width=1800,  # Set the width
            height=400  # Set the height
            )
            fig.update_xaxes(
            title_font={"size": 20},  # Increase x-axis label font size
            # Increase x-axis tick font size
            )

            fig.update_yaxes(
            title_font={"size": 20},  # Increase y-axis label font size
            # Increase y-axis tick font size
            )
            fig
        

       

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,data)

        fig,ax = plt.subplots()
        fig, ax = plt.subplots(figsize=(10, 3))
        ax=sns.heatmap(user_heatmap, linewidths=0.5,  cmap='coolwarm', annot=True, annot_kws={'size': 5})
        ax.set_xlabel('period',fontsize=20)
        ax.set_ylabel('day',fontsize=20)
        st.pyplot(fig)

        # finding the busiest users in the group(Group level)
       
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x,new_df = helper.most_busy_users(data)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)
            user_counts_df = pd.DataFrame({'username': x.index, 'count': x.values})
            fig = px.bar(user_counts_df, x='username', y='count', color='username', labels={'username': 'username', 'count': 'Message Count'})
            fig.update_xaxes(tickangle=-45)
            fig.update_xaxes(
            title_font={"size": 20},  # Increase x-axis label font size
            # Increase x-axis tick font size
            )

            fig.update_yaxes(
            title_font={"size": 20},  # Increase y-axis label font size
            # Increase y-axis tick font size
            )
            with col1:
                fig
               
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user,data)
        fig, ax = plt.subplots(figsize=(15, 3))
        ax.imshow(df_wc)
        ax.axis('off')

        st.pyplot(fig)

        # most common words
        most_common_df = helper.most_common_words(selected_user,data)

        fig,ax = plt.subplots()
        st.title('Most commmon words')
        # ax.barh(most_common_df[0],most_common_df[1])
        fig = px.bar(most_common_df, x=0, y=1, color=0)
        fig.update_layout(
            xaxis_title='words',
            yaxis_title='count',
            xaxis=dict(tickangle=-90)  # Rotate x-axis labels
             # Increase font size for labels
        )
        fig.update_xaxes(
            title_font={"size": 20},  # Increase x-axis label font size
            # Increase x-axis tick font size
            )

        fig.update_yaxes(
            title_font={"size": 20},  # Increase y-axis label font size
            # Increase y-axis tick font size
            )
        fig.update_xaxes(tickangle=-45)

        fig
        
       
        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user,data)
        st.title("Emoji Analysis")

        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig,ax = plt.subplots()
            fig = px.pie(emoji_df.head(25), values=1, labels=emoji_df[0],names=0)
            colours = ['#1f77b4', '#fc6c44', '#2b8a2b', '#fc7c7c', '#9467bd', '#4ba4ad', '#c7ad18', '#7f7f7f', '#69d108', '#1f77b4', '#fc6c44', '#2b8a2b','#fc7c7c', '#9467bd', '#4ba4ad','#c7ad18', '#7f7f7f', '#69d108', '#1f77b4', '#fc6c44', '#2b8a2b','#fc7c7c', '#9467bd', '#4ba4ad','#2b8a2b', '#fc7c7c', '#9467bd', '#4ba4ad', '#c7ad18', '#7f7f7f', '#69d108', '#1f77b4']
            fig.update_traces(marker=dict(colors=colours))
            fig.update_xaxes(
            title_font={"size": 20},  # Increase x-axis label font size
            # Increase x-axis tick font size
            )

            fig.update_yaxes(
            title_font={"size": 20},  # Increase y-axis label font size
            # Increase y-axis tick font size
            )

            fig
            # ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(),autopct="%0.2f")











