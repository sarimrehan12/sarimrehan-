import os
import time
import json
import hashlib
import datetime
import random
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
from base64 import urlsafe_b64encode


# ===============================
#     Set Page Configuration
# ===============================
st.set_page_config(
    page_title="Personal Library System",
    page_icon="📚",
    layout="centered"
)


# ===============================
#           Custom CSS
# ===============================
custom_css = """
<style>

    /* ======= Main Header ======= */
    h1.main-header {
        text-align: center;
        font-size: 48px;
        padding: 20px;
        color: #4CAF50;
        font-family: 'Segoe UI', sans-serif;
    }

    /* ======= Subheader ======= */
    h3.sub-header {
        font-size: 24px;
        padding: 10px;
        color: #2e2e2e;
        font-weight: 600;
    }

    /* ======= Success Message ======= */
    .stAlert-success {
        background-color: #e6ffed;
        border-left: 6px solid #2ecc71;
        color: #1e4620;
        padding: 10px;
    }

    /* ======= Warning Message ======= */
    .stAlert-warning {
        background-color: #fff8e1;
        border-left: 6px solid #ff9800;
        color: #665c00;
        padding: 10px;
    }

    /* ======= Book Card ======= */
    .book-card {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        padding: 16px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }

    /* ======= Book Card Hover ======= */
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }

    /* ======= Read Badge ======= */
    .badge-read {
        background-color: #4CAF50;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        margin-right: 5px;
    }

    /* ======= Unread Badge ======= */
    .badge-unread {
        background-color: #f44336;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
    }

    /* ======= Action Button ======= */
    .action-button {
        background-color: #2196F3;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        margin-top: 10px;
        transition: background-color 0.2s ease-in-out;
    }

    .action-button:hover {
        background-color: #1976D2;
    }

</style>
"""

# Apply CSS
st.markdown(custom_css, unsafe_allow_html=True)
# ===============================
#       Part 2: Helper Functions
# ===============================

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def load_library():
    if os.path.exists("library.json"):
        with open("library.json", "r") as file:
            return json.load(file)
    return []

def save_library(library):
    with open("library.json", "w") as file:
        json.dump(library, file, indent=4)

def add_book(author, title, published, genre, read=False):
    book = {
        "author": author,
        "title": title,
        "published": published,
        "genre": genre,
        "read": read
    }
    st.session_state.library.append(book)
    save_library(st.session_state.library)

def remove_book(title):
    st.session_state.library = [book for book in st.session_state.library if book["title"] != title]
    save_library(st.session_state.library)
    st.session_state.book_removed = True

def search_books(library, term, field):
    results = []
    term = term.lower()
    for book in library:
        if term in str(book.get(field, "")).lower():
            results.append(book)
    return results

def get_library_stats():
    stats = {
        "total_books": 0,
        "read_books": 0,
        "genre": {},
        "author": {},
        "decades": {}
    }

    library = st.session_state.library
    if not library:
        return stats

    stats["total_books"] = len(library)
    for book in library:
        if book.get("read"):
            stats["read_books"] += 1
        genre = book.get("genre")
        author = book.get("author")
        year = str(book.get("published"))

        if genre:
            stats["genre"][genre] = stats["genre"].get(genre, 0) + 1
        if author:
            stats["author"][author] = stats["author"].get(author, 0) + 1
        if year.isdigit():
            decade = year[:3] + "0s"
            stats["decades"][decade] = stats["decades"].get(decade, 0) + 1

    return stats
# ===============================
#       Part 3: Visualizations
# ===============================

def create_visualization(stats):
    if stats['total_books']:
        # Read Status Pie Chart
        fig_read = px.pie(
            names=["Read", "Unread"],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            title="Reading Status",
            color_discrete_sequence=["green", "red"]
        )
        fig_read.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_read, use_container_width=True)

        # Genre Chart
        if stats['genre']:
            fig_genre = px.bar(
                x=list(stats['genre'].keys()),
                y=list(stats['genre'].values()),
                title="Books by Genre",
                labels={'x': 'Genre', 'y': 'Count'},
                color_discrete_sequence=["#FFB347"]
            )
            fig_genre.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_genre, use_container_width=True)

        # Decade Chart
        if stats['decades']:
            fig_decades = px.bar(
                x=list(stats['decades'].keys()),
                y=list(stats['decades'].values()),
                title="Books by Decade",
                labels={'x': 'Decade', 'y': 'Count'},
                color_discrete_sequence=["#87CEFA"]
            )
            fig_decades.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_decades, use_container_width=True)
            #PArt 4
            # Load library into session state
st.session_state.library = load_library() if "library" not in st.session_state else st.session_state.library

# Sidebar Navigation Header
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)

# Navigation options
nav_option = st.sidebar.selectbox(
    "Choose an option:",
    ("Home", "Add Book", "Search Books", "Library Statistics")
)

# Lottie animation
book_lottie = load_lottie_url("https://assets1.lottiefiles.com/private_files/lf30_t8gqfbij.json")
if book_lottie:
    st_lottie(book_lottie, height=200)

# Main App Title
st.markdown("<h1 style='text-align:center;'>Personal Library Manager</h1>", unsafe_allow_html=True)

# ADD BOOK SECTION
if nav_option == "Add Book":
    st.markdown("### Add a New Book")

    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("Title")
        author = st.text_input("Author")
        published_year = st.number_input("Published Year", min_value=0, max_value=2100, step=1)

    with col2:
        genre = st.text_input("Genre")
        read_status = st.selectbox("Read Status", ["Read", "Unread"])
        read = True if read_status == "Read" else False

    submit = st.button("Add Book", use_container_width=True)

    if submit and title and author:
        add_book(author, title, published_year, genre, read)
        st.session_state.book_added = True
        st.success("Book added successfully!", icon="✅")

    # Display all books
    elif st.session_state.library:
        col = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with col[i % 2]:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['published_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <span class='{ "read-badge" if book["read"] else "unread-badge"}'>
                        {"Read" if book["read"] else "Unread"}
                    </span>
                    <br><br>
                    <button onclick="window.location.reload(true);" class="action-button">Remove Book</button>
                </div>
                """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        title_to_remove = st.text_input("Enter title of book to remove")

    with col2:
        remove = st.button("Remove Book", use_container_width=True)

    if remove and title_to_remove:
        remove_book(title_to_remove)
        save_library()
        st.rerun()

    if st.session_state.get("book_removed", False):
        st.markdown("<p class='success-message'>Book removed successfully!</p>", unsafe_allow_html=True)
        st.session_state.book_removed = False

# SEARCH & STATS start in Part 5

   
  #===============================

#Part 5: Search + Stats

#===============================

elif st.session_state.current_view == "search": search_by = st.selectbox("Search by", ["Title", "Author", "Genre"]) 
search_term = st.text_input("Enter search term")

if st.button("Search", use_container_width=False):
    if search_term:
        with st.spinner("Searching..."):
            time.sleep(0.5)
            st.session_state.search_results = search_books(st.session_state.library, search_term, search_by)

    if hasattr(st.session_state, "search_results"):
        if st.session_state.search_results:
            st.markdown(f"<h3>Search Results for '{search_term}'</h3>", unsafe_allow_html=True)

            for i, book in enumerate(st.session_state.search_results):
                st.markdown(f"""
                    <div class="book-card">
                        <h4>{book['Title']}</h4>
                        <p><strong>Author:</strong> {book['Author']}</p>
                        <p><strong>Genre:</strong> {book['Genre']}</p>
                        <p><strong>Year:</strong> {book['Year']}</p>
                        <p><strong>Status:</strong> 
                            <span class="{'badge-read' if book['Status'] == 'Read' else 'badge-unread'}">{book['Status']}</span>
                        </p>
                    </div>
                """, unsafe_allow_html=True)

elif st.session_state.current_view == "status": st.markdown(""" <div class='book-card'> <h3>Your Library is empty</h3> <p>Add some books to see the stats.</p> </div> """, unsafe_allow_html=True)

else: stats = get_library_stats(st.session_state.library)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Books", stats['total_books'])
with col2:
    st.metric("Books Read", stats['read_books'])
with col3:
    st.metric("% Read", f"{stats['percent_read']}%")

create_visualization(stats)

if stats['author']:
    st.markdown("<h4>Top Authors in your collection:</h4>", unsafe_allow_html=True)
    top_authors = pd.Series(stats['author']).value_counts().head(5)
    st.write(top_authors)

st.markdown("---")
st.markdown("<p style='text-align:center;'>&copy; 2025 Sarim Personal Library Manager</p>", unsafe_allow_html=True)
