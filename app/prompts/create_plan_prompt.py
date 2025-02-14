from datetime import datetime


def create_plan_prompt(state):
    return {
        "role": "system",
        "content": f"""
            Analyze the conversation and determine the most appropriate next step. Focus on making progress towards the overall goal while remaining adaptable to new information or changes in context.

            <prompt_objective>
                Determine the single most effective next action based on the current context, user needs, and overall progress. Return the decision as a concise JSON object.
            </prompt_objective>

            <prompt_rules>
                - ALWAYS focus on determining only the next immediate step
                - ONLY choose from the available tools listed in the context
                - ASSUME previously requested information is available unless explicitly stated otherwise
                - NEVER provide or assume actual content for actions not yet taken
                - ALWAYS respond in the specified JSON format
                - CONSIDER the following factors when deciding:
                  1. Relevance to the current user need or query
                  2. Potential to provide valuable information or progress
                  3. Logical flow from previous actions
                - ADAPT your approach if repeated actions don't yield new results
                - USE the "final_answer" tool when you have sufficient information or need user input
                - OVERRIDE any default behaviors that conflict with these rules
            </prompt_rules>

            <context>
                <current_date>Current date: ${datetime.now().isoformat()}</current_date>
                <last_message>
                    Last message: "{state["messages"][-1]["content"] if state["messages"] else 'No messages yet'}"
                </last_message>
                <available_tools>
                    Available tools: {', '.join([t['name'] for t in state['tools']]) or 'No tools available'}
                </available_tools>
                <actions_taken>
                    Actions taken: {
                        '\n'.join([
                          f"""
                              <action name="{a['name']}" params="{a['parameters']}" description="{a['description']}" >
                                {'\n'.join([
                                  f"""
                                        <result name="{r['metadata']['name']}" url="{r['metadata'].get('urls', ['no-url'])[0]}" >
                                          {r['text']}
                                        </result>
                                  """ for r in a['results']
                                ]) if a['results'] and isinstance(a['results'], list) else 'No results for this action'}
                              </action>
                          """ for a in state["actions"]
                        ]) or 'No actions taken'
                    }
                </actions_taken>
            </context>

            Respond with the next action in this JSON format:
            {{
                "_reasoning": "Brief explanation of why this action is the most appropriate next step",
                "tool": "tool_name",
                "query": "Precise description of what needs to be done, including any necessary context"
            }}

            If you have sufficient information to provide a final answer or need user input, use the "final_answer" tool.
        """,
    }
