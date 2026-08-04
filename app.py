from flask import Flask, render_template, request, redirect, url_for,session,flash
from database import conn, cursor
from werkzeug.utils import secure_filename
import os


app=Flask(__name__)#flask application is being created
app.secret_key="techhub123"

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "email" not in session:
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "admin" not in session:
            return redirect("/admin")

        return f(*args, **kwargs)

    return decorated_function



#Home
@app.route("/")#URL route
def home():
    return render_template("index.html")

#About us
@app.route("/about")#URL route
@login_required
def about():
    return render_template("about.html")



#Resource page
@app.route("/resources")
@login_required
def resources():

    cursor.execute("""
        SELECT * FROM resources
        ORDER BY id DESC
    """)

    resources = cursor.fetchall()

    return render_template(
        "resources.html",
        resources=resources
    )

#resource_details
@app.route("/resource/<int:id>")
@login_required
def resource_details(id):

    cursor.execute(
        "SELECT * FROM resources WHERE id=%s",
        (id,)
    )

    resource = cursor.fetchone()

    if not resource:
        flash("Resource not found.", "danger")
        return redirect("/resources")

    return render_template(
        "resource_details.html",
        resource=resource
    )

#add_resources
@app.route("/add_resource", methods=["GET", "POST"])
@admin_required
def add_resource():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        notes = request.form["notes"]
        link = request.form["link"]

        # Check if the resource already exists
        cursor.execute(
            "SELECT * FROM resources WHERE title = %s",
            (title,)
        )

        existing_resource = cursor.fetchone()

        if existing_resource:
            flash("A resource with this title already exists.", "warning")
            return redirect("/add_resource")

        cursor.execute(
            """
            INSERT INTO resources(title, description,notes, link)
            VALUES(%s, %s, %s, %s)
            """,
            (title, description, notes, link)
        )

        conn.commit()

        flash("Resource added successfully!", "success")

        return redirect("/admin_dashboard")

    return render_template("add_resource.html")

#manage_resources
@app.route("/manage_resources")
@admin_required
def manage_resources():

    cursor.execute("""
        SELECT * FROM resources
        ORDER BY id DESC
    """)

    resources = cursor.fetchall()

    return render_template(
        "manage_resources.html",
        resources=resources
    )

#delete_resource
@app.route("/delete_resource/<int:id>")
@admin_required
def delete_resource(id):

    cursor.execute(
        "DELETE FROM resources WHERE id=%s",
        (id,)
    )

    conn.commit()

    flash("Resources deleted successfully.","danger")

    return redirect("/manage_resources")

#edit_resource
@app.route("/edit_resource/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_resource(id):

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        notes = request.form["notes"]
        link = request.form["link"]

        cursor.execute("""
            UPDATE resources
            SET title=%s,
                description=%s,
                notes=%s,
                link=%s
            WHERE id=%s
        """, (title, description, notes, link, id))

        conn.commit()

        flash("Resource updated successfully!", "success")

        return redirect("/manage_resources")

    cursor.execute(
        "SELECT * FROM resources WHERE id=%s",
        (id,)
    )

    resource = cursor.fetchone()

    return render_template(
        "edit_resource.html",
        resource=resource
    )

#gallery
@app.route("/gallery")
@login_required
def gallery():

    cursor.execute("""
        SELECT * FROM gallery
        ORDER BY id DESC
    """)

    images = cursor.fetchall()

    return render_template(
        "gallery.html",
        images=images
    )

#add_gallery
@app.route("/add_gallery", methods=["GET", "POST"])
@admin_required
def add_gallery():

    if request.method == "POST":

        title = request.form["title"]

        image = request.files["image"]

        filename = secure_filename(image.filename)

        image.save(os.path.join("static/images", filename))

        cursor.execute(
            """
            INSERT INTO gallery(title, image_url)
            VALUES(%s, %s, %s)
            """,
            (title, filename)
        )

        conn.commit()

        flash("Images uploaded successfully.","success")

        return redirect("/admin_dashboard")

    return render_template("add_gallery.html")

#manage_gallery
@app.route("/manage_gallery")
@admin_required
def manage_gallery():

    cursor.execute("""
        SELECT * FROM gallery
        ORDER BY id DESC
    """)

    images = cursor.fetchall()

    return render_template(
        "manage_gallery.html",
        images=images
    )
#delete_gallery
@app.route("/delete_gallery/<int:id>")
@admin_required
def delete_gallery(id):

    cursor.execute(
        "DELETE FROM gallery WHERE id=%s",
        (id,)
    )

    conn.commit()

    flash("Images deleted successfully.","danger")

    return redirect("/manage_gallery")

#edit gallery
@app.route("/edit_gallery/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_gallery(id):

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]

        cursor.execute("""
            UPDATE gallery
            SET title=%s,
                description=%s
            WHERE id=%s
        """, (title, description, id))

        conn.commit()

        return redirect("/manage_gallery")

    cursor.execute(
        "SELECT * FROM gallery WHERE id=%s",
        (id,)
    )

    image = cursor.fetchone()

    return render_template(
        "edit_gallery.html",
        image=image
    )

#contact

@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        cursor.execute(
            """
            INSERT INTO contact_messages
            (name, email, subject, message)
            VALUES(%s, %s, %s, %s)
            """,
            (name, email, subject, message)
        )

        conn.commit()

        flash("Your message has been sent successfully!", "success")

        return redirect("/contact")

    return render_template("contact.html")

#view_messages
@app.route("/view_messages")
@admin_required
def view_messages():

    cursor.execute("""
        SELECT * FROM contact_messages
        ORDER BY date DESC
    """)

    messages = cursor.fetchall()

    return render_template(
        "view_messages.html",
        messages=messages
    )

#register

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        roll_number = request.form["roll_number"]
        department = request.form["department"]
        semester = request.form["semester"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        # Check if email already exists
        cursor.execute(
            "SELECT * FROM members WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email is already registered. Please use another email.", "warning")
            return redirect("/register")

        # Insert new member
        cursor.execute("""
            INSERT INTO members
            (full_name, roll_number, department, semester, email, phone, password)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            full_name,
            roll_number,
            department,
            semester,
            email,
            phone,
            password
        ))

        conn.commit()

        flash("Registration successful! Please login.", "success")
        return redirect("/login")

    return render_template("register.html")

#login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM members WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            session["email"] = user[5]   # email column
            flash("Login sucessfull Welcome back.","sucess")
            return redirect("/dashboard")
        else:
            flash("Invalid email or password.","danger")
            return "Invalid Email or Password"

    return render_template("login.html")

#dashboard
@app.route("/dashboard")
def dashboard():

    if "email" not in session:
        return redirect("/login")

    cursor.execute(
        "SELECT * FROM members WHERE email=%s",
        (session["email"],)
    )

    member = cursor.fetchone()

    return render_template("dashboard.html", member=member)

#admin_login
@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM admin WHERE email=%s AND password=%s",
            (email, password)
        )

        admin = cursor.fetchone()

        if admin:
            session["admin"] = admin[1]  
            return redirect("/admin_dashboard")
        else:
            return "Invalid Admin Login"

    return render_template("admin_login.html")

#admin_dashboard
@admin_required
@app.route("/admin_dashboard")
def admin_dashboard():

    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]

    return render_template(
        "admin_dashboard.html",
        total_members=total_members
    )

#manage_members

@app.route("/manage_members")
@admin_required
def manage_members():

    search = request.args.get("search")

    if search:
        cursor.execute("""
            SELECT * FROM members
            WHERE full_name ILIKE %s
               OR roll_number ILIKE %s
               OR email ILIKE %s
            ORDER BY id
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("""
            SELECT * FROM members
            ORDER BY id
        """)

    members = cursor.fetchall()

    return render_template(
        "manage_members.html",
        members=members,
        search=search
    )

#delete_members
@app.route("/delete_member/<int:id>")
@admin_required
def delete_member(id):

    cursor.execute("DELETE FROM members WHERE id = %s", (id,))
    conn.commit()

    return redirect("/manage_members")

#Announcement page
@app.route("/announcements")
@login_required
def announcements():

    cursor.execute("""
        SELECT * FROM announcements
        ORDER BY announcement_date DESC
    """)

    announcements = cursor.fetchall()

    from datetime import datetime

    formatted_announcements = []

    for announcement in announcements:
        formatted_date = announcement[5].strftime("%d %B %Y")

        formatted_announcements.append(
            (
                announcement[0],  # id
                announcement[1],  # title
                announcement[2],  # description
                announcement[4],  # category
                formatted_date    # announcement_date
            )
        )

    return render_template(
        "announcements.html",
        announcements=formatted_announcements
    )

  



#add_announcement
@app.route("/add_announcement", methods=["GET", "POST"])
@admin_required
def add_announcement():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        announcement_date = request.form["announcement_date"]

        cursor.execute("""
            INSERT INTO announcements
            (title, description, category, announcement_date)
            VALUES(%s, %s, %s, %s)
        """, (title, description, category, announcement_date))

        conn.commit()

        flash("Announcement added successfully.", "success")

        return redirect("/admin_dashboard")

    return render_template("add_announcement.html")

#manage_announcements
@app.route("/manage_announcements")
@admin_required
def manage_announcements():

    cursor.execute("""
        SELECT * FROM announcements
        ORDER BY announcement_date DESC
    """)

    announcements = cursor.fetchall()

    return render_template(
        "manage_announcements.html",
        announcements=announcements
    )

#delete_announcements
@app.route("/delete_announcement/<int:id>")
@admin_required
def delete_announcement(id):

    cursor.execute(
        "DELETE FROM announcements WHERE id = %s",
        (id,)
    )

    conn.commit()

    flash("Announcement deleted successfully.","danger")

    return redirect("/manage_announcements")

#edit_announcements
@app.route("/edit_announcement/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_announcement(id):

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        announcement_date = request.form["announcement_date"]

        cursor.execute("""
            UPDATE announcements
            SET title=%s,
                description=%s,
                category=%s,
                announcement_date=%s
            WHERE id=%s
        """, (title, description, category, announcement_date, id))

        conn.commit()

        flash("Announcement updated successfully!", "success")

        return redirect("/manage_announcements")

    cursor.execute(
        "SELECT * FROM announcements WHERE id=%s",
        (id,)
    )

    announcement = cursor.fetchone()

    return render_template(
        "edit_announcement.html",
        announcement=announcement
    )

#logout
@app.route("/logout")
def logout():
    session.clear()
    flash ("You have logged out successfully.","info")
    return redirect("/login")

#admin_logout
@app.route("/admin_logout")
@admin_required
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin")

#Run application
if __name__=="__main__":
    app.run(debug=True)