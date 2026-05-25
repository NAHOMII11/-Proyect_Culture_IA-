#!/bin/bash
# AI Assistant API Gateway Integration - Quick Test Script

echo "🚀 AI Assistant API Gateway Integration Tests"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if services are running
echo -e "${BLUE}1. Checking Gateway Health...${NC}"
curl -s http://localhost:8000/health | jq . || echo "❌ Gateway not responding"
echo ""

echo -e "${BLUE}2. Checking AI Assistant Health (via Gateway)...${NC}"
curl -s http://localhost:8000/api/v1_aiassistant/aiassistant/health | jq . || echo "❌ AI Assistant not responding"
echo ""

echo -e "${BLUE}3. Testing Chat Endpoint (via Gateway)...${NC}"
curl -X POST http://localhost:8000/api/v1_aiassistant/aiassistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-001",
    "query_text": "What is cultural heritage?"
  }' | jq . || echo "❌ Chat endpoint failed"
echo ""

echo -e "${BLUE}4. Getting Chat History (via Gateway)...${NC}"
curl -s 'http://localhost:8000/api/v1_aiassistant/aiassistant/chat?user_id=test-user-001' | jq . || echo "❌ History endpoint failed"
echo ""

echo -e "${GREEN}✅ Integration tests complete!${NC}"
echo ""
echo "📝 Documentation files:"
echo "  - API_AIASSISTANT_GATEWAY.md - Frontend integration guide"
echo "  - GATEWAY_INTEGRATION_SUMMARY.md - Summary of changes"
echo "  - API_DOCUMENTATION.md - Complete API documentation"
