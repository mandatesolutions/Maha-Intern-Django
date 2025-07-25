def get_room_name(user1_id, user2_id):
    return f"room_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"