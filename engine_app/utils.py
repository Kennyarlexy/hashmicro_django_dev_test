from engine_app.models import RoleChoices

def get_role_name(current_role: int) -> str:
    for role, role_name in RoleChoices.choices:
        if current_role == role:
            return role_name
        
    return None