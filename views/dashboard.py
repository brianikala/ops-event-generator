"""
Functions checking page 
1. Can send to ER Pub/Sub 
2. Can query ER API
"""
from flask import Blueprint, render_template

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
def show():
    # return "Hello Blueprint dashboard"
    render_template('../templates/dashboard.html')