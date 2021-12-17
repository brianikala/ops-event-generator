"""
Functions checking page 
1. Can send to ER Pub/Sub 
2. Can query ER API
"""
from flask import Blueprint, render_template

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
def show():
    er_status = check_er()
    pubsub_status = check_pubsub()
    return render_template('dashboard.html')

def check_pubsub():
    return "up"

def check_er():
    return "down"