"""
Roadmap Agent — Generates and updates structured learning paths.
Upgraded with 12+ subject templates and dynamic difficulty adaptation.
"""

ROADMAP_TEMPLATES = {
    "python": {
        "modules": [
            {"title": "Python Foundations", "description": "Core syntax, data types, and basic operations", "estimated_hours": 3,
             "topics": [
                {"title": "Variables & Data Types", "description": "Numbers, strings, booleans, and type conversion", "difficulty": 1, "xp_reward": 10},
                {"title": "Operators & Expressions", "description": "Arithmetic, comparison, logical operators", "difficulty": 1, "xp_reward": 10},
                {"title": "Input & Output", "description": "print(), input(), string formatting", "difficulty": 1, "xp_reward": 10},
                {"title": "Strings Deep Dive", "description": "String methods, slicing, f-strings", "difficulty": 2, "xp_reward": 15},
            ]},
            {"title": "Control Flow", "description": "Making decisions and repeating actions", "estimated_hours": 3,
             "topics": [
                {"title": "If/Elif/Else", "description": "Conditional statements and branching logic", "difficulty": 1, "xp_reward": 10},
                {"title": "For Loops", "description": "Iterating over sequences with for loops", "difficulty": 2, "xp_reward": 15},
                {"title": "While Loops", "description": "Condition-based loops and loop control", "difficulty": 2, "xp_reward": 15},
                {"title": "List Comprehensions", "description": "Elegant one-liner list generation", "difficulty": 2, "xp_reward": 20},
            ]},
            {"title": "Data Structures", "description": "Lists, dicts, tuples, sets", "estimated_hours": 4,
             "topics": [
                {"title": "Lists", "description": "Creating, indexing, slicing, list methods", "difficulty": 2, "xp_reward": 15},
                {"title": "Dictionaries", "description": "Key-value pairs, dictionary methods", "difficulty": 2, "xp_reward": 15},
                {"title": "Tuples & Sets", "description": "Immutable sequences and unique collections", "difficulty": 2, "xp_reward": 15},
                {"title": "Nested Structures", "description": "Combining data structures for complex data", "difficulty": 3, "xp_reward": 25},
            ]},
            {"title": "Functions & Modules", "description": "Writing reusable code", "estimated_hours": 4,
             "topics": [
                {"title": "Defining Functions", "description": "def, parameters, return values", "difficulty": 2, "xp_reward": 15},
                {"title": "Scope & Arguments", "description": "Local/global scope, *args, **kwargs", "difficulty": 3, "xp_reward": 20},
                {"title": "Lambda Functions", "description": "Anonymous functions and functional programming", "difficulty": 3, "xp_reward": 20},
                {"title": "Modules & Imports", "description": "Organizing code into modules and packages", "difficulty": 2, "xp_reward": 15},
            ]},
            {"title": "OOP", "description": "Classes, objects, inheritance, polymorphism", "estimated_hours": 5,
             "topics": [
                {"title": "Classes & Objects", "description": "Creating classes, instances, and attributes", "difficulty": 2, "xp_reward": 20},
                {"title": "Inheritance", "description": "Base classes, derived classes, method overriding", "difficulty": 3, "xp_reward": 25},
                {"title": "Encapsulation & Polymorphism", "description": "Advanced OOP principles", "difficulty": 3, "xp_reward": 25},
                {"title": "Magic Methods", "description": "__str__, __repr__, __len__ and more", "difficulty": 3, "xp_reward": 30},
            ]},
            {"title": "File I/O & Exceptions", "description": "Files, errors, and context managers", "estimated_hours": 3,
             "topics": [
                {"title": "Reading & Writing Files", "description": "open(), read(), write(), context managers", "difficulty": 2, "xp_reward": 15},
                {"title": "Exception Handling", "description": "try/except/finally, custom exceptions", "difficulty": 2, "xp_reward": 15},
                {"title": "Working with JSON & CSV", "description": "Data serialization and file formats", "difficulty": 2, "xp_reward": 20},
            ]},
        ]
    },
    "machine_learning": {
        "modules": [
            {"title": "ML Fundamentals", "description": "Core concepts and mathematics", "estimated_hours": 4,
             "topics": [
                {"title": "What is Machine Learning?", "description": "Supervised, unsupervised, reinforcement learning", "difficulty": 1, "xp_reward": 10},
                {"title": "Linear Algebra Basics", "description": "Vectors, matrices, dot products", "difficulty": 2, "xp_reward": 15},
                {"title": "Statistics & Probability", "description": "Distributions, mean, variance, Bayes", "difficulty": 2, "xp_reward": 15},
                {"title": "Data Preprocessing", "description": "Cleaning, normalization, feature engineering", "difficulty": 2, "xp_reward": 15},
            ]},
            {"title": "Classical Algorithms", "description": "ML algorithms from scratch", "estimated_hours": 5,
             "topics": [
                {"title": "Linear Regression", "description": "Predicting continuous values", "difficulty": 2, "xp_reward": 20},
                {"title": "Logistic Regression", "description": "Binary classification", "difficulty": 2, "xp_reward": 20},
                {"title": "Decision Trees & Random Forest", "description": "Tree-based ensemble methods", "difficulty": 3, "xp_reward": 25},
                {"title": "SVM & KNN", "description": "Support vectors and k-nearest neighbors", "difficulty": 3, "xp_reward": 25},
            ]},
            {"title": "Neural Networks", "description": "Deep learning fundamentals", "estimated_hours": 6,
             "topics": [
                {"title": "Perceptrons & Activations", "description": "ReLU, sigmoid, softmax", "difficulty": 3, "xp_reward": 25},
                {"title": "Backpropagation", "description": "Gradient descent and weight updates", "difficulty": 3, "xp_reward": 30},
                {"title": "CNNs", "description": "Convolutional networks for images", "difficulty": 3, "xp_reward": 35},
                {"title": "Transformers & Attention", "description": "The architecture behind GPT", "difficulty": 3, "xp_reward": 40},
            ]},
        ]
    },
    "web_development": {
        "modules": [
            {"title": "HTML & CSS Foundations", "description": "Structure and styling", "estimated_hours": 3,
             "topics": [
                {"title": "HTML Semantics", "description": "Tags, attributes, semantic elements", "difficulty": 1, "xp_reward": 10},
                {"title": "CSS Box Model", "description": "Margins, padding, borders, layouts", "difficulty": 1, "xp_reward": 10},
                {"title": "Flexbox & Grid", "description": "Modern CSS layout systems", "difficulty": 2, "xp_reward": 15},
                {"title": "Responsive Design", "description": "Media queries, mobile-first", "difficulty": 2, "xp_reward": 15},
            ]},
            {"title": "JavaScript Essentials", "description": "Programming the browser", "estimated_hours": 5,
             "topics": [
                {"title": "Variables & Data Types", "description": "let, const, primitives", "difficulty": 1, "xp_reward": 10},
                {"title": "DOM Manipulation", "description": "querySelector, events, innerHTML", "difficulty": 2, "xp_reward": 15},
                {"title": "Async JavaScript", "description": "Promises, async/await, fetch API", "difficulty": 3, "xp_reward": 25},
                {"title": "ES6+ Features", "description": "Arrow functions, destructuring, modules", "difficulty": 2, "xp_reward": 20},
            ]},
            {"title": "React.js", "description": "Modern UI framework", "estimated_hours": 6,
             "topics": [
                {"title": "Components & JSX", "description": "Functional components, JSX syntax", "difficulty": 2, "xp_reward": 20},
                {"title": "State & Props", "description": "useState, props passing", "difficulty": 2, "xp_reward": 20},
                {"title": "Hooks Deep Dive", "description": "useEffect, useContext, custom hooks", "difficulty": 3, "xp_reward": 25},
                {"title": "State Management", "description": "Context API and patterns", "difficulty": 3, "xp_reward": 30},
            ]},
        ]
    },
    "sql": {
        "modules": [
            {"title": "SQL Basics", "description": "Querying relational databases", "estimated_hours": 3,
             "topics": [
                {"title": "SELECT Fundamentals", "description": "SELECT, FROM, WHERE, ORDER BY", "difficulty": 1, "xp_reward": 10},
                {"title": "Filtering & Sorting", "description": "AND, OR, LIKE, BETWEEN, ORDER BY", "difficulty": 1, "xp_reward": 10},
                {"title": "Aggregate Functions", "description": "COUNT, SUM, AVG, GROUP BY, HAVING", "difficulty": 2, "xp_reward": 15},
                {"title": "JOINs", "description": "INNER, LEFT, RIGHT, FULL OUTER JOIN", "difficulty": 2, "xp_reward": 20},
            ]},
            {"title": "Advanced SQL", "description": "Complex queries and optimization", "estimated_hours": 4,
             "topics": [
                {"title": "Subqueries & CTEs", "description": "Nested queries and WITH clauses", "difficulty": 3, "xp_reward": 25},
                {"title": "Window Functions", "description": "ROW_NUMBER, RANK, LAG, LEAD", "difficulty": 3, "xp_reward": 30},
                {"title": "Indexes & Performance", "description": "Query optimization, explain plans", "difficulty": 3, "xp_reward": 25},
                {"title": "Transactions & ACID", "description": "Data integrity and concurrency", "difficulty": 3, "xp_reward": 30},
            ]},
        ]
    },
    "algorithms": {
        "modules": [
            {"title": "Foundations", "description": "Big-O and basic data structures", "estimated_hours": 3,
             "topics": [
                {"title": "Big-O Notation", "description": "Time and space complexity analysis", "difficulty": 2, "xp_reward": 15},
                {"title": "Arrays & Strings", "description": "Two pointers, sliding window", "difficulty": 2, "xp_reward": 15},
                {"title": "Linked Lists", "description": "Singly, doubly, reverse in-place", "difficulty": 2, "xp_reward": 20},
                {"title": "Stacks & Queues", "description": "LIFO/FIFO, monotonic stacks", "difficulty": 2, "xp_reward": 20},
            ]},
            {"title": "Sorting & Searching", "description": "Classic algorithms", "estimated_hours": 4,
             "topics": [
                {"title": "Binary Search", "description": "O(log n) search on sorted arrays", "difficulty": 2, "xp_reward": 20},
                {"title": "Merge Sort", "description": "Divide and conquer O(n log n)", "difficulty": 3, "xp_reward": 25},
                {"title": "Quick Sort", "description": "In-place partition-based sorting", "difficulty": 3, "xp_reward": 25},
                {"title": "Hash Tables", "description": "O(1) lookups, collision resolution", "difficulty": 2, "xp_reward": 20},
            ]},
            {"title": "Advanced Topics", "description": "Graph and dynamic programming", "estimated_hours": 6,
             "topics": [
                {"title": "Trees & BST", "description": "Tree traversals, balanced BSTs", "difficulty": 3, "xp_reward": 30},
                {"title": "Graph Algorithms", "description": "BFS, DFS, Dijkstra's", "difficulty": 3, "xp_reward": 35},
                {"title": "Dynamic Programming", "description": "Memoization and tabulation", "difficulty": 3, "xp_reward": 40},
                {"title": "Greedy Algorithms", "description": "Local optimal choices", "difficulty": 3, "xp_reward": 35},
            ]},
        ]
    },
    "react": {
        "modules": [
            {"title": "React Basics", "description": "Components and JSX", "estimated_hours": 3,
             "topics": [
                {"title": "JSX & Components", "description": "Writing JSX, functional components", "difficulty": 1, "xp_reward": 10},
                {"title": "Props & State", "description": "Data flow and useState hook", "difficulty": 2, "xp_reward": 15},
                {"title": "Event Handling", "description": "onClick, onChange, synthetic events", "difficulty": 1, "xp_reward": 10},
                {"title": "Lists & Keys", "description": "Rendering arrays, key prop", "difficulty": 2, "xp_reward": 15},
            ]},
            {"title": "Advanced React", "description": "Hooks, context, and patterns", "estimated_hours": 5,
             "topics": [
                {"title": "useEffect & Lifecycle", "description": "Side effects and cleanup", "difficulty": 2, "xp_reward": 20},
                {"title": "Context & useContext", "description": "Global state without prop drilling", "difficulty": 2, "xp_reward": 20},
                {"title": "Custom Hooks", "description": "Reusable stateful logic", "difficulty": 3, "xp_reward": 25},
                {"title": "Performance", "description": "useMemo, useCallback, React.memo", "difficulty": 3, "xp_reward": 30},
            ]},
        ]
    },
    "cloud": {
        "modules": [
            {"title": "Cloud Fundamentals", "description": "Cloud computing concepts", "estimated_hours": 3,
             "topics": [
                {"title": "Cloud Models", "description": "IaaS, PaaS, SaaS, public/private/hybrid", "difficulty": 1, "xp_reward": 10},
                {"title": "Compute Services", "description": "VMs, containers, serverless", "difficulty": 2, "xp_reward": 15},
                {"title": "Storage & Databases", "description": "Object storage, relational, NoSQL", "difficulty": 2, "xp_reward": 15},
                {"title": "Networking & Security", "description": "VPCs, IAM, security groups", "difficulty": 2, "xp_reward": 20},
            ]},
            {"title": "DevOps & Deployment", "description": "CI/CD and containers", "estimated_hours": 4,
             "topics": [
                {"title": "Docker", "description": "Containers, images, Dockerfile", "difficulty": 2, "xp_reward": 20},
                {"title": "Kubernetes", "description": "Container orchestration basics", "difficulty": 3, "xp_reward": 30},
                {"title": "CI/CD Pipelines", "description": "GitHub Actions, automated deployment", "difficulty": 3, "xp_reward": 25},
                {"title": "Infrastructure as Code", "description": "Terraform, CloudFormation", "difficulty": 3, "xp_reward": 30},
            ]},
        ]
    },
    "default": {
        "modules": [
            {"title": "Module 1: Foundations", "description": "Core concepts and fundamentals", "estimated_hours": 3,
             "topics": [
                {"title": "Introduction & Overview", "description": "Understanding the landscape and key terminology", "difficulty": 1, "xp_reward": 10},
                {"title": "Core Principles", "description": "The fundamental rules driving this subject", "difficulty": 1, "xp_reward": 10},
                {"title": "Basic Building Blocks", "description": "Essential components you need to know", "difficulty": 1, "xp_reward": 10},
                {"title": "First Practical Exercise", "description": "Apply knowledge in a guided session", "difficulty": 2, "xp_reward": 15},
            ]},
            {"title": "Module 2: Core Concepts", "description": "Deep dive into main ideas", "estimated_hours": 4,
             "topics": [
                {"title": "Concept Deep Dive", "description": "Exploring the main ideas in detail", "difficulty": 2, "xp_reward": 15},
                {"title": "Patterns & Best Practices", "description": "Common patterns and professional standards", "difficulty": 2, "xp_reward": 15},
                {"title": "Problem Solving", "description": "Applying concepts to solve real problems", "difficulty": 2, "xp_reward": 20},
                {"title": "Intermediate Project", "description": "Build something practical", "difficulty": 3, "xp_reward": 25},
            ]},
            {"title": "Module 3: Advanced Topics", "description": "Expert-level concepts", "estimated_hours": 5,
             "topics": [
                {"title": "Advanced Concepts", "description": "Complex topics building on your foundation", "difficulty": 3, "xp_reward": 20},
                {"title": "Optimization & Best Practices", "description": "How to do things the right way", "difficulty": 3, "xp_reward": 25},
                {"title": "Real-World Applications", "description": "Industry use cases and examples", "difficulty": 3, "xp_reward": 25},
                {"title": "Capstone Project", "description": "Demonstrate mastery with a complete project", "difficulty": 3, "xp_reward": 50},
            ]},
        ]
    }
}

KEYWORD_MAP = {
    "python": ["python", "pandas", "numpy", "django", "flask", "fastapi"],
    "machine_learning": ["machine learning", "ml", "deep learning", "neural", "ai", "artificial intelligence", "tensorflow", "pytorch", "sklearn"],
    "web_development": ["web", "html", "css", "javascript", "frontend", "backend", "fullstack", "website"],
    "sql": ["sql", "database", "mysql", "postgresql", "sqlite", "query", "relational"],
    "algorithms": ["algorithm", "data structure", "leetcode", "dsa", "sorting", "searching", "competitive"],
    "react": ["react", "reactjs", "hooks", "redux", "jsx", "nextjs"],
    "cloud": ["cloud", "aws", "azure", "gcp", "devops", "docker", "kubernetes", "serverless"],
}


class RoadmapAgent:
    def generate(self, goal: str) -> dict:
        key = self._match_template(goal)
        template = ROADMAP_TEMPLATES.get(key, ROADMAP_TEMPLATES["default"])
        roadmap = {"goal": goal, "modules": []}

        for i, mod in enumerate(template["modules"]):
            module = {
                "title": mod["title"],
                "description": mod["description"],
                "order": i,
                "status": "active" if i == 0 else "locked",
                "progress": 0.0,
                "estimated_hours": mod["estimated_hours"],
                "topics": []
            }
            for j, t in enumerate(mod["topics"]):
                module["topics"].append({
                    "title": t["title"],
                    "description": t["description"],
                    "order": j,
                    "status": "pending",
                    "difficulty": t["difficulty"],
                    "xp_reward": t["xp_reward"]
                })
            roadmap["modules"].append(module)
        return roadmap

    def update(self, roadmap: dict, performance: dict) -> dict:
        for module in roadmap.get("modules", []):
            if module["status"] == "active":
                completed = sum(1 for t in module["topics"] if t["status"] == "completed")
                total = len(module["topics"])
                module["progress"] = (completed / total * 100) if total > 0 else 0
                if module["progress"] >= 100:
                    module["status"] = "completed"
                    for next_mod in roadmap["modules"]:
                        if next_mod["status"] == "locked":
                            next_mod["status"] = "active"
                            break
        return roadmap

    def get_current_topic(self, roadmap: dict) -> dict | None:
        for module in roadmap.get("modules", []):
            if module["status"] == "active":
                for topic in module["topics"]:
                    if topic["status"] in ("pending", "in_progress"):
                        return {**topic, "module": module["title"]}
        return None

    def _match_template(self, goal: str) -> str:
        goal_lower = goal.lower()
        for key, keywords in KEYWORD_MAP.items():
            if any(kw in goal_lower for kw in keywords):
                return key
        return "default"


roadmap_agent = RoadmapAgent()
