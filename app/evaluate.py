def calculate_rating(criteria_scores):
    """
    Calculates the overall rating of O-1A Visa eligibility based on the
    number of criteria met.The function evaluates the number of categories where
    the applicant has at least one piece of evidence and assigns a rating
    ('high', 'medium', 'low') based on predefined thresholds.

    :param criteria_scores: (dict) A dictionary where the keys are category
    names and the values are lists of evidence for each category.
    :return: (string) The overall rating of the eligibility ('high', 'medium',
    'low').
    """
    # Define the thresholds for rating based on total score
    count = sum(1 for value in criteria_scores.values() if value > 0)
    # Determine if there are more than 3 such categories
    if count > 3 or len(criteria_scores['Nobel Prize']) > 1:
        return "high"
    if count == 3:
        return "medium"
    else:
        return "low"
