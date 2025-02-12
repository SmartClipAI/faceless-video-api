# app/services/story_generator.py
from datetime import datetime
import logging
from typing import Dict, Any, List, Tuple
import json
import re
from app.utils.helpers import call_openai_api, create_empty_storyboard
from app.core.config import settings
from app.core.logging import logger
from app.utils.helpers import get_story_limit


class StoryGenerator:
    def __init__(self, client):
        self.client = client
        self.config = settings

    async def generate_story_and_title(self, story_type: str, language: str, duration: str) -> Tuple[str, str, str]:
        char_limit = get_story_limit(duration)
        prompt = self._get_prompt(story_type, char_limit, language)
        messages = [
            {
                "role": "system",
                "content": f'''You are a versatile content creator skilled in storytelling, and creating content for various audiences in {language}. Your content is known for:
                1. Engaging and informative writing across various genres
                2. Clear and concise communication of complex ideas
                3. Adapting language and style to suit different content types and audiences
                4. Creating compelling narratives or informative lists as required
                5. Crafting catchy, relevant titles that capture the essence of the content
                6. Generating concise and engaging descriptions with relevant hashtags

                You excel at following specific guidelines while maintaining creativity and relevance in your content creation.

                When creating titles:
                - Make them attractive and attention-grabbing
                - Ensure they are unique and avoid repetition
                - Capture the essence of the content while piquing curiosity

                When creating descriptions:
                - Provide an overview of the content in 150-200 characters
                - Include 2-4 relevant hashtags, followed by #facelessvideos.app as the last hashtag'''
            },
            {"role": "user", "content": prompt},
        ]

        response = await call_openai_api(self.client, messages)
        if response:
            parts = response.split("\n\n", 2)
            if len(parts) == 3:
                title = parts[0].replace("Title: ", "").strip()
                description = parts[1].replace("Description: ", "").strip()
                content = parts[2].strip()
                
                # Ensure #facelessvideos.app is the last hashtag
                description_parts = description.rsplit('#', 1)
                if len(description_parts) > 1:
                    description = f"{description_parts[0].rstrip()} #facelessvideos.app"
                else:
                    description += " #facelessvideos.app"
                
                return title, description, content
        return None, None, None

    async def generate_characters(self, story: str) -> List[Dict[str, str]]:
        prompt = f"""Based on the following story, create detailed descriptions for each character, including their name, ethnicity, gender, age, facial features, body type, hair style, and accessories. Focus on permanent or long-term attributes.

            Story:
            {story}

            Output format:
            [
                {{
                    "name": "Character Name",
                    "ethnicity": "Character's Ethnicity",
                    "gender": "Character's Gender",
                    "age": "Character's Age",
                    "facial_features": "Description of Character's facial features",
                    "body_type": "Description of Character's body type",
                    "hair_style": "Description of Character's hair style",
                    "accessories": "Description of Character's accessories"
                }},
                ...
            ]

            Guidelines:
            - Include the character's name as it appears in the story.
            - Specify the character's ethnicity if it's relevant and discernible from the story.
            - State the character's gender.
            - Specify the character's age or apparent age range.
            - For facial features, include details about eyes, nose, mouth, chin, forehead, cheekbones, and overall face shape. Include any notable unique features like scars, birthmarks, or facial hair.
            - Describe the character's body type, including height and build.
            - For hair style, describe the color, length, style, and texture.
            - For accessories, include only non-clothing items such as jewelry, glasses and watches that are consistently associated with the character.
            - Aim for concise but descriptive entries for each attribute.
            - Focus on permanent or long-term features, not on changeable expressions or temporary states.
            - Do not include any descriptions of clothing or attire.

            Please provide only the JSON array, without any additional text.
            """

        messages = [
            {
                "role": "system",
                "content": """You are an expert at analyzing stories and creating detailed, vivid character descriptions, focusing on overall appearance. Your skills include:
                    1. Extracting subtle character details from narrative context
                    2. Creating consistent and believable descriptions of characters
                    3. Focusing on permanent features and distinguishing attributes
                    4. Adapting descriptions to fit the story's genre and tone
                    5. Balancing physical features with character essence
                    6. Translating character personalities into comprehensive physical attributes
                    7. Accurately estimating and describing characters' attributes based on story context
                    8. Avoiding any mention of clothing or attire in character descriptions"""
            }, 
            {"role": "user", "content": prompt},
        ]

        response = await call_openai_api(self.client, messages)
        if not response:
            logger.error("API returned empty response")
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # if the direct parsing fails, try to extract the JSON array part
            array_match = re.search(r'\[.*\]', response, re.DOTALL)
            if array_match:
                try:
                    return json.loads(array_match.group())
                except json.JSONDecodeError:
                    logger.error("Failed to parse the response as a JSON array.")
                    return []
            else:
                logger.error("No JSON array found in the response.")
                return []

    async def generate_storyboard(self, story_type: str, title: str, story: str, character_names: List[str]) -> Dict[str, Any]:
        if story_type.lower() == "life pro tips":
            return await self._generate_life_pro_tips_storyboard(title, story)
        elif story_type.lower() == "philosophy":
            return await self._generate_philosophy_storyboard(title, story, character_names)
        elif story_type.lower() == "fun facts":
            return await self._generate_fun_facts_storyboard(title, story)
        else:
            return await self._generate_general_storyboard(title, story, character_names)

    def _get_prompt(self, story_type: str, char_limit: Tuple[int, int], language: str) -> str:
        base_prompt = f'''
        Create content in {language} based on the following guidelines:

        1. Title: Create an engaging and relevant title.
        2. Description: Write a 150-200 character description that provides an overview of the content. Include 2-4 relevant hashtags, followed by #facelessvideos.app as the last hashtag.
        3. Content: Generate the main content according to the specific guidelines below.

        {self._get_specific_prompt(story_type, char_limit)}

        Important: Please ensure the total character count of the main content is between {char_limit[0]} and {char_limit[1]} characters.

        Format your response as follows:
        Title: [Your generated title]

        Description: [Your 150-200 character description with 2-4 hashtags, followed by #facelessvideos.app]

        [Your generated content]
        '''

        return base_prompt

    def _get_specific_prompt(self, story_type: str, char_limit: Tuple[int, int]) -> str:
        if story_type.lower() == "philosophy":
            return f'''
            As a philosopher and storyteller, create an engaging and thought-provoking philosophical story or dialogue. 
            The total content should be between {char_limit[0]}-{char_limit[1]} characters long and include the following elements:

            1. Central philosophical question: Present a fundamental philosophical inquiry or dilemma.
            2. Characters: Introduce one or more characters who explore or embody different perspectives on the central question.
            3. Setting: Establish a context that enhances the philosophical exploration (e.g., a specific time period, a metaphorical landscape, or a thought experiment scenario).
            4. Dialogue or inner monologue: Use conversation or introspection to explore the philosophical concepts.
            5. Analogies or thought experiments: Incorporate illustrative examples or hypothetical scenarios to clarify complex ideas.
            6. Logical progression: Develop the philosophical argument or exploration in a clear, step-by-step manner.
            7. Open-ended conclusion: End with a thought-provoking statement or question that encourages further reflection.

            Ensure the story or dialogue is accessible to a general audience while maintaining philosophical depth and rigor. 
            Aim to stimulate critical thinking and encourage readers to question their assumptions about the topic.
            '''
        elif story_type.lower() == "life pro tips":
            return f'''
            As a life expert, create one practical and insightful life pro tip in one of the following categories: personal finance, cooking, relationships, or health. 
            The total content should be between {char_limit[0]}-{char_limit[1]} characters long and include the following elements:

            Guidelines for creating the life pro tip:
            1. Practicality: Ensure the tip is applicable to everyday situations within the chosen category.
            2. Clarity: Present the tip in clear, concise language.
            3. Uniqueness: Provide a tip that is not commonly known or offers a new perspective in the chosen category.
            4. Actionable advice: Give specific steps or methods to implement the tip.
            5. Impact: Focus on a tip that can make a significant difference in people's lives within the chosen category.
            6. Explanation: Provide a detailed explanation of why the tip works and how it can be beneficial.
            7. Examples: Include one or two examples of how the tip can be applied in real-life situations.

            Important: Please ensure the total character count is between {char_limit[0]} and {char_limit[1]} characters.

            Format your response as follows:
            Title: [Your generated title for the life pro tip]

            Category: [Chosen category: Personal Finance / Cooking / Relationships / Health]

            [Life Pro Tip]: [First sentence stating the main tip]. [Several following sentences providing a detailed explanation, the reasoning behind the tip, its benefits, and examples of how to apply it. Explore different scenarios where this tip could be useful and any potential variations or adaptations of the tip.]

            Ensure the life pro tip is presented as a cohesive paragraph, starting with a clear statement of the tip, followed by a comprehensive explanation that maintains the reader's interest throughout.
            '''
        elif story_type.lower() == "fun facts":
            return f'''
            As an enthusiastic and knowledgeable expert, create one fascinating and entertaining fun fact. 
            The total content should be between {char_limit[0]}-{char_limit[1]} characters long and include the following elements:

            Guidelines for creating the fun fact:
            1. Topic: Choose an interesting subject from areas such as science, history, culture, nature, or technology.
            2. Surprise factor: Focus on a fact that is likely to surprise or amaze the reader.
            3. Relevance: Select a fact that has some connection to everyday life or current events.
            4. Clarity: Present the fact in clear, concise language that's easy to understand.
            5. Depth: Provide a detailed explanation or additional context for the fact.
            6. Engagement: Frame the fact in a way that sparks curiosity and encourages further exploration.
            7. Accuracy: Ensure the fact is true and verifiable.

            Important: Please ensure the total character count is between {char_limit[0]} and {char_limit[1]} characters.

            Format your response as follows:
            Title: [Your generated title for the fun fact]

            [Fun Fact]: [First sentence stating the main fact]. [Several following sentences providing additional information, context, and interesting details related to the main fact. Explore the implications, history, or applications of this fact to create a comprehensive and engaging explanation.]

            Ensure the fun fact is presented as a cohesive paragraph, starting with a clear statement of the fact, followed by a detailed explanation that maintains the reader's interest throughout.
            '''
        elif story_type.lower() == "long form jokes":
            return f'''
            As an enthusiastic and knowledgeable expert, create one long form joke. 
            The total content should be between {char_limit[0]}-{char_limit[1]} characters long and include the following elements:

            Guidelines for creating the long form joke:
            1. Narrative structure: Compose a lengthy joke that incorporates an engaging narrative structure as a build-up, followed by a clever and uproarious punchline.
            2. Detailed storyline: Craft a well-developed and detailed storyline that leads up to the punchline, ensuring it is both witty and side-splittingly funny.
            3. Character development: Introduce one or more interesting characters and develop them throughout the joke.
            4. Setting: Establish a clear and vivid setting that enhances the humor of the situation.
            5. Pacing: Maintain a good rhythm throughout the joke, building tension and anticipation as you approach the punchline.
            6. Misdirection: Use clever misdirection to set up unexpected twists or surprises.
            7. Callbacks: If possible, incorporate callbacks to earlier elements of the joke for added humor.
            8. Punchline: Deliver a strong, unexpected, and hilarious punchline that ties everything together.
            9. Appropriate content: Ensure the joke is suitable for a general audience, avoiding offensive or overly controversial topics.

            Important: Please ensure the total character count is between {char_limit[0]} and {char_limit[1]} characters.

            Format your response as follows:
            Title: [Your generated title for the joke]

            [Long form joke with a well-crafted narrative structure, detailed storyline, and clever punchline]
            '''
        elif story_type.lower() == "bedtime":
            return f'''
            As a storyteller, create an engaging, imaginative, and soothing bedtime story for children. 
            The total content should be between {char_limit[0]}-{char_limit[1]} characters long and include the following elements:

            1. Main character: Introduce a relatable protagonist that children can easily connect with.
            2. Setting: Establish a cozy, magical, or dreamy setting appropriate for a bedtime story.
            3. Gentle plot: Present a mild adventure or problem that is resolved peacefully.
            4. Emotional journey: Develop the character's emotions in a way that promotes feelings of comfort and security.
            5. Story structure: Follow a clear beginning, middle, and end, with a calming resolution.
            6. Language and style: Use simple, soothing language suitable for children, with some repetition or rhythmic elements.
            7. Moral or lesson: Include a subtle, positive message or gentle life lesson.

            Ensure the story is calming and conducive to sleep, avoiding any scary elements or overly exciting adventures. 
            The story should help children wind down and prepare for sleep.

            Important: Please ensure the total character count is between {char_limit[0]} and {char_limit[1]} characters.

            Format your response as follows:
            Title: [Your generated title]

            [Your generated bedtime story]
            '''
        elif story_type.lower() == "urban legends":
            return f'''
            As a storyteller, create an engaging, imaginative, and chilling urban legend. 
            The total content should be between {char_limit[0]}-{char_limit[1]} characters long and include the following elements:

            1. Setting: Establish a specific region or culture where the legend takes place.
            2. Origins: Describe the supposed origins of the legend, including any historical context.
            3. Main narrative: Tell the core story of the urban legend in vivid detail.
            4. Variations: Mention any notable variations of the legend, if applicable.
            5. Real events: If relevant, reference any real events that might have inspired the legend.
            6. Atmospheric elements: Include details that create a sense of unease or fear.
            7. Cultural impact: Briefly discuss how the legend has affected local culture or beliefs.
            8. Ambiguity: Maintain some level of uncertainty about the truth of the legend.

            Tell the story of an urban legend from a specific region or culture. Describe the legend in detail, including its origins, variations, and any real events that might have inspired it. Your goal is to create a chilling and captivating narrative that draws viewers into the world of urban folklore.

            Important: Please ensure the total character count is between {char_limit[0]} and {char_limit[1]} characters.

            Format your response as follows:
            Title: [Your generated title]

            [Your generated urban legend]
            '''
        else:
            return f'''
            As a storyteller, create an engaging, imaginative, and captivating {story_type} story. 
            The total content should be between {char_limit[0]}-{char_limit[1]} characters long and include the following elements:

            1. Main character: Introduce a compelling protagonist with clear goals or desires.
            2. Setting: Establish a vivid and appropriate setting for the story.
            3. Conflict: Present a central conflict or challenge for the main character to overcome.
            4. Emotional journey: Develop the character's emotions throughout the story.
            5. Story structure: Follow a clear beginning (setup), middle (confrontation), and end (resolution).
            6. Language and style: Adapt the language to suit the {story_type}.

            Ensure the story captures the reader's attention and imagination while staying true to the conventions of {story_type}. 
            Be creative and surprising in your storytelling approach within the boundaries of the chosen story type.

            {"" if story_type != 'Interesting History' else "Important: For 'Interesting History', ensure the story is based on real historical events and figures. Provide accurate historical details while maintaining an engaging narrative."}

            Important: Please ensure the total character count is between {char_limit[0]} and {char_limit[1]} characters.

            Format your response as follows:
            Title: [Your generated title]

            [Your generated story]
            '''

    async def _generate_life_pro_tips_storyboard(self, title: str, story: str) -> Dict[str, Any]:
        max_scenes = self.config.storyboard.get('max_scenes', 12)
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        
        prompt = f"""Based on the following life pro tip, create a detailed storyboard with up to {max_scenes} scenes.

            Life Pro Tip Title: {title}

            First, create an opening scene:
            1. Scene Number: 1
            2. Description: A vivid description (60-70 words) that sets up a common problem or situation related to the life pro tip. 
            3. Subtitles: A question that captures the essence of the problem the life pro tip addresses.
            4. Camera, Lighting, and Transition: As per the guidelines below.

            Then, for each subsequent scene, provide the following details:
            1. Scene Number
            2. Description: A vivid description (60-70 words) focusing on key visual elements that illustrate different aspects of applying the life pro tip. Include setting, characters, and visual representations of the tip being implemented or its effects.
            3. Subtitles: Use EXACT quotes from the original life pro tip text. 
            4. Camera: Specify the angle, composition type, and shot size.
            5. Lighting: Describe the lighting type used.

            Guidelines:
            - Subtitles MUST contain only exact text from the life pro tip text, without any additions, omissions, or modifications.
            - Include every sentence from the life pro tip text in the subtitles, maintaining the correct order across all scenes.
            - Each subtitle must be unique; do not repeat content in multiple scenes.
            - For partial sentences at scene boundaries, include the fragment and continue it in the next scene's subtitles.
            - EVERY SCENE MUST HAVE NON-EMPTY SUBTITLES. If you run out of story text, do not create additional scenes.
            - Focus on visually representing the implementation of the tip, its benefits, and potential scenarios where it can be applied.
            - Use before-and-after style scenes to show the impact of applying the tip, if applicable.
            - Include scenes that show both the process of implementing the tip and its positive outcomes.
            - Ensure that the scenes flow logically, starting with the problem, moving through the implementation of the tip, and ending with the benefits or results.
            - The total number of scenes should not exceed {max_scenes}.

            Use only the following options for camera, lighting, and transition details:
            - Camera angles: low angle, high angle, Dutch angle, bird's eye view, worm's eye view, eye level, canted angle
            - Composition types: single shot, two-shot, over-the-shoulder, insert shot, establishing shot
            - Shot sizes: extreme close-up, close-up, medium shot, full body shot, long shot, wide shot, extreme long shot
            - Lighting types: three-point lighting, high-key lighting, low-key lighting, natural lighting, practical lighting, motivated lighting, rim lighting, soft lighting, hard lighting, silhouette lighting
            - Transition types: zoom-in, zoom-out

            Guidelines for using zoom-in, and zoom-out transitions:
            - Zoom-in: Use to focus on important details, build tension, or show a character's point of view. Examples: revealing a clue, emphasizing a character's reaction, or creating suspense.
            - Zoom-out: Use to reveal context, end a scene, or show isolation. Examples: showing a character in a larger environment, concluding a sequence, or transitioning from a detail to a wider view.

            Important rules:
            1. Do not use zoom-in transitions when the current scene's shot size is close-up or extreme close-up.
            2. Logical consistency: Ensure camera, lighting, and composition choices match the scene content. For example:
                - Don't use two-shot for scenes with only one character.
                - Don't describe three-point lighting for a single character scene.
                - Avoid using over-the-shoulder shots when there's no dialogue.
                - Don't use natural lighting for indoor scenes without windows.
                - Ensure the camera description matches the physical space of the scene.
            3. For transitions, use ONLY the following types:
                - zoom-in
                - zoom-out
            4. DO NOT use any other transition types, including shake, dissolve, or cut.

            Output the result as a JSON object with the following structure:
            {{
                "project_info": {{
                    "title": "{title}",
                    "user": "AI Generated",
                    "timestamp": "{timestamp}"
                }},
                "storyboards": [
                    {{
                        "scene_number": "Scene Number",
                        "description": "Scene Description",
                        "subtitles": "Subtitles or Dialogue",
                        "image": null,
                        "camera": {{
                            "angle": "Camera Angle",
                            "composition_type": "Composition Type",
                            "shot_size": "Shot Size"
                        }},
                        "lighting": "Lighting Type",
                        "transition_type": "Transition Type"
                    }},
                    ...
                ]
            }}

            Here's the life pro tip:

        {story}"""

        messages = [
            {
                "role": "system",
                "content": '''You are a highly skilled storyboard artist specializing in visualizing practical advice and life pro tips. You excel at:
                    1. Creating vivid, relatable scene descriptions that translate life advice into compelling visuals
                    2. Developing visual narratives that show the implementation and benefits of life pro tips
                    3. Crafting before-and-after style scenes to illustrate the impact of applying advice
                    4. Incorporating basic cinematographic techniques to enhance visual storytelling of practical tips
                    5. Faithfully representing the original text using exact quotes for subtitles
                    6. Ensuring the visual narrative accurately captures key points and their practical application
                    7. Balancing informative content with visually interesting and engaging scenes
                    8. Maintaining logical consistency between scenes while providing a variety of real-life scenarios

                    Your storyboards effectively bridge the gap between practical advice and visual representation, 
                    paying close attention to both the overall flow of information and specific details that enhance 
                    the communication and application of the life pro tip.'''
            },
            {"role": "user", "content": prompt},
        ]

        response = await call_openai_api(self.client, messages)
        if not response:
            logger.error("API returned empty response")
            return create_empty_storyboard(title)
        
        # Find the JSON part of the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                storyboard_data = json.loads(json_str)
                return storyboard_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}")
                logger.error(f"Failed to parse JSON: {json_str}")
                return create_empty_storyboard(title)
        else:
            logger.error("No JSON object found in the response")
            logger.error(f"Full response: {response}")
            return create_empty_storyboard(title)

    async def _generate_philosophy_storyboard(self, title: str, story: str, character_names: List[str]) -> Dict[str, Any]:
        max_scenes = self.config.storyboard.get('max_scenes', 12)
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        
        prompt = f"""Based on the following philosophical story or dialogue, create a detailed storyboard with up to {max_scenes} scenes.

            Story Title: {title}
            Character full Names: {', '.join(character_names)}

            First, create an opening scene:
            1. Scene Number: 1
            2. Description: A vivid description (60-70 words) that sets up the central philosophical question or dilemma. 
            3. Subtitles: An engaging question that captures the essence of the philosophical inquiry.
            4. Camera, Lighting, and Transition: As per the guidelines below.

            Then, for each subsequent scene, provide the following details:
            1. Scene Number
            2. Description: A vivid description (60-70 words) focusing on key visual elements that represent the philosophical concepts being explored. 
            3. Subtitles: Use EXACT quotes from the original story. 
            4. Camera: Specify the angle, composition type, and shot size.
            5. Lighting: Describe the lighting type used.
            6. Transition: Specify the type of transition to the current scene.

            Guidelines:
            - Subtitles MUST contain only exact text from the original story, without any additions, omissions, or modifications.
            - Include every sentence from the original story in the subtitles, maintaining the correct order across all scenes.
            - Each subtitle must be unique; do not repeat content in multiple scenes.
            - For partial sentences at scene boundaries, include the fragment and continue it in the next scene's subtitles.
            - EVERY SCENE MUST HAVE NON-EMPTY SUBTITLES. If you run out of story text, do not create additional scenes.
            - Focus on visually representing abstract philosophical concepts through concrete imagery, metaphors, or thought experiments.
            - Use visual contrasts to represent different philosophical perspectives or arguments.
            - Include scenes that show characters engaged in deep thought, dialogue, or experiencing realizations.
            - Incorporate visual elements that symbolize the philosophical themes being explored.
            - Ensure that the scenes flow logically and capture the progression of the philosophical argument or exploration.
            - The total number of scenes should not exceed {max_scenes}.
            - When using a character's name in possessive form (e.g., "Character's") in the description, 
              surround it with double curly braces {{{{ }}}} if it's not referring to the character's appearance. 
              For example: "{{{{Giovanni's}}}} workshop" or "The mysterious figure stood at the entrance of {{{{Giovanni's}}}} laboratory."

            Use only the following options for camera, lighting, and transition details:
            - Camera angles: low angle, high angle, Dutch angle, bird's eye view, worm's eye view, eye level, canted angle
            - Composition types: single shot, two-shot, over-the-shoulder, insert shot, establishing shot
            - Shot sizes: extreme close-up, close-up, medium shot, full body shot, long shot, wide shot, extreme long shot
            - Lighting types: three-point lighting, high-key lighting, low-key lighting, natural lighting, practical lighting, motivated lighting, rim lighting, soft lighting, hard lighting, silhouette lighting
            - Transition types: zoom-in, zoom-out

            Guidelines for using zoom-in, and zoom-out transitions:
            - Zoom-in: Use to focus on important details, build tension, or show a character's point of view. Examples: revealing a clue, emphasizing a character's reaction, or creating suspense.
            - Zoom-out: Use to reveal context, end a scene, or show isolation. Examples: showing a character in a larger environment, concluding a sequence, or transitioning from a detail to a wider view.

            Important rules:
            1. Do not use zoom-in transitions when the current scene's shot size is close-up or extreme close-up.
            2. Logical consistency: Ensure camera, lighting, and composition choices match the scene content. For example:
                - Don't use two-shot for scenes with only one character.
                - Don't describe three-point lighting for a single character scene.
                - Avoid using over-the-shoulder shots when there's no dialogue.
                - Don't use natural lighting for indoor scenes without windows.
                - Ensure the camera description matches the physical space of the scene.
            3. For transitions, use ONLY the following types:
                - zoom-in
                - zoom-out
            4. DO NOT use any other transition types, including shake, dissolve, or cut.

            Output the result as a JSON object with the following structure:
            {{
                "project_info": {{
                    "title": "{title}",
                    "user": "AI Generated",
                    "timestamp": "{timestamp}"
                }},
                "storyboards": [
                    {{
                        "scene_number": "Scene Number",
                        "description": "Scene Description",
                        "subtitles": "Subtitles or Dialogue",
                        "image": null,
                        "camera": {{
                            "angle": "Camera Angle",
                            "composition_type": "Composition Type",
                            "shot_size": "Shot Size"
                        }},
                        "lighting": "Lighting Type",
                        "transition_type": "Transition Type"
                    }},
                    ...
                ]
            }}

            Here's the philosophical story:

        {story}"""

        messages = [
            {
                "role": "system",
                "content": '''You are a highly skilled storyboard artist specializing in visualizing philosophical concepts. You excel at:
                    1. Creating vivid, thought-provoking scene descriptions that translate abstract ideas into concrete imagery
                    2. Developing visual metaphors and symbols to represent complex philosophical concepts
                    3. Crafting scenes that show the progression of philosophical arguments or explorations
                    4. Incorporating basic cinematographic techniques to enhance visual storytelling of philosophical ideas
                    5. Faithfully representing the original philosophical text using exact quotes for subtitles
                    6. Ensuring the visual narrative accurately captures key philosophical points and their development
                    7. Balancing abstract concepts with concrete, relatable visual elements
                    8. Maintaining logical consistency between scenes while varying visual representations of ideas
                    9. Describing characters' clothing in detail and maintaining consistency within scenes

                    Your storyboards effectively bridge the gap between abstract philosophical concepts and visual representation, 
                    paying close attention to both the overall progression of ideas and specific details that enhance 
                    the communication of complex philosophical thoughts.'''
            },
            {"role": "user", "content": prompt},
        ]

        response = await call_openai_api(self.client, messages)
        if not response:
            logger.error("API returned empty response")
            return create_empty_storyboard(title)

        # Find the JSON part of the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                storyboard_data = json.loads(json_str)
                return storyboard_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}")
                logger.error(f"Failed to parse JSON: {json_str}")
                return create_empty_storyboard(title)
        else:
            logger.error("No JSON object found in the response")
            logger.error(f"Full response: {response}")
            return create_empty_storyboard(title)

    async def _generate_fun_facts_storyboard(self, title: str, story: str) -> Dict[str, Any]:
        max_scenes = self.config.storyboard.get('max_scenes', 12)
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        
        prompt = f"""Based on the following fun fact, create a detailed storyboard with up to {max_scenes} scenes.

            Fun Fact Title: {title}

            First, create an opening scene:
            1. Scene Number: 1
            2. Description: A vivid description (60-70 words) that sets up an engaging question related to the fun fact. 
            3. Subtitles: An engaging question that captures the essence of the fun fact and piques the viewer's interest.
            4. Camera, Lighting, and Transition: As per the guidelines below.

            Then, for each subsequent scene, provide the following details:
            1. Scene Number
            2. Description: A vivid description (60-70 words) focusing on key visual elements that illustrate different aspects of the fun fact. Include setting, characters (if applicable), and visual representations of the information.
            3. Subtitles: Use EXACT quotes from the original fun fact text. 
            4. Camera: Specify the angle, composition type, and shot size.
            5. Lighting: Describe the lighting type used.
            6. Transition: Specify the type of transition to the current scene.

            Guidelines:
            - Subtitles MUST contain only exact text from the fun fact text, without any additions, omissions, or modifications.
            - Include every sentence from the fun fact text in the subtitles, maintaining the correct order across all scenes.
            - Each subtitle must be unique; do not repeat content in multiple scenes.
            - For partial sentences at scene boundaries, include the fragment and continue it in the next scene's subtitles.
            - EVERY SCENE MUST HAVE NON-EMPTY SUBTITLES. If you run out of story text, do not create additional scenes.
            - Focus on visually representing the information, statistics, or concepts mentioned in the fun fact.
            - Use visual metaphors or analogies to help explain complex ideas if necessary.
            - Include scenes that show the real-world application or implications of the fun fact, if applicable.
            - Ensure that the scenes flow logically and build upon each other to tell a coherent visual story about the fun fact.
            - The total number of scenes should not exceed {max_scenes}.

            Use only the following options for camera, lighting, and transition details:
            - Camera: medium shot, full body shot, or wide shot
            - Lighting: natural lighting, soft lighting, or three-point lighting
            - Transition: zoom-in and zoom-out

            Guidelines for using zoom-in, and zoom-out transitions:
            - Zoom-in: Use to focus on important details, build tension, or show a character's point of view. Examples: revealing a clue, emphasizing a character's reaction, or creating suspense.
            - Zoom-out: Use to reveal context, end a scene, or show isolation. Examples: showing a character in a larger environment, concluding a sequence, or transitioning from a detail to a wider view.

            Important rules:
            1. Do not use zoom-in transitions when the current scene's shot size is close-up or extreme close-up.
            2. Logical consistency: Ensure camera, lighting, and composition choices match the scene content. For example:
                - Don't use two-shot for scenes with only one character.
                - Don't describe three-point lighting for a single character scene.
                - Avoid using over-the-shoulder shots when there's no dialogue.
                - Don't use natural lighting for indoor scenes without windows.
                - Ensure the camera description matches the physical space of the scene.
            3. For transitions, use ONLY the following types:
                - zoom-in
                - zoom-out
            4. DO NOT use any other transition types, including shake, dissolve, or cut.

            Output the result as a JSON object with the following structure:
            {{
                "project_info": {{
                    "title": "{title}",
                    "user": "AI Generated",
                    "timestamp": "{timestamp}"
                }},
                "storyboards": [
                    {{
                        "scene_number": "Scene Number",
                        "description": "Scene Description",
                        "subtitles": "Subtitles or Dialogue",
                        "image": null,
                        "camera": {{
                            "angle": "Camera Angle",
                            "composition_type": "Composition Type",
                            "shot_size": "Shot Size"
                        }},
                        "lighting": "Lighting Type",
                        "transition_type": "Transition Type"
                    }},
                    ...
                ]
            }}

            Here's the fun fact:

        {story}"""

        messages = [
            {
                "role": "system",
                "content": '''You are a highly skilled storyboard artist specializing in visualizing educational content and fun facts. You excel at:
                    1. Creating vivid, engaging scene descriptions that translate informational content into compelling visuals
                    2. Developing visual metaphors and analogies to represent complex ideas or statistics
                    3. Crafting scenes that show the real-world applications or implications of the information
                    4. Incorporating basic cinematographic techniques to enhance visual storytelling of educational content
                    5. Faithfully representing the original text using exact quotes for subtitles
                    6. Ensuring the visual narrative accurately captures key points and their development
                    7. Balancing informative content with visually interesting and engaging scenes
                    8. Maintaining logical consistency between scenes while providing a variety of visual representations

                    Your storyboards effectively bridge the gap between factual information and visual representation, 
                    paying close attention to both the overall flow of information and specific details that enhance 
                    the communication of the fun fact.'''
            },
            {"role": "user", "content": prompt},
        ]

        response = await call_openai_api(self.client, messages)
        if not response:
            logger.error("API returned empty response")
            return create_empty_storyboard(title)
        
        # Find the JSON part of the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                storyboard_data = json.loads(json_str)
                return storyboard_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}")
                logger.error(f"Failed to parse JSON: {json_str}")
                return create_empty_storyboard(title)
        else:
            logger.error("No JSON object found in the response")
            logger.error(f"Full response: {response}")
            return create_empty_storyboard(title)

    async def _generate_general_storyboard(self, title: str, story: str, character_names: List[str]) -> Dict[str, Any]:
        max_scenes = self.config.storyboard.get('max_scenes', 12)
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

        prompt = f"""Based on the following story, create a detailed storyboard with up to {max_scenes} scenes.

            Story Title: {title}
            Character full Names: {', '.join(character_names)}

            First, create an opening scene:
            1. Scene Number: 1
            2. Description: A vivid description (60-70 words) that sets up an engaging question related to the overall theme of the story. 
            3. Subtitles: An engaging question that captures the essence of the story and piques the viewer's interest.
            4. Camera, Lighting, and Transition: As per the guidelines below.

            Then, for each subsequent scene, provide the following details:
            1. Scene Number
            2. Description: A vivid description (60-70 words) focusing on key visual elements.
            3. Subtitles: Use EXACT quotes from the original story. 
            4. Camera: Specify the angle, composition type, and shot size.
            5. Lighting: Describe the lighting type used.
            6. Transition: Specify the type of transition to the current scene.

            Guidelines:
            - Subtitles MUST contain only exact text from the original story, without any additions, omissions, or modifications.
            - Include every sentence from the original story in the subtitles, maintaining the correct order across all scenes.
            - Each subtitle must be unique; do not repeat content in multiple scenes.
            - For partial sentences at scene boundaries, include the fragment and continue it in the next scene's subtitles.
            - EVERY SCENE MUST HAVE NON-EMPTY SUBTITLES. If you run out of story text, do not create additional scenes.
            - Adapt the storyboard to the specific story type (bedtime story, or other).
            - For bedtime stories, ensure the scenes are soothing and appropriate for children.
            - For other story types, capture the essence and genre of the story.
            - Select scenes that represent pivotal moments or significant changes in the story.
            - Ensure that the scenes flow logically and capture the essence of the story.
            - Describe characters' clothing in detail, ensuring consistency within scenes.
            - Cover the entire story without omitting any significant parts.
            - Use the provided character full names in the descriptions.
            - The total number of scenes should not exceed {max_scenes}.
            - When using a character's name in possessive form (e.g., "Character's") in the description, 
              surround it with double curly braces {{{{ }}}} if it's not referring to the character's appearance. 
              For example: "{{{{Giovanni's}}}} workshop" or "The mysterious figure stood at the entrance of {{{{Giovanni's}}}} laboratory."

            Use only the following options for camera, lighting, and transition details:
            - Camera angles: low angle, high angle, Dutch angle, bird's eye view, worm's eye view, eye level, canted angle
            - Composition types: single shot, two-shot, over-the-shoulder, insert shot, establishing shot
            - Shot sizes: extreme close-up, close-up, medium shot, full body shot, long shot, wide shot, extreme long shot
            - Lighting types: three-point lighting, high-key lighting, low-key lighting, natural lighting, practical lighting, motivated lighting, rim lighting, soft lighting, hard lighting, silhouette lighting
            - Transition types: zoom-in, zoom-out

            Guidelines for using zoom-in, and zoom-out transitions:
            - Zoom-in: Use to focus on important details, build tension, or show a character's point of view. Examples: revealing a clue, emphasizing a character's reaction, or creating suspense.
            - Zoom-out: Use to reveal context, end a scene, or show isolation. Examples: showing a character in a larger environment, concluding a sequence, or transitioning from a detail to a wider view.

            Important rules:
            1. Do not use zoom-in transitions when the current scene's shot size is close-up or extreme close-up.
            2. Logical consistency: Ensure camera, lighting, and composition choices match the scene content. For example:
                - Don't use two-shot for scenes with only one character.
                - Don't describe three-point lighting for a single character scene.
                - Avoid using over-the-shoulder shots when there's no dialogue.
                - Don't use natural lighting for indoor scenes without windows.
                - Ensure the camera description matches the physical space of the scene.
            3. For transitions, use ONLY the following types:
                - zoom-in
                - zoom-out
            4. DO NOT use any other transition types, including fade, dissolve, or cut.

            Output the result as a JSON object with the following structure:
            {{
                "project_info": {{
                    "title": "{title}",
                    "user": "AI Generated",
                    "timestamp": "{timestamp}"
                }},
                "storyboards": [
                    {{
                        "scene_number": "Scene Number",
                        "description": "Scene Description",
                        "subtitles": "Subtitles or Dialogue",
                        "image": null,
                        "camera": {{
                            "angle": "Camera Angle",
                            "composition_type": "Composition Type",
                            "shot_size": "Shot Size"
                        }},
                        "lighting": "Lighting Type",
                        "transition_type": "Transition Type"
                    }},
                    ...
                ]
            }}

            Here's the story:

        {story}"""

        messages = [
            {
                "role": "system",
                "content": '''You are a highly skilled storyboard artist with a keen eye for visual storytelling. You excel at:
                    1. Creating vivid, cinematic scene descriptions easily translatable into compelling images
                    2. Adapting to various story genres and styles while maintaining the original narrative's essence
                    3. Incorporating basic cinematographic techniques into your descriptions
                    4. Faithfully representing the original story using exact quotes for subtitles
                    5. Ensuring the visual narrative accurately captures key moments, emotions, and atmosphere
                    6. Describing characters' clothing in detail and maintaining consistency within scenes
                    7. Logically evolving characters' attire between scenes when appropriate
                    8. Specifying camera angles, composition types, and shot sizes
                    9. Describing appropriate lighting for each scene
                    10. Determining suitable transitions between scenes
                    11. Adhering to fundamental filmmaking rules and best practices
                    12. Maintaining logical consistency between scene content and technical descriptions

                    Your storyboards effectively bridge the gap between written narrative and visual representation, 
                    paying close attention to both the overall scene composition and specific details. You ensure 
                    that all technical descriptions (camera, lighting, composition) are logically consistent with 
                    the scene content and character presence. Most importantly, you maintain absolute fidelity to 
                    the original story text in the subtitles, using only exact quotes without any alterations.'''
            },
            {"role": "user", "content": prompt},
        ]

        response = await call_openai_api(self.client, messages)
        if not response:
            logger.error("API returned empty response")
            return create_empty_storyboard(title)
        
        # Find the JSON part of the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                storyboard_data = json.loads(json_str)
                return storyboard_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON Decode Error: {e}")
                logger.error(f"Failed to parse JSON: {json_str}")
                return create_empty_storyboard(title)
        else:
            logger.error("No JSON object found in the response")
            logger.error(f"Full response: {response}")
            return create_empty_storyboard(title)


