**🍕 QuickBite: Food Delivery Backend**
**FastAPI - Final Project Submission**
This project is a fully functional real-world backend system for a food delivery application.
It was built after completing 6 days of intensive FastAPI training and implements all 20 required milestones, 
from basic CRUD to advanced search and multi-step workflows.
**🛠️Key Features ImplementedRESTful APIs: **
Comprehensive set of endpoints for menu management and order tracking.
Pydantic Data Validation: 
Strict request body validation using Field constraints for security and data integrity.
Complete CRUD Operations: 
Functionality to Create, Read, Update, and Delete menu items with appropriate HTTP status codes (201 Created, 404 Not Found).
Multi-Step Workflow: 
A connected Cart-to-Checkout system that handles item availability and automatic bill calculation.
Advanced Querying: 
Efficient Search, Sorting, and Pagination logic for browsing large menus.
Swagger Documentation: 
Fully tested and interactive API documentation available at /docs.
Project Structure
main.py: The core application file containing all 20 task implementations.
requirements.txt: List of Python dependencies needed to run the project.
screenshots/: Contains 20 screenshots of API testing performed in Swagger UI.
README.md: Project documentation and submission details.
**How to Run the Project**
Clone the Repository:
git clone https://github.com/charith7sai/innomatics-internship-tasks/new/main/fastapi-food-delivery-app
Install Dependencies:
pip install -r requirements.txt
Start the Server:
uvicorn main:app --reload
Access the API:
Open your browser and go to http://127.0.0.1:8000/docs to test the 20 endpoints.
