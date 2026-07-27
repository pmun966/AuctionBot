from config import OWNER_IDS

def owner_only(interaction):
    return interaction.user.id in OWNER_IDS
