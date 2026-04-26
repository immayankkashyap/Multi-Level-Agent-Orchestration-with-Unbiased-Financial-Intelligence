#!/bin/bash

echo "Creating remaining backend directories and files..."

# Backend directories
mkdir -p backend/agents/debate
mkdir -p backend/graph
mkdir -p backend/api/routes
mkdir -p backend/api/models
mkdir -p backend/api/middleware
mkdir -p backend/retrieval
mkdir -p backend/database/migrations
mkdir -p backend/evaluation/fixtures
mkdir -p backend/config

# Backend files
touch backend/agents/debate/__init__.py
touch backend/agents/debate/advocate.py
touch backend/agents/debate/devil_advocate.py
touch backend/agents/judge.py

touch backend/graph/edges.py

touch backend/api/main.py
touch backend/api/routes/query.py
touch backend/api/routes/reports.py
touch backend/api/routes/auth.py
touch backend/api/models/request.py
touch backend/api/models/response.py
touch backend/api/middleware/auth_middleware.py

touch backend/database/models.py
touch backend/database/migrations/001_init.sql

touch backend/evaluation/fairness_metrics.py
touch backend/evaluation/test_scenarios.py
touch backend/evaluation/fixtures/bias_scenarios.json

touch backend/Dockerfile
touch backend/.env.example

echo "Creating frontend directories and files..."

# Frontend directories
mkdir -p frontend/app/\(auth\)/login
mkdir -p frontend/app/\(auth\)/signup
mkdir -p frontend/app/\(dashboard\)/assistant
mkdir -p frontend/app/\(dashboard\)/workflow
mkdir -p frontend/app/\(dashboard\)/spaces
mkdir -p frontend/app/api/auth/\[...nextauth\]
mkdir -p frontend/components/layout
mkdir -p frontend/components/assistant
mkdir -p frontend/components/debate
mkdir -p frontend/components/workflow
mkdir -p frontend/components/ui
mkdir -p frontend/lib
mkdir -p frontend/hooks
mkdir -p frontend/store
mkdir -p frontend/types
mkdir -p frontend/public

# Frontend files
touch frontend/app/layout.tsx
touch frontend/app/page.tsx
touch frontend/app/globals.css
touch frontend/app/\(auth\)/login/page.tsx
touch frontend/app/\(auth\)/signup/page.tsx
touch frontend/app/\(dashboard\)/layout.tsx
touch frontend/app/\(dashboard\)/assistant/page.tsx
touch frontend/app/\(dashboard\)/workflow/page.tsx
touch frontend/app/\(dashboard\)/spaces/page.tsx
touch frontend/app/api/auth/\[...nextauth\]/route.ts

touch frontend/components/layout/Sidebar.tsx
touch frontend/components/layout/SidebarNav.tsx
touch frontend/components/layout/TopBar.tsx

touch frontend/components/assistant/ChatWindow.tsx
touch frontend/components/assistant/MessageBubble.tsx
touch frontend/components/assistant/ThinkingIndicator.tsx
touch frontend/components/assistant/ThinkingDropdown.tsx
touch frontend/components/assistant/QueryInput.tsx

touch frontend/components/debate/DebateDocument.tsx
touch frontend/components/debate/AdvocatePane.tsx
touch frontend/components/debate/DevilPane.tsx
touch frontend/components/debate/BiasReport.tsx

touch frontend/components/workflow/WorkflowCanvas.tsx
touch frontend/components/workflow/WorkflowNode.tsx
touch frontend/components/workflow/WorkflowEdge.tsx
touch frontend/components/workflow/NodePalette.tsx

touch frontend/lib/api.ts
touch frontend/lib/websocket.ts
touch frontend/lib/firebase.ts
touch frontend/lib/utils.ts

touch frontend/hooks/useQuery.ts
touch frontend/hooks/useWebSocket.ts
touch frontend/hooks/useWorkflow.ts

touch frontend/store/queryStore.ts

touch frontend/types/index.ts

touch frontend/next.config.js
touch frontend/tailwind.config.js
touch frontend/tsconfig.json
touch frontend/package.json

echo "Done! All remaining files and folders have been created."
