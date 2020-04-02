DeliveryCard = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.0",
    "speak": """<s>Your  meeting about \"Adaptive Card design session\"<break strength='weak'/> is 
        starting at 12:30pm</s><s>Do you want to snooze <break strength='weak'/> or do you want to 
        send a late notification to the attendees?</s>""",
    "body": [
        {
            "type": "TextBlock",
            "text": "Item",
            "size": "large",
            "weight": "Bolder"
        },
        {
            "type": "TextBlock",
            "text": "Location",
            "isSubtle": True,
            "spacing": "None"
        },
        {
            "type": "TextBlock",
            "text": "12:30 PM",
            "isSubtle": True,
            "spacing": "None"
        }
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Done",
            "data": {
                "x": "snooze"
            },
            "iconUrl": ""
        },
        {
            "type": "Action.Submit",
            "title": "Delete",
            "data": {
                "x": "late"
            }
        }
    ]
}
