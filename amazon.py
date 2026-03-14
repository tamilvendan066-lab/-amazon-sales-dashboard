# Step 1 — Import libraries
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Step 2 — Load the CSV
df = pd.read_csv(r'C:\Users\tamil\Downloads\amazon.csv')

#EDA------

# Step 3 — Shape (rows, columns)
print("Shape:", df.shape)

# Step 4 — Column names and data types
print("\nData Types:")
print(df.dtypes)

# Step 5 — Missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Step 6 — First 5 rows
print("\nFirst 5 rows:")
print(df.head())

# Step 7 — Basic stats
print("\nBasic Statistics:")
print(df.describe())

#DATA CLEANING------

# CLEAN discounted_price 
df['discounted_price'] = df['discounted_price'].str.replace('₹', '', regex=False)
df['discounted_price'] = df['discounted_price'].str.replace(',', '', regex=False)
df['discounted_price'] = df['discounted_price'].astype(float)

# CLEAN actual_price
df['actual_price'] = df['actual_price'].str.replace('₹', '', regex=False)
df['actual_price'] = df['actual_price'].str.replace(',', '', regex=False)
df['actual_price'] = df['actual_price'].astype(float)

#  CLEAN discount_percentage 
df['discount_percentage'] = df['discount_percentage'].str.replace('%', '', regex=False)
df['discount_percentage'] = df['discount_percentage'].astype(float)

# CLEAN rating 
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

#  CLEAN rating_count
df['rating_count'] = df['rating_count'].str.replace(',', '', regex=False)
df['rating_count'] = pd.to_numeric(df['rating_count'], errors='coerce')

# DROP null rows
df = df.dropna(subset=['rating_count', 'rating'])

#  SPLIT category → main_category
df['main_category'] = df['category'].str.split('|').str[0]

# CONFIRM
print("Shape after cleaning:", df.shape)
print("\nData Types after cleaning:")
print(df[['discounted_price','actual_price','discount_percentage','rating','rating_count']].dtypes)
print("\nMissing values after cleaning:")
print(df.isnull().sum())
print("\nSample of main_category:")
print(df['main_category'].unique())

# Save to SQLite-------

# Step 1 — Create connection to database
# This creates 'amazon.db' file in your Downloads folder
conn = sqlite3.connect(r'C:\Users\tamil\Downloads\amazon.db')

# Step 2 — Write clean DataFrame into SQLite as a table called 'products'
df.to_sql('products', conn, if_exists='replace', index=False)

# Step 3 — Confirm it worked
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM products")
count = cursor.fetchone()[0]
print(f"Total rows in database: {count}")

# Step 4 — Preview first 3 rows from database using SQL
query = "SELECT product_id, product_name, discounted_price, actual_price, rating, main_category FROM products LIMIT 3"
result = pd.read_sql(query, conn)
print("\nFirst 3 rows from database:")
print(result)

# Step 5 — Close connection
conn.close()
print("\nDatabase saved successfully! Check your Downloads folder for 'amazon.db'")

#SQL KPIs Queries-------

# connect to my database
conn = sqlite3.connect(r'C:\Users\tamil\Downloads\amazon.db')

# kpi 1 - top 10 highest rated products
# only including products with more than 1000 reviews
# so we dont get products with just 1 or 2 reviews rated 5 stars
q1 = pd.read_sql("""
    SELECT product_name, rating, rating_count, main_category
    FROM products
    WHERE rating_count > 1000
    ORDER BY rating DESC
    LIMIT 10
""", conn)
print("top 10 highest rated products")
print(q1)

# kpi 2 - top 10 most reviewed products
q2 = pd.read_sql("""
    SELECT product_name, rating_count, rating, main_category
    FROM products
    ORDER BY rating_count DESC
    LIMIT 10
""", conn)
print("\ntop 10 most reviewed products")
print(q2)

# kpi 3 - average discount by category
# using group by to group all products under same category
q3 = pd.read_sql("""
    SELECT main_category,
           ROUND(AVG(discount_percentage), 2) as avg_discount,
           COUNT(*) as total_products
    FROM products
    GROUP BY main_category
    ORDER BY avg_discount DESC
""", conn)
print("\naverage discount by category")
print(q3)

# kpi 4 - which category has best average rating
q4 = pd.read_sql("""
    SELECT main_category,
           ROUND(AVG(rating), 2) as avg_rating,
           COUNT(*) as total_products
    FROM products
    GROUP BY main_category
    ORDER BY avg_rating DESC
""", conn)
print("\naverage rating by category")
print(q4)

# kpi 5 - best value products
# i am filtering products where rating is 4 or above
# and discount is 50% or more
q5 = pd.read_sql("""
    SELECT product_name, rating, discount_percentage,
           actual_price, discounted_price, main_category
    FROM products
    WHERE rating >= 4.0
    AND discount_percentage >= 50
    ORDER BY discount_percentage DESC
    LIMIT 10
""", conn)
print("\nbest value products (high rating + high discount)")
print(q5)

# load data
q1 = pd.read_sql("SELECT product_name, rating, rating_count, main_category FROM products WHERE rating_count > 1000 ORDER BY rating DESC LIMIT 10", conn)
q2 = pd.read_sql("SELECT product_name, rating_count, rating, main_category FROM products ORDER BY rating_count DESC LIMIT 10", conn)
q3 = pd.read_sql("SELECT main_category, ROUND(AVG(discount_percentage),2) as avg_discount FROM products GROUP BY main_category ORDER BY avg_discount DESC", conn)
q4 = pd.read_sql("SELECT main_category, ROUND(AVG(rating),2) as avg_rating FROM products GROUP BY main_category ORDER BY avg_rating DESC", conn)
q5 = pd.read_sql("SELECT product_name, rating, discount_percentage, main_category FROM products WHERE rating >= 4.0 AND discount_percentage >= 50", conn)

conn.close()

# shorten names — THIS IS THE MISSING PART FOR THE CHARTS
q1['short_name'] = q1['product_name'].str[:38]
q2['short_name'] = q2['product_name'].str[:38]

#VISUALIZATION-------

#chart 1 - horizontal bar - top 10 highest rated
plt.figure(figsize=(10, 6))
sns.barplot(data=q1, x='rating', y='short_name', color='#4C72B0')
plt.title('top 10 highest rated products')
plt.xlabel('rating')
plt.ylabel('product')
plt.tight_layout()
plt.savefig(r'C:\Users\tamil\Downloads\chart1_top_rated.png')
plt.show()
print("chart 1 saved!")

#chart 2 - horizontal bar - most reviewed 
plt.figure(figsize=(10, 6))
sns.barplot(data=q2, x='rating_count', y='short_name', color='#2ca02c')
plt.title('top 10 most reviewed products')
plt.xlabel('number of reviews')
plt.ylabel('product')
plt.tight_layout()
plt.savefig(r'C:\Users\tamil\Downloads\chart2_most_reviewed.png')
plt.show()
print("chart 2 saved!")

#chart 3 - pie chart - avg discount by category
plt.figure(figsize=(8, 8))
colors = ['#ff7f0e', '#ff9f3e', '#ffbf6e', '#ffdf9e',
          '#ffe5b4', '#ffd700', '#ffc300', '#ffb300',
          '#ffa500']
plt.pie(
    q3['avg_discount'],
    labels=q3['main_category'],
    colors=colors[:len(q3)],
    autopct='%1.1f%%',
    startangle=140,
    pctdistance=0.85
)
plt.title('average discount % by category')
plt.tight_layout()
plt.savefig(r'C:\Users\tamil\Downloads\chart3_discount_pie.png')
plt.show()
print("chart 3 saved!")

#chart 4 - pie chart - avg rating by category
plt.figure(figsize=(8, 8))
colors2 = ['#9467bd', '#a87cc7', '#bc91d1', '#d0a6db',
           '#e4bbe5', '#c39bd3', '#a569bd', '#8e44ad',
           '#7d3c98']
plt.pie(
    q4['avg_rating'],
    labels=q4['main_category'],
    colors=colors2[:len(q4)],
    autopct='%1.1f%%',
    startangle=140,
    pctdistance=0.85
)
plt.title('average rating by category')
plt.tight_layout()
plt.savefig(r'C:\Users\tamil\Downloads\chart4_rating_pie.png')
plt.show()
print("chart 4 saved!")

#chart 5 - scatter plot - rating vs discount
plt.figure(figsize=(10, 6))
sns.scatterplot(data=q5, x='discount_percentage', y='rating',
                hue='main_category', alpha=0.7, s=80)
plt.title('rating vs discount % (best value products)')
plt.xlabel('discount %')
plt.ylabel('rating')
plt.tight_layout()
plt.savefig(r'C:\Users\tamil\Downloads\chart5_scatter.png')
plt.show()
print("chart 5 saved!")

print("all charts saved!")

# Cleaned data for Power BI------

df.to_csv(r'C:\Users\tamil\Downloads\amazon_clean.csv', index=False)
print("clean data exported!")