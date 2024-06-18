from fastapi import FastAPI, UploadFile, File
from parser import parse_document
from ml import extract_information, refine_information, evaluate_criteria
from evaluate import calculate_rating

app = FastAPI()


@app.post("/assess_visa_eligibility/")
async def assess_visa_eligibility(file: UploadFile = File(...)):
    """
    Endpoint to assess eligibility for an O-1A Visa based on the provided resume.

    This function takes an uploaded resume file, extracts relevant
    information for the O-1A Visa categories, refines the extracted information,
    evaluates the eligibility based on the criteria, and calculates an overall
    rating.

    :param: file: (UploadFile) The resume file uploaded by the user.

    :return: A dictionary containing:
            - criterion (dict): The refined information categorized according to
              the O-1A Visa criteria.
            - overall_rating (str): The overall rating of the eligibility
    """
    content = await file.read()
    text = parse_document(content)
    extracted_info = extract_information(text)
    refined_info = refine_information(extracted_info)
    rating_info = evaluate_criteria(refined_info)
    rating = calculate_rating(rating_info)
    return {
        "criterion": refined_info,
        "overall_rating": rating
    }
