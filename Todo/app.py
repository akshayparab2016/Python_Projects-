from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secretkey"

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todoS.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    
with app.app_context():
    db.create_all()
    
@app.route('/')
def home():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# Add Task
@app.route('/add', methods=['POST'])
def add():
    task_content = request.form.get('task')
    new_task = Task(content=task_content)
    db.session.add(new_task)
    db.session.commit()
    flash("Task added successfully!", "success")
    return redirect(url_for('home'))

# Delete Task
@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted!", "danger")
    return redirect(url_for('home'))

# Edit Task Page
@app.route('/edit/<int:id>')
def edit(id):
    task = Task.query.get(id)
    return render_template('edit.html', task=task)

# Update Task
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    task = Task.query.get(id)
    task.content = request.form.get('task')
    db.session.commit()
    flash("Task updated successfully!", "info")
    return redirect(url_for('home'))

@app.route('/complete/<int:id>')
def complete(id):
    task = Task.query.get(id)
    task.completed = not task.completed
    db.session.commit()

    flash("Task status updated!", "secondary")
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run()     

