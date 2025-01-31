from flask import render_template
from app import appy, db

@appy.errorhandler(404) # decorator for custom error handling
def not_found_error(error):
    return render_template('404.html'), 404

@appy.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500