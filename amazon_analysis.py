import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import string
import subprocess
import os

# ----------------- PDF File Setup -----------------
pdf_filename = "all_plots.pdf"  # final pdf ka naam
pdf_path = os.path.abspath(pdf_filename)  # full path

# Chrome ka path (Windows default installation)
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# ----------------- Graph Settings -----------------
sns.set_style("whitegrid")
plt.rcParams["figure.autolayout"] = True

# ----------------- Load Dataset -----------------
df = pd.read_csv('bestsellers with categories.csv')
df.rename(columns={"User Rating": "User_Rating"}, inplace=True)

# Author name fix
df.loc[df.Author == 'J. K. Rowling', 'Author'] = 'J.K. Rowling'

# ----------------- Feature Engineering -----------------
# Book name length without spaces
df['name_len'] = df['Name'].apply(lambda x: len(x) - x.count(" "))

# Punctuation % calculation
punctuations = string.punctuation
def count_punc(text):
    count = sum(1 for char in text if char in punctuations)
    return round(count / (len(text) - text.count(" ")) * 100, 3)

df['punc%'] = df['Name'].apply(count_punc)

# ----------------- PDF Export Start -----------------
with PdfPages(pdf_filename) as pdf:

    # 1️⃣ Genre Distribution Pie Chart
    no_dup = df.drop_duplicates('Name')
    g_count = no_dup['Genre'].value_counts()

    fig, ax = plt.subplots(figsize=(8, 8))
    genre_col = sns.color_palette("Set2")

    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return '{p:.2f}%\n({v:d})'.format(p=pct, v=val)
        return my_autopct

    center_circle = plt.Circle((0, 0), 0.7, color='white')
    ax.pie(g_count.values, labels=g_count.index, autopct=make_autopct(g_count.values),
           startangle=90, textprops={'size': 15}, pctdistance=0.5, colors=genre_col)
    ax.add_artist(center_circle)
    plt.title('Distribution of Genre (2009-2019)', fontsize=20, fontweight='bold')
    pdf.savefig()
    plt.close()

    # 2️⃣ Yearly Genre Distribution
    y1 = np.arange(2009, 2014)
    y2 = np.arange(2014, 2020)
    fig, ax = plt.subplots(2, 6, figsize=(14, 7))
    genre_col = sns.color_palette("coolwarm", 2)

    ax[0, 0].pie(g_count.values, autopct='%1.1f%%', startangle=90,
                 textprops={'size': 12, 'color': 'white'}, pctdistance=0.5,
                 radius=1.3, colors=genre_col)
    ax[0, 0].set_title('2009-2019 (Overall)', color='darkgreen', fontsize=13)

    for i, year in enumerate(y1):
        counts = df[df['Year'] == year]['Genre'].value_counts()
        ax[0, i + 1].pie(counts.values, autopct='%1.1f%%', startangle=90,
                         textprops={'size': 12, 'color': 'white'},
                         pctdistance=0.5, colors=genre_col, radius=1.1)
        ax[0, i + 1].set_title(year, color='darkred', fontsize=12)

    for i, year in enumerate(y2):
        counts = df[df['Year'] == year]['Genre'].value_counts()
        ax[1, i].pie(counts.values, autopct='%1.1f%%', startangle=90,
                     textprops={'size': 12, 'color': 'white'},
                     pctdistance=0.5, colors=genre_col, radius=1.1)
        ax[1, i].set_title(year, color='darkred', fontsize=12)

    fig.legend(g_count.index, loc='center right', fontsize=12)
    plt.suptitle('Fiction vs Non-Fiction by Year', fontsize=16, fontweight='bold')
    pdf.savefig()
    plt.close()

    # 3️⃣ Top Authors by Genre
    best_nf_authors = df.groupby(['Author', 'Genre']).agg({'Name': 'count'}).unstack()['Name', 'Non Fiction'].sort_values(ascending=False)[:11]
    best_f_authors = df.groupby(['Author', 'Genre']).agg({'Name': 'count'}).unstack()['Name', 'Fiction'].sort_values(ascending=False)[:11]

    fig, ax = plt.subplots(1, 2, figsize=(10, 8))
    ax[0].barh(best_nf_authors.index, best_nf_authors.values, color=genre_col[0])
    ax[0].set_title('Top Non-Fiction Authors', fontsize=14, fontweight='bold')
    ax[0].invert_yaxis()

    ax[1].barh(best_f_authors.index, best_f_authors.values, color=genre_col[1])
    ax[1].set_title('Top Fiction Authors', fontsize=14, fontweight='bold')
    ax[1].invert_yaxis()

    pdf.savefig()
    plt.close()

    # 4️⃣ Top 20 Authors Detailed View
    n_best = 20
    top_authors = df.Author.value_counts().nlargest(n_best)
    no_dup = df.drop_duplicates('Name')
    fig, ax = plt.subplots(1, 3, figsize=(14, 8), sharey=True)
    color = sns.color_palette("husl", n_best)

    # Appearances
    ax[0].hlines(y=top_authors.index, xmin=0, xmax=top_authors.values, color=color, linestyles='dashed')
    ax[0].plot(top_authors.values, top_authors.index, 'o', color='green', markersize=7)
    ax[0].set_title('Appearances')

    # Unique books
    book_count = [len(no_dup[no_dup.Author == name]['Name']) for name in top_authors.index]
    ax[1].hlines(y=top_authors.index, xmin=0, xmax=book_count, color=color, linestyles='dashed')
    ax[1].plot(book_count, top_authors.index, 'o', color='blue', markersize=7)
    ax[1].set_title('Unique Books')

    # Total reviews
    total_reviews = [no_dup[no_dup.Author == name]['Reviews'].sum() / 1000 for name in top_authors.index]
    ax[2].barh(top_authors.index, total_reviews, color=color, edgecolor='black')
    ax[2].set_title('Total Reviews (in 1000s)')

    plt.suptitle('Top 20 Bestselling Authors (2009-2019)', fontsize=16, fontweight='bold')
    pdf.savefig()
    plt.close()

# ----------------- Final Message & Auto Open -----------------
print(f" All plots saved as {pdf_path}")
subprocess.Popen([chrome_path, f"file:///{pdf_path}"])