from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta

 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    result = []
    completed = request.args.get('completed', default=None)
    if completed:
        completed = completed.lower() == 'true'

    window = request.args.get('window', default=None, type=int)
    if window is not None:
        cutoff_date = datetime.utcnow() + timedelta(days=window)

    for todo in todos:
        if completed is not None and todo.completed != completed:
            continue

        if window is not None and todo.deadline_at and todo.deadline_at > cutoff_date:
            continue

        result.append(todo.to_dict())
    
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():

    expected_fields = {'title', 'description', 'completed', 'deadline_at'}


    # Check if there are any extra fields in the request
    extra_fields = set(request.json.keys()) - expected_fields
    
    if extra_fields:
        # Return 400 Bad Request if extra fields are found
        return jsonify({"error": f"Unexpected fields: {', '.join(extra_fields)}"}), 400

    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

    if todo.title is None:
        return jsonify({'error': 'Title cannot be null'}), 400

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    # Fetch the Todo object by ID
    todo = Todo.query.get(todo_id)
    
    # If Todo is not found, return 400
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    # If Todo is not found, return 400
    if request.json.get('title') is None:
        return jsonify({'error': 'Todo not found'}), 400
    
    # List the allowed fields that can be updated
    allowed_fields = {'title', 'description', 'completed', 'deadline_at'}
    
    # Check if the request JSON contains any extra fields
    for key in request.json.keys():
        if key not in allowed_fields:
            return jsonify({'error': f"Invalid field: {key}"}), 400

    # Update the Todo fields based on the request
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)

    # Commit the changes to the database
    db.session.commit()

    # Return the updated Todo as a response (optional, but useful for validation)
    return jsonify(todo.to_dict()), 200

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
