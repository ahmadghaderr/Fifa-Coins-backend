import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import HTTPException
from database import get_current_rate

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise HTTPException(status_code=500, detail="GOOGLE_API_KEY missing")

genai.configure(api_key=api_key)

model_name = "gemini-2.5-pro"
model = genai.GenerativeModel(model_name)

async def handle_chatbot_message(message: str, is_first_message: bool = False) -> str:
    msg_lower = message.lower()

    if is_first_message:
        return (
            "Hello! As the assistant for the FIFA Coins website, I can help you with:\n"
            "* The current coin rate\n"
            "* Calculating your profit\n"
            "* Signup or login help\n"
            "* Your calculation history\n"
            "How can I assist you today?"
        )

    if msg_lower in ["great","oh okay", "thanks", "thank you", "good", "nice"]:
        return "Glad to hear that! Do you need any more help?"

    if msg_lower in ["hi", "hello", "hey", "hi there", "hello there", "what can you do", "what do you do", "help"]:
        return (
            "Hello! I'm your assistant for the FIFA Coins website.\n\n"
            "I can help you with:\n"
            "- Coin rate\n"
            "- Profit calculations\n"
            "- Viewing your calculation history\n"
            "Ask me anything related to those!"
        )

    if any(phrase in msg_lower for phrase in [
        "try to do calculation with my own rate",
        "use my own rate",
        "calculate with my rate",
        "can i use my own rate",
        "use custom rate",
        "use different rate",
        "try calculation with my rate",
    ]):
        return (
            "No, the rate used for calculations is taken directly from the website’s current coin rate "
            "and cannot be manually changed. This ensures accuracy and consistency for all users."
        )

    if any(kw in msg_lower for kw in [
        "importance", "important", "what is the website for", "why website",
        "why use website", "what can i do on website", "purpose of the website",
        "what does the website do", "what is the point of the website"
    ]):
        return (
            "The chatbot helps with quick answers, but the website offers the full experience:\n\n"
            "Why Use the Website?\n"
            "- Save and track all your profit calculations in your personal history.\n"
            "- Mark deals as 'Paid' to stay organized.\n"
            "- Access a faster, more visual profit calculator.\n"
            "- Manage your account, see full stats, and access premium features.\n\n"
            "You’ll get more value when you log in and use the full website!"
        )

    if any(phrase in msg_lower for phrase in [
        "use without login", "without login", "without signup", "without account",
        "can i use without login", "i can't use any page without login"
    ]):
        return (
            "For security and personalized features, you need to log in or sign up to access most pages on the site.\n\n"
            "You can use some features like the profit calculator without logging in, but to save your calculations, view history, "
            "and access other pages, an account is required."
        )

    if "rate" in msg_lower or "coin rate" in msg_lower:
        rate_response = await get_current_rate()
        if rate_response is None:
            return "Sorry, the current coin rate is not available right now."
        return f"The current coin rate is {rate_response}$ per 1M coins."

    if "calculate profit" in msg_lower:
        real_price_match = re.search(r"real price\s*([0-9]+)", msg_lower)
        buy_price_match = re.search(r"buy price\s*([0-9]+)", msg_lower)

        if real_price_match and buy_price_match:
            try:
                real_price = int(real_price_match.group(1))
                buy_price = int(buy_price_match.group(1))

                rate = await get_current_rate()
                if rate is None:
                    return "Sorry, the current coin rate is not available right now."

                coins_received = buy_price * 0.95
                coin_profit = coins_received - real_price
                money_profit = (coin_profit / 1_000_000) * rate

                return (
                    "Profit Calculation:\n"
                    f"- You listed the player for {buy_price} coins.\n"
                    f"- After 5% EA tax, you receive: {coins_received:.0f} coins.\n"
                    f"- Real price of player: {real_price} coins.\n"
                    f"- Coin profit: {coin_profit:.0f} coins.\n"
                    f"- Money profit: ${money_profit:.2f} (at ${rate} per 1M).\n\n"
                    "You can also do this calculation directly on our website for faster results, "
                    "and your calculations will be saved in your history automatically!"
                )
            except Exception as e:
                print("Profit Calculation Error:", type(e), e)
                return "There was an error processing your profit calculation. Please try again."
        else:
            return (
                "To calculate your profit, please provide both values like this:\n"
                "`calculate profit enter the real and buy price`"
            )

    if any(keyword in msg_lower for keyword in [
        "how calculate", "how to calculate", "calculation method", "how profit", "profit work"
    ]):
        rate = await get_current_rate()
        if rate is None:
            return "Sorry, the current coin rate is not available right now."

        system_prompt = (
            "You are a helpful assistant for the FIFA Coins website.\n"
            "Explain in simple, clear steps how profit calculation works, using these rules:\n"
            "1. EA takes 5% tax from the player's sell price.\n"
            "2. Subtract the real price the user paid from the amount received (after tax) to get coin profit.\n"
            "3. Then convert coin profit to money using this formula:\n"
            "(Coin Profit / 1,000,000) × Rate per 1M.\n\n"
            f"The current coin rate is ${rate} per 1M coins.\n"
            "Give a helpful example using 1,000,000 coins and a realistic scenario."
        )

        prompt = f"{system_prompt}\nUser: {message}\nAssistant:"
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print("AI API Error:", type(e), e)
            return "Sorry, I couldn't process that right now. Please try again later."

    rate = await get_current_rate()
    rate_str = f"${rate} per 1M coins." if rate else "Unavailable"

    system_prompt = (
        "You are a helpful assistant for the FIFA Coins website.\n"
        "You can only answer questions about: coin rate, profit calculation, and calculation history.\n"
        "If the user asks about profit, always include both the coin profit and the money profit.\n"
        "Money profit is calculated as: (coin profit / 1,000,000) × rate.\n"    
        f"The current coin rate is {rate_str}\n"
    )

    prompt = f"{system_prompt}\nUser: {message}\nAssistant:"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("AI API Error:", type(e), e)
        return "Sorry, I couldn't process that right now. Please try again later."
