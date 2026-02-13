# How pydantic solves the problem of data and type validation.
# STEPS:
# 1. Define a pydantic model that represents the data structure you want to validate.
# 2. Make object of the that model and pass the data to it. Pydantic will automatically validate the data and raise an error if the data is not valid.
from pydantic import BaseModel, ValidationError

class Patient(BaseModel):
    name: str
    age: int
    
    
patient_data = {
    "name": "khan",
    "age": 24
}

patient1 = Patient(**patient_data) # This will work because the data is valid and it matches the structure defined in the Patient model.

def insert_patient(patient: Patient):
    print(patient.name, patient.age)
    print("Patient inserted successfully")

try:
    insert_patient(patient1) # This will work because patient1 is a valid Patient object.
except ValidationError as e:
    print(e)