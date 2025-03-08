from fastapi import FastAPI, HTTPException
import uvicorn
import numpy as np
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace '*' with your specific origin if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    name: str
    age: int
    city: str

students = {
    1: Student(name="John", age=20, city="New York"),
    2: Student(name="Jane", age=22, city="Los Angeles"),
    3: Student(name="Doe", age=21, city="Chicago"),
    4: Student(name="Smith", age=23, city="San Francisco")
    # Add more students as needed
}

grades = {
    1: [np.random.randint(0, 100) for _ in range(25)],
    2: [np.random.poisson(50) for _ in range(25)],
    3: [np.random.randint(0, 100) for _ in range(25)],
    4: [np.random.pareto(a=3.0) for _ in range(25)]
}

@app.get("/students/")
async def get_students():
    return {"students": list(students.keys())}

@app.get("/student/")
async def get_student(student_id: int):
    if student_id not in students:
        raise HTTPException(
            status_code=404,
            detail=f"Student with id {student_id} not found"
            )
    return students[student_id]

@app.get("/grades/")
async def get_grades(student_id: int):
    if student_id not in students:
        raise HTTPException(
            status_code=404,
            detail=f"Student with id {student_id} not found"
            )
    return grades[student_id]

@app.get("/grade_statistics/")
async def get_grade_statistics(student_id: int):
    if student_id not in students:
        raise HTTPException(
            status_code=404,
            detail=f"Student with id {student_id} not found"
            )
    out = {grade: grades[student_id].count(grade) for grade in set(grades[student_id])}
    print(out)
    return out

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)