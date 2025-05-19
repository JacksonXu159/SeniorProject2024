def get_page_suggestions(frontend_url: str):

    page = frontend_url.strip('/').lower() 
    if not page: 
        page = 'dashboard'
    elif '/' in page:
        page = page.split('/')[-1]
    
    print(f"Getting suggestions for page: {page}")
    
    suggestions = {
        'dashboard': [
            "What's my current balance?",
            "Show me my recent transactions",
            "How can I transfer money?"
        ],
        'services': [
            "What services am I enrolled in?",
            "How do I enroll in a new service?",
            "What are my service fees?",
            "How do I cancel a service?"
        ],
        'transactions': [
            "Show me my recent transactions",
            "How do I make a transfer?",
            "What are the transaction fees?",
            "How do I set up recurring payments?"
        ],
        'account': [
            "How do I update my address?",
            "How do I change my password?",
            "How do I update my contact information?"
        ]
    }
    
    result = suggestions.get(page, [])
    print(f"Suggestions for {page}: {result}")
    return result 