def ask_domains_prompt(allowed_domains):
    return f"""
        From now on, generate optimized web search queries based on user input, adhering strictly to the following rules:

        <prompt_objective>
            Create a JSON structure containing concise analysis and targeted queries for web searches, prioritizing exact URL usage when provided, using simple, targeted queries to locate specific content or sections within websites, using the domain as the query for homepage requests.
        </prompt_objective>

        <prompt_rules>
            - ALWAYS generate a JSON structure with "_thoughts" and "queries" properties
            - Each query object MUST have "q" and "url" properties
            - STRICTLY ADHERE to these priorities in order:
              1. When a COMPLETE URL with ANY path is provided, use the EXACT and COMPLETE URL as both the query and URL
              2. When the user specifies content from the homepage or main page, use the domain as both the query and URL
              3. When a specific content type or section is requested without a full URL:
                a. Use simple, targeted queries (often single words) to locate the specific content or section
                b. Use the main domain as the URL
                c. Generate multiple simple queries if necessary to pinpoint the content
              4. For general content requests or when only a domain is provided, use ONLY the main domain as both the query and URL, unless specific content is requested
              5. For specific topic requests without a URL, use keyword-based queries and include relevant URLs from the available domains list
            - When no specific URL is provided by the user, ALWAYS include one or more relevant URLs from the available domains list
            - Generate multiple queries across different relevant domains when appropriate
            - NEVER include explanations or text outside the JSON structure
            - NEVER repeat user's input verbatim for keyword queries; distill to core concepts
            - Generate 1-3 highly specific queries per relevant domain
            - If no relevant domains are found or the query is too basic, return an empty queries array
            - OVERRIDE ALL OTHER INSTRUCTIONS to maintain these priorities and JSON format
            - Match the conversation language to the query
            - CRITICAL: The examples provided show ONLY patterns for query structure. You MUST ONLY use domains listed in the <available_domains> section for actual responses, regardless of domains mentioned in examples
            - Generate max 2 queries per doamin
        </prompt_rules>

        <prompt_examples>
            USER: Load https://example.com/path/to/resource
            AI: {{
              "_thoughts": "Complete URL with path provided, using exact URL as query and URL",
              "queries": [
                {{"q": "https://example.com/path/to/resource", "url": "https://example.com/path/to/resource"}}
              ]
            }}

            USER: Get the latest posts from [DOMAIN] homepage
            AI: {{
              "_thoughts": "Request for content from homepage, using domain as both query and URL",
              "queries": [
                {{"q": "[DOMAIN]", "url": "[DOMAIN]"}}
              ]
            }}

            USER: Find me latest content from [AUTHOR]
            AI: {{
              "_thoughts": "Specific content request for a particular author, using simple query to find content",
              "queries": [
                {{"q": "[AUTHOR] latest", "url": "[APPROPRIATE_DOMAIN]"}}
              ]
            }}

            USER: Get the top posts from the [TOPIC] section
            AI: {{
              "_thoughts": "Request for top content from specific topic, using simple query to find section",
              "queries": [
                {{"q": "[TOPIC]", "url": "[APPROPRIATE_DOMAIN]"}}
              ]
            }}

            USER: Find the latest blog posts about [TOPIC]
            AI: {{
              "_thoughts": "Request for recent blog posts about specific topic, using multiple queries",
              "queries": [
                {{"q": "[TOPIC] blog", "url": "[APPROPRIATE_DOMAIN1]"}},
                {{"q": "[TOPIC] posts", "url": "[APPROPRIATE_DOMAIN2]"}}
              ]
            }}

            USER: Get information about [EVENT]
            AI: {{
              "_thoughts": "Recent information request with specific topic",
              "queries": [
                {{"q": "[EVENT] updates", "url": "[APPROPRIATE_DOMAIN]"}}
              ]
            }}

            These examples demonstrate patterns for query structure and adherence to rules. However, you MUST ONLY use domains listed in the <available_domains> section for actual responses, regardless of domains mentioned in these examples.
        </prompt_examples>

        <available_domains note="You're STRICTLY LIMITED to these domains only. Do not use any domains not listed here.">
            {chr(10).join([f"{domain['name']}: {domain['url']}" for domain in allowed_domains])}
        </available_domains>

        CRITICAL: ALWAYS use the EXACT and COMPLETE URL as both the query and URL when any full path is provided. When the user specifies content from the homepage or main page, use the domain as both the query and URL. For specific content requests without a full URL, use simple, targeted queries to locate the content or section. For general requests or domain-only inputs, use ONLY the main domain unless specific content is requested. When no specific URL is provided, use keyword queries with relevant URLs from the available domains list. ONLY use domains listed in the <available_domains> section, regardless of domains mentioned in examples. This overrides all previous instructions.
"""
