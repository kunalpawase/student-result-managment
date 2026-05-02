from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import time
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

# ── Logging Setup ─────────────────────────────────────────────────────────────
log_dir = '/app/logs'
os.makedirs(log_dir, exist_ok=True)

handlers = [logging.StreamHandler()]
try:
    handlers.append(RotatingFileHandler(f'{log_dir}/app.log', maxBytes=1_000_000, backupCount=3))
except PermissionError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

# ── Database ──────────────────────────────────────────────────────────────────
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'mysql'),
        user=os.environ.get('DB_USER', 'app_user'),
        password=os.environ.get('DB_PASSWORD', 'securepassword123'),
        database=os.environ.get('DB_NAME', 'student_db')
    )

def init_db():
    for attempt in range(1, 31):
        try:
            conn = mysql.connector.connect(
                host=os.environ.get('DB_HOST', 'mysql'),
                user='root',
                password=os.environ.get('DB_ROOT_PASSWORD', 'rootpassword123')
            )
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS student_db")
            cursor.execute("USE student_db")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    roll_number VARCHAR(50) NOT NULL,
                    subject VARCHAR(100) NOT NULL,
                    marks INT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE USER IF NOT EXISTS 'app_user'@'%'
                IDENTIFIED BY %s
            """, (os.environ.get('DB_PASSWORD', 'securepassword123'),))
            cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON student_db.* TO 'app_user'@'%'")
            cursor.execute("FLUSH PRIVILEGES")
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Database initialized successfully")
            return
        except mysql.connector.Error as err:
            logger.warning(f"DB connection attempt {attempt}/30 failed: {err}")
            time.sleep(2)
    raise RuntimeError("Could not connect to database after 30 attempts")

# ── Helpers ───────────────────────────────────────────────────────────────────
def calculate_grade(marks):
    if marks >= 90: return 'A'
    if marks >= 75: return 'B'
    if marks >= 60: return 'C'
    return 'D'

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    logger.info("Home page accessed")
    return render_template('index.html')

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name        = request.form['name']
        roll_number = request.form['roll_number']
        subject     = request.form['subject']
        marks       = int(request.form['marks'])

        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO results (name, roll_number, subject, marks) VALUES (%s, %s, %s, %s)",
            (name, roll_number, subject, marks)
        )
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Student added: Roll={roll_number} | Subject={subject} | Marks={marks}")
        return redirect(url_for('view_result'))

    return render_template('add_student.html')

@app.route('/view_result')
def view_result():
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM results ORDER BY marks DESC")
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    for result in results:
        result['grade'] = calculate_grade(result['marks'])

    # Grade distribution counts for chart
    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for r in results:
        grade_counts[r['grade']] += 1

    logger.info(f"Results page accessed — {len(results)} records returned")
    return render_template('view_result.html', results=results, grade_counts=grade_counts)

@app.route('/search')
def search():
    query   = request.args.get('roll_number', '').strip()
    results = []
    if query:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM results WHERE roll_number LIKE %s ORDER BY subject",
            (f'%{query}%',)
        )
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        for r in results:
            r['grade'] = calculate_grade(r['marks'])
        safe_query = ''.join(c for c in query if c.isalnum() or c in '-_')
        logger.info(f"Search: '{safe_query}' — {len(results)} results")
    return render_template('search.html', results=results, query=query)

@app.route('/stats')
def stats():
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Average marks per subject
    cursor.execute("""
        SELECT subject, ROUND(AVG(marks), 2) AS avg_marks,
               MAX(marks) AS highest, MIN(marks) AS lowest,
               COUNT(*) AS total_students
        FROM results
        GROUP BY subject
        ORDER BY avg_marks DESC
    """)
    subject_stats = cursor.fetchall()

    # Topper — highest marks overall
    cursor.execute("""
        SELECT * FROM results
        ORDER BY marks DESC
        LIMIT 1
    """)
    topper = cursor.fetchone()

    # Top scorer per subject
    cursor.execute("""
        SELECT r.* FROM results r
        INNER JOIN (
            SELECT subject, MAX(marks) AS max_marks FROM results GROUP BY subject
        ) t ON r.subject = t.subject AND r.marks = t.max_marks
        ORDER BY r.subject
    """)
    subject_toppers = cursor.fetchall()

    cursor.close()
    conn.close()

    if topper:
        topper['grade'] = calculate_grade(topper['marks'])
    for s in subject_toppers:
        s['grade'] = calculate_grade(s['marks'])

    logger.info("Stats page accessed")
    return render_template('stats.html',
                           subject_stats=subject_stats,
                           topper=topper,
                           subject_toppers=subject_toppers)

@app.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id):
    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results WHERE id = %s", (record_id,))
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Record deleted: id={record_id}")
    return redirect(url_for('view_result'))

@app.route('/health')
def health():
    try:
        conn = get_db_connection()
        conn.close()
        logger.info("Health check: OK")
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'status': 'unhealthy', 'error': str(e)}, 500

if __name__ == '__main__':
    init_db()
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    # 0.0.0.0 is required inside Docker so the container is reachable from outside
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)  # noqa: S104
