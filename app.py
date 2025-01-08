from datetime import date, datetime
from flask import Flask, jsonify, render_template, redirect, url_for, flash, request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import send_from_directory
from models import ForumComment, ForumFavorite, ForumLike, ForumTopic, Task, db, User, BlogPost, Comment, MoodEntry
from models import BlogPostAdmin
from werkzeug.utils import secure_filename 
from werkzeug.security import generate_password_hash
print(generate_password_hash("test_password", method="pbkdf2:sha256"))
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize serializer with a secret key
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Generate a token
def generate_reset_token(email):
    return s.dumps(email, salt='password-reset-salt')

# Validate a token
def verify_reset_token(token, expiration=3600):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return email

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your email provider's SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'joazx2661@gmail.com'
app.config['MAIL_PASSWORD'] = 'fgoukncccjynmmgq'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

mail=Mail(app)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIDEO_UPLOAD_FOLDER'] = os.path.join('static', 'videos')

app.config['PROFILE_UPLOAD_FOLDER'] = 'static/uploads/profile_images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB file size limit

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configure the main database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spacecampus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
migrate = Migrate(app, db)


# Initialize Flask-Admin
admin = Admin(app, name='Space Campus Admin', template_mode='bootstrap3')
#admin.add_view(ModelView(BlogPost, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(ForumTopic, db.session))
admin.add_view(ModelView(ForumComment, db.session))
admin.add_view(ModelView(ForumLike, db.session))
admin.add_view(ModelView(ForumFavorite, db.session))
admin.add_view(BlogPostAdmin(BlogPost, db.session))



# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Add this logout route to the existing app.py
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

# Routes
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
@login_required  # Ensure only logged-in users can upload files
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File successfully uploaded', 'success')
        return redirect(url_for('dashboard'))  # Redirect to an appropriate page


@app.route('/blog')
@login_required
def blog():
    # Fetch all blog posts from the database
    blog_posts = BlogPost.query.all()  
    return render_template('blog.html', blog_posts=blog_posts)


@app.route('/blog/<int:post_id>', methods=['GET', 'POST'])
@login_required
def blog_post(post_id):
    # Fetch the blog post
    post = BlogPost.query.get_or_404(post_id)

    # Check if post.image exists and assign a default image if missing
    if not post.image:
        post.image = 'images/default_blog_post.png'  # Assign file path, not URL

    # Pagination logic
    page = request.args.get('page', 1, type=int)  # Get the current page from the query string, default to page 1
    per_page = 5  # Number of comments to display per page
    pagination = Comment.query.filter_by(post_id=post.id).order_by(Comment.date.desc()).paginate(page=page, per_page=per_page)

    # Fetch the paginated comments
    comments = pagination.items

    # Handle adding a comment
    if request.method == 'POST':
        author = current_user.username  # Use the logged-in user's username
        content = request.form.get('comment')
        if content:
            new_comment = Comment(post_id=post.id, author=author, content=content.strip(), date=date.today())
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added successfully!', 'comment_success')
            return redirect(url_for('blog_post', post_id=post_id))  # Redirect to the same page to avoid form resubmission
        else:
            flash('Comment cannot be empty.', 'comment_error')

    return render_template(
        'blog_post.html',
        post=post,
        comments=comments,
        pagination=pagination
    )



@app.route('/search_blog', methods=['GET'])
def search_blog():
    query = request.args.get('q', '').strip()  # Trim whitespace
    if query:
        # Query blog posts by title or content
        filtered_posts = BlogPost.query.filter(
            BlogPost.title.ilike(f'%{query}%') | BlogPost.content.ilike(f'%{query}%')
        ).all()
    else:
        filtered_posts = BlogPost.query.all()  # If no query, return all posts
    return render_template('blog.html', blog_posts=filtered_posts, search_query=query)


@app.route('/forum', methods=['GET'])
def forum():
    topics = ForumTopic.query.all()
    return render_template('forum.html', topics=topics)

@app.route('/forum/create', methods=['POST'])
@login_required
def create_topic():
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category')
    image = request.files.get('image')
    video = request.files.get('video')

    if not (title and content and category):
        flash("All fields are required!", "danger")
        return redirect('/forum')

    # Define directories for image and video uploads
    image_upload_folder = 'static/images'
    video_upload_folder = 'static/videos'

    # Ensure directories exist
    os.makedirs(image_upload_folder, exist_ok=True)
    os.makedirs(video_upload_folder, exist_ok=True)

    # Save files to static directory if provided
    image_path = None
    video_path = None
    if image and image.filename != '':
        image_filename = secure_filename(image.filename)
        image_path = f"images/{image_filename}"
        try:
            image.save(os.path.join(image_upload_folder, image_filename))
        except Exception as e:
            flash(f"Image upload failed: {e}", "danger")
            return redirect('/forum')

    if video and video.filename != '':
        video_filename = secure_filename(video.filename)
        video_path = f"videos/{video_filename}"
        try:
            video.save(os.path.join(video_upload_folder, video_filename))
        except Exception as e:
            flash(f"Video upload failed: {e}", "danger")
            return redirect('/forum')

    new_topic = ForumTopic(
        title=title,
        content=content,
        category=category,
        image=image_path if image_path else 'images/default_blog_post.png',  # Use default image if none provided
        video=video_path,
        user_id=current_user.id
    )
    db.session.add(new_topic)
    db.session.commit()

    flash("New topic created successfully!", "success")
    return redirect('/forum')


@app.route('/forum/like/<int:topic_id>', methods=['POST'])
@login_required
def like_topic(topic_id):
    topic = ForumTopic.query.get_or_404(topic_id)
    like = ForumLike.query.filter_by(user_id=current_user.id, topic_id=topic_id).first()
    if like:
        db.session.delete(like)
        flash("You unliked this topic.", "info")
    else:
        new_like = ForumLike(user_id=current_user.id, topic_id=topic_id)
        db.session.add(new_like)
        flash("You liked this topic.", "success")
    db.session.commit()
    return redirect('/forum')

@app.route('/favorites', methods=['GET'])
@login_required
def favorites():
    # Query all favorite topics for the logged-in user
    favorites = ForumFavorite.query.filter_by(user_id=current_user.id).all()
    topics = [favorite.topic for favorite in favorites]  # Retrieve associated topics
    return render_template('favorites.html', topics=topics)


@app.route('/forum/favorite/<int:topic_id>', methods=['POST'])
@login_required
def favorite_topic(topic_id):
    topic = ForumTopic.query.get_or_404(topic_id)
    favorite = ForumFavorite.query.filter_by(user_id=current_user.id, topic_id=topic_id).first()
    if favorite:
        db.session.delete(favorite)
        flash("Removed from favorites.", "info")
    else:
        new_favorite = ForumFavorite(user_id=current_user.id, topic_id=topic_id)
        db.session.add(new_favorite)
        flash("Added to favorites.", "success")
    db.session.commit()
    return redirect('/forum')

@app.route('/forum/<int:topic_id>/add_to_favorites', methods=['POST'])
@login_required
def add_to_favorites(topic_id):
    # Check if the topic is already in the user's favorites
    existing_favorite = ForumFavorite.query.filter_by(topic_id=topic_id, user_id=current_user.id).first()
    if not existing_favorite:
        # Add the topic to favorites
        new_favorite = ForumFavorite(topic_id=topic_id, user_id=current_user.id)
        db.session.add(new_favorite)
        db.session.commit()
        flash('Topic added to your favorites!', 'success')
    else:
        flash('This topic is already in your favorites.', 'info')

    return redirect(url_for('view_topic', topic_id=topic_id))


@app.route('/forum/<int:topic_id>', methods=['GET', 'POST'])
def view_topic(topic_id):
    # Retrieve the topic by ID or return a 404 error if it doesn't exist
    topic = ForumTopic.query.get_or_404(topic_id)
    comments = ForumComment.query.filter_by(topic_id=topic_id).order_by(ForumComment.created_at.desc()).all()

    if request.method == 'POST':
        # Get the comment content from the form
        content = request.form.get('content', '').strip()

        # Ensure the content is not empty
        if not content:
            flash('Comment content cannot be empty.', 'danger')
            return redirect(url_for('view_topic', topic_id=topic_id))

        # Ensure the user is authenticated
        if not current_user.is_authenticated:
            flash('You must be logged in to post a comment.', 'warning')
            return redirect(url_for('login'))

        # Add the new comment to the database
        new_comment = ForumComment(
            content=content,
            topic_id=topic_id,
            user_id=current_user.id,
            created_at=datetime.utcnow()
        )
        try:
            db.session.add(new_comment)
            db.session.commit()
            flash('Your comment has been added!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while adding your comment: {str(e)}', 'danger')
        
        return redirect(url_for('view_topic', topic_id=topic_id))

    # Render the topic and comments on the page
    return render_template('forum_topic.html', topic=topic, comments=comments)





@app.route('/surveys')
@login_required
def surveys():
    return render_template('surveys.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    user = current_user  # Fetch the logged-in user

    # Fetch activity statistics
    activity_stats = {
        "mood_entries": len(user.mood_entries),
        "forum_comments": len(user.forum_comments),
        "forum_topics": len(user.forum_topics),
        "forum_favorites": len(user.forum_favorites),
        "planner_entries": len(user.tasks),  # Use the tasks relationship
    }

    return render_template('profile.html', user=user, activity_stats=activity_stats)

@app.route('/profile/update', methods=['POST'])
@login_required
def profile_update():
    try:
        user = current_user  # Fetch the logged-in user
        print("Debug: Current user fetched:", user.username)

        # Update username
        username = request.form.get('username')
        if username:
            user.username = username.strip()  # Ensure no leading/trailing spaces
            print("Debug: Username updated to:", username.strip())

        # Update email
        email = request.form.get('email')
        if email:
            user.email = email.strip()  # Ensure no leading/trailing spaces
            print("Debug: Email updated to:", email.strip())

        # Update password
        password = request.form.get('password')
        if password:
            if password.strip():  # Ensure the password is not empty or spaces
                hashed_password = bcrypt.generate_password_hash(password.strip()).decode('utf-8')  # Use bcrypt
                user.password = hashed_password
                print("Debug: Password updated successfully.")
            else:
                flash('Password cannot be empty.', 'danger')
                print("Debug: Password update failed - empty password.")
                return redirect(url_for('profile'))

        # Update profile image
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '' and allowed_file(file.filename):  # Validate file
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['PROFILE_UPLOAD_FOLDER'], filename)
                file.save(file_path)
                user.profile_image = filename
                print("Debug: Profile image updated to:", filename)
            elif file.filename == '':
                flash('No file selected for upload.', 'danger')
                print("Debug: No file selected for upload.")
                return redirect(url_for('profile'))
            else:
                flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed!', 'danger')
                print("Debug: Invalid file type.")
                return redirect(url_for('profile'))

        # Save changes to the database
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        print("Debug: Changes committed to the database.")

    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while updating the profile: {str(e)}', 'danger')
        print("Debug: Error occurred:", str(e))

    return redirect(url_for('profile'))

@app.route('/profile/upload-image', methods=['POST'])
@login_required
def upload_profile_image():
    # Check if a file is part of the request
    if 'profile_image' not in request.files:
        flash('No file selected for upload.', 'danger')
        return redirect(url_for('profile'))

    image = request.files['profile_image']

    # Check if the file has a name
    if not image or image.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('profile'))

    # Validate the file type
    if allowed_file(image.filename):
        filename = secure_filename(image.filename)

        # Create a unique filename to prevent overwriting
        unique_filename = f"{current_user.id}_{filename}"
        filepath = os.path.join(app.config['PROFILE_UPLOAD_FOLDER'], unique_filename)

        try:
            # Save the file
            image.save(filepath)

            # If the user already has a profile image, delete the old one
            if current_user.profile_image:
                old_filepath = os.path.join(app.config['PROFILE_UPLOAD_FOLDER'], current_user.profile_image)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

            # Update the user's profile image in the database
            current_user.profile_image = unique_filename
            db.session.commit()

            flash('Profile image updated successfully!', 'success')

        except Exception as e:
            flash('An error occurred while uploading the image. Please try again.', 'danger')
            return redirect(url_for('profile'))
    else:
        flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'danger')

    return redirect(url_for('profile'))


@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    user = current_user

    try:
        # Optionally delete associated profile image file
        if user.profile_image and user.profile_image != 'default-profile.png':  # Adjust default image name if needed
            image_path = os.path.join(app.config['PROFILE_UPLOAD_FOLDER'], user.profile_image)
            if os.path.exists(image_path):
                os.remove(image_path)

        # Delete the user and cascade delete associated data
        db.session.delete(user)
        db.session.commit()

        flash('Your account has been deleted successfully!', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting your account: {str(e)}', 'danger')
        return redirect(url_for('profile'))

@app.route('/profile/activity', methods=['GET'])
@login_required
def activity_data():
    user = current_user
    activity_stats = {
        "mood_entries": len(user.mood_entries),
        "forum_comments": len(user.forum_comments),
        "forum_topics": len(user.forum_topics),
        "forum_favorites": len(user.forum_favorites),
        "planner_entries": len(user.tasks),  # Use the tasks relationship
    }
    return jsonify(activity_stats)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
                               
@app.route('/educator-resources')
@login_required
def educator_resources():
    return render_template('educator_resources.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):  # Consistent with bcrypt
            login_user(user)
            flash('Login successful!', 'login_success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'login_error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate inputs
        if not username or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please use another one.', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another one.', 'danger')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('signup'))

        # Hash password using bcrypt for consistency
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create and save user
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')



@app.route('/moodtracker', methods=['GET', 'POST'])
@login_required
def moodtracker():
    if request.method == 'POST':
        # Get user inputs
        mood = request.form.get('mood')
        journal = request.form.get('journal')

        # Validate mood input
        valid_moods = ["Excited", "Happy", "Neutral", "Stressed", "Sad"]
        if mood not in valid_moods:
            flash("Invalid mood selected. Please choose a valid mood.", "mood_error")
            return redirect(url_for('moodtracker'))

        # Validate journal input
        if not journal or not journal.strip():
            flash("Journal entry cannot be empty. Please write something about your day.", "mood_error")
            return redirect(url_for('moodtracker'))

        # Save the mood entry to the database
        try:
            mood_entry = MoodEntry(
                user_id=current_user.id,
                mood=mood,
                journal=journal.strip(),
                date=date.today()
            )
            db.session.add(mood_entry)
            db.session.commit()
            flash("Mood entry saved successfully!", "mood_success")
        except Exception as e:
            flash(f"An error occurred while saving your mood entry: {str(e)}", "mood_error")
            return redirect(url_for('moodtracker'))

        return redirect(url_for('moodtracker'))

    # Fetch mood entries for the current user, sorted by ascending date
    mood_entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date.asc()).all()

    # Prepare mood data for rendering the chart
    mood_dates = [entry.date.strftime('%Y-%m-%d') for entry in mood_entries]
    mood_scores = [map_mood_to_score(entry.mood) for entry in mood_entries]

    return render_template(
        'moodtracker.html',
        mood_entries=mood_entries,
        mood_dates=mood_dates,
        mood_scores=mood_scores
    )


def map_mood_to_score(mood):
    # Map moods to numerical scores for charting
    mood_mapping = {
        "Excited": 5,
        "Happy": 4,
        "Neutral": 3,
        "Stressed": 2,
        "Sad": 1
    }
    return mood_mapping.get(mood,3)


@app.route('/planner', methods=['GET'])
@login_required
def planner():
    return render_template('planner.html')

@app.route('/get-tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.date, Task.time).all()
    return jsonify({
        "tasks": [{
            "id": task.id,
            "description": task.description,
            "date": task.date.strftime("%Y-%m-%d"),
            "time": task.time.strftime("%H:%M"),
            "type": task.type,
            "completed": task.completed
        } for task in tasks]
    })


@app.route('/add-task', methods=['POST'])
@login_required
def add_task():
    data = request.get_json()
    description = data.get('description')
    date = data.get('date')
    time = data.get('time')
    task_type = data.get('type')

    # Validate input fields
    if not description or not date or not time or not task_type:
        return jsonify({"error": "All fields are required!"}), 400

    try:
        # Create a new task and associate it with the logged-in user
        task = Task(
            description=description,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            time=datetime.strptime(time, "%H:%M").time(),
            type=task_type,
            completed=False,
            user_id=current_user.id  # Associate task with the logged-in user
        )
        db.session.add(task)
        db.session.commit()

        # Return the newly created task as JSON
        return jsonify({
            "message": "Task added successfully!",
            "task": {
                "id": task.id,
                "description": task.description,
                "date": task.date.strftime("%Y-%m-%d"),
                "time": task.time.strftime("%H:%M"),
                "type": task.type,
                "completed": task.completed
            }
        }), 201

    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        return jsonify({"error": f"Error adding task: {str(e)}"}), 500


@app.route('/toggle-task/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()  # Ensure the task belongs to the current user
    if task:
        task.completed = not task.completed
        db.session.commit()
        return jsonify({"message": "Task status updated!"})
    return jsonify({"error": "Task not found or unauthorized access!"}), 404

@app.route('/events')
@login_required
def events():
    return render_template('events.html')

@app.route('/educator-toolkit', methods=['GET'])
@login_required
def educator_toolkit():
    return render_template('educator_toolkit.html')

@app.route('/worksheets', methods=['GET'])
@login_required
def worksheets():
    return render_template('worksheets.html')

@app.route('/presentations', methods=['GET'])
@login_required
def presentations():
    return render_template('presentations.html')

@app.route('/community-collaboration', methods=['GET'])
@login_required
def community_collaboration():
    return render_template('community_collaboration.html')

@app.route('/webinars', methods=['GET'])
@login_required
def webinars():
    return render_template('webinars.html')

@app.route('/certification', methods=['GET'])
@login_required
def certification():
    return render_template('certification.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        # Check if the email exists in the database
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(email)
            reset_url = url_for('reset_with_token', token=token, _external=True)
            send_reset_email(email, reset_url)
            flash('A password reset link has been sent to your email.', 'success')
        else:
            flash('Email address not found.', 'danger')
        return redirect(url_for('reset_password'))
    return render_template('reset_password.html')

def send_reset_email(email, reset_url):
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f'Please click the link to reset your password: {reset_url}'
    mail.send(msg)

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    email = verify_reset_token(token)
    if not email:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('reset_password'))
    if request.method == 'POST':
        new_password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)  # Implement this method in your User model
            db.session.commit()
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('login'))
    return render_template('reset_with_token.html', token=token)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
