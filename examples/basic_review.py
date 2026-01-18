"""
Example code review requests for testing the Python Codebase Reviewer.

This file demonstrates various code issues that the reviewer agents should detect.
"""

# Example 1: Security Vulnerability - SQL Injection
example_1_sql_injection = """
Review this login function:

```python
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    return result.fetchone()
```
"""

# Example 2: Architecture - SOLID Violation
example_2_solid_violation = """
Review this user manager class:

```python
class UserManager:
    def create_user(self, username, email, password):
        # Validate user
        if not username or not email:
            raise ValueError("Invalid input")

        # Hash password
        import hashlib
        hashed = hashlib.md5(password.encode()).hexdigest()

        # Save to database
        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()

        # Send welcome email
        send_email(email, "Welcome to our platform!")

        # Log the action
        log_file = open('users.log', 'a')
        log_file.write(f"User {username} created at {datetime.now()}\\n")
        log_file.close()

        return user
```
"""

# Example 3: Code Quality - Non-Pythonic Code
example_3_non_pythonic = """
Review this data processing function:

```python
def process_data(items):
    result = []
    for i in range(len(items)):
        if items[i] % 2 == 0:
            result.append(items[i] * 2)

    output = ""
    for item in result:
        output = output + str(item) + ","

    return output
```
"""

# Example 4: Performance - O(n²) Algorithm
example_4_performance = """
Review this duplicate finder:

```python
def find_duplicates(data):
    duplicates = []
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j] and data[i] not in duplicates:
                duplicates.append(data[i])
    return duplicates

# Usage with large dataset
large_data = get_user_data()  # 10,000 items
dupes = find_duplicates(large_data)
```
"""

# Example 5: Multiple Issues - Real-world Code
example_5_multiple_issues = """
Review this complete user API endpoint:

```python
from flask import Flask, request
import pickle

app = Flask(__name__)
DEBUG = True

@app.route('/api/user/<user_id>')
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    user = db.execute(query).fetchone()

    if user:
        return user
    else:
        return "User not found"

@app.route('/api/users')
def get_users():
    users = []
    for id in range(1, 1000):
        user = db.execute(f"SELECT * FROM users WHERE id = {id}").fetchone()
        if user:
            users.append(user)
    return users

@app.route('/api/save', methods=['POST'])
def save_data():
    data = request.get_data()
    obj = pickle.loads(data)
    obj.save()
    return "OK"

@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    response = requests.get(url)
    return response.content

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```
"""

# Example 6: Django-specific Issues
example_6_django = """
Review this Django view:

```python
from django.shortcuts import render
from .models import Article

def article_list(request):
    articles = Article.objects.all()

    result = []
    for article in articles:
        result.append({
            'title': article.title,
            'author': article.author.name,
            'category': article.category.name,
            'comments': [c.text for c in article.comments.all()]
        })

    return render(request, 'articles.html', {'articles': result})
```
"""

# Example 7: Async/Await Issues
example_7_async = """
Review this async data fetching:

```python
import asyncio
import aiohttp

async def fetch_data(url):
    response = requests.get(url)  # Blocking call in async function!
    return response.json()

async def process_urls(urls):
    results = []
    for url in urls:
        data = await fetch_data(url)
        results.append(data)
    return results
```
"""

if __name__ == "__main__":
    print("Python Codebase Reviewer - Example Review Requests")
    print("=" * 60)
    print("\nThese examples demonstrate various code issues:")
    print("1. SQL Injection vulnerability")
    print("2. SOLID principle violations")
    print("3. Non-Pythonic code patterns")
    print("4. Performance issues (O(n²))")
    print("5. Multiple security and quality issues")
    print("6. Django-specific problems (N+1 queries)")
    print("7. Async/await anti-patterns")
    print("\nUse these examples to test the reviewer agent.")
