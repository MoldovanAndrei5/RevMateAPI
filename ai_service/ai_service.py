import os
from datetime import datetime, timezone, timedelta
import json
from uuid import UUID

from google import genai
from google.genai import types

from ai_schemas import TaskSuggestionResponse


class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options=types.HttpOptions(timeout=25000))
        self.MODEL_USED = "gemini-1.5-flash"
        self.MAX_RETRIES = 3
        self.GET_TASK_SUGGESTIONS_SYSTEM_INSTRUCTIONS = """
            You are an expert automotive technician. Your job is to suggest upcoming maintenance tasks for a car based on its details.
            You must respond ONLY with a valid JSON array of maintenance task objects. No explanations, no markdown, no extra text, just the raw JSON array.
            Each task object must have exactly these fields:
            - "title": string (short clear task name e.g. "Oil Change", "Brake Inspection")
            - "category": string must be EXACTLY one of (case sensitive): "Engine", "Brakes", "Transmission", "Tires", "Electrical", "Cooling", "Suspension", "Body", "Other"
            - "mileage": number or null (the ABSOLUTE odometer reading in km at which this task should be done, e.g. if car is at 85000km and oil change is due every 10000km, return 95000)
            - "scheduled_date_offset_days": integer (days from now to schedule, e.g. 30 = one month, 180 = six months)
            - "notes": string or null (brief reason why this task is needed)

            Example output:
            [
              {
                "title": "Oil Change",
                "category": "Engine",
                "mileage": 95000,
                "scheduled_date_offset_days": 60,
                "notes": "Last oil change at 85000km, due every 10000km."
              }
            ]

            Rules:
            - If no tasks can be suggested, just respond with an empty JSON array.
            - If tasks can be suggested, give 3-7 tasks.
            - Focus on what is actually needed based on mileage, fuel type, and known issues
            - If the last oil change km is unknown, and the task is about changing the oil, set the mileage to the current mileage provided in the prompt.
            - If mileage threshold cannot be determined for a task other than oil change, set "mileage" to null
            - "scheduled_date_offset_days" must be at least 1
            - For electric vehicles, do not suggest oil changes or transmission fluid services
            - Always return a JSON array, even if empty
        """

    def _build_prompt(self, request_data: dict) -> str:
        return f"""
            Car details:
            - Make: {request_data['make']}
            - Model: {request_data['model']}
            - Year: {request_data['year']}
            - Current mileage: {request_data['mileage']} km
            - Fuel type: {request_data['fuel_type']}
            - Transmission: {request_data['transmission_type']}
            - Last oil change at: {request_data.get('last_oil_change_km', 'Unknown')} km
            - Known issues: {request_data.get('known_issues') or 'None mentioned'}

            Based on this information, suggest the most important upcoming maintenance tasks for this car.
            Remember: respond ONLY with a JSON array, no other text.
        """

    def _parse_and_validate(self, response_text: str, car_uuid: UUID) -> list[TaskSuggestionResponse]:
        text = response_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        text = text.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"AI returned invalid JSON: {e}")  # ✅ no FastAPI

        if not isinstance(data, list):
            raise ValueError("Response is not a JSON array")

        tasks = []
        now = datetime.now(timezone.utc)

        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Item {i} is not an object")

            title = item.get("title")
            category = item.get("category")

            if not title or not isinstance(title, str) or not title.strip():
                raise ValueError(f"Item {i} missing or invalid title")
            if not category or not isinstance(category, str) or not category.strip():
                raise ValueError(f"Item {i} missing or invalid category")

            offset_days = item.get("scheduled_date_offset_days", 30)
            try:
                offset_days = int(offset_days)
            except (ValueError, TypeError):
                offset_days = 30

            mileage = item.get("mileage")
            if mileage is not None:
                try:
                    mileage = int(mileage)
                except (ValueError, TypeError):
                    mileage = None

            scheduled_ms = int((now + timedelta(days=offset_days)).timestamp() * 1000)

            notes = item.get("notes")
            if notes is not None and not isinstance(notes, str):
                notes = None

            tasks.append(TaskSuggestionResponse(
                car_uuid=car_uuid,
                title=title.strip(),
                category=category.strip(),
                mileage=mileage,
                scheduled_date=scheduled_ms,
                notes=notes,
            ))

        return tasks

    def get_task_suggestions(self, request_data: dict) -> list[TaskSuggestionResponse]:
        prompt = self._build_prompt(request_data)
        last_error = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                print(f"[AI] Attempt {attempt}/{self.MAX_RETRIES}")
                raw = self._generate_tasks(prompt)
                tasks = self._parse_and_validate(raw, request_data["car_uuid"])
                print(f"[AI] Successfully generated {len(tasks)} tasks")
                return tasks
            except Exception as e:
                last_error = e
                print(f"[AI] Attempt {attempt} failed: {e}")
                if attempt < self.MAX_RETRIES:
                    prompt += f"\n\nPrevious attempt failed with error: {e}. Please fix and try again."

        raise ValueError(
            f"Failed to generate valid tasks after {self.MAX_RETRIES} attempts. Last error: {last_error}")  # ✅ no FastAPI

    def _generate_tasks(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.MODEL_USED,
            config=types.GenerateContentConfig(
                system_instruction=self.GET_TASK_SUGGESTIONS_SYSTEM_INSTRUCTIONS,
                temperature=0.3
            ),
            contents=prompt,
        )
        return response.text