"""Main application file for StudyPlanner.

Production-grade Flask entry point configuring routing, authentication,
security headers, exception handlers, logging, and database operations.
"""

import os
import logging
from datetime import datetime, timedelta
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    abort,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from werkzeug.middleware.proxy_fix import ProxyFix
from config import config_by_name
from models import db, User, Task, Session
from forms import LoginForm, RegisterForm, TaskForm, SearchFilterForm


def create_app(config_name: str = None) -> Flask:
    """Application factory for creating and configuring the Flask app instance."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Wrap WSGI app for reverse proxies (e.g. Render / Cloudflare)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # Setup Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger("studyplanner")
    logger.info(f"Initializing StudyPlanner in {config_name} mode.")

    # Initialize Extensions
    db.init_app(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=[app.config.get("RATELIMIT_DEFAULT", "200 per day;50 per hour")],
        storage_uri=app.config.get("RATELIMIT_STORAGE_URI", "memory://"),
    )
    app.limiter = limiter

    @login_manager.user_loader
    def load_user(user_id: str) -> User:
        """Flask-Login user loader callback."""
        return User.query.get(int(user_id))

    # Security Headers Middleware
    @app.after_request
    def set_security_headers(response):
        """Inject production security headers into every response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Global Context Processor
    @app.context_processor
    def inject_global_vars():
        """Provide current year and navigation helpers to all templates."""
        return {"current_year": datetime.utcnow().year}

    # -------------------------------------------------------------------------
    # Route Definitions
    # -------------------------------------------------------------------------

    @app.route("/")
    def index():
        """Landing page or direct redirect to user dashboard."""
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    @limiter.limit("10 per hour")
    def register():
        """Register a new user account."""
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        form = RegisterForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data.strip(),
                email=form.email.data.strip().lower(),
            )
            user.set_password(form.password.data)
            try:
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash("Account created successfully! Welcome to StudyPlanner.", "success")
                logger.info(f"New user registered: {user.username}")
                return redirect(url_for("dashboard"))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error creating user {form.username.data}: {str(e)}")
                flash("An database error occurred while creating your account. Please try again.", "danger")

        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("15 per hour")
    def login():
        """Authenticate existing user."""
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data.strip()).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash(f"Welcome back, {user.username}!", "success")
                logger.info(f"User logged in: {user.username}")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("dashboard"))
            else:
                flash("Invalid username or password. Please try again.", "danger")
                logger.warning(f"Failed login attempt for username: {form.username.data}")

        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        """Log out current user."""
        username = current_user.username
        logout_user()
        flash("You have been logged out successfully.", "info")
        logger.info(f"User logged out: {username}")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        """User main dashboard showing task metrics and study timer stats."""
        tasks = Task.query.filter_by(user_id=current_user.id).all()

        total_tasks = len(tasks)
        pending_count = sum(1 for t in tasks if t.status == "Pending")
        in_progress_count = sum(1 for t in tasks if t.status == "In Progress")
        completed_count = sum(1 for t in tasks if t.status == "Completed")
        total_study_seconds = sum(t.total_study_time for t in tasks)

        # Formatted total study hours and minutes
        hours, remainder = divmod(total_study_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        formatted_total_time = f"{hours}h {minutes}m"

        # Upcoming tasks (Pending or In Progress, sorted by due date)
        upcoming_tasks = (
            Task.query.filter(
                Task.user_id == current_user.id,
                Task.status.in_(["Pending", "In Progress"]),
            )
            .order_by(Task.due_date.asc().nullslast(), Task.priority.desc())
            .limit(5)
            .all()
        )

        return render_template(
            "dashboard.html",
            total_tasks=total_tasks,
            pending_count=pending_count,
            in_progress_count=in_progress_count,
            completed_count=completed_count,
            total_study_time=formatted_total_time,
            upcoming_tasks=upcoming_tasks,
        )

    @app.route("/tasks", methods=["GET"])
    @login_required
    def task_list():
        """Display paginated task list with filter, search, and sort options."""
        form = SearchFilterForm(request.args)
        page = request.args.get("page", 1, type=int)

        query = Task.query.filter_by(user_id=current_user.id)

        # Apply search query
        if form.query.data:
            search_term = f"%{form.query.data.strip()}%"
            query = query.filter(
                (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
            )

        # Apply status filter
        if form.status.data and form.status.data != "All":
            query = query.filter(Task.status == form.status.data)

        # Apply priority filter
        if form.priority.data and form.priority.data != "All":
            query = query.filter(Task.priority == form.priority.data)

        # Apply sorting
        sort_by = form.sort_by.data or "due_date_asc"
        if sort_by == "due_date_asc":
            query = query.order_by(Task.due_date.asc().nullslast())
        elif sort_by == "due_date_desc":
            query = query.order_by(Task.due_date.desc().nullslast())
        elif sort_by == "priority_desc":
            # Order High, Medium, Low
            query = query.order_by(
                db.case(
                    (Task.priority == "High", 1),
                    (Task.priority == "Medium", 2),
                    (Task.priority == "Low", 3),
                    else_=4,
                )
            )
        elif sort_by == "created_desc":
            query = query.order_by(Task.created_at.desc())
        elif sort_by == "title_asc":
            query = query.order_by(Task.title.asc())

        per_page = app.config.get("TASKS_PER_PAGE", 10)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        tasks = pagination.items

        return render_template(
            "task_list.html",
            tasks=tasks,
            pagination=pagination,
            form=form,
        )

    @app.route("/task/new", methods=["GET", "POST"])
    @login_required
    def task_new():
        """Create a new task."""
        form = TaskForm()
        if form.validate_on_submit():
            task = Task(
                user_id=current_user.id,
                title=form.title.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
                due_date=form.due_date.data,
                priority=form.priority.data,
                status=form.status.data,
            )
            try:
                db.session.add(task)
                db.session.commit()
                flash("Task created successfully!", "success")
                logger.info(f"Task '{task.title}' created by user {current_user.username}")
                return redirect(url_for("task_list"))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to create task: {str(e)}")
                flash("Error creating task. Please try again.", "danger")

        return render_template("task_form.html", form=form, title="Create Task", action="Create")

    @app.route("/task/<int:id>", methods=["GET"])
    @login_required
    def task_detail(id: int):
        """View details of a specific task and its study sessions."""
        task = Task.query.get_or_404(id)
        if task.user_id != current_user.id:
            abort(403)

        sessions = Session.query.filter_by(task_id=task.id).order_by(Session.start_time.desc()).all()
        return render_template("task_detail.html", task=task, sessions=sessions)

    @app.route("/task/<int:id>/edit", methods=["GET", "POST"])
    @login_required
    def task_edit(id: int):
        """Edit an existing task."""
        task = Task.query.get_or_404(id)
        if task.user_id != current_user.id:
            abort(403)

        form = TaskForm(obj=task)
        if form.validate_on_submit():
            task.title = form.title.data.strip()
            task.description = form.description.data.strip() if form.description.data else None
            task.due_date = form.due_date.data
            task.priority = form.priority.data
            task.status = form.status.data

            try:
                db.session.commit()
                flash("Task updated successfully!", "success")
                logger.info(f"Task ID {id} updated by {current_user.username}")
                return redirect(url_for("task_list"))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to update task ID {id}: {str(e)}")
                flash("Error updating task. Please try again.", "danger")

        return render_template("task_form.html", form=form, title="Edit Task", action="Update", task=task)

    @app.route("/task/<int:id>/delete", methods=["POST"])
    @login_required
    def task_delete(id: int):
        """Delete a task."""
        task = Task.query.get_or_404(id)
        if task.user_id != current_user.id:
            abort(403)

        try:
            db.session.delete(task)
            db.session.commit()
            flash("Task deleted successfully.", "success")
            logger.info(f"Task ID {id} deleted by {current_user.username}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete task ID {id}: {str(e)}")
            flash("Error deleting task.", "danger")

        return redirect(url_for("task_list"))

    @app.route("/task/<int:id>/timer", methods=["GET"])
    @login_required
    def timer(id: int):
        """Study timer page for tracking focus sessions."""
        task = Task.query.get_or_404(id)
        if task.user_id != current_user.id:
            abort(403)

        active_session = Session.query.filter_by(
            task_id=task.id, user_id=current_user.id, end_time=None
        ).first()

        return render_template("timer.html", task=task, active_session=active_session)

    @app.route("/task/<int:id>/timer/start", methods=["POST"])
    @login_required
    def timer_start(id: int):
        """API endpoint to start a timer session for a task."""
        task = Task.query.get_or_404(id)
        if task.user_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403

        # Check if an active session already exists
        existing_session = Session.query.filter_by(
            task_id=task.id, user_id=current_user.id, end_time=None
        ).first()

        if existing_session:
            return jsonify({
                "success": True,
                "session_id": existing_session.id,
                "start_time": existing_session.start_time.isoformat(),
                "message": "Session already running."
            })

        new_session = Session(task_id=task.id, user_id=current_user.id)
        new_session.start()

        if task.status == "Pending":
            task.status = "In Progress"

        try:
            db.session.add(new_session)
            db.session.commit()
            return jsonify({
                "success": True,
                "session_id": new_session.id,
                "start_time": new_session.start_time.isoformat(),
                "message": "Timer started successfully."
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error starting timer for task {id}: {str(e)}")
            return jsonify({"success": False, "error": "Database error"}), 500

    @app.route("/task/<int:id>/timer/stop", methods=["POST"])
    @login_required
    def timer_stop(id: int):
        """API endpoint to stop an active timer session and log study time."""
        task = Task.query.get_or_404(id)
        if task.user_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403

        active_session = Session.query.filter_by(
            task_id=task.id, user_id=current_user.id, end_time=None
        ).first()

        if not active_session:
            return jsonify({"success": False, "error": "No active session found."}), 400

        session_duration = active_session.stop()
        task.total_study_time += session_duration

        try:
            db.session.commit()
            return jsonify({
                "success": True,
                "duration": session_duration,
                "formatted_duration": task.formatted_study_time(),
                "total_study_time": task.total_study_time,
                "message": "Timer stopped successfully."
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error stopping timer for task {id}: {str(e)}")
            return jsonify({"success": False, "error": "Database error"}), 500

    @app.route("/about")
    def about():
        """About page providing feature information."""
        return render_template("about.html")

    @app.route("/health")
    def health():
        """Health check endpoint for status monitoring."""
        try:
            db.session.execute(db.text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            logger.error(f"Health check DB failure: {str(e)}")
            db_status = "disconnected"

        return jsonify({
            "status": "healthy" if db_status == "connected" else "unhealthy",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat(),
        }), 200 if db_status == "connected" else 500

    # -------------------------------------------------------------------------
    # Error Handlers
    # -------------------------------------------------------------------------

    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 Page Not Found errors."""
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle 500 Internal Server errors."""
        logger.error(f"Server Error: {str(e)}")
        return render_template("500.html"), 500

    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle 429 Rate Limit Exceeded errors."""
        flash("You have exceeded the maximum request limit. Please wait before trying again.", "danger")
        return render_template("404.html", error_message="Rate Limit Exceeded"), 429

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
