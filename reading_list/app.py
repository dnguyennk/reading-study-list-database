# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
DATABASE = 'test_database.db'

# Table to Primary Key mapping
table_keys = {
    'BOOK': 'Book_id',
    'USER': 'User_id',
}

# Utility to get database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/er_model')
def er_model():
    return render_template('er_model.html')

@app.route('/view/<table>', methods=['GET'])
def view_entries(table):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    conn.close()
    return render_template('list.html', rows=rows, table=table, primary_key=table_keys[table])

@app.route('/addBookToReadingList', methods=['GET', 'POST'])
def add_reading_list():
    if request.method == "GET":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM User")
        rows = cursor.fetchall()
        cursor.execute(f"SELECT * FROM Reading_list")
        read_rows = cursor.fetchall()
        cursor.execute(f"SELECT * FROM Book")
        list_book = cursor.fetchall()
        conn.close()
        return render_template('add_reading_list.html', rows=rows, table=read_rows, dropdown=list_book)
    else:
        readingList_id = request.form['reading_name']
        book_id = request.form['book_name']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO Processes_on (Book_id, List_id, Process, Notes) VALUES({book_id},{readingList_id}, 'not_started', 'Note') ON CONFLICT(List_id, Book_id) DO NOTHING")
        conn.commit()
        return render_template('home.html')
    
@app.route('/add_book', methods=['POST', 'GET'])
def add_book():
    if request.method == 'POST':
        try:
            # Get form data
            isbn = request.form['isbn']
            title = request.form['title']
            published_year = request.form['published_year']
            genre = request.form['genre']
            author = request.form['author']

            # Connect to the database and execute the query
            with sqlite3.connect('test_database.db') as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO Book (ISBN, Title, Published_year, Genre, Author) VALUES (?, ?, ?, ?, ?)",
                    (isbn, title, published_year, genre, author)
                )
                con.commit()
                flash("Book added successfully!", "success")
        except sqlite3.Error as e:
            con.rollback()
            flash(f"Database error: {e}", "danger")
        finally:
            con.close()

        # Redirect to home after adding the book
        return redirect(url_for('add_book'))


    # If GET request, render the form
    return render_template('add_book.html')

        
@app.route('/view_reading_list/', methods=['GET'])
def view_reading_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch all reading lists for dropdown
    cursor.execute(f"SELECT * FROM Reading_list")
    all_reading_lists = cursor.fetchall()
    # Fetch books for the selected reading list
    cursor.execute("""
    SELECT 
    READING_LIST.List_name AS Reading_List,
    BOOK.Title AS Book_Title,
    USER.Username AS User_Name,
    COLLABORATION.Role AS Role,
    Access.Permission_level AS Permission_Level,
    PROCESSES_ON.PROCESS AS Process
    FROM READING_LIST
    INNER JOIN PROCESSES_ON ON READING_LIST.List_id = PROCESSES_ON.List_id
    INNER JOIN BOOK ON PROCESSES_ON.Book_id = BOOK.Book_id
    INNER JOIN USER ON READING_LIST.User_id = USER.User_id
    LEFT JOIN COLLABORATION ON COLLABORATION.User_id = USER.User_id
    LEFT JOIN Access ON Access.USER_id = READING_LIST.USER_id
    ORDER BY READING_LIST.List_id;
    """)
    rows = cursor.fetchall()
    conn.close()

    # Pass data to the template
    return render_template('view_reading_list.html',
            rows=rows,
            all_reading_lists=all_reading_lists)      
    
@app.route('/eachList', methods=['GET'])
def search_book():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch all reading lists for dropdown
    cursor.execute(f"SELECT * FROM Reading_list")
    all_reading_lists = cursor.fetchall()
    conn.close()

    # Pass data to the template
    return render_template('eachList.html',
            dropdown=all_reading_lists)

@app.route('/result', methods=['POST'])
def result():
    conn = get_db_connection()
    cursor = conn.cursor()
    list_id = request.form['List']
    
    # Fetch all reading lists for dropdown
    cursor.execute(f"SELECT BOOK.* FROM BOOK INNER JOIN PROCESSES_ON ON PROCESSES_ON.List_id = {list_id} AND BOOK.Book_id = PROCESSES_ON.Book_id")
    all_books = cursor.fetchall()
    conn.close()

    # Pass data to the template
    return render_template('result.html',
            all_books = all_books)         
    
@app.route('/bookByGenre', methods=['GET'])
def bookByGenre():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch all reading lists for dropdown
    cursor.execute(f"SELECT distinct GENRE FROM BOOK")
    all_reading_lists = cursor.fetchall()
    conn.close()

    # Pass data to the template
    return render_template('bookByGenre.html',
            dropdown=all_reading_lists)

@app.route('/result2', methods=['GET','POST'])
def result2():
    conn = get_db_connection()
    cursor = conn.cursor()
    genre = 'a'
    if request.method == 'POST':
        genre = request.form['Genre']
    else:
        genre = request.args.get('genre')
    print(genre)
    # Fetch all reading lists for dropdown
    cursor.execute(f"SELECT * FROM BOOK WHERE Genre = '{genre}'")
    all_books = cursor.fetchall()
    conn.close()

    # Pass data to the template
    return render_template('result2.html',
            all_books = all_books)
         


@app.route('/edit/<table>/<int:id>', methods=['GET', 'POST'])
def edit_entry(table, id):
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        author = request.form['author']
    
        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"UPDATE {table} SET TITLE = '{title}', GENRE = '{genre}', AUTHOR = '{author}' WHERE Book_id = {id}"
        cursor.execute(query)
        conn.commit()
        conn.close()

        return redirect(url_for('view_entries', table=table))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE Book_id = {id}")
        row = cursor.fetchall()
        print(row)
        conn.close()
        return render_template('edit.html', row=row[0], table=table)
    except sqlite3.Error as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('home'))
   
@app.route('/delete/<table>/<int:id>', methods=['POST'])
def delete_entry(table, id):
    primary_key = table_keys.get(table)
    if not primary_key:
        flash("Invalid table for deleting.", "danger")
        return redirect(url_for("home"))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE {primary_key} = ?", (id,))
        conn.commit()
        conn.close()
        flash(f"Deleted entry from {table}.", "success")
    except sqlite3.Error as e:
        flash(f"Error deleting entry: {e}", "danger")
    return redirect(url_for("view_entries", table=table))

if __name__ == '__main__':
    app.run(debug=True)
