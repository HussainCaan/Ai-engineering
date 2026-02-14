from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
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
        return round(self.weight / (self.height ** 2), 2)

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
        
        
        
        
@app.post("/create")
def create_patient(patient: Patient):
    pass