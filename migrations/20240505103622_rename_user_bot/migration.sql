/*
  Warnings:

  - You are about to drop the `User` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropTable
DROP TABLE "User";

-- CreateTable
CREATE TABLE "Bot" (
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
    "prompt" TEXT,
    "llmModel" TEXT,

    CONSTRAINT "Bot_pkey" PRIMARY KEY ("id")
);
