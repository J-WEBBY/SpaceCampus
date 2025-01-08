import bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

class BlogPostAdmin(ModelView):
    form_excluded_columns = ['uthor_id']
    def on_model_change(sekf, form, model, is_created):
        model.author_id = 1


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)  # Path to profile image

    # Relationships for activity tracking
    mood_entries = db.relationship('MoodEntry', backref='user', lazy=True, cascade="all, delete-orphan")
    blog_posts = db.relationship('BlogPost', backref='author_user', lazy=True, cascade="all, delete-orphan")
    forum_topics = db.relationship('ForumTopic', backref='author_user', lazy=True, cascade="all, delete-orphan")
    forum_comments = db.relationship('ForumComment', backref='author_user', lazy=True, cascade="all, delete-orphan")
    forum_likes = db.relationship('ForumLike', backref='user', lazy=True, cascade="all, delete-orphan")
    forum_favorites = db.relationship('ForumFavorite', backref='user', lazy=True, cascade="all, delete-orphan")

    # Relationship for tasks
    tasks = db.relationship('Task', backref='user', lazy=True, cascade="all, delete-orphan")  # Cascade delete tasks

    def repr(self):
        return f"User('{self.username}', '{self.email}')"
    
    def set_password(self, password):
        """Hash and set the password."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the stored password."""
        return bcrypt.check_password_hash(self.password, password)

# MoodEntry model
class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood = db.Column(db.String(20), nullable=False)
    journal = db.Column(db.Text, nullable=True)  # Journal is optional
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"MoodEntry('{self.mood}', '{self.date}', '{self.journal or 'No journal'}')"

# BlogPost model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=True, default='static/images/default_blog.png')  # Default image
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=1)  # Foreign Key to User
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # Relationship to link comments to a blog post
    comments = db.relationship('Comment', backref='post', lazy=True)

    def __repr__(self):
        return f"BlogPost('{self.title}', '{self.date}')"

# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"Comment('{self.author}', '{self.date}')"

# ForumTopic model
class ForumTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Category column (e.g., Educator or Student)
    image = db.Column(db.String(200), nullable=True)  # Optional image (default handled in the route)
    video = db.Column(db.String(200), nullable=True)  # Optional video
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    comments = db.relationship('ForumComment', backref='topic', lazy=True)
    likes = db.relationship('ForumLike', backref='topic', lazy=True)
    favorites = db.relationship('ForumFavorite', backref='topic', lazy=True)

    def _repr_(self):
        return f"ForumTopic('{self.title}', '{self.category}', '{self.created_at}')"



class ForumComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topic.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='comments')

    def __repr__(self):
        return f"ForumComment('{self.content}', '{self.created_at}')"


# ForumLike model
class ForumLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topic.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"ForumLike('{self.id}')"

# ForumFavorite model
class ForumFavorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topic.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"ForumFavorite('{self.id}', '{self.user_id}')"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    # Relationship to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # New: Foreign key to associate tasks with users

    def repr(self):
        return f"<Task {self.description}>"