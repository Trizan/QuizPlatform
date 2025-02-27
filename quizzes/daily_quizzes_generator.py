import os
import json
from huggingface_hub import InferenceClient
import time
import requests


def get_quiz_from_awan_api(topic):
    """
    Generate a quiz using the Awan LLM API.
    """
    try:
        # API key should be stored in environment variables
        API_KEY = os.environ.get('AWANLLM_API_KEY', '')
        
        # API endpoint for Awan LLM
        API_ENDPOINT = "https://api.awanllm.com/v1/chat/completions"
        
        # Headers for the API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {API_KEY}"
        }
        
        # Craft an exceptional prompt for quiz generation
        system_prompt = """You are a quiz generation expert that creates high-quality multiple-choice questions. Your output must be a valid JSON object."""
        
        user_prompt = f"""
        Generate a high-quality, engaging multiple-choice quiz question about {topic}. 
        
        Requirements:
        - Create a challenging but fair question that tests knowledge about {topic}
        - Provide four possible answer options (labeled 1, 2, 3, 4)
        - One option must be correct, and the other three should be plausible but incorrect
        - Indicate which option (1-4) is the correct answer
        - Include a detailed explanation for why the correct answer is right and why the other options are wrong
        - Make the question engaging, educational, and thought-provoking
        
        Format your response as a valid JSON object with these exact keys:
        - question: The full question text
        - option1: First answer choice
        - option2: Second answer choice  
        - option3: Third answer choice
        - option4: Fourth answer choice
        - answer: Integer between 1-4 indicating the correct option
        - explanation: A detailed explanation of the correct answer
        
        Example format:
        {{
          "question": "What is the capital of France?",
          "option1": "London",
          "option2": "Paris",
          "option3": "Berlin",
          "option4": "Madrid",
          "answer": 2,
          "explanation": "Paris is the capital and largest city of France. London is the capital of the United Kingdom, Berlin is the capital of Germany, and Madrid is the capital of Spain."
        }}
        
        Return ONLY the JSON object, with no additional text.
        """
        
        # Create payload for the API request
        payload = {
            "model": "Meta-Llama-3.1-8B-Instruct",  # Replace with the appropriate model name
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "repetition_penalty": 1.1,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_tokens": 1024,
            "stream": False  # Set to False to get the full response at once
        }
        
        # Make the API request
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=30)
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract content from the response based on Awan LLM API structure
            if "choices" in response_data and len(response_data["choices"]) > 0:
                generated_text = response_data["choices"][0]["message"]["content"]
                
                # Find JSON in the text (sometimes models add extra text)
                json_start = generated_text.find("{")
                json_end = generated_text.rfind("}") + 1
                
                if json_start != -1 and json_end != -1:
                    json_text = generated_text[json_start:json_end]
                    # Parse the JSON
                    try:
                        quiz_data = json.loads(json_text)
                        
                        # Validate all required fields are present
                        required_fields = ["question", "option1", "option2", "option3", "option4", "answer"]
                        if all(field in quiz_data for field in required_fields):
                            # Ensure answer is an integer
                            try:
                                quiz_data["answer"] = int(quiz_data["answer"])
                                # If explanation is missing, get it from API
                                if "explanation" not in quiz_data or not quiz_data["explanation"]:
                                    explanation = get_explanation_from_awan_api(quiz_data, API_KEY)
                                    quiz_data["explanation"] = explanation
                                return quiz_data
                            except (ValueError, TypeError):
                                # If we can't convert answer to int, default to 1
                                quiz_data["answer"] = 1
                                # Still get explanation if needed
                                if "explanation" not in quiz_data or not quiz_data["explanation"]:
                                    explanation = get_explanation_from_awan_api(quiz_data, API_KEY)
                                    quiz_data["explanation"] = explanation
                                return quiz_data
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to extract the data manually
                        quiz_data = parse_non_json_response(generated_text, topic)
                        # Get explanation for manually parsed quiz
                        explanation = get_explanation_from_awan_api(quiz_data, API_KEY)
                        quiz_data["explanation"] = explanation
                        return quiz_data
                else:
                    # If no JSON markers found, try to extract data manually
                    quiz_data = parse_non_json_response(generated_text, topic)
                    # Get explanation for manually parsed quiz
                    explanation = get_explanation_from_awan_api(quiz_data, API_KEY)
                    quiz_data["explanation"] = explanation
                    return quiz_data
        
        # Handle rate limiting or other errors
        elif response.status_code == 429:
            print("Rate limit exceeded, waiting and trying again...")
            time.sleep(30)
            return create_fallback_quiz(topic)
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return create_fallback_quiz(topic)
                
    except Exception as e:
        print(f"Quiz Generation Error: {e}")
        return create_fallback_quiz(topic)

def get_explanation_from_awan_api(quiz_data, api_key):
    """
    Generate an explanation for the quiz answer using the Awan LLM API.
    """
    try:
        # Get the correct option text
        correct_option_number = quiz_data["answer"]
        correct_option_key = f"option{correct_option_number}"
        correct_option_text = quiz_data.get(correct_option_key, "")
        
        # API endpoint
        API_ENDPOINT = "https://api.awanllm.com/v1/chat/completions"
        
        # Headers for the API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {api_key}"
        }
        
        # Craft a system prompt for generating explanation
        system_prompt = "You are an educational expert who provides clear, concise explanations for quiz questions."
        
        # Craft a user prompt for generating explanation
        question = quiz_data.get("question", "")
        options = [
            quiz_data.get("option1", ""), 
            quiz_data.get("option2", ""),
            quiz_data.get("option3", ""),
            quiz_data.get("option4", "")
        ]
        
        user_prompt = f"""
        I need a clear, educational explanation for a quiz question.
        
        Question: {question}
        
        Options:
        1. {options[0]}
        2. {options[1]}
        3. {options[2]}
        4. {options[3]}
        
        Correct Answer: Option {correct_option_number} - {correct_option_text}
        
        Please provide a detailed explanation (about 3-5 sentences) of why this answer is correct and why the other options are incorrect. The explanation should be informative and educational.
        """
        
        # Create payload for the API request
        payload = {
            "model": "Meta-Llama-3.1-8B-Instruct",  # Replace with the appropriate model name
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "repetition_penalty": 1.1,
            "temperature": 0.5,
            "top_p": 0.9,
            "top_k": 40,
            "max_tokens": 400,
            "stream": False
        }
        
        # Make the API request
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=30)
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract content from the response based on Awan LLM API structure
            if "choices" in response_data and len(response_data["choices"]) > 0:
                generated_text = response_data["choices"][0]["message"]["content"].strip()
                return generated_text
            
        # Fallback explanation if request fails
        return f"The correct answer is option {correct_option_number}: {correct_option_text}. This option accurately represents the facts about this topic."
            
    except Exception as e:
        print(f"Explanation Generation Error: {e}")
        return f"The correct answer is option {correct_option_number}: {correct_option_text}."

# Reuse the existing helper functions from your original code
def parse_non_json_response(text, topic):
    """
    Attempt to parse quiz data from text that isn't valid JSON.
    This is a fallback method.
    """
    try:
        # Look for question and options in the text
        lines = text.split('\n')
        question = ""
        options = []
        answer = 1
        explanation = ""
        
        # Extract explanation if present
        explanation_start = -1
        for i, line in enumerate(lines):
            if "explanation" in line.lower() and ":" in line:
                explanation_start = i
                break
                
        if explanation_start > -1:
            # Collect all text after "explanation:"
            explanation_parts = []
            for i in range(explanation_start, len(lines)):
                line_text = lines[i].strip()
                if ":" in line_text and i == explanation_start:
                    line_text = line_text.split(":", 1)[1].strip()
                explanation_parts.append(line_text)
            explanation = " ".join(explanation_parts).strip()
        
        for line in lines:
            line = line.strip()
            
            # Try to identify the question
            if ('?' in line and not question and 
                not line.startswith(('option', 'answer', '1.', '2.', '3.', '4.'))):
                question = line
                continue
                
            # Try to identify options
            if (line.startswith(('1.', '2.', '3.', '4.')) or 
                line.startswith(('Option 1:', 'Option 2:', 'Option 3:', 'Option 4:'))):
                
                # Extract the option text
                option_text = line.split(':', 1)[-1].strip()
                if not option_text and len(line.split('.')) > 1:
                    option_text = line.split('.', 1)[-1].strip()
                
                if option_text:
                    options.append(option_text)
                continue
                
            # Try to identify the answer
            if 'answer' in line.lower() and ':' in line and 'explanation' not in line.lower():
                try:
                    answer_text = line.split(':', 1)[1].strip()
                    # Convert answer to int (handle various formats)
                    if answer_text.isdigit():
                        answer = int(answer_text)
                    elif answer_text.startswith(('1', '2', '3', '4')):
                        answer = int(answer_text[0])
                except:
                    answer = 1
        
        # If we have a question and 4 options, construct the quiz data
        if question and len(options) == 4:
            return {
                "question": question,
                "option1": options[0],
                "option2": options[1],
                "option3": options[2],
                "option4": options[3],
                "answer": answer,
                "explanation": explanation
            }
        
        # If we don't have enough data, create a generic quiz about the topic
        return create_fallback_quiz(topic)
        
    except Exception as e:
        print(f"Manual Parsing Error: {e}")
        # Last resort fallback
        return create_fallback_quiz(topic)

def create_fallback_quiz(topic):
    """
    Create a fallback quiz when API calls or parsing fails.
    """
    return {
        "question": f"Which of the following best describes {topic}?",
        "option1": f"A fundamental concept in its field",
        "option2": f"An innovative approach to problem-solving",
        "option3": f"A historically significant development",
        "option4": f"A cutting-edge area of research",
        "answer": 1,
        "explanation": f"The option describing {topic} as 'a fundamental concept in its field' is correct. {topic} forms the foundation of its discipline and is essential for understanding related concepts."
    }

if __name__ == "__main__":
    print("Hello")