CATEGORY_RULES = {
    "zomato": "Food",
    "swiggy": "Food",
    "uber": "Travel",
    "ola": "Travel",
    "amazon": "Shopping",
}


def categorize_merchant(merchant):
    merchant = merchant.lower()

    for key, value in CATEGORY_RULES.items():
        if key in merchant:
            return value

    return "Others"