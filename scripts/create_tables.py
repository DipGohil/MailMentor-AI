from app.dependencies import Base, engine
from app.models.email_model import Email
from app.models.action_model import Action

Base.metadata.create_all(bind = engine)

print("Tables created successfully!")