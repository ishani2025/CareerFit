import sqlite3

DB_NAME = "career_recommendation.db"


def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS USERS(
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        password TEXT,
        age INTEGER,
        gender TEXT,
        city TEXT
    );

    CREATE TABLE IF NOT EXISTS USER_PROFILE(
        profile_id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE,
        education_level TEXT,
        stream TEXT,
        career_goal TEXT,
        FOREIGN KEY(user_id) REFERENCES USERS(user_id)
    );

    CREATE TABLE IF NOT EXISTS SUBJECTS(
        subject_id INTEGER PRIMARY KEY,
        subject_name TEXT
    );

    CREATE TABLE IF NOT EXISTS USER_SUBJECTS(
        us_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        subject_id INTEGER,
        marks INTEGER,
        FOREIGN KEY(user_id) REFERENCES USERS(user_id),
        FOREIGN KEY(subject_id) REFERENCES SUBJECTS(subject_id)
    );

    CREATE TABLE IF NOT EXISTS INTERESTS(
        interest_id INTEGER PRIMARY KEY,
        interest_name TEXT
    );

    CREATE TABLE IF NOT EXISTS USER_INTERESTS(
        ui_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        interest_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES USERS(user_id),
        FOREIGN KEY(interest_id) REFERENCES INTERESTS(interest_id)
    );

    CREATE TABLE IF NOT EXISTS SKILLS(
        skill_id INTEGER PRIMARY KEY,
        skill_name TEXT
    );

    CREATE TABLE IF NOT EXISTS USER_SKILLS(
        uskill_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        skill_id INTEGER,
        skill_level TEXT,
        FOREIGN KEY(user_id) REFERENCES USERS(user_id),
        FOREIGN KEY(skill_id) REFERENCES SKILLS(skill_id)
    );

    CREATE TABLE IF NOT EXISTS CAREERS(
        career_id INTEGER PRIMARY KEY,
        career_name TEXT,
        description TEXT,
        avg_salary INTEGER
    );

    CREATE TABLE IF NOT EXISTS CAREER_SUBJECTS(
        cs_id INTEGER PRIMARY KEY,
        career_id INTEGER,
        subject_id INTEGER,
        FOREIGN KEY(career_id) REFERENCES CAREERS(career_id),
        FOREIGN KEY(subject_id) REFERENCES SUBJECTS(subject_id)
    );

    CREATE TABLE IF NOT EXISTS CAREER_SKILLS(
        cskill_id INTEGER PRIMARY KEY,
        career_id INTEGER,
        skill_id INTEGER,
        FOREIGN KEY(career_id) REFERENCES CAREERS(career_id),
        FOREIGN KEY(skill_id) REFERENCES SKILLS(skill_id)
    );

    CREATE TABLE IF NOT EXISTS CAREER_INTERESTS(
        ci_id INTEGER PRIMARY KEY,
        career_id INTEGER,
        interest_id INTEGER,
        FOREIGN KEY(career_id) REFERENCES CAREERS(career_id),
        FOREIGN KEY(interest_id) REFERENCES INTERESTS(interest_id)
    );

    CREATE TABLE IF NOT EXISTS COURSES(
        course_id INTEGER PRIMARY KEY,
        career_id INTEGER,
        course_name TEXT,
        platform TEXT,
        link TEXT,
        level TEXT,
        duration TEXT,
        FOREIGN KEY(career_id) REFERENCES CAREERS(career_id)
    );

    CREATE TABLE IF NOT EXISTS RECOMMENDATIONS(
        rec_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        career_id INTEGER,
        match_score INTEGER,
        rec_date TEXT,
        FOREIGN KEY(user_id) REFERENCES USERS(user_id),
        FOREIGN KEY(career_id) REFERENCES CAREERS(career_id)
    );

    CREATE TABLE IF NOT EXISTS RATINGS (
        rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        career_id INTEGER,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        feedback TEXT,
        FOREIGN KEY(user_id) REFERENCES USERS(user_id),
        FOREIGN KEY(career_id) REFERENCES CAREERS(career_id)
    );
    """)

    # ---------------- USERS ----------------
    cur.executemany("INSERT OR IGNORE INTO USERS VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (1, 'Riya Sharma', 'riya@gmail.com', 'pass1', 18, 'F', 'Kolkata'),
        (2, 'Arjun Mehta', 'arjun@gmail.com', 'pass2', 19, 'M', 'Delhi'),
        (3, 'Sneha Patel', 'sneha@gmail.com', 'pass3', 20, 'F', 'Mumbai'),
        (4, 'Rahul Verma', 'rahul@gmail.com', 'pass4', 21, 'M', 'Chennai'),
        (5, 'Priya Nair', 'priya@gmail.com', 'pass5', 22, 'F', 'Bangalore'),
        (6, 'Karan Singh', 'karan@gmail.com', 'pass6', 23, 'M', 'Pune'),
        (7, 'Neha Gupta', 'neha@gmail.com', 'pass7', 18, 'F', 'Jaipur'),
        (8, 'Vikram Das', 'vikram@gmail.com', 'pass8', 24, 'M', 'Hyderabad'),
        (9, 'Ananya Roy', 'ananya@gmail.com', 'pass9', 20, 'F', 'Kolkata'),
        (10, 'Rohit Shah', 'rohit@gmail.com', 'pass10', 25, 'M', 'Ahmedabad'),
        (11, 'Meera Iyer', 'meera@gmail.com', 'pass11', 21, 'F', 'Chennai'),
        (12, 'Aditya Kapoor', 'aditya@gmail.com', 'pass12', 22, 'M', 'Delhi')
    ])

    # ---------------- SUBJECTS ----------------
    cur.executemany("INSERT OR IGNORE INTO SUBJECTS VALUES (?, ?)", [
        (1, 'Mathematics'),
        (2, 'Physics'),
        (3, 'Chemistry'),
        (4, 'Biology'),
        (5, 'Computer Science'),
        (6, 'English'),
        (7, 'Economics'),
        (8, 'History'),
        (9, 'Geography'),
        (10, 'Statistics'),
        (11, 'Psychology'),
        (12, 'Business Studies')
    ])

    # ---------------- INTERESTS ----------------
    cur.executemany("INSERT OR IGNORE INTO INTERESTS VALUES (?, ?)", [
        (1, 'Technology'),
        (2, 'Healthcare'),
        (3, 'Finance'),
        (4, 'Design'),
        (5, 'Business'),
        (6, 'AI'),
        (7, 'Cybersecurity'),
        (8, 'Blockchain'),
        (9, 'Robotics'),
        (10, 'Aerospace'),
        (11, 'Environment'),
        (12, 'Gaming'),
        (13, 'UI/UX'),
        (14, 'Cloud'),
        (15, 'Data Engineering'),
        (16, 'Product'),
        (17, 'Law'),
        (18, 'Biotech'),
        (19, 'Automobile'),
        (20, 'Energy')
    ])

    # ---------------- SKILLS ----------------
    cur.executemany("INSERT OR IGNORE INTO SKILLS VALUES (?, ?)", [
        (1, 'Programming'),
        (2, 'Data Analysis'),
        (3, 'Communication'),
        (4, 'Problem Solving'),
        (5, 'Machine Learning'),
        (6, 'Graphic Design'),
        (7, 'Public Speaking'),
        (8, 'Research'),
        (9, 'Leadership'),
        (10, 'Writing'),
        (11, 'Networking'),
        (12, 'Project Management'),
        (13, 'Cybersecurity'),
        (14, 'Cloud Computing'),
        (15, 'UI/UX Design'),
        (16, 'Product Strategy'),
        (17, 'Legal Reasoning'),
        (18, 'Biotechnology'),
        (19, 'Electrical Fundamentals'),
        (20, 'Sustainability')
    ])

    # ---------------- USER PROFILE ----------------
    cur.executemany("INSERT OR IGNORE INTO USER_PROFILE VALUES (?, ?, ?, ?, ?)", [
        (1, 1, '12th', 'Science', 'Software Engineer'),
        (2, 2, '12th', 'Science', 'Doctor'),
        (3, 3, 'Graduate', 'IT', 'Data Scientist'),
        (4, 4, 'Graduate', 'Arts', 'Teacher'),
        (5, 5, 'Graduate', 'Design', 'Designer'),
        (6, 6, 'Graduate', 'Engineering', 'Civil Engineer'),
        (7, 7, '12th', 'Commerce', 'CA'),
        (8, 8, 'Graduate', 'Media', 'Journalist'),
        (9, 9, 'Graduate', 'Psychology', 'Psychologist'),
        (10, 10, 'Graduate', 'Business', 'Marketing'),
        (11, 11, 'Graduate', 'Commerce', 'Banking'),
        (12, 12, 'Postgraduate', 'Science', 'Research')
    ])

    # ---------------- USER SUBJECTS ----------------
    cur.executemany("INSERT OR IGNORE INTO USER_SUBJECTS VALUES (?, ?, ?, ?)", [
        (1, 1, 1, 90), (2, 1, 5, 95),
        (3, 2, 4, 88), (4, 3, 10, 92),
        (5, 4, 6, 85), (6, 5, 6, 80),
        (7, 6, 1, 87), (8, 7, 7, 90),
        (9, 8, 6, 89), (10, 9, 11, 91),
        (11, 10, 7, 88), (12, 11, 7, 85),
        (13, 12, 2, 93)
    ])

    # ---------------- USER INTERESTS ----------------
    cur.executemany("INSERT OR IGNORE INTO USER_INTERESTS VALUES (?, ?, ?)", [
        (1, 1, 1), (2, 2, 2), (3, 3, 6), (4, 4, 4),
        (5, 5, 4), (6, 6, 1), (7, 7, 3), (8, 8, 12),
        (9, 9, 17), (10, 10, 5), (11, 11, 3), (12, 12, 8)
    ])

    # ---------------- USER SKILLS ----------------
    cur.executemany("INSERT OR IGNORE INTO USER_SKILLS VALUES (?, ?, ?, ?)", [
        (1, 1, 1, 'Advanced'),
        (2, 1, 4, 'Intermediate'),
        (3, 2, 8, 'Advanced'),
        (4, 3, 2, 'Advanced'),
        (5, 4, 3, 'Intermediate'),
        (6, 5, 6, 'Advanced'),
        (7, 6, 4, 'Advanced'),
        (8, 7, 2, 'Intermediate'),
        (9, 8, 10, 'Advanced'),
        (10, 9, 8, 'Intermediate'),
        (11, 10, 9, 'Advanced'),
        (12, 11, 2, 'Intermediate'),
        (13, 12, 8, 'Advanced')
    ])

    # ---------------- CAREERS ----------------
    cur.executemany("INSERT OR IGNORE INTO CAREERS VALUES (?, ?, ?, ?)", [
        (1, 'Software Engineer', 'Builds software products and systems', 900000),
        (2, 'Doctor', 'Medical diagnosis and treatment', 1200000),
        (3, 'Data Scientist', 'Extracts insight from data and builds ML systems', 1100000),
        (4, 'Cybersecurity Analyst', 'Protects digital systems and data', 1000000),
        (5, 'Blockchain Developer', 'Builds decentralized applications and smart contracts', 1200000),
        (6, 'Robotics Engineer', 'Designs automation and robotics systems', 1100000),
        (7, 'Aerospace Engineer', 'Works on aircraft and flight systems', 1300000),
        (8, 'Game Developer', 'Builds interactive games and simulations', 950000),
        (9, 'UI/UX Designer', 'Designs user interfaces and user experiences', 850000),
        (10, 'Cloud Engineer', 'Designs and maintains cloud infrastructure', 1150000),
        (11, 'Product Manager', 'Owns product strategy and delivery', 1400000),
        (12, 'Lawyer', 'Handles legal research and advocacy', 1000000),
        (13, 'Biotech Engineer', 'Works on biotech innovation and applications', 1100000),
        (14, 'Energy Engineer', 'Works on power, sustainability and energy systems', 1100000)
    ])

    # ---------------- CAREER SUBJECTS ----------------
    cur.executemany("INSERT OR IGNORE INTO CAREER_SUBJECTS VALUES (?, ?, ?)", [
        (1, 1, 1), (2, 1, 5),
        (3, 2, 4), (4, 2, 3),
        (5, 3, 1), (6, 3, 10),
        (7, 4, 5), (8, 4, 1),
        (9, 5, 5), (10, 5, 7),
        (11, 6, 2), (12, 6, 1),
        (13, 7, 2), (14, 7, 1),
        (15, 8, 5), (16, 8, 6),
        (17, 9, 6), (18, 9, 11),
        (19, 10, 5), (20, 10, 1),
        (21, 11, 12), (22, 11, 7),
        (23, 12, 6), (24, 12, 8),
        (25, 13, 4), (26, 13, 3),
        (27, 14, 2), (28, 14, 1)
    ])

    # ---------------- CAREER SKILLS ----------------
    cur.executemany("INSERT OR IGNORE INTO CAREER_SKILLS VALUES (?, ?, ?)", [
        (1, 1, 1), (2, 1, 4), (3, 1, 5), (4, 1, 11),
        (5, 2, 8), (6, 2, 4), (7, 2, 3),
        (8, 3, 2), (9, 3, 5), (10, 3, 4), (11, 3, 8),
        (12, 4, 13), (13, 4, 4), (14, 4, 1), (15, 4, 11),
        (16, 5, 1), (17, 5, 4), (18, 5, 11), (19, 5, 16),
        (20, 6, 1), (21, 6, 4), (22, 6, 19), (23, 6, 12),
        (24, 7, 4), (25, 7, 19), (26, 7, 8), (27, 7, 12),
        (28, 8, 1), (29, 8, 6), (30, 8, 4), (31, 8, 15),
        (32, 9, 6), (33, 9, 15), (34, 9, 3), (35, 9, 4),
        (36, 10, 1), (37, 10, 14), (38, 10, 11), (39, 10, 12),
        (40, 11, 16), (41, 11, 9), (42, 11, 3), (43, 11, 12),
        (44, 12, 17), (45, 12, 3), (46, 12, 10), (47, 12, 7),
        (48, 13, 18), (49, 13, 8), (50, 13, 4), (51, 13, 5),
        (52, 14, 20), (53, 14, 19), (54, 14, 4), (55, 14, 12)
    ])

    # ---------------- CAREER INTERESTS ----------------
    cur.executemany("INSERT OR IGNORE INTO CAREER_INTERESTS VALUES (?, ?, ?)", [
        (1, 1, 1), (2, 1, 6), (3, 1, 14), (4, 1, 15),
        (5, 2, 2), (6, 2, 18),
        (7, 3, 6), (8, 3, 15), (9, 3, 1),
        (10, 4, 7), (11, 4, 1), (12, 4, 14),
        (13, 5, 8), (14, 5, 1), (15, 5, 5),
        (16, 6, 9), (17, 6, 1), (18, 6, 19),
        (19, 7, 10), (20, 7, 1), (21, 7, 8),
        (22, 8, 12), (23, 8, 4), (24, 8, 1),
        (25, 9, 4), (26, 9, 13), (27, 9, 1),
        (28, 10, 14), (29, 10, 1), (30, 10, 15),
        (31, 11, 16), (32, 11, 5), (33, 11, 3),
        (34, 12, 17), (35, 12, 5), (36, 12, 3),
        (37, 13, 18), (38, 13, 2), (39, 13, 8),
        (40, 14, 20), (41, 14, 11), (42, 14, 1)
    ])

    # ---------------- COURSES ----------------
    cur.executemany("""
        INSERT OR IGNORE INTO COURSES
        (course_id, career_id, course_name, platform, link, level, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        (1, 1, 'CS50: Introduction to Computer Science', 'YouTube',
         'https://www.youtube.com/playlist?list=PLhQjrBD2T383q7Vn8QnTsVgSvyLpsqL_R', 'Beginner', '12 Weeks'),
        (2, 1, 'Python for Beginners', 'Udemy',
         'https://www.udemy.com/courses/search/?q=python%20for%20beginners', 'Beginner', '20 Hours'),
        (3, 1, 'Web Development Bootcamp', 'Udemy',
         'https://www.udemy.com/courses/search/?q=web%20development%20bootcamp', 'Intermediate', '60 Hours'),

        (4, 2, 'Human Biology and Health', 'Coursera',
         'https://www.coursera.org/search?query=human%20biology%20health', 'Beginner', '6 Weeks'),
        (5, 2, 'Medicine and Patient Care', 'YouTube',
         'https://www.youtube.com/results?search_query=medicine+patient+care+course', 'Beginner', '10 Hours'),

        (6, 3, 'Machine Learning Specialization', 'Coursera',
         'https://www.coursera.org/specializations/machine-learning-introduction', 'Intermediate', '3 Months'),
        (7, 3, 'Deep Learning Specialization', 'Coursera',
         'https://www.coursera.org/specializations/deep-learning', 'Advanced', '4 Months'),
        (8, 3, 'Machine Learning Course', 'YouTube',
         'https://www.youtube.com/results?search_query=machine+learning+course+krish+naik', 'Beginner', '15 Hours'),

        (9, 4, 'Google Cybersecurity Professional Certificate', 'Coursera',
         'https://www.coursera.org/professional-certificates/google-cybersecurity', 'Beginner', '6 Months'),
        (10, 4, 'Foundations of Cybersecurity', 'Coursera',
         'https://www.coursera.org/learn/foundations-of-cybersecurity', 'Beginner', '4 Weeks'),
        (11, 4, 'Cybersecurity Basics', 'YouTube',
         'https://www.youtube.com/results?search_query=cybersecurity+course+networkchuck', 'Beginner', '10 Hours'),
        (12, 4, 'Ethical Hacking', 'Udemy',
         'https://www.udemy.com/courses/search/?q=ethical%20hacking', 'Intermediate', '25 Hours'),

        (13, 5, 'Blockchain Development', 'Coursera',
         'https://www.coursera.org/search?query=blockchain%20development', 'Intermediate', '6 Weeks'),
        (14, 5, 'Blockchain Tutorial', 'YouTube',
         'https://www.youtube.com/results?search_query=blockchain+tutorial', 'Beginner', '8 Hours'),

        (15, 6, 'Modern Robotics', 'Coursera',
         'https://www.coursera.org/specializations/modernrobotics', 'Advanced', '4 Months'),
        (16, 6, 'Robotics Full Course', 'YouTube',
         'https://www.youtube.com/results?search_query=robotics+course', 'Beginner', '10 Hours'),

        (17, 7, 'Aerospace Engineering Intro', 'Coursera',
         'https://www.coursera.org/search?query=aerospace%20engineering', 'Intermediate', '6 Weeks'),
        (18, 7, 'Aerospace Engineering Basics', 'YouTube',
         'https://www.youtube.com/results?search_query=aerospace+engineering+course', 'Beginner', '8 Hours'),

        (19, 8, 'Game Design and Development', 'Coursera',
         'https://www.coursera.org/search?query=game%20development', 'Intermediate', '6 Weeks'),
        (20, 8, 'Game Development Course', 'YouTube',
         'https://www.youtube.com/results?search_query=game+development+course', 'Beginner', '10 Hours'),

        (21, 9, 'Google UX Design Professional Certificate', 'Coursera',
         'https://www.coursera.org/professional-certificates/google-ux-design', 'Beginner', '6 Months'),
        (22, 9, 'Foundations of User Experience Design', 'Coursera',
         'https://www.coursera.org/learn/foundations-user-experience-design', 'Beginner', '4 Weeks'),
        (23, 9, 'UX Design Fundamentals', 'YouTube',
         'https://www.youtube.com/results?search_query=ux+design+course', 'Beginner', '8 Hours'),
        (24, 9, 'UI UX Design Bootcamp', 'Udemy',
         'https://www.udemy.com/courses/search/?q=ui%20ux%20design', 'Intermediate', '20 Hours'),

        (25, 10, 'AWS Cloud Practitioner Essentials', 'Coursera',
         'https://www.coursera.org/learn/aws-cloud-practitioner-essentials', 'Beginner', '6 Weeks'),
        (26, 10, 'Cloud Computing Tutorial', 'YouTube',
         'https://www.youtube.com/results?search_query=cloud+computing+tutorial', 'Beginner', '10 Hours'),
        (27, 10, 'AWS Certified Solutions Architect', 'Udemy',
         'https://www.udemy.com/courses/search/?q=aws%20solutions%20architect', 'Advanced', '30 Hours'),

        (28, 11, 'Digital Product Management', 'Coursera',
         'https://www.coursera.org/learn/uva-darden-digital-product-management', 'Intermediate', '5 Weeks'),
        (29, 11, 'Product Management Tutorial', 'YouTube',
         'https://www.youtube.com/results?search_query=product+management+tutorial', 'Beginner', '6 Hours'),
        (30, 11, 'Product Manager Bootcamp', 'Udemy',
         'https://www.udemy.com/courses/search/?q=product%20manager', 'Intermediate', '15 Hours'),

        (31, 12, 'Introduction to Law', 'Coursera',
         'https://www.coursera.org/search?query=law%20introduction', 'Beginner', '6 Weeks'),
        (32, 12, 'Legal Studies Course', 'YouTube',
         'https://www.youtube.com/results?search_query=legal+studies+course', 'Beginner', '5 Hours'),

        (33, 13, 'Biotechnology Course', 'Coursera',
         'https://www.coursera.org/search?query=biotechnology', 'Intermediate', '8 Weeks'),
        (34, 13, 'Biotech Full Course', 'YouTube',
         'https://www.youtube.com/results?search_query=biotechnology+course', 'Beginner', '6 Hours'),

        (35, 14, 'Sustainability and Energy Systems', 'Coursera',
         'https://www.coursera.org/search?query=sustainability%20engineering', 'Intermediate', '8 Weeks'),
        (36, 14, 'Energy Engineering Basics', 'YouTube',
         'https://www.youtube.com/results?search_query=energy+engineering+course', 'Beginner', '6 Hours')
    ])

    # ---------------- RECOMMENDATIONS ----------------
    cur.executemany("INSERT OR IGNORE INTO RECOMMENDATIONS VALUES (?, ?, ?, ?, datetime('now'))", [
        (1, 1, 1, 90),
        (2, 2, 2, 88),
        (3, 3, 3, 92),
        (4, 4, 4, 85),
        (5, 5, 9, 87)
    ])

    # ---------------- RATINGS ----------------
    cur.executemany("""
        INSERT OR IGNORE INTO RATINGS (rating_id, user_id, career_id, rating, feedback)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1, 1, 1, 5, 'Excellent'),
        (2, 2, 2, 4, 'Good'),
        (3, 3, 3, 5, 'Very good'),
        (4, 4, 1, 3, 'Average')
    ])

    conn.commit()
    conn.close()
    print("Database fully created and populated.")


if __name__ == "__main__":
    init_db()