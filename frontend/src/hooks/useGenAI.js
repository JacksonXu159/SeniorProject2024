import OpenAI from "openai";

const OPENAI_API_KEY = import.meta.env.VITE_OPENAI_API_KEY

const useGenAI = async (content) => {
    const openai = new OpenAI({
        apiKey: OPENAI_API_KEY
    });
    
    const completion = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            { role: "system", content: "You are a financial assistant" },
            {
                role: "user",
                content: "content",
            },
        ],
    });
    
    console.log(completion.choices[0].message);
    return completion.choices[0].message
}

useGenAI("Hi, what is your role?")

export default useGenAI