
# Problem Statement
NL Request to converted to plan. The plan will be used to execute tools for the task.task may be a success or failure.The failute may be due to tool call time out or error.cancel_order tool has 20% failure rate(simulated) once that is done we shoulnot send mail.
# Need
 - An event driven procesing architecture
 - Basic Planner,Orchestrator,Executor with Guardrails.

 #  First things First
 - A basic scaffold
 - Input-string of user NL english string.
 - Output- A structured list of actions i.e. a plan.
 - Need to parse the string . Will go for some regex based parsing for now.Can add openAI api later.
 - List of actions/Plan that wil be formed will be a simple DAG.