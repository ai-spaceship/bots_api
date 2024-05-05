-- CreateTable
CREATE TABLE "Workflow" (
    "id" TEXT NOT NULL,
    "username" TEXT NOT NULL,
    "yaml" TEXT NOT NULL,
    "count" INTEGER NOT NULL,

    CONSTRAINT "Workflow_pkey" PRIMARY KEY ("id")
);
