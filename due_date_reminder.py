################################################################################
# 
# Weekly Due Date Reminders
# Author: Josh Avery
# Date Created: 8/28/21
#
################################################################################
import pandas as pd
import os
from twilio.rest import Client
import datetime
from dotenv import load_dotenv
load_dotenv() # Loads local environment variables

# Environment variables
ACC_SID = os.getenv('TWILIO_ACCOUNT_SID')
TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
MESSAGING_SERVICE_SID = os.getenv('MESSAGE_SERVICE_SID')
PHONE = os.getenv('TO_PHONE')
FILE = os.getenv('FILE_NAME')

# Establish connection
client = Client(ACC_SID, TOKEN)

MY_CLASSES = ["Big Data", "Analysis", "Finance", "Data Mining", "Business Intel", "Technical Writing"]

def main():
    """
        Delivers formatted assignemnt due dates via SMS for the next week.
    """
    # Read in the data
    all_data = pd.read_excel(FILE)

    # Create empty dataframe for this week's assignemnts
    this_weeks_assignments = pd.DataFrame(columns = all_data.columns)

    # Convert due dates from default assumed type TimeStamp to datetime.date
    for this_date in all_data["Due Date"]:
        all_data.loc[(all_data["Due Date"] == this_date), ["Due Date"]] = this_date.date()

    today = datetime.date.today()
    one_day = datetime.timedelta(days = 1)

    # Collect all the assignments for the next week into this_weeks_assignments
    for days in range(1,8):
        due_today = today + (one_day*days)
        frames = [this_weeks_assignments, all_data.loc[all_data["Due Date"] == due_today]]
        this_weeks_assignments = pd.concat(frames)

    
    # Header text announcing the dates
    message_block = f"{len(this_weeks_assignments)} ASSIGNMNTS DUE FROM {today} TO {today + one_day*7}:"
    # print(message_block)
    message = client.messages.create(  
                            messaging_service_sid = MESSAGING_SERVICE_SID, 
                            body = "- - - - - " + message_block,      
                            to = PHONE) 
                                            

    # Have a separate text for each class.
    for this_class in MY_CLASSES:
        if not this_weeks_assignments.loc[this_weeks_assignments["Class"] == this_class].empty:
            class_assignments = pd.DataFrame(data = this_weeks_assignments.loc[this_weeks_assignments["Class"] == this_class])
            message_block = f"{this_class} Assignments: \n"
            for index in class_assignments.index:
                message_block = message_block + f"""\t- {class_assignments.loc[index, 'Assignment Title']}: Due on {class_assignments.loc[index, 'Due Date'].strftime('%A')}. \n"""
            # print(message_block)
            message = client.messages.create(  
                                        messaging_service_sid = MESSAGING_SERVICE_SID, 
                                        body = "- - - - - " + message_block,      
                                        to = PHONE
                                        )

    # Give the total estimated work time for the week
    sum_of_time = sum(this_weeks_assignments['Est. Time (Hrs)'])
    message_block = f"Total Estimated work time this week: {sum_of_time} Hours"
    # print(message_block)
    message = client.messages.create(  
                                            messaging_service_sid = MESSAGING_SERVICE_SID, 
                                            body = "- - - - - " + message_block,      
                                            to = PHONE
                                            )
# Run the program
if __name__ == "__main__":
    main()