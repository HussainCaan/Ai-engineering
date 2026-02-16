from fastapi import FastAPI, Path, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()




class Patient(BaseModel):
    
    id: Annotated[str, Field(..., json_schema_extra = ["P001"], max_length=10, description="Unique identifier for the patient")]
    name: Annotated[str, Field(..., json_schema_extra= "John Doe", max_length=50, description="Full name of the patient")]
    city: Annotated[str, Field(..., json_schema_extra= "New York", max_length=50, description="City of residence of the patient")]
    age: Annotated[int, Field(..., json_schema_extra= 30, gt=0, description="Age of the patient in years")]
    gender: Annotated[Literal["male", "female", "others"], Field(..., json_schema_extra= "Male", max_length=10, pattern="^(male|female|others)$", description="Gender of the patient")]
    height: Annotated[float, Field(..., json_schema_extra= 175.0, gt=0, description="Height of the patient in cm")]
    weight: Annotated[float, Field(..., json_schema_extra= 70.0, gt=0, description="Weight of the patient in kg")]
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi =  round(self.weight / (self.height ** 2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 25:
            return "Normal weight"
        elif 25 <= self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"
        
def load_data():
    with open("bmi_data.json", 'r') as f:
        data = json.load(f)
    return data       

def save_data(data):
    with open("bmi_data.json", 'w') as f:
        json.dump(data, f)    
        
@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    
    # Check if patient ID already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
    
    # Add new patient to the data
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    # Save updated data back to the file
    save_data(data)
    
    return JSONResponse(content={"message": "Patient record created successfully", "patient_id": patient.id}, status_code=201)
    


###### PUT ############## DELETE ENDPOINTS ###################################
class PatientUpdate(BaseModel):
    name: Optional[Annotated[str, Field(max_length=50, description="Full name of the patient")]] = None
    age: Optional[Annotated[int, Field(gt=0, description="Age of the patient in years")]] = None
    city: Optional[Annotated[str, Field(max_length=50, description="City of residence of the patient")]] = None
    height: Optional[Annotated[float, Field(gt=0, description="Height of the patient in cm")]] = None
    weight: Optional[Annotated[float, Field(gt=0, description="Weight of the patient in kg")]] = None
    
    
    

@app.put("/update/{patient_id}")
def update_patient(patient_id: str, patient_update:PatientUpdate):
    
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient_info = data[patient_id]
    
    patient_dict = patient_update.model_dump(exclude_unset=True)
    
    for key, value in patient_dict.items():
       patient_info[key] = value
    
    # Update the patient info with the new values
    patient_info['id'] = patient_id
    patient_info_pydantic = Patient(**patient_info)
    
    patient_dict = patient_info_pydantic.model_dump(exclude='id')
    
    data[patient_id] = patient_dict
    
    # Save updated data back to the file
    save_data(data)
    
    return JSONResponse(content={"message": "Patient record updated successfully", "patient_id": patient_id}, status_code=200)
     
        