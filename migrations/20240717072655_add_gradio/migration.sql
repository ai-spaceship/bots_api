/*
  Warnings:

  - Added the required column `streaming` to the `Bot` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Bot" ADD COLUMN     "category" TEXT NOT NULL DEFAULT 'fun',
ADD COLUMN     "streaming" BOOLEAN NOT NULL;

-- CreateTable
CREATE TABLE "gradio" (
    "id" TEXT NOT NULL,
    "data" JSONB NOT NULL,

    CONSTRAINT "gradio_pkey" PRIMARY KEY ("id")
);
