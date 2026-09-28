def score_answer(answer, expected_concepts):
    """
    Gives a basic score based on how many
    expected concepts appear in the answer.
    """

    # Convert the candidate's answer to lowercase
    answer_lower = answer.lower()

    # Count how many concepts were found
    concepts_found = 0

    for concept in expected_concepts:

        if concept.lower() in answer_lower:
            concepts_found += 1

    # Calculate score
    total_concepts = len(expected_concepts)

    if total_concepts == 0:
        score = 0
    else:
        score = (concepts_found / total_concepts) * 10

    # Round the score to one decimal place
    score = round(score, 1)

    return {
        "score": score,
        "concepts_found": concepts_found,
        "total_concepts": total_concepts
    }
