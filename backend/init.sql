-- Initialize the database schema for Todo List application

-- Create todos table
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on completed status for faster queries
CREATE INDEX idx_todos_completed ON todos(completed);

-- Create index on created_at for sorting
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);

-- Insert sample data for testing
INSERT INTO todos (title, description, completed) VALUES
    ('Welcome to Todo App', 'This is your first todo item. Try editing or deleting it!', false),
    ('Create a new todo', 'Click the add button to create a new todo item', false),
    ('Mark todos as complete', 'Check the checkbox to mark a todo as completed', false);

-- Create a function to update the updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at on row updates
CREATE TRIGGER update_todos_updated_at
    BEFORE UPDATE ON todos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
