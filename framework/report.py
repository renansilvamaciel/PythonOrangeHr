
from framework.state import STATE
import jinja2
import logging

logger = logging.getLogger(__name__)

'''
report.py
    Generates a report with the summary of the automation process.
'''



def generate_jinja_report():
    environment = jinja2.Environment()
    template = environment.from_string(""" 
                                       <!DOCTYPE html>
<html>
<head>
    <style>
        body {font-family: Arial, sans-serif; margin: 0 auto; width: 650px; background-color: #f4f4f4;}
        .container {border: 1px solid #ddd; padding: 20px; background-color: white;}
    </style>
</head>
<body>
    <div class="container">
        <h2>Task Completed - BotCity Process Notification</h2>
        <p><b>Process:</b> {{automation_name}}</p>
        <p><b>Description:</b> {{automation_description}} </p>
        <hr />
        <h3>Task Summary</h3>
        <blockquote>
            <p>In our run for <b>task {{ task_id }}</b> we processed <b>{{total_items}}</b> items, from which <b>{{ success_count }}</b> were with success.
        </blockquote>
        <p>For more details, access the BotCity Orchestrator Task <a href="{{server}}/task/{{ task_id }}">here</a></p>
		<p>If you have any questions, please reach out to {{ email_responsible}}</p>
        <hr />
        <p><small><i>This is an automated email. Do not reply to this message.</small></p></i>
    </div>
</body>
</html>
                                       """)
    return template.render(**STATE.as_dict(),
                           total_items=STATE.total_items,
                           server=STATE.maestro.server,
                           automation_name=STATE.maestro.get_task(
                               STATE.task_id).activity_name,
                           automation_description="TODO fetch info",
                           # STATE.maestro.get_execution(STATE.task_id).parameters.get("email_responsible"),
                           email_responsible="email TODO change"
                           )
