from prisma.models import Post
from pydantic import BaseModel

Post.create_partial('Bots', include={'bot_username'})