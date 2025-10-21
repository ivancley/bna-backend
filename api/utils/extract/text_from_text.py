from dotmap import DotMap


def extract_text_from_conversation(data: DotMap) -> str:
    return data.data.message.conversation