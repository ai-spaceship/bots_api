-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "username" TEXT NOT NULL,
    "email_id" TEXT NOT NULL,
    "bot_username" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "api_key" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "desc" TEXT NOT NULL,
    "profile_photo" TEXT,
    "access_token" TEXT NOT NULL,
    "publish" BOOLEAN NOT NULL,
    "tags" TEXT[],
    "avatar_mxc" TEXT,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);
