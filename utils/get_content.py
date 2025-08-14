def get_content(msg):
    try:
        return msg["content"]
    except (TypeError, KeyError):
        return msg.content