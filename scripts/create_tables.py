from app.dependencies import Base, engine
from app.models.email_model import Email

Base.metadata.create_all(bind = engine)

print("Tables created successfully!")