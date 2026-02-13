from fastapi import FastAPI, Path, HTTPException, Query
import json
app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello World!"}

@app.get("/about")
def about():
    return {"message": "A Fully functional API to manage patient record"}

def load_data():
    with open("bmi_data.json", 'r') as f:
        data = json.load(f)
    
    return data

@app.get("/view_patients")
def view_patients():
    data = load_data()
    return data



##### PATH PARAMETERS ##### QUERY PARAMETERS #####
@app.get("/patient/{patient_id}")
def get_patient(
    patient_id: str = Path(..., description="The ID of the patient to retrieve", example="P001")
):
    data = load_data()
    try:
        patient = data[patient_id]
        return patient
    except KeyError:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    
@app.get("/sort")
def sort_patients(sort_by:str = Query(..., description= "Sort on the basis of age and bmi"), order: str = Query("asc", description="Sort order (asc or desc)")):
    if sort_by not in ["age", "bmi"]:
        raise HTTPException(status_code=400, detail="Invalid sort_by value. Must be 'age' or 'bmi'.")
    
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order value. Must be 'asc' or 'desc'.")
    sort_order = True if order == "desc" else False
    data = load_data()
    sorted_patients = sorted(data.values(), key=lambda x: x[sort_by], reverse=sort_order)
    return sorted_patients
    