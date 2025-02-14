from datetime import datetime


def generate_params_prompt(state, tool_info, query):
    return {
        "role": "system",
        "content": f"""
            Generate specific parameters for the "{tool_info['name']}" tool.
            <context>
                <current_date>
                    Current date: ${datetime.now().isoformat()}
                </current_date>
                Tool description: {tool_info['description']}
                Required parameters: {tool_info['parameters']}
                Original query: {query}
                Last message: "{state["messages"][-1]['content'] if state["messages"] else ''}"
                Previous actions: {', '.join([f"{a['name']}: {a['parameters']}" for a in state["actions"]])}
                Previous actions results: {', '.join([
                                              f"{a['name']}: " + "\n, ".join([
                                                  f"source: {r['metadata']['source']}, name: {r['metadata']['name']}, description: {r['metadata']['description']}"
                                                  for r in a['results'] if isinstance(a['results'], list) and 'metadata' in r
                                              ])
                                              for a in state["actions"]
                                          ])}
            </context>

            Respond with ONLY a JSON object matching the tool's parameter structure.
            Example for web_search: {{"query": "specific search query"}}
            Example for final_answer: {{"answer": "detailed response"}}
            Example for mailer: {{"title": "email subject", "content": "Email body. Make sure to format it as a proper email with courteses like Hello, Best Wises. The sender name should be Arsen Uhliar. Take into consideration results of previous actions.", "address": "recipient email"}}
        """,
    }
