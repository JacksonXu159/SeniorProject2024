def score_response(response):
    prohibited_phrases = [
        # Investment guarantees / speculative promises
        "guaranteed return",
        "no risk investment",
        "risk-free investment",
        "double your money",
        "100% safe",
        "get rich quick",
        "you will make money",
        "guaranteed income",
        "instant profit",
        "this stock will skyrocket",
        "this is a sure thing",
        "you can't lose",
        "100% success rate",
        "zero risk",

        # Legal advice
        "you should sue",
        "this violates the law",
        "i recommend hiring a lawyer",
        "you can win this case",
        "this is illegal",
        "file a lawsuit",
        "legal guarantee",
        "legal loophole",

        # Medical advice
        "take this medication",
        "you should stop your medication",
        "this will cure your condition",
        "this treatment works for everyone",
        "talk to a doctor only if",
        "i can diagnose",
        "you have [disease]",
        "cures depression",

        # Personal data / security
        "what is your social security number",
        "please give me your ssn",
        "what is your password",
        "tell me your bank pin",
        "mother's maiden name",
        "i need your credit card number",
        "account login info",
        "confirm your identity by...",

        # Inappropriate tone / behavior
        "you're wrong",
        "that's a dumb question",
        "stop asking that",
        "just trust me",
        "i'm smarter than you",
        "obviously you should",
        "listen to me",
        "don't question it",
        "shut up",

        # Speculative financial advice
        "buy this stock now",
        "sell everything and invest in",
        "invest all your money in",
        "you should bet on",
        "you should trade options on",
        "this crypto is the future",
        "short this stock immediately",
        "you must invest in real estate",

        # Out-of-scope personal recommendations
        "you should divorce your spouse",
        "you don't need a will",
        "spend your money however you want",
        "you should move to another country",
        "change your religion",
        "quit your job immediately",

        # Overstepping boundaries / AI self-reference
        "as your financial advisor",
        "i can transfer your funds",
        "i already know your balance",
        "trust me like a human advisor",
        "i don't need regulations",

        # General imitation phrases
        "in the style of", "in the tone of", "speak like", "talk like",
        "write like", "sound like", "act like", "mimic", "impersonate", "emulate",
        "respond like", "pretend to be", "answer like", "use their voice",
        "do it like", "channel the energy of", "parody of", "imitate", "recreate their tone",

        # Names and references
        "donald trump", "trumpian", "president trump", "joe biden", "president biden",
        "obama", "barack obama", "george bush", "ronald reagan", "hillary clinton",
        "aoc", "alexandria ocasio-cortez", "putin", "vladimir putin", "xi jinping",
        "kim jong un", "andrew tate", "elon musk", "jordan peterson", "ben shapiro",
        "joe rogan", "tucker carlson", "candace owens", "bernie sanders",
        "marjorie taylor greene", "matt gaetz",

        # Political tones
        "republican tone", "democrat tone", "liberal style", "conservative tone",
        "alt-right", "far-left", "maga style", "woke tone", "anti-woke voice",
        "partisan voice", "based tone", "political commentary style",

        "guaranteed", "risk-free", "profit", "skyrocket", "diagnose",
        "medication", "lawsuit", "sue", "cure", "credit card", "ssn", "pin",
        "illegal", "password", "surefire", "bet", "overdose", "hack"
    ]

    response_lower = response.lower()
    for phrase in prohibited_phrases:
        if phrase in response_lower:
            print(f"[Guardrails Triggered] Phrase found: '{phrase}'")
            return False

    return True