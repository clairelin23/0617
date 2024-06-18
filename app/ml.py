import ast
import re
from openai import OpenAI
import os

# Defining necessary rompt information
CATEGORIES = ["Nobel Prize", "Awards", "Membership",
              "Press", "Judging", "Original Contribution",
              "Scholarly Articles",
              "Critical Employment", "High Remuneration"]
CATEGORIES_DEFINITION = \
    [("Nobel Prize", "Awarded the Nobel Prize in the field of endeavor"),
     ("Awards",
      "Documentation of the beneficiary's receipt of nationally or "
      "internationally recognized prizes or awards for excellence in the "
      "field of endeavor"),
     ("Membership",
      "Documentation of the beneficiary's membership in associations in "
      "the field for which classification is sought, which require "
      "outstanding achievements of their members, as judged by recognized "
      "national or international experts in their disciplines or fields"),
     ("Press",
      "Published material in professional or major trade publications or "
      "major media about the beneficiary, relating to the beneficiary's "
      "work in the field for which classification is sought, which must "
      "include the title, date, and author of such published material, "
      "and any necessary translation"),
     ("Judging",
      "Evidence of the beneficiary's participation on a panel or "
      "individually, as a judge of the work of others in the same or in "
      "an allied field of specialization for which classification is "
      "sought"),
     ("Original Contribution",
      "Evidence of the beneficiary's original scientific, scholarly, "
      "or business-related contributions of major significance in the "
      "field"),
     ("Scholarly Articles",
      "Evidence of the beneficiary's authorship of scholarly articles in "
      "the field, in professional journals, or other major media"),
     ("Critical Employment",
      "Evidence that the beneficiary has been employed in a critical or "
      "essential capacity for organizations and establishments that have "
      "a distinguished reputation"),
     ("High Remuneration",
      "Evidence that the beneficiary has either commanded a high salary "
      "or will command a high salary or other remuneration for services, "
      "as evidenced by contracts or other reliable evidence")]

# TODO set as env variable
# Setup OpenAI API client to call APIs
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def clean_text(text):
    """
    Cleans the input text by removing leading and trailing spaces, numbers,
    and hyphens. Used for cleaning OpenAI API response
    :param text: (String) The input text to be cleaned
    :return: Text with leading and trailing spaces, numbers, and hyphens
    removed.
    """
    return re.sub(r"^[\s\d\-]+|[\s\d\-]+$", "", text)


def extract_information(text):
    max_tokens = 2000  # Max tokens per request
    stride = 500  # Overlapping tokens

    extracted_info = {category: [] for category in CATEGORIES}

    role_assignment_prompt = (
        "You are assessing how a person is qualified for an O-1A immigration "
        "visa."
        "You need to determine whether the resume contains information "
        "related to the following categories:")

    categories_prompt = "\n".join(
        [f"{category}: {definition}" for category, definition
         in CATEGORIES_DEFINITION])

    partial_prompt = (f"{role_assignment_prompt}\n\n"
                      f"{categories_prompt}\n\n"
                      f"Context: The categories are: Nobel Prize, Awards, "
                      f"Membership,"
                      f"Press, Judging, Original Contribution, Scholarly "
                      f"Articles, "
                      f"Critical Employment, High Remuneration \n\n"
                      f"Question: List the categorizes with extracted "
                      f"information from the the CV. \n\n "
                      f"Rule: Do not list numbers."
                      f"Be sure to utilize the section headers in the CV"
                      f"in which each entry lies in to determine the categories."
                      f"Make sure each experience does not lie in multiple "
                      f"categories. Do not change original content.\n\n")

    # Process text in sliding window chunks and construct full prompt
    for i in range(0, len(text), max_tokens - stride):
        # Adjust max_tokens as per OpenAI's limit
        chunk = text[i:i + max_tokens]
        full_prompt = partial_prompt + chunk
        # call openAI API
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": full_prompt}],
            model="gpt-3.5-turbo")

        # Split the response text into lines
        lines = chat_completion.choices[0].message.content.split("\n")
        # Iterate through each line to extract response
        for line in lines:
            # Split each line into category and content
            parts = line.strip().split(": ", 1)
            if len(parts) == 2:
                category = clean_text(parts[0])
                content = parts[1].strip()
                if category in extracted_info:
                    extracted_info[category].append(content)
    return extracted_info


def refine_information(extracted_info):
    role_assignment_prompt = (
        "You need to identify and separate difference experiences in a "
        "dictionary entry into multiple experiences. Remove any N/A or None "
        "mentioned")

    full_prompt = (
        f"{role_assignment_prompt}\n\n"
        f"{extracted_info}\n\n"
        f"Context: The categories are: Nobel Prize, Awards, "
        f"Membership, Press, Judging, Original Contribution, Scholarly "
        f"Articles, Critical Employment, High Remuneration. \n\n"
        f"In Context Example: The experiences, Software Engineer Intern at "
        f"Adobe and "
        f"Software Engineer at Clario, should be separated into two "
        f"experiences in the same category\n\n"
        f"Rule: Do not list numbers. Do not rewrite. "
        f"Make sure each experience only show up in one category. Output in "
        f"python dictionary. \n\n")
    # call openAI API
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": full_prompt}],
        model="gpt-3.5-turbo", )

    # Process the response text into python dictionary
    lines = chat_completion.choices[0].message.content
    refined_info = ast.literal_eval(lines)

    return refined_info


def evaluate_criteria(refined_info):
    extracted_info_count = {category: 0 for category in CATEGORIES}

    full_prompt = (
        f"Evaluate the following information in each category and summarize "
        f"the count of evidence in each category:\n"
        f"{refined_info}\n"
        f"Question: Provide counts in integers for each category."
        f"Answer:"
        f"\n\n")
    # call openAI API
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": full_prompt}],
        model="gpt-3.5-turbo")

    # Split the response text into lines
    lines = chat_completion.choices[0].message.content.split("\n")
    # Iterate through each line to extract category and content
    for line in lines:
        # Split each line into category and content
        parts = line.strip().split(": ", 1)
        if len(parts) == 2:
            category = clean_text(parts[0])
            count = int(parts[1].strip())
            if category in extracted_info_count:
                extracted_info_count[category] = count
    return extracted_info_count
