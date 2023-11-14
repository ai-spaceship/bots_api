from prisma.models import Post

Post.create_partial('Bots', include={'bot_username'})