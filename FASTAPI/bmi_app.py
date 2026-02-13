from fastapi import FastAPI, Path, HTTPException
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



##### PATH PARAMETERS #####
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
    
    